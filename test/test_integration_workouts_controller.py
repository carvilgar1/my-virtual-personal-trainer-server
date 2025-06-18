import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import jwt
from flask import Flask, json

from src.common.domain.user_credentials import UserCredentials
from src.workouts.controllers.controllers import workouts_blueprint
from src.workouts.domain.workouts import Workout


class TestIntegrationWorkoutsController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(workouts_blueprint)
        self.client = self.app.test_client()

        user_payload = {
            'sub': '123',
            'username': 'usertest',
            'email': 'usertest2@usertest.com',
            'iat': int(datetime.now().timestamp()),
            'exp': int(datetime.now().timestamp() + 86400)
        }
        self.refresh_token = jwt.encode(
            user_payload, os.environ['SECRET_KEY'], algorithm='HS256')
        self.auth_header = {'Authorization': f'Bearer {self.refresh_token}'}

    @patch('src.token_auth.application.validations.validate_bearer_token')
    def test_save_workouts_success(self, mock_validate_token):
        # Preparar mocks
        mock_validate_token.return_value = ('valid_token', None)

        mock_user = MagicMock()
        mock_user.username = 'testuser'

        from src.workouts.controllers import controllers

        # Forzar que el decorador ya aplicado use el mock
        with patch.object(controllers, 'authentication_service') as mock_auth_service, \
                patch.object(controllers, 'workouts_repository') as mock_repo:

            mock_auth_service.authenticate.return_value = mock_user
            mock_repo.save_many.return_value = None

            data = [
                {
                    "duration": 20,
                    "intensity": 3,
                    "sleepScore": 80,
                    "startTime": "2025-07-09T14:48:00.00000Z"
                }
            ]

            headers = self.auth_header
            response = self.client.post(
                '/workouts/',
                data=json.dumps(data),
                content_type='application/json',
                headers=headers
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['status'], 'Success')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_save_workouts_partial_success(self, mock_repo):
        mock_repo.save_many.return_value = None
        data = [
            {
                "duration": 20,
                "intensity": 3,
                "sleepScore": 80,
                "startTime": "2025-07-09T14:48:00.00000Z"
            },
            {"startTime": "bad-date", "duration": "bad", "averageHeartRate": "bad"}
        ]
        with self.app.test_request_context():
            response = self.client.post(
                '/workouts/', data=json.dumps(data), content_type='application/json', headers=self.auth_header)
        self.assertEqual(response.status_code, 207)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Warning')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_save_workouts_all_invalid(self, mock_repo):
        data = [
            {"startTime": "bad-date", "duration": "bad", "averageHeartRate": "bad"}
        ]
        with self.app.test_request_context():
            response = self.client.post(
                '/workouts/', data=json.dumps(data), content_type='application/json', headers=self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_save_workouts_empty_list(self, mock_repo):
        data = []
        with self.app.test_request_context():
            response = self.client.post(
                '/workouts/', data=json.dumps(data), content_type='application/json', headers=self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_save_workouts_exception(self, mock_repo):
        mock_repo.save_many.side_effect = Exception('Test exception')
        data = [{
            "duration": 20,
            "intensity": 3,
            "sleepScore": 80,
            "startTime": "2025-07-09T14:48:00.00000Z"
        }]
        with self.app.test_request_context():
            response = self.client.post(
                '/workouts/', data=json.dumps(data), content_type='application/json', headers=self.auth_header)
        self.assertEqual(response.status_code, 500)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_get_workouts_success(self, mock_repo):
        worwout_mock = MagicMock(spec=Workout)
        worwout_mock.to_json.return_value = {
            'startTime': '2024-01-05T10:00:00Z',
            'duration': 30,
            'averageHeartRate': 120
        }
        mock_repo.retrieve_workouts_by_dates.return_value = [worwout_mock]
        with self.app.test_request_context():
            response = self.client.get('/workouts/', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Success')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_get_workouts_by_dates_success(self, mock_repo):
        worwout_mock = MagicMock(spec=Workout)
        worwout_mock.to_json.return_value = {
            'startTime': '2024-01-05T10:00:00Z',
            'duration': 30,
            'averageHeartRate': 120
        }
        mock_repo.retrieve_workouts_by_dates.return_value = [worwout_mock]
        with self.app.test_request_context():
            response = self.client.get(
                '/workouts/?dateFrom=2024-01-01&dateTo=2024-01-10', headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Success')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_get_workouts_by_dates_invalid_date(self, mock_repo):
        mock_repo.retrieve_workouts_by_dates.return_value = []
        with self.app.test_request_context():
            response = self.client.get(
                '/workouts/?dateFrom=invalid&dateTo=2024-01-10', headers=self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_get_workouts_by_dates_range_exceeded(self, mock_repo):
        with self.app.test_request_context():
            response = self.client.get(
                '/workouts/?dateFrom=2020-01-01&dateTo=2024-01-10', headers=self.auth_header)
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.workouts.controllers.controllers.workouts_repository')
    def test_get_workouts_exception(self, mock_repo):
        mock_repo.retrieve_workouts.side_effect = Exception('Test exception')
        with self.app.test_request_context():
            response = self.client.get('/workouts/', headers=self.auth_header)
        self.assertEqual(response.status_code, 500)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'Error')


if __name__ == "__main__":
    unittest.main()

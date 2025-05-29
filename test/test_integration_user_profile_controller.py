import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import jwt
from flask import Flask, json

from src.common.domain.user_credentials import UserCredentials
from src.user_profile.controllers.controllers import user_blueprint
from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfile)


class TestIntegrationUserProfileController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(user_blueprint)
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

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_save_user_profile_success(self, mock_repo):
        mock_repo.save.return_value = None
        mock_repo.find.return_value = UserProfile(
            birth_date=datetime(1990, 1, 1),
            weight=70,
            height=175,
            max_heart_rate=190,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )
        data = {
            "birthDate": "1990-01-01",
            "weight": "70",
            "height": "175",
            "maxHeartRate": "190",
            "gender": "MALE",
            "activityLevel": "MODERATELY_ACTIVE"
        }
        with self.app.test_request_context():
            response = self.client.post('/user/', data=json.dumps(data), content_type='application/json', headers={
                                        'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 201)
        self.assertIn('status', response.json)

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_save_user_profile_invalid_form(self, mock_repo):
        mock_repo.save.return_value = None
        data = {}  # Formulario vacío
        with self.app.test_request_context():
            response = self.client.post('/user/', data=json.dumps(data), content_type='application/json', headers={
                                        'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_save_user_profile_exception(self, mock_repo):
        mock_repo.save.side_effect = Exception('Test exception')
        data = {
            "birthDate": "1990-01-01",
            "weight": "70",
            "height": "175",
            "maxHeartRate": "190",
            "gender": "MALE",
            "activityLevel": "MODERATELY_ACTIVE"
        }
        with self.app.test_request_context():
            response = self.client.post('/user/', data=json.dumps(data), content_type='application/json', headers={
                                        'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['status'], 'Error')
        self.assertEqual(response.json['error']
                         ['code'], 'INTERNAL_SERVER_ERROR')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_update_user_profile_exception(self, mock_repo):
        mock_repo.save.side_effect = Exception('Test exception')
        data = {
            "weight": "70",
            "height": "175"
        }
        with self.app.test_request_context():
            response = self.client.put('/user/', data=json.dumps(data), content_type='application/json',
                                       headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['status'], 'Error')
        self.assertEqual(response.json['error']
                         ['code'], 'INTERNAL_SERVER_ERROR')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_get_user_profile_exception(self, mock_repo):
        mock_repo.find.side_effect = Exception('Test exception')
        with self.app.test_request_context():
            response = self.client.get(
                '/user/', headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['status'], 'Error')
        self.assertEqual(response.json['error']
                         ['code'], 'INTERNAL_SERVER_ERROR')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_get_user_profile_not_completed_error(self, mock_repo):

        mock_profile = UserProfile(
            birth_date=datetime(1990, 1, 1),
            weight=70,
            height=175,
            max_heart_rate=190
        )
        mock_repo.find.return_value = mock_profile
        with self.app.test_request_context():
            response = self.client.get(
                '/user/', headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['status'], 'Error')
        self.assertEqual(response.json['error']
                         ['code'], 'USER_PROFILE_NOT_COMPLETED')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_delete_user_profile_exception(self, mock_repo):
        mock_repo.delete.side_effect = Exception('Test exception')
        with self.app.test_request_context():
            response = self.client.delete(
                '/user/', headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['status'], 'Error')
        self.assertEqual(response.json['error']
                         ['code'], 'INTERNAL_SERVER_ERROR')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_update_user_profile_success(self, mock_repo):
        mock_repo.update.return_value = None
        mock_repo.find.return_value = UserProfile(
            birth_date=datetime(1990, 1, 1),
            weight=75,
            height=175,
            max_heart_rate=190,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )
        data = {
            "weight": "75"
        }
        with self.app.test_request_context():
            response = self.client.put('/user/', data=json.dumps(data), content_type='application/json',
                                       headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json)

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_retrieve_user_profile_success(self, mock_repo):
        mock_profile = UserProfile(
            birth_date=datetime(1990, 1, 1),
            weight=70,
            height=175,
            max_heart_rate=190,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )
        mock_repo.find.return_value = mock_profile
        with self.app.test_request_context():
            response = self.client.get(
                '/user/', headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json)

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_retrieve_user_profile_not_found(self, mock_repo):
        mock_repo.find.return_value = None
        with self.app.test_request_context():
            response = self.client.get(
                '/user/', headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['status'], 'Error')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_delete_user_profile_success(self, mock_repo):
        mock_repo.delete.return_value = None
        with self.app.test_request_context():
            response = self.client.delete(
                '/user/', headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'Deleted')

    @patch('src.user_profile.controllers.controllers.user_profile_repository')
    def test_update_user_profile_invalid_form(self, mock_repo):
        mock_repo.update.return_value = None
        data = {"weight": "not_a_float"}
        with self.app.test_request_context():
            response = self.client.put('/user/', data=json.dumps(data), content_type='application/json',
                                       headers={'Authorization': 'Bearer ' + self.refresh_token})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'Error')


if __name__ == '__main__':
    unittest.main()

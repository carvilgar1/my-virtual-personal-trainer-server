import os
import unittest
from datetime import datetime
from unittest.mock import patch

import bcrypt
import jwt
from flask import Flask

from src.common.domain.user_credentials import UserCredentials
from src.token_auth.controllers.controllers import (handle_new_token_request,
                                               handle_refresh_token_request)


class TestIntegrationTokenControllerBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure virtual DB
        default_user = UserCredentials(
            '123', 'usertest@usertest.com', 'usertest', bcrypt.hashpw(b'T3stP@ss', bcrypt.gensalt()))

        def get_existing_user_side_effect(*args, **kwargs):
            if args and (args[0] == default_user.username or args[1] == default_user.email):
                return default_user
            else:
                return None

        cls.mock_find_user_patch = patch(
            'src.token_auth.controllers.controllers.user_credentials_repository.find_by_username_or_email')
        cls.mock_find_user = cls.mock_find_user_patch.start()
        cls.mock_find_user.side_effect = get_existing_user_side_effect

    @classmethod
    def tearDownClass(cls):
        cls.mock_find_user_patch.stop()


class TestHandleNewTokenTokenRequestIntegration(TestIntegrationTokenControllerBase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule(
            '/token/new',
            'handle_new_token_request',
            handle_new_token_request,
            methods=['POST']
        )

    def test_handle_new_token_request_success(self):
        with self.client as client:
            response = client.post(
                '/token/new',
                data={
                    'username': 'usertest',
                    'password': 'T3stP@ss',
                    'email': 'usertest@usertest.com'
                }
            )

        self.assertEqual(response.status, '200 OK')
        self.assertIsNotNone(response.json)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)
        self.assertIn('expires_in', response.json)
        self.assertEqual('Bearer', response.json['token_type'])

    def test_handle_new_token_request_invalid_user_credentials(self):
        with self.client as client:
            response = client.post(
                '/token/new',
                data={
                    'username': 'other',
                    'password': 'T3stP@ss',
                    'email': 'other@usertest.com'
                }
            )

        self.assertEqual(response.status, '401 UNAUTHORIZED')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('INVALID_USER_CREDENTIALS',
                         response.json['error']['code'])

    def test_handle_new_token_request_invalid_form_data(self):
        with self.client as client:
            response = client.post(
                '/token/new',
                data={
                    'email': 'usertest@usertest.com'
                }
            )

        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('FORM_CONTAINS_ERRORS',
                         response.json['error']['code'])
        self.assertEqual('The form contains errors',
                         response.json['error']['message'])

    def test_handle_new_token_request_invalid_form_localized_response(self):
        with self.client as client:
            response = client.post(
                '/token/new?lang=es',
                data={
                    'email': 'usertest@usertest.com'
                }
            )

        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('FORM_CONTAINS_ERRORS',
                         response.json['error']['code'])
        self.assertEqual('El formulario contiene errores',
                         response.json['error']['message'])

    @patch('src.token_auth.controllers.controllers.user_credentials_repository.find_by_username_or_email')
    def test_handle_new_token_request_raises_exception(self, mock_find_user):
        mock_find_user.side_effect = Exception('Test exception')

        with self.client as client:
            response = client.post(
                '/token/new?lang=es',
                data={
                    'username': 'usertest',
                    'password': 'T3stP@ss',
                    'email': 'usertest@usertest.com'
                }
            )

        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('INTERNAL_SERVER_ERROR',
                         response.json['error']['code'])


class TestHandleRefreshTokenRequestIntegration(TestIntegrationTokenControllerBase):
    def setUp(self):
        self.refresh_key = os.environ['REFRESH_KEY']

        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.app.add_url_rule(
            '/token/refresh',
            'handle_refresh_token_request',
            handle_refresh_token_request,
            methods=['POST']
        )

    def test_handle_refresh_token_request_success(self):
        user_payload = {
            'sub': '123',
            'username': 'usertest',
            'email': 'usertest2@usertest.com',
            'iat': int(datetime.now().timestamp()),
            'exp': int(datetime.now().timestamp() + 86400)
        }
        refresh_token = jwt.encode(
            user_payload, self.refresh_key, algorithm='HS256')

        with self.client as client:
            response = client.post(
                '/token/refresh?lang=es',
                headers={'Authorization': f'Bearer {refresh_token}'}
            )

        self.assertEqual(response.status, '200 OK')
        self.assertIsNotNone(response.json)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)
        self.assertIn('expires_in', response.json)
        self.assertEqual('Bearer', response.json['token_type'])

    def test_handle_refresh_token_request_null_authorization_error(self):
        with self.client as client:
            response = client.post(
                '/token/refresh?lang=es'
            )

        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('INVALID_AUTHORIZATION_HEADER',
                         response.json['error']['code'])

    def test_handle_refresh_token_request_invalid_authorization_type(self):
        with self.client as client:
            response = client.post(
                '/token/refresh?lang=es',
                headers={'Authorization': 'Basic some'}
            )

        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('INVALID_AUTHORIZATION_TYPE',
                         response.json['error']['code'])

    def test_handle_refresh_token_request_invalid_token(self):
        with self.client as client:
            response = client.post(
                '/token/refresh?lang=es',
                headers={'Authorization': 'Bearer wrong_token'}
            )

        self.assertEqual(response.status, '401 UNAUTHORIZED')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('INVALID_TOKEN', response.json['error']['code'])

    @patch('src.token_auth.controllers.controllers.user_credentials_repository.find_by_username_or_email')
    def test_handle_refresh_token_request_raises_exception(self, mock_find_user):
        mock_find_user.side_effect = Exception('Test exception')

        user_payload = {
            'sub': '123',
            'username': 'usertest',
            'email': 'usertest2@usertest.com',
            'iat': int(datetime.now().timestamp()),
            'exp': int(datetime.now().timestamp() + 86400)
        }
        refresh_token = jwt.encode(
            user_payload, self.refresh_key, algorithm='HS256')

        with self.client as client:
            response = client.post(
                '/token/refresh?lang=es',
                headers={'Authorization': f'Bearer {refresh_token}'}
            )

        self.assertEqual(response.status, '500 INTERNAL SERVER ERROR')
        self.assertIsNotNone(response.json)
        self.assertIsNotNone(response.json['error'])
        self.assertEqual('INTERNAL_SERVER_ERROR',
                         response.json['error']['code'])


if __name__ == '__main__':
    unittest.main()

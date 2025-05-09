import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import jwt
from flask import Flask

from src.common.domain import Status, UserCredentials
from src.constants import CommonErrorCodes, TokenErrorCodes
from src.token_auth.application.authentication import (AuthenticationService,
                                                  JWTAuthenticationService,
                                                  authorization_required)


class TestAuthorizationRequiredMiddleware(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.mock_auth_service = MagicMock(AuthenticationService)

    @patch('src.token_auth.application.authentication.validate_bearer_token')
    def test_authorization_required_valid_token(self, mock_validate_bearer_token):
        mock_validate_bearer_token.return_value = ('valid_token', None)
        user_credentials_mock = MagicMock(UserCredentials)
        user_credentials_mock.username = 'testuser'
        self.mock_auth_service.authenticate.return_value = user_credentials_mock

        @self.app.route('/protected')
        @authorization_required(self.mock_auth_service)
        def protected_route(current_user):
            return {'message': 'Access granted', 'user': current_user.username}, 200

        headers = {'Authorization': 'Bearer valid_token'}
        response = self.client.get('/protected', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Access granted', response.json['message'])
        self.assertIn(user_credentials_mock.username, response.json['user'])

    @patch('src.token_auth.application.authentication.validate_bearer_token')
    def test_authorization_required_invalid_token(self, mock_validate_bearer_token):
        mock_validate_bearer_token.return_value = ('valid_token', None)
        self.mock_auth_service.authenticate.side_effect = jwt.InvalidTokenError

        @self.app.route('/protected')
        @authorization_required(self.mock_auth_service)
        def protected_route():
            pass

        headers = {'Authorization': 'Bearer invalid_token'}
        response = self.client.get('/protected', headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], Status.ERROR.value)
        self.assertEqual(response.json['error']
                         ['code'], TokenErrorCodes.INVALID_TOKEN)

    @patch('src.token_auth.application.authentication.validate_bearer_token')
    def test_authorization_required_expired_token(self, mock_validate_bearer_token):
        mock_validate_bearer_token.return_value = ('valid_token', None)
        self.mock_auth_service.authenticate.side_effect = jwt.ExpiredSignatureError

        @self.app.route('/protected')
        @authorization_required(self.mock_auth_service)
        def protected_route():
            pass

        headers = {'Authorization': 'Bearer expired_token'}
        response = self.client.get('/protected', headers=headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], Status.ERROR.value)
        self.assertEqual(response.json['error']
                         ['code'], TokenErrorCodes.EXPIRED_TOKEN)

    @patch('src.token_auth.application.authentication.validate_bearer_token')
    def test_authorization_required_internal_server_error(self, mock_validate_bearer_token):
        mock_validate_bearer_token.return_value = ('valid_token', None)
        self.mock_auth_service.authenticate.side_effect = Exception(
            'some random and unexpected error')

        @self.app.route('/protected')
        @authorization_required(self.mock_auth_service)
        def protected_route():
            pass

        headers = {'Authorization': 'Bearer expired_token'}
        response = self.client.get('/protected', headers=headers)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['status'], Status.ERROR.value)
        self.assertEqual(
            response.json['error']['code'], CommonErrorCodes.INTERNAL_SERVER_ERROR)

    def test_authorization_required_token_type_validation_error(self):
        @self.app.route('/protected')
        @authorization_required(self.mock_auth_service)
        def protected_route():
            pass

        headers = {'Authorization': 'Basic some'}
        response = self.client.get('/protected', headers=headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], Status.ERROR.value)
        self.assertEqual(
            response.json['error']['code'], TokenErrorCodes.INVALID_AUTHORIZATION_TYPE)

    def test_authorization_required_null_token_validation_error(self):
        @self.app.route('/protected')
        @authorization_required(self.mock_auth_service)
        def protected_route():
            pass

        response = self.client.get('/protected')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], Status.ERROR.value)
        self.assertEqual(
            response.json['error']['code'], TokenErrorCodes.INVALID_AUTHORIZATION_HEADER)


class TestJWTAuthenticationService(unittest.TestCase):
    def setUp(self):
        self.secret_key = 'test_secret_key'
        self.refresh_secret_key = 'test_refresh_secret_key'
        self.access_token_expiration_hours = 1
        self.refresh_token_expiration_days = 7
        self.algorithm = 'HS256'
        self.jwt_service = JWTAuthenticationService(
            self.secret_key,
            self.refresh_secret_key,
            self.access_token_expiration_hours,
            self.refresh_token_expiration_days,
            self.algorithm
        )
        self.user_credentials = UserCredentials(
            user_id='123',
            email='test@example.com',
            username='testuser',
            password=None
        )

    def test_grant_access(self):
        token_response = self.jwt_service.grant_access(self.user_credentials)

        self.assertIsNotNone(token_response.access_token)
        self.assertIsNotNone(token_response.refresh_token)
        self.assertEqual(token_response.expires_in,
                         self.access_token_expiration_hours * 3600)

        decoded_access_token = jwt.decode(
            token_response.access_token, self.secret_key, algorithms=[
                self.algorithm]
        )
        self.assertEqual(
            decoded_access_token['sub'], self.user_credentials.user_id)
        self.assertEqual(
            decoded_access_token['username'], self.user_credentials.username)
        self.assertEqual(
            decoded_access_token['email'], self.user_credentials.email)

    def test_authenticate_with_access_token(self):
        token_response = self.jwt_service.grant_access(self.user_credentials)
        auth_context = {'access_token': token_response.access_token}

        authenticated_user = self.jwt_service.authenticate(auth_context)

        self.assertEqual(authenticated_user.user_id,
                         self.user_credentials.user_id)
        self.assertEqual(authenticated_user.username,
                         self.user_credentials.username)
        self.assertEqual(authenticated_user.email, self.user_credentials.email)

    def test_authenticate_with_refresh_token(self):
        token_response = self.jwt_service.grant_access(self.user_credentials)
        auth_context = {'refresh_token': token_response.refresh_token}

        authenticated_user = self.jwt_service.authenticate(auth_context)

        self.assertEqual(authenticated_user.user_id,
                         self.user_credentials.user_id)
        self.assertEqual(authenticated_user.username,
                         self.user_credentials.username)
        self.assertEqual(authenticated_user.email, self.user_credentials.email)

    def test_authenticate_with_invalid_token(self):
        invalid_token = 'invalid_token'
        auth_context = {'access_token': invalid_token}

        with self.assertRaises(jwt.InvalidTokenError):
            self.jwt_service.authenticate(auth_context)

    def test_authenticate_with_expired_token(self):
        expired_token_payload = {
            'sub': self.user_credentials.user_id,
            'username': self.user_credentials.username,
            'email': self.user_credentials.email,
            'iat': int(datetime.now().timestamp()) - 3600,
            'exp': int(datetime.now().timestamp()) - 1800
        }
        expired_token = jwt.encode(
            expired_token_payload, self.secret_key, algorithm=self.algorithm
        )
        auth_context = {'access_token': expired_token}

        with self.assertRaises(jwt.ExpiredSignatureError):
            self.jwt_service.authenticate(auth_context)

    def test_authenticate_with_missing_auth_context(self):
        with self.assertRaises(AttributeError):
            self.jwt_service.authenticate({})


if __name__ == '__main__':
    unittest.main()

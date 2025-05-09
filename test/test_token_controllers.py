import unittest
from unittest.mock import MagicMock, patch

from src.common.domain import Status, UserCredentials
from src.constants import TokenErrorCodes
from src.token.controllers.controllers import generate_new_token, refresh_token
from src.token.domain.response import JwtTokenResponse


class TestGenerateNewTokenController(unittest.TestCase):
    def setUp(self):
        self.lang = 'en'
        self.user_repository_mock = MagicMock()
        self.mock_auth_service = MagicMock()

    @patch('src.token.controllers.controllers.bcrypt.checkpw')
    def test_generate_new_token_success(self, mock_bcrypt_checkpw):
        user_credentials = UserCredentials(
            None, 'test@example.com', 'testuser', 'T3stP@ss')
        expected_token_response = JwtTokenResponse(
            'access_token_test_fixture', 'refresh_token_test_fixture', 3600)

        mock_bcrypt_checkpw.return_value = True
        self.user_repository_mock.find_by_username_or_email.return_value = MagicMock()
        self.mock_auth_service.grant_access.return_value = expected_token_response

        response, status = generate_new_token(
            self.mock_auth_service, self.user_repository_mock, user_credentials, self.lang)
        token_json_payload = response.to_json()

        self.assertEqual(status, 200)
        self.assertIsInstance(response, JwtTokenResponse)
        self.assertEqual(token_json_payload['access_token'],
                         expected_token_response.access_token)
        self.assertEqual(token_json_payload['refresh_token'],
                         expected_token_response.refresh_token)
        self.assertEqual(token_json_payload['expires_in'],
                         expected_token_response.expires_in)
        self.assertEqual(token_json_payload['token_type'],
                         expected_token_response.token_type)

    @patch('src.token.controllers.controllers.bcrypt.checkpw')
    def test_generate_new_token_invalid_credentials_error(self, mock_bcrypt_checkpw):
        user_credentials = UserCredentials(
            None, 'test@example.com', 'testuser', 'T3stP@ss')

        mock_bcrypt_checkpw.return_value = False
        self.user_repository_mock.find_by_username_or_email.return_value = MagicMock()

        response, status = generate_new_token(
            self.mock_auth_service, self.user_repository_mock, user_credentials, self.lang)

        self.assertEqual(status, 401)
        self.assertEqual(response.status, Status.ERROR)
        self.assertEqual(response.error.code,
                         TokenErrorCodes.INVALID_USER_CREDENTIALS)

    def test_generate_new_token_validation_errors(self):
        user_credentials = MagicMock(
            email=None, username=None, password=None)

        response, status = generate_new_token(
            self.mock_auth_service, self.user_repository_mock, user_credentials, self.lang)

        # Assert
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)
        self.assertTrue(response.error)

    def test_generate_new_token_user_not_found(self):
        user_credentials = UserCredentials(
            None, 'test@example.com', 'testuser', 'T3stP@ss')
        self.user_repository_mock.find_by_username_or_email.return_value = None

        response, status = generate_new_token(
            self.mock_auth_service, self.user_repository_mock, user_credentials, self.lang)

        self.assertEqual(status, 401)
        self.assertEqual(response.status, Status.ERROR)
        self.assertEqual(response.error.code,
                         TokenErrorCodes.INVALID_USER_CREDENTIALS)


class TestRefreshTokenController(unittest.TestCase):
    def setUp(self):
        self.lang = 'en'
        self.user_repository_mock = MagicMock()
        self.mock_auth_service = MagicMock()

    def test_refresh_token_success(self):
        current_user = UserCredentials(
            None, 'test@example.com', 'testuser', None)
        expected_token_response = JwtTokenResponse(
            'access_token_test_fixture', 'refresh_token_test_fixture', 3600)

        self.user_repository_mock.find_by_username_or_email.return_value = MagicMock()
        self.mock_auth_service.grant_access.return_value = expected_token_response

        response, status = refresh_token(
            self.mock_auth_service, self.user_repository_mock, current_user, self.lang)
        token_json_payload = response.to_json()

        self.assertEqual(status, 200)
        self.assertIsInstance(response, JwtTokenResponse)
        self.assertEqual(token_json_payload['access_token'],
                         expected_token_response.access_token)
        self.assertEqual(token_json_payload['refresh_token'],
                         expected_token_response.refresh_token)
        self.assertEqual(token_json_payload['expires_in'],
                         expected_token_response.expires_in)
        self.assertEqual(token_json_payload['token_type'],
                         expected_token_response.token_type)

    def test_refresh_token_user_not_found(self):
        current_user = UserCredentials(
            None, 'test@example.com', 'testuser', None)

        self.user_repository_mock.find_by_username_or_email.return_value = None

        response, status = refresh_token(
            self.mock_auth_service, self.user_repository_mock, current_user, self.lang)

        self.assertEqual(status, 403)
        self.assertEqual(response.status, Status.ERROR)
        self.assertEqual(response.error.code,
                         TokenErrorCodes.INVALID_USER_CREDENTIALS)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock

from src.common.domain import Error, UserCredentials, UserCredentialsFormFields
from src.constants import SignUpErrorCodes
from src.sign_up.application.validations import UniqueUserValidator


class TestUniqueUserValidator(unittest.TestCase):
    def setUp(self):
        self.mock_user_credentials_repository = MagicMock()
        self.user_credentials = UserCredentials(
            None, "test@example.com", "testuser", "password123"
        )
        self.validator = UniqueUserValidator(
            self.mock_user_credentials_repository, self.user_credentials
        )

    def test_validate_no_errors(self):
        # Mock repository methods to return None (no user found)
        self.mock_user_credentials_repository.find_by_username.return_value = None
        self.mock_user_credentials_repository.find_by_email.return_value = None

        self.validator.validate()

        self.assertFalse(self.validator.has_errors())
        self.mock_user_credentials_repository.find_by_username.assert_called_once_with(
            self.user_credentials.username
        )
        self.mock_user_credentials_repository.find_by_email.assert_called_once_with(
            self.user_credentials.email
        )

    def test_validate_username_already_exists(self):
        # Mock repository to return a user for the username
        self.mock_user_credentials_repository.find_by_username.return_value = True
        self.mock_user_credentials_repository.find_by_email.return_value = None

        self.validator.validate()

        self.assertTrue(self.validator.has_errors())
        errors = self.validator.get_errors()
        self.assertEqual(errors.code, SignUpErrorCodes.USER_ALREADY_REGISTERED)
        self.assertEqual(len(errors.errors), 1)
        self.assertEqual(
            errors.errors[0].code, SignUpErrorCodes.USERNAME_ALREADY_EXISTS
        )
        self.mock_user_credentials_repository.find_by_username.assert_called_once_with(
            self.user_credentials.username
        )
        self.mock_user_credentials_repository.find_by_email.assert_called_once_with(
            self.user_credentials.email
        )

    def test_validate_email_already_exists(self):
        # Mock repository to return a user for the email
        self.mock_user_credentials_repository.find_by_username.return_value = None
        self.mock_user_credentials_repository.find_by_email.return_value = True

        self.validator.validate()

        self.assertTrue(self.validator.has_errors())
        errors = self.validator.get_errors()
        self.assertEqual(errors.code, SignUpErrorCodes.USER_ALREADY_REGISTERED)
        self.assertEqual(len(errors.errors), 1)
        self.assertEqual(errors.errors[0].code,
                         SignUpErrorCodes.EMAIL_ALREADY_EXISTS)
        self.mock_user_credentials_repository.find_by_username.assert_called_once_with(
            self.user_credentials.username
        )
        self.mock_user_credentials_repository.find_by_email.assert_called_once_with(
            self.user_credentials.email
        )

    def test_validate_both_username_and_email_already_exist(self):
        # Mock repository to return a user for both username and email
        self.mock_user_credentials_repository.find_by_username.return_value = True
        self.mock_user_credentials_repository.find_by_email.return_value = True

        self.validator.validate()

        self.assertTrue(self.validator.has_errors())
        errors = self.validator.get_errors()
        self.assertEqual(errors.code, SignUpErrorCodes.USER_ALREADY_REGISTERED)
        self.assertEqual(len(errors.errors), 2)
        self.assertEqual(
            errors.errors[0].code, SignUpErrorCodes.USERNAME_ALREADY_EXISTS
        )
        self.assertEqual(errors.errors[1].code,
                         SignUpErrorCodes.EMAIL_ALREADY_EXISTS)
        self.mock_user_credentials_repository.find_by_username.assert_called_once_with(
            self.user_credentials.username
        )
        self.mock_user_credentials_repository.find_by_email.assert_called_once_with(
            self.user_credentials.email
        )


if __name__ == "__main__":
    unittest.main()

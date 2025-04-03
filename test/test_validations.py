import unittest
from unittest.mock import MagicMock

from src.common.domain import Error, UserCredentials, UserCredentialsRepository
from src.constants import (EMAIL_PATTERN, PASSWORD_ALLOWED_SYMBOLS,
                           PASSWORD_MIN_LENGTH)
from src.sign_up.application.validations import (EmailValidator,
                                                 PasswordValidator,
                                                 SignUpFormValidator,
                                                 UniqueUserValidator)


class TestSignUpFormValidator(unittest.TestCase):
    def setUp(self):
        self.user_credentials = UserCredentials(
            id=None,
            username="testuser",
            email="testuser@example.com",
            password="ValidPassword1!"
        )
        self.validator = SignUpFormValidator(self.user_credentials)

    def test_validate_with_valid_data(self):
        self.validator.validate()
        self.assertFalse(self.validator.has_errors())

    def test_validate_with_missing_username(self):
        self.user_credentials.username = ""
        self.validator.validate()
        self.assertTrue(self.validator.has_errors())

    def test_validate_with_invalid_email(self):
        self.user_credentials.email = "invalid-email"
        self.validator.validate()
        self.assertTrue(self.validator.has_errors())

    def test_validate_with_weak_password(self):
        self.user_credentials.password = "weak"
        self.validator.validate()
        self.assertTrue(self.validator.has_errors())


class TestUniqueUserValidator(unittest.TestCase):
    def setUp(self):
        self.user_credentials = UserCredentials(
            id=None,
            username="testuser",
            email="testuser@example.com",
            password="ValidPassword1!"
        )
        self.mock_repository = MagicMock(spec=UserCredentialsRepository)
        self.validator = UniqueUserValidator(
            self.mock_repository, self.user_credentials)

    def test_validate_with_unique_user(self):
        self.mock_repository.find_by_username.return_value = None
        self.mock_repository.find_by_email.return_value = None
        self.validator.validate()
        self.assertFalse(self.validator.has_errors())

    def test_validate_with_existing_username(self):
        self.mock_repository.find_by_username.return_value = self.user_credentials
        self.mock_repository.find_by_email.return_value = None
        self.validator.validate()
        self.assertTrue(self.validator.has_errors())

    def test_validate_with_existing_email(self):
        self.mock_repository.find_by_username.return_value = None
        self.mock_repository.find_by_email.return_value = self.user_credentials
        self.validator.validate()
        self.assertTrue(self.validator.has_errors())

    def test_get_errors_with_no_errors(self):
        self.validator.validate()
        self.assertIsNone(self.validator.get_errors())

    def test_get_errors_with_errors(self):
        self.user_credentials.username = ""  # Missing username
        self.validator.validate()
        errors = self.validator.get_errors()
        self.assertIsNotNone(errors)
        self.assertTrue(errors.message.startswith("Form contains errors"))


class TestPasswordValidator(unittest.TestCase):
    def test_validate_with_valid_password(self):
        validator = PasswordValidator("ValidPassword1!")
        validator.validate()
        self.assertFalse(validator.errors)

    def test_validate_with_short_password(self):
        validator = PasswordValidator("Short1!")
        validator.validate()
        self.assertTrue(validator.errors)

    def test_validate_with_missing_lowercase(self):
        validator = PasswordValidator("PASSWORD1!")
        validator.validate()
        self.assertTrue(validator.errors)

    def test_validate_with_missing_uppercase(self):
        validator = PasswordValidator("password1!")
        validator.validate()
        self.assertTrue(validator.errors)

    def test_validate_with_missing_digit(self):
        validator = PasswordValidator("Password!")
        validator.validate()
        self.assertTrue(validator.errors)

    def test_validate_with_missing_special_character(self):
        validator = PasswordValidator("Password1")
        validator.validate()
        self.assertTrue(validator.errors)


class TestEmailValidator(unittest.TestCase):
    def test_validate_with_valid_email(self):
        validator = EmailValidator("testuser@example.com")
        validator.validate()
        self.assertFalse(validator.errors)

    def test_validate_with_invalid_email(self):
        validator = EmailValidator("invalid-email")
        validator.validate()
        self.assertTrue(validator.errors)

    def test_validate_with_empty_email(self):
        validator = EmailValidator("")
        validator.validate()
        self.assertTrue(validator.errors)


if __name__ == "__main__":
    unittest.main()

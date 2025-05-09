import unittest
from unittest.mock import MagicMock

from src.common.domain import UserCredentials, UserCredentialsFormFields
from src.constants import (MAX_USERNAME_CHARS, PASSWORD_MIN_LENGTH,
                           CommonErrorCodes, SignUpErrorCodes)
from src.sign_up.application.validations import (SignUpFormValidator,
                                                 UniqueUserValidator,
                                                 validate_email,
                                                 validate_password,
                                                 validate_username)


class TestValidationsFunctions(unittest.TestCase):

    def test_validate_password_empty(self):
        errors = []
        validate_password("   ", "en", errors)
        self.assertTrue(errors)
        self.assertEqual(errors[0].validation_field,
                         UserCredentialsFormFields.PASSWORD)

    def test_validate_password_too_short(self):
        errors = []
        pwd = "A1!" if PASSWORD_MIN_LENGTH > 3 else "A" * \
            (PASSWORD_MIN_LENGTH - 1)
        validate_password(pwd, "en", errors)
        self.assertTrue(
            any(e.code == SignUpErrorCodes.PASSWORD_TOO_SHORT for e in errors))

    def test_validate_password_missing_lowercase(self):
        errors = []
        pwd = "PASSWORD1!"
        validate_password(pwd, "en", errors)
        self.assertTrue(
            any(e.code == SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE for e in errors))

    def test_validate_password_missing_uppercase(self):
        errors = []
        pwd = "password1!"
        validate_password(pwd, "en", errors)
        self.assertTrue(
            any(e.code == SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE for e in errors))

    def test_validate_password_missing_digit(self):
        errors = []
        pwd = "Password!"
        validate_password(pwd, "en", errors)
        self.assertTrue(
            any(e.code == SignUpErrorCodes.PASSWORD_MISSING_DIGIT for e in errors))

    def test_validate_password_missing_special_char(self):
        errors = []
        pwd = "Password1"
        validate_password(pwd, "en", errors)
        self.assertTrue(
            any(e.code == SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR for e in errors))

    def test_validate_password_valid(self):
        errors = []
        valid_pwd = "Valid1!"
        if len(valid_pwd) < PASSWORD_MIN_LENGTH:
            valid_pwd += "a" * (PASSWORD_MIN_LENGTH - len(valid_pwd))
        validate_password(valid_pwd, "en", errors)
        self.assertFalse(errors)

    def test_validate_email_empty(self):
        errors = []
        validate_email("   ", "en", errors)
        self.assertTrue(errors)
        self.assertEqual(errors[0].validation_field,
                         UserCredentialsFormFields.EMAIL)

    def test_validate_email_invalid(self):
        errors = []
        validate_email("invalid.email", "en", errors)
        self.assertTrue(
            any(e.code == CommonErrorCodes.INVALID_EMAIL for e in errors))

    def test_validate_email_valid(self):
        errors = []
        validate_email("test@example.com", "en", errors)
        self.assertFalse(errors)

    def test_validate_username_empty(self):
        errors = []
        validate_username("   ", "en", errors)
        self.assertTrue(errors)
        self.assertEqual(errors[0].validation_field,
                         UserCredentialsFormFields.USERNAME)

    def test_validate_username_too_long(self):
        errors = []
        long_username = "a" * (MAX_USERNAME_CHARS + 1)
        validate_username(long_username, "en", errors)
        self.assertTrue(
            any(e.code == CommonErrorCodes.FIELD_TOO_LARGE for e in errors))

    def test_validate_username_valid(self):
        errors = []
        validate_username("validuser", "en", errors)
        self.assertFalse(errors)


class TestSignUpFormValidator(unittest.TestCase):

    def test_form_validator_no_errors(self):
        pwd = "Valid1!"
        if len(pwd) < PASSWORD_MIN_LENGTH:
            pwd += "a" * (PASSWORD_MIN_LENGTH - len(pwd))
        user = UserCredentials("1", "test@example.com", "validuser", pwd)
        validator = SignUpFormValidator(user, "en")
        validator.validate()
        self.assertFalse(validator.has_errors())
        self.assertIsNone(validator.errors)

    def test_form_validator_with_errors(self):
        long_username = "u" * (MAX_USERNAME_CHARS + 1)
        user = UserCredentials("1", "   ", long_username, "weak")
        validator = SignUpFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertIsNotNone(errors)
        error_codes = [e.code for e in errors.errors]
        self.assertIn(CommonErrorCodes.MISSING_MANDATORY_FIELD, error_codes)
        self.assertIn(CommonErrorCodes.FIELD_TOO_LARGE, error_codes)
        self.assertTrue(any(code in (
            SignUpErrorCodes.PASSWORD_TOO_SHORT,
            SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE,
            SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE,
            SignUpErrorCodes.PASSWORD_MISSING_DIGIT,
            SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR
        ) for code in error_codes))


class TestUniqueUserValidator(unittest.TestCase):

    def test_unique_user_validator_no_errors(self):
        repo = MagicMock()
        repo.find_by_username.return_value = None
        repo.find_by_email.return_value = None
        user = UserCredentials("1", "unique@example.com",
                               "uniqueuser", "Valid1!")
        validator = UniqueUserValidator(repo, user, "en")
        validator.validate()
        self.assertFalse(validator.has_errors())
        self.assertIsNone(validator.errors)

    def test_unique_user_validator_username_exists(self):
        existing_user = UserCredentials(
            "2", "other@example.com", "existinguser", "Pass1!")
        repo = MagicMock()
        repo.find_by_username.return_value = existing_user
        repo.find_by_email.return_value = None
        user = UserCredentials("1", "unique@example.com",
                               "existinguser", "Valid1!")
        validator = UniqueUserValidator(repo, user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(
            any(e.code == SignUpErrorCodes.USERNAME_ALREADY_EXISTS for e in errors.errors))

    def test_unique_user_validator_email_exists(self):
        existing_user = UserCredentials(
            "2", "existing@example.com", "someuser", "Pass1!")
        repo = MagicMock()
        repo.find_by_username.return_value = None
        repo.find_by_email.return_value = existing_user
        user = UserCredentials(
            "1", "existing@example.com", "uniqueuser", "Valid1!")
        validator = UniqueUserValidator(repo, user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(
            any(e.code == SignUpErrorCodes.EMAIL_ALREADY_EXISTS for e in errors.errors))

    def test_unique_user_validator_both_exists(self):
        existing_user1 = UserCredentials(
            "2", "existing@example.com", "existinguser", "Pass1!")
        existing_user2 = UserCredentials(
            "3", "existing@example.com", "existinguser", "Pass1!")
        repo = MagicMock()
        repo.find_by_username.return_value = existing_user1
        repo.find_by_email.return_value = existing_user2
        user = UserCredentials("1", "existing@example.com",
                               "existinguser", "Valid1!")
        validator = UniqueUserValidator(repo, user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        codes = [e.code for e in errors.errors]
        self.assertIn(SignUpErrorCodes.USERNAME_ALREADY_EXISTS, codes)
        self.assertIn(SignUpErrorCodes.EMAIL_ALREADY_EXISTS, codes)


if __name__ == "__main__":
    unittest.main()

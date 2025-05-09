import unittest

from src.common.domain import UserCredentials, UserCredentialsFormFields
from src.constants import CommonErrorCodes, TokenErrorCodes
from src.token_auth.application.validations import TokenFormValidator


class TestTokenFormValidator(unittest.TestCase):
    def test_valid_user_credentials(self):
        user = UserCredentials("1", "test@example.com",
                               "validuser", "ValidPassword123!")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertFalse(validator.has_errors())
        self.assertIsNone(validator.errors)

    def test_missing_password(self):
        user = UserCredentials("1", "test@example.com", "validuser", "   ")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(any(e.validation_field ==
                        UserCredentialsFormFields.PASSWORD for e in errors.errors))

    def test_missing_username_and_email(self):
        user = UserCredentials("1", "   ", "   ", "ValidPassword123!")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(any(e.validation_field ==
                        UserCredentialsFormFields.USERNAME for e in errors.errors))
        self.assertTrue(any(e.validation_field ==
                        UserCredentialsFormFields.EMAIL for e in errors.errors))

    def test_invalid_email_format(self):
        user = UserCredentials("1", "invalid-email",
                               "validuser", "ValidPassword123!")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(
            any(e.code == CommonErrorCodes.INVALID_EMAIL for e in errors.errors))

    def test_whitespace_email(self):
        user = UserCredentials("1", "a @gmail.com", None, "ValidPassword123!")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(
            any(e.code == CommonErrorCodes.INVALID_EMAIL for e in errors.errors))

    def test_combined_errors(self):
        user = UserCredentials("1", "invalid-email", "   ", "   ")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        codes = [e.code for e in errors.errors]
        self.assertIn(CommonErrorCodes.INVALID_EMAIL, codes)
        self.assertIn(CommonErrorCodes.MISSING_MANDATORY_FIELD, codes)

    def test_empty_user_credentials(self):
        user = UserCredentials("1", None, None, None)
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertTrue(validator.has_errors())
        errors = validator.errors
        self.assertTrue(
            any(e.code == TokenErrorCodes.MISSING_USER_IDENTIFIER for e in errors.errors))

    def test_valid_email_only(self):
        user = UserCredentials("1", "test@example.com",
                               None, "ValidPassword123!")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertFalse(validator.has_errors())

    def test_valid_username_only(self):
        user = UserCredentials("1", None, "validuser", "ValidPassword123!")
        validator = TokenFormValidator(user, "en")
        validator.validate()
        self.assertFalse(validator.has_errors())


if __name__ == "__main__":
    unittest.main()

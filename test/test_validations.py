import unittest

from src.common.domain.errors import Error
from src.constants import CommonErrorCodes, TokenErrorCodes
from src.token.application.validations import TokenFormValidator
from src.user_credentials.domain import UserCredentials


class TestTokenValidator(unittest.TestCase):

    def setUp(self):
        self.valid_username = "validuser"
        self.valid_email = "validuser@example.com"
        self.invalid_email = "invalidemail"
        self.valid_password = "validpassword"
        self.user_credentials = UserCredentials(
            username=self.valid_username, email=self.valid_email, password=self.valid_password)
        self.validator = TokenFormValidator(self.user_credentials)

    def test_validate_with_valid_credentials(self):
        self.validator.validate()
        self.assertFalse(self.validator.has_errors)

    def test_validate_with_missing_username_and_email(self):
        self.user_credentials.username = ""
        self.user_credentials.email = ""
        self.validator.validate()
        errors = self.validator.get_errors()
        self.assertTrue(errors)
        self.assertEqual(len(errors.errors), 2)
        self.assertEqual(errors.errors[0].code,
                         TokenErrorCodes.MISSING_USER_IDENTIFIER)
        self.assertEqual(errors.errors[1].code,
                         TokenErrorCodes.MISSING_USER_IDENTIFIER)

    def test_validate_with_invalid_email_format(self):
        self.user_credentials.email = self.invalid_email
        self.validator.validate()
        errors = self.validator.get_errors()
        self.assertTrue(errors)
        self.assertEqual(len(errors.errors), 1)
        self.assertEqual(errors.errors[0].code, CommonErrorCodes.INVALID_EMAIL)

    def test_validate_with_missing_password(self):
        self.user_credentials.password = ""
        self.validator.validate()
        errors = self.validator.get_errors()
        self.assertTrue(errors)
        self.assertEqual(len(errors.errors), 1)
        self.assertEqual(errors.errors[0].code,
                         CommonErrorCodes.MISSING_MANDATORY_FIELD)


if __name__ == '__main__':
    unittest.main()

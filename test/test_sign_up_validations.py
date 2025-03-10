import unittest

from src.sign_up.application.validations import (EmailValidator,
                                                 PasswordValidator,
                                                 SignUpValidator)
from src.user_credentials.domain.user_credentials import UserCredentials


class TestPasswordValidator(unittest.TestCase):
    def test_password_too_short(self):
        password = 'Ab1!'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0].code, 'PASSWORD_TOO_SHORT')

    def test_password_missing_lowercase(self):
        password = 'AABC123!'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(
            validator.errors[0].code, 'PASSWORD_MISSING_LOWERCASE')

    def test_password_missing_uppercase(self):
        password = 'aabc123!'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(
            validator.errors[0].code, 'PASSWORD_MISSING_UPPERCASE')

    def test_password_missing_digit(self):
        password = 'Aabcdef!'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0].code, 'PASSWORD_MISSING_DIGIT')

    def test_password_missing_special_character(self):
        password = 'Aabcdef1'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(
            validator.errors[0].code, 'PASSWORD_MISSING_SPECIAL_CHAR')

    def test_valid_password(self):
        password = 'Abcdef1!'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertFalse(validator.contains_error)
        self.assertEqual(len(validator.errors), 0)

    def test_password_multiple_errors(self):
        password = 'abc'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertGreater(len(validator.errors), 1)
        error_codes = [error.code for error in validator.errors]
        self.assertIn('PASSWORD_TOO_SHORT', error_codes)
        self.assertIn('PASSWORD_MISSING_UPPERCASE', error_codes)
        self.assertIn('PASSWORD_MISSING_DIGIT', error_codes)
        self.assertIn('PASSWORD_MISSING_SPECIAL_CHAR', error_codes)

    def test_password_with_newline_character(self):
        password = 'Abcdef1!\n'
        validator = PasswordValidator(password)
        validator.validate()
        self.assertFalse(validator.contains_error)


class TestEmailValidator(unittest.TestCase):
    def test_email_missing_at_symbol(self):
        email = 'testemail.com'
        validator = EmailValidator(email)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0].code, 'INVALID_EMAIL')

    def test_email_missing_domain(self):
        email = 'test@'
        validator = EmailValidator(email)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0].code, 'INVALID_EMAIL')

    def test_email_with_spaces(self):
        email = 'test @email.com'
        validator = EmailValidator(email)
        validator.validate()
        self.assertTrue(validator.contains_error)
        self.assertEqual(len(validator.errors), 1)
        self.assertEqual(validator.errors[0].code, 'INVALID_EMAIL')

    def test_valid_email(self):
        email = 'test@email.com'
        validator = EmailValidator(email)
        validator.validate()
        self.assertFalse(validator.contains_error)
        self.assertEqual(len(validator.errors), 0)


class TestSignUpValidator(unittest.TestCase):
    def test_sign_up_validator_with_valid_credentials(self):
        user_credentials = UserCredentials(
            username='validuser', email='test@email.com', password='Vaaaalid1!')
        validator = SignUpValidator(user_credentials)
        validator.validate()
        self.assertFalse(validator.form_contains_errors())
        self.assertIsNone(validator.get_error())

    def test_sign_up_validator_with_invalid_username(self):
        user_credentials = UserCredentials(
            username='', email='test@email.com', password='Valid1!')
        validator = SignUpValidator(user_credentials)
        validator.validate()
        self.assertTrue(validator.form_contains_errors())
        self.assertIsNotNone(validator.get_error())
        self.assertEqual(validator.get_error().code, 'FORM_CONTAINS_ERRORS')

    def test_sign_up_validator_with_invalid_email(self):
        user_credentials = UserCredentials(
            username='validuser', email='invalidemail', password='Valid1!')
        validator = SignUpValidator(user_credentials)
        validator.validate()
        self.assertTrue(validator.form_contains_errors())
        self.assertIsNotNone(validator.get_error())
        self.assertEqual(validator.get_error().code, 'FORM_CONTAINS_ERRORS')

    def test_sign_up_validator_with_invalid_password(self):
        user_credentials = UserCredentials(
            username='validuser', email='test@email.com', password='short')
        validator = SignUpValidator(user_credentials)
        validator.validate()
        self.assertTrue(validator.form_contains_errors())
        self.assertIsNotNone(validator.get_error())
        self.assertEqual(validator.get_error().code, 'FORM_CONTAINS_ERRORS')

    def test_sign_up_validator_with_multiple_errors(self):
        user_credentials = UserCredentials(
            username='', email='invalidemail', password='short')
        validator = SignUpValidator(user_credentials)
        validator.validate()
        self.assertTrue(validator.form_contains_errors())
        self.assertIsNotNone(validator.get_error())
        self.assertEqual(validator.get_error().code, 'FORM_CONTAINS_ERRORS')
        self.assertGreater(len(validator.get_error().errors), 1)


if __name__ == '__main__':
    unittest.main()

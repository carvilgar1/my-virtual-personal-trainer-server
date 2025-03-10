import re

from src.common.application.localizations import ErrorLocalizable
from src.common.application.validations import (FieldValidator,
                                                validate_mandatory_field)
from src.common.domain import Error
from src.constants import (EMAIL_PATTERN, PASSWORD_ALLOWED_SYMBOLS,
                           PASSWORD_MIN_LENGTH, CommonErrorCodes,
                           SignUpErrorCodes)
from src.user_credentials.domain.user_credentials import (
    UserCredentials, UserCredentialsFormFields)


def init_password_error_localizable(code: str, locale_id: str, default_message: str):
    return init_form_field_error_localizable(code, locale_id, default_message, UserCredentialsFormFields.PASSWORD)


def init_email_error_localizable(code: str, locale_id: str, default_message: str):
    return init_form_field_error_localizable(code, locale_id, default_message, UserCredentialsFormFields.EMAIL)


def init_form_field_error_localizable(code: str, locale_id: str, default_message: str, form_field: str):
    return ErrorLocalizable(code, locale_id, default_message, form_field)


class PasswordValidator(FieldValidator):
    def __init__(self, password: str, errors: list[Error] = None):
        super().__init__(password, errors)

    def validate(self) -> None:
        is_filled, error = validate_mandatory_field(
            UserCredentialsFormFields.PASSWORD, self.field_value)
        if not is_filled:
            self.add_error(error)
        else:
            self.__validate_password_length()
            self.__validate_password_has_lowercase()
            self.__validate_password_has_uppercase()
            self.__validate_password_has_digit()
            self.__validate_password_has_special_character()

    def __validate_password_length(self):
        if len(self.field_value) < PASSWORD_MIN_LENGTH:
            code = SignUpErrorCodes.PASSWORD_TOO_SHORT
            locale_id = SignUpErrorCodes.PASSWORD_TOO_SHORT
            default_message = 'Password must be at least 8 characters long'
            error = init_password_error_localizable(
                code, locale_id, default_message)
            self.add_error(error)

    def __validate_password_has_lowercase(self):
        if not any(char.islower() for char in self.field_value):
            code = SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE
            locale_id = SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE
            default_message = 'Password must contain at least one lowercase letter'
            error = init_password_error_localizable(
                code, locale_id, default_message)
            self.add_error(error)

    def __validate_password_has_uppercase(self):
        if not any(char.isupper() for char in self.field_value):
            code = SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE
            locale_id = SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE
            default_message = 'Password must contain at least one uppercase letter'
            error = init_password_error_localizable(
                code, locale_id, default_message)
            self.add_error(error)

    def __validate_password_has_digit(self):
        if not any(char.isdigit() for char in self.field_value):
            code = SignUpErrorCodes.PASSWORD_MISSING_DIGIT
            locale_id = SignUpErrorCodes.PASSWORD_MISSING_DIGIT
            default_message = 'Password must contain at least one digit'
            error = init_password_error_localizable(
                code, locale_id, default_message)
            self.add_error(error)

    def __validate_password_has_special_character(self):
        if not any(char in PASSWORD_ALLOWED_SYMBOLS for char in self.field_value):
            code = SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR
            locale_id = SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR
            default_message = 'Password must contain at least one special character'
            error = init_password_error_localizable(
                code, locale_id, default_message)
            self.add_error(error)


class EmailValidator(FieldValidator):
    __EMAIL_REGEX = re.compile(EMAIL_PATTERN)

    def __init__(self, email: str, errors: list[Error] = None):
        super().__init__(email, errors)

    def validate(self) -> None:
        is_filled, error = validate_mandatory_field(
            UserCredentialsFormFields.EMAIL, self.field_value)
        if not is_filled:
            self.add_error(error)
        else:
            self.__validate_email_format()

    def __validate_email_format(self):
        if not self.__EMAIL_REGEX.match(self.field_value):
            code = CommonErrorCodes.INVALID_EMAIL
            locale_id = CommonErrorCodes.INVALID_EMAIL
            default_message = 'Invalid email format'
            error = init_email_error_localizable(
                code, locale_id, default_message)
            self.add_error(error)


class SignUpValidator:
    def __init__(self, user_credentials: UserCredentials):
        self.__errors = []

        self.__user_credentials = user_credentials

    def validate(self) -> None:
        self.__validate_username()
        self.__validate_email()
        self.__validate_password()

    def form_contains_errors(self) -> bool:
        return any(self.__errors)

    def get_error(self) -> Error:
        if self.form_contains_errors():
            code = CommonErrorCodes.FORM_CONTAINS_ERRORS
            locale_id = CommonErrorCodes.FORM_CONTAINS_ERRORS
            default_message = 'Form contains errors'
            return ErrorLocalizable(code, locale_id, default_message, errors=self.__errors)
        return None

    def __validate_username(self):
        is_filled, error = validate_mandatory_field(
            UserCredentialsFormFields.USERNAME, self.__user_credentials.username)
        if not is_filled:
            self.__errors.append(error)

    def __validate_email(self):
        self.__email_validator = EmailValidator(
            self.__user_credentials.email, self.__errors)
        self.__email_validator.validate()

    def __validate_password(self):
        self.__password_validator = PasswordValidator(
            self.__user_credentials.password, self.__errors)
        self.__password_validator.validate()

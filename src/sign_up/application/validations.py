import re

from src.common.application import error_builders
from src.common.application.validations import (FieldValidator,
                                                validate_mandatory_field)
from src.common.domain import (Error, UserCredentials,
                               UserCredentialsFormFields,
                               UserCredentialsRepository)
from src.constants import (EMAIL_PATTERN, PASSWORD_ALLOWED_SYMBOLS,
                           PASSWORD_MIN_LENGTH)


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
            error = error_builders.init_password_too_short_error()
            self.add_error(error)

    def __validate_password_has_lowercase(self):
        if not any(char.islower() for char in self.field_value):
            error = error_builders.init_password_missing_lowercase_error()
            self.add_error(error)

    def __validate_password_has_uppercase(self):
        if not any(char.isupper() for char in self.field_value):
            error = error_builders.init_password_missing_uppercase_error()
            self.add_error(error)

    def __validate_password_has_digit(self):
        if not any(char.isdigit() for char in self.field_value):
            error = error_builders.init_password_missing_digit_error()
            self.add_error(error)

    def __validate_password_has_special_character(self):
        if not any(char in PASSWORD_ALLOWED_SYMBOLS for char in self.field_value):
            error = error_builders.init_password_missing_special_character_error()
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
            error = error_builders.init_email_format_error()
            self.add_error(error)


class SignUpFormValidator:
    def __init__(self, user_credentials: UserCredentials):
        self.__errors = []

        self.user_credentials = user_credentials

    def has_errors(self) -> bool:
        return bool(self.__errors)

    def get_errors(self) -> Error:
        if self.has_errors():
            return error_builders.init_form_contains_errors_error(self.__errors)
        return None

    def validate(self) -> None:
        self.__validate_username()
        self.__validate_email()
        self.__validate_password()

    def __validate_username(self):
        is_filled, error = validate_mandatory_field(
            UserCredentialsFormFields.USERNAME, self.user_credentials.username)
        if not is_filled:
            self.__errors.append(error)

    def __validate_email(self):
        email_validator = EmailValidator(
            self.user_credentials.email, self.__errors)
        email_validator.validate()

    def __validate_password(self):
        password_validator = PasswordValidator(
            self.user_credentials.password, self.__errors)
        password_validator.validate()


class UniqueUserValidator:
    def __init__(self, user_credentials_repository: UserCredentialsRepository, user_credentials: UserCredentials):
        self.errors = []

        self.user_credentials_repository = user_credentials_repository
        self.user_credentials = user_credentials

    def has_errors(self) -> bool:
        return bool(self.errors)

    def get_errors(self) -> Error:
        return error_builders.init_user_already_registered_error(self.errors)

    def validate(self) -> None:
        self.__check_unique_username()
        self.__check_unique_email()

    def __check_unique_username(self):
        registered_user = self.user_credentials_repository.find_by_username(
            self.user_credentials.username)
        if registered_user:
            error = error_builders.init_username_already_exists_error()
            self.errors.append(error)

    def __check_unique_email(self):
        registered_user = self.user_credentials_repository.find_by_email(
            self.user_credentials.email)
        if registered_user:
            error = error_builders.init_email_already_exists_error()
            self.errors.append(error)

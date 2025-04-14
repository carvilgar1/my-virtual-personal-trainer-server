import re

from src.common.application import error_builders
from src.common.application.validations import build_empyt_field_error
from src.common.domain import (Error, UserCredentials,
                               UserCredentialsFormFields,
                               UserCredentialsRepository)
from src.constants import (EMAIL_PATTERN, PASSWORD_ALLOWED_SYMBOLS,
                           PASSWORD_MIN_LENGTH)


def validate_password(password: str, errors: list[Error]) -> None:
    is_filled = password and password.strip()
    if not is_filled:
        errors.append(build_empyt_field_error())
        return

    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(error_builders.init_password_too_short_error())

    if not any(char.islower() for char in password):
        errors.append(error_builders.init_password_missing_lowercase_error())

    if not any(char.isupper() for char in password):
        errors.append(error_builders.init_password_missing_uppercase_error())

    if not any(char.isdigit() for char in password):
        errors.append(error_builders.init_password_missing_digit_error())

    if not any(char in PASSWORD_ALLOWED_SYMBOLS for char in password):
        errors.append(
            error_builders.init_password_missing_special_character_error())


def validate_email(email: str, errors: list[Error]) -> None:
    is_filled = email and email.strip()
    if not is_filled:
        errors.append(build_empyt_field_error())
        return

    email_regex = re.compile(EMAIL_PATTERN)
    if not email_regex.match(email):
        errors.append(error_builders.init_email_format_error())


def validate_username(username: str, errors: list[Error]) -> None:
    is_filled = username and username.strip()
    if not is_filled:
        errors.append(build_empyt_field_error())


class SignUpFormValidator:
    def __init__(self, user_credentials: UserCredentials):
        self.email = user_credentials.email
        self.username = user_credentials.username
        self.password = user_credentials.password

        self.__errors = []

    def has_errors(self) -> bool:
        return bool(self.__errors)

    def get_errors(self) -> Error:
        if self.has_errors():
            return error_builders.init_form_contains_errors_error(self.__errors)
        return None

    def validate(self) -> None:
        validate_email(self.email, self.__errors)
        validate_username(self.username, self.__errors)
        validate_password(self.password, self.__errors)


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

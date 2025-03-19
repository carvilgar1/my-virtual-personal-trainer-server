
import re

from src.common.application import validations as common_validations
from src.common.domain import Error, ErrorLocalizable, errors
from src.constants import TokenErrorCodes
from src.user_credentials.domain import (UserCredentials,
                                         UserCredentialsFormFields)


def build_build_wrong_user_credentials_error(errors: list[Error]) -> Error:
    return ErrorLocalizable(TokenErrorCodes.WRONG_USER_CREDENTIALS, TokenErrorCodes.WRONG_USER_CREDENTIALS, 'Invalid user credentials', errors=errors)


def build_missing_user_identifier_error(validation_field: str) -> Error:
    return ErrorLocalizable(TokenErrorCodes.MISSING_USER_IDENTIFIER, TokenErrorCodes.MISSING_USER_IDENTIFIER, 'Any of username or email should be provided', validation_field)


def build_missing_username_identifier_error() -> Error:
    return build_missing_user_identifier_error(UserCredentialsFormFields.USERNAME)


def build_missing_email_identifier_error() -> Error:
    return build_missing_user_identifier_error(UserCredentialsFormFields.EMAIL)


class TokenFormValidator:
    def __init__(self, user_credentials: UserCredentials):
        self.__user_credentials = user_credentials

        self.__errors = []
        self.__found_user_identifier = False

    @property
    def has_errors(self) -> bool:
        return self.__errors

    def get_errors(self) -> Error:
        return build_build_wrong_user_credentials_error(self.__errors) if self.has_errors else None

    def validate(self) -> None:
        self.__validate_username()
        self.__validate_email()
        self.__validate_password()
        self.__validate_user_identifiers_exists()

    def __validate_user_identifiers_exists(self):
        if not self.__found_user_identifier:
            self.__errors.append(build_missing_username_identifier_error())
            self.__errors.append(build_missing_email_identifier_error())

    def __validate_username(self) -> None:
        username = self.__user_credentials.username
        if common_validations.string_is_none_or_blank(username):
            pass
        else:
            self.__found_user_identifier = True

    def __validate_email(self) -> None:
        email = self.__user_credentials.email
        if common_validations.string_is_none_or_blank(email):
            pass
        elif not common_validations.validate_email_format(email):
            self.__errors.append(errors.build_invalid_email_format_error())
        else:
            self.__found_user_identifier = True

    def __validate_password(self) -> None:
        password = self.__user_credentials.password
        if common_validations.string_is_none_or_blank(password):
            self.__errors.append(errors.build_missing_mandatory_field_error(
                UserCredentialsFormFields.PASSWORD))

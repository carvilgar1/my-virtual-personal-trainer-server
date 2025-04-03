
import re

from src.common.application import validations as common_validations
from src.common.application import error_builders
from src.common.domain import Error, ErrorLocalizable, errors
from src.common.domain.user_credentials import (UserCredentials,
                                                UserCredentialsFormFields)
from src.constants import TokenErrorCodes




class TokenFormValidator:
    def __init__(self, user_credentials: UserCredentials):
        self.__errors = []
        self.error = Error()

        self.user_credentials = user_credentials

    def has_errors(self) -> bool:
        return bool(self.__errors)

    def get_errors(self) -> Error:
        return error_builders.init_form_contains_errors_error(self.__errors) if self.has_errors else None

    def validate(self) -> None:
        self.__validate_password()
        self.__validate_user_id()

    def __validate_user_id(self):
        if not self.__found_user_identifier:
            self.__errors.append(error_builders.init_missing_username_identifier_error())
            self.__errors.append(error_builders.init_missing_email_identifier_error())
    def __contains_user_identifier(self) -> bool:
        return self.__found_user_identifier

    def __validate_username(self) -> None:
        username = self.user_credentials.username
        if common_validations.string_is_none_or_blank(username):
            pass
        else:
            self.__found_user_identifier = True

    def __validate_email(self) -> None:
        email = self.user_credentials.email
        if common_validations.string_is_none_or_blank(email):
            pass
        elif not common_validations.validate_email_format(email):
            self.__errors.append(error_builders.init_missing_username_identifier_error())
        else:
            self.__found_user_identifier = True

    def __validate_password(self) -> None:
        password = self.user_credentials.password
        if common_validations.string_is_none_or_blank(password):
            self.__errors.append(error_builders.build_missing_mandatory_field_error(
                UserCredentialsFormFields.PASSWORD))



from binascii import Error

from src.common.application.validations import (BaseFormValidator,
                                                build_empyt_field_error,
                                                build_invalid_email_error,
                                                validate_email_format)
from src.common.domain import (Error, ErrorLocalizable, UserCredentials,
                               UserCredentialsFormFields)
from src.constants import TokenErrorCodes


def build_wrong_user_credentials_error() -> Error:
    return ErrorLocalizable(TokenErrorCodes.WRONG_USER_CREDENTIALS,
                            TokenErrorCodes.WRONG_USER_CREDENTIALS,
                            'Wrong user credentials',
                            UserCredentialsFormFields.USERNAME)


def build_wrong_password_error() -> Error:
    parent_error = build_wrong_user_credentials_error()
    wrong_password_error = ErrorLocalizable(TokenErrorCodes.WRONG_PASSWORD,
                                            TokenErrorCodes.WRONG_PASSWORD,
                                            'Wrong password',
                                            UserCredentialsFormFields.PASSWORD)
    parent_error.add_error(wrong_password_error)
    return parent_error


def build_user_not_found_error() -> Error:
    parent_error = build_wrong_user_credentials_error()
    user_not_found_error = ErrorLocalizable(TokenErrorCodes.USER_NOT_FOUND,
                                            TokenErrorCodes.USER_NOT_FOUND,
                                            'User not found',
                                            UserCredentialsFormFields.USERNAME)
    email_not_found_error = ErrorLocalizable(TokenErrorCodes.USER_NOT_FOUND,
                                             TokenErrorCodes.USER_NOT_FOUND,
                                             'Email not found',
                                             UserCredentialsFormFields.EMAIL)
    parent_error.add_error(user_not_found_error)
    parent_error.add_error(email_not_found_error)
    return parent_error


class TokenFormValidator(BaseFormValidator):
    def __init__(self, user_credentials: UserCredentials):
        super().__init__()
        self.username = user_credentials.username
        self.email = user_credentials.email
        self.password = user_credentials.password

    def validate(self):
        self.__validate_user_id()
        self.__validate_password()

    def __validate_password(self):
        if not (self.password and self.password.strip()):
            error = build_empyt_field_error(UserCredentialsFormFields.PASSWORD)
            self._accumulate_error(error)

    def __validate_user_id(self):
        if self.__has_any_user_id():
            self.__validate_email_format()
        else:
            self.__init_missing_user_id_errors()

    def __has_any_user_id(self):
        return self.username and self.username.strip() or \
            self.email and self.email.strip()

    def __validate_email_format(self):
        if self.email:
            if not validate_email_format(self.email):
                error = build_invalid_email_error()
                self._accumulate_error(error)

    def __init_missing_user_id_errors(self):
        missing_username_error = ErrorLocalizable(TokenErrorCodes.MISSING_USER_IDENTIFIER, TokenErrorCodes.MISSING_USER_IDENTIFIER,
                                                  'Either username or email should be provided', UserCredentialsFormFields.USERNAME)
        missing_email_error = ErrorLocalizable(TokenErrorCodes.MISSING_USER_IDENTIFIER, TokenErrorCodes.MISSING_USER_IDENTIFIER,
                                               'Either username or email should be provided', UserCredentialsFormFields.EMAIL)
        self._accumulate_error(missing_username_error)
        self._accumulate_error(missing_email_error)

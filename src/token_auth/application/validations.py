from src.common.application.localizations import localize as _
from src.common.application.user_credentials_validations import (
    validate_email, validate_password, validate_username)
from src.common.application.validations import BaseFormValidator
from src.common.domain import Error, UserCredentials, UserCredentialsFormFields
from src.constants import TokenErrorCodes


def validate_bearer_token(token: str, lang: str) -> tuple[str, Error]:
    if not token:
        error = Error(TokenErrorCodes.INVALID_AUTHORIZATION_HEADER,
                      _(TokenErrorCodes.INVALID_AUTHORIZATION_HEADER, lang))
        return None, error

    if 'Bearer ' not in token:
        error = Error(TokenErrorCodes.INVALID_AUTHORIZATION_TYPE,
                      _(TokenErrorCodes.INVALID_AUTHORIZATION_TYPE, lang))
        return None, error

    token = token.replace('Bearer ', '')
    return token, None


class TokenFormValidator(BaseFormValidator):
    def __init__(self, user_credentials: UserCredentials, language: str):
        super().__init__(language)
        self.username = user_credentials.username
        self.email = user_credentials.email
        self.password = user_credentials.password

    def validate(self):
        self.__validate_user_id()
        validate_password(self.password, self.language, self._errors)

    def __validate_user_id(self):
        found_any_user_id = False

        if self.username:
            if validate_username(self.username, self.language, self._errors):
                found_any_user_id = True

        if self.email:
            if validate_email(self.email, self.language, self._errors):
                found_any_user_id = True

        if not found_any_user_id:
            self.__init_missing_user_id_errors()

    def __init_missing_user_id_errors(self):
        missing_username_error = Error(
            TokenErrorCodes.MISSING_USER_IDENTIFIER,
            _(TokenErrorCodes.MISSING_USER_IDENTIFIER, self.language),
            UserCredentialsFormFields.USERNAME
        )
        missing_email_error = Error(
            TokenErrorCodes.MISSING_USER_IDENTIFIER,
            _(TokenErrorCodes.MISSING_USER_IDENTIFIER, self.language),
            UserCredentialsFormFields.EMAIL
        )
        self._errors.append(missing_username_error)
        self._errors.append(missing_email_error)

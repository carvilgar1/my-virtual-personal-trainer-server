
from src.common.application.localizations import localize as _
from src.common.application.user_credentials_validations import (
    validate_email, validate_password, validate_username)
from src.common.application.validations import BaseFormValidator
from src.common.domain import (Error, UserCredentials,
                               UserCredentialsFormFields,
                               UserCredentialsRepository)
from src.constants import SignUpErrorCodes


class SignUpFormValidator(BaseFormValidator):
    def __init__(self, user_credentials: UserCredentials, language: str):
        super().__init__(language)
        self.email = user_credentials.email
        self.username = user_credentials.username
        self.password = user_credentials.password

    def validate(self) -> None:
        validate_email(self.email, self.language, self._errors)
        validate_username(self.username, self.language, self._errors)
        validate_password(self.password, self.language, self._errors)


class UniqueUserValidator:
    def __init__(self, user_credentials_repository: UserCredentialsRepository, user_credentials: UserCredentials, language: str):
        self._errors = []
        self.language = language

        self.user_credentials_repository = user_credentials_repository
        self.email = user_credentials.email
        self.username = user_credentials.username

    def has_errors(self) -> bool:
        return bool(self._errors)

    @property
    def errors(self) -> Error:
        error = None
        if self.has_errors():
            error = Error(SignUpErrorCodes.USER_ALREADY_REGISTERED, _(
                SignUpErrorCodes.USER_ALREADY_REGISTERED, self.language), errors=self._errors)
        return error

    def validate(self) -> None:
        self.__check_unique_username()
        self.__check_unique_email()

    def __check_unique_username(self):
        registered_user = self.user_credentials_repository.find_by_username(
            self.username)
        if registered_user:
            error = Error(SignUpErrorCodes.USERNAME_ALREADY_EXISTS, _(
                SignUpErrorCodes.USERNAME_ALREADY_EXISTS, self.language), UserCredentialsFormFields.USERNAME)
            self._errors.append(error)

    def __check_unique_email(self):
        registered_user = self.user_credentials_repository.find_by_email(
            self.email)
        if registered_user:
            error = Error(SignUpErrorCodes.EMAIL_ALREADY_EXISTS, _(
                SignUpErrorCodes.EMAIL_ALREADY_EXISTS, self.language), UserCredentialsFormFields.EMAIL)
            self._errors.append(error)


from typing import Iterator

from src.common.application.localizations import (LocalizableProperty,
                                                  LocalizableType)
from src.constants import CommonErrorCodes
from src.user_credentials.domain import UserCredentialsFormFields


class Error:

    def __init__(self, code: str, message: str, validation_field: str = None, errors: list['Error'] = None):
        if not code:
            raise ValueError("Error code must be set")
        self.code = code
        self.message = message
        self.validation_field = validation_field
        self.errors = errors

    def add_error(self, error: 'Error'):
        if not self.errors:
            self.errors = []
        self.errors.append(error)

    def to_json(self):
        error = {
            'code': self.code,
            'message': self.message
        }

        if self.validation_field:
            error['validationField'] = self.validation_field

        if self.errors:
            error['errors'] = [error.to_json() for error in self.errors]

        return error


class ErrorMessageLocalization(LocalizableProperty):
    def __init__(self, locale_id: str, error: Error):
        self.locale_id = locale_id
        self.error = error

    def get_loacale_id(self) -> str:
        return self.locale_id

    def localize(self, text: str) -> None:
        self.error.message = text


class ErrorLocalizable(Error, LocalizableType):

    def __init__(self, code: str, message_locale_id: str, default_message: str = None, validation_field: str = None, errors: list['Error'] = None):
        super().__init__(code, default_message, validation_field, errors)
        self.error_message_localization = ErrorMessageLocalization(
            message_locale_id, self)

    def get_localizable_properties(self) -> Iterator[LocalizableProperty]:
        yield self.error_message_localization
        if self.errors:
            yield from self.__get_nested_localizable_properties()

    def __get_nested_localizable_properties(self) -> Iterator[LocalizableProperty]:
        for nested_error in self.errors:
            if isinstance(nested_error, LocalizableType):
                for localizable_property in nested_error.get_localizable_properties():
                    yield localizable_property


def build_invalid_email_format_error() -> Error:
    return ErrorLocalizable(CommonErrorCodes.INVALID_EMAIL, CommonErrorCodes.INVALID_EMAIL, 'Invalid email format', UserCredentialsFormFields.EMAIL)


def build_missing_mandatory_field_error(validation_field: str) -> Error:
    return ErrorLocalizable(CommonErrorCodes.MISSING_MANDATORY_FIELD, CommonErrorCodes.MISSING_MANDATORY_FIELD, 'Mandatory field is missing', validation_field)

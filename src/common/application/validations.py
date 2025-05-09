import re
from datetime import datetime
from typing import Any

from src.common.application.localizations import localize as _
from src.common.domain import Error
from src.constants import (DATE_FORMAT, DATE_TIME_FORMAT,
                           DEFAULT_MAX_VARCHAR_LENGTH, EMAIL_PATTERN,
                           CommonErrorCodes)

__email_regex = re.compile(EMAIL_PATTERN)


def validate_mandatory_field(field_value: str | Any, field_key: str, language: str) -> tuple[bool, Error]:
    if field_value and field_value.strip():
        return True, None
    message = _(CommonErrorCodes.MISSING_MANDATORY_FIELD, language)
    if message:
        message = message.format(field_key=field_key)
    error = Error(CommonErrorCodes.MISSING_MANDATORY_FIELD,
                  message, validation_field=field_key)
    return False, error


def validate_content_length(field_value: str, lang: str, max_content_length_allowed=DEFAULT_MAX_VARCHAR_LENGTH) -> tuple[bool, Error]:
    if len(field_value) <= max_content_length_allowed:
        return True, None
    message = _(CommonErrorCodes.FIELD_TOO_LARGE, lang)
    if message:
        message = message.format(max_allowed_chars=max_content_length_allowed)
    error = Error(CommonErrorCodes.FIELD_TOO_LARGE, message)
    return False, error


def build_unexpected_server_error(e: Exception):
    return Error(CommonErrorCodes.INTERNAL_SERVER_ERROR, str(e))


def validate_email_format(email: str) -> bool:
    return __email_regex.match(email)


def validate_integer(field: str | Any, language: str) -> tuple[int, Error]:
    try:
        number = int(field)
        return number, None
    except ValueError:
        error = Error(
            CommonErrorCodes.INVALID_INTEGER, _(CommonErrorCodes.INVALID_INTEGER, language))
        return None, error


def validate_float(field: str | Any, language: str) -> tuple[float, Error]:
    try:
        decimal = float(field)
        return decimal, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_FLOAT, _(
            CommonErrorCodes.INVALID_FLOAT, language))
        return None, error


def validate_date(field: str | Any, language: str) -> tuple[datetime, Error]:
    try:
        date = datetime.strptime(field, DATE_FORMAT)
        return date, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_DATE, _(
            CommonErrorCodes.INVALID_DATE, language))
        return None, error


def validate_datetime(field: str | Any, language: str) -> tuple[datetime, Error]:
    try:
        date = datetime.strptime(field, DATE_TIME_FORMAT)
        return date, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_DATETIME,
                      _(CommonErrorCodes.INVALID_DATETIME, language))
        return None, error


class BaseFormValidator:
    def __init__(self, language: str = None):
        self.language = language
        self._errors = []

    def has_errors(self) -> bool:
        return bool(self._errors)

    @property
    def errors(self) -> Error:
        error = None
        if self.has_errors():
            error = Error(CommonErrorCodes.FORM_CONTAINS_ERRORS, _(
                CommonErrorCodes.FORM_CONTAINS_ERRORS, self.language), errors=self._errors)
        return error

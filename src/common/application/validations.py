import re
from datetime import datetime
from typing import Any

from src.common.domain.response import Error
from src.constants import (DATE_FORMAT, DATE_TIME_FORMAT, EMAIL_PATTERN,
                           CommonErrorCodes)

EMAIL_REGEX = re.compile(EMAIL_PATTERN)


def string_is_none_or_blank(value: str) -> bool:
    return not (value or value.strip())


def validate_email_format(email: str) -> bool:
    return EMAIL_REGEX.match(email)


def validate_mandatory_field(field_name: str, field_value: str) -> tuple[bool, Error]:
    if string_is_none_or_blank(field_value):
        error = Error(CommonErrorCodes.MISSING_MANDATORY_FIELD,
                      CommonErrorCodes.MISSING_MANDATORY_FIELD, field_name)
        return False, error
    return True, None


def validate_integer(field: str | Any) -> tuple[int, Error]:
    try:
        number = int(field)
        return number, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_INTEGER,
                      CommonErrorCodes.INVALID_INTEGER)
        return None, error


def validate_float(field: str | Any) -> tuple[float, Error]:
    try:
        decimal = float(field)
        return decimal, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_FLOAT,
                      CommonErrorCodes.INVALID_FLOAT)
        return None, error


def validate_date(field: str | Any) -> tuple[datetime, Error]:
    try:
        date = datetime.strptime(field, DATE_FORMAT)
        return date, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_DATE,
                      CommonErrorCodes.INVALID_DATE)
        return None, error


def validate_datetime(field: str | Any) -> tuple[datetime, Error]:
    try:
        date = datetime.strptime(field, DATE_TIME_FORMAT)
        return date, None
    except ValueError:
        error = Error(CommonErrorCodes.INVALID_DATETIME,
                      CommonErrorCodes.INVALID_DATETIME)
        return None, error


class FieldValidator:
    def __init__(self, field_value: str | Any, errors: list[Error] = None):
        self.__field_value = field_value
        self.__errors = [] if errors is None else errors
        self.__contains_error = False

    @property
    def field_value(self) -> str:
        return self.__field_value

    @property
    def errors(self) -> list[Error]:
        return self.__errors

    @property
    def contains_error(self) -> bool:
        return self.__contains_error

    def __activate_error_flag(self):
        self.__contains_error = True

    def add_error(self, error: Error):
        self.__errors.append(error)
        self.__activate_error_flag()

    def validate(self) -> None:
        raise NotImplementedError

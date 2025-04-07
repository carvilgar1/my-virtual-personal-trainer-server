import re
from datetime import datetime
from typing import Any

from src.common.domain import ErrorLocalizable, Error
from src.constants import (DATE_FORMAT, DATE_TIME_FORMAT, EMAIL_PATTERN,
                           CommonErrorCodes)

__email_regex = re.compile(EMAIL_PATTERN)


def validate_email_format(email: str) -> bool:
    return __email_regex.match(email)

def validate_integer(field: str | Any) -> tuple[int, Error]:
    try:
        number = int(field)
        return number, None
    except ValueError:
        error = ErrorLocalizable(CommonErrorCodes.INVALID_INTEGER, CommonErrorCodes.INVALID_INTEGER, 'Invalid integer')
        return None, error


def validate_float(field: str | Any) -> tuple[float, Error]:
    try:
        decimal = float(field)
        return decimal, None
    except ValueError:
        error = ErrorLocalizable(CommonErrorCodes.INVALID_FLOAT, CommonErrorCodes.INVALID_FLOAT, 'Invalid float')
        return None, error


def validate_date(field: str | Any) -> tuple[datetime, Error]:
    try:
        date = datetime.strptime(field, DATE_FORMAT)
        return date, None
    except ValueError:
        error = ErrorLocalizable(CommonErrorCodes.INVALID_DATE, CommonErrorCodes.INVALID_DATE, 'The field must be a valid date, format yyyy-MM-dd is expected')	
        return None, error


def validate_datetime(field: str | Any) -> tuple[datetime, Error]:
    try:
        date = datetime.strptime(field, DATE_TIME_FORMAT)
        return date, None
    except ValueError:
        error = ErrorLocalizable(CommonErrorCodes.INVALID_DATETIME, CommonErrorCodes.INVALID_DATETIME, 'The field must be a valid datetime, format ISO8601 yyyy-MM-ddTHH:mm:ss.ffffff±hh:mm is expected')
        return None, error


class BaseFormValidator:
    def __init__(self):
        self.__errors: Error
    
    def has_errors(self) -> bool:
        return bool(self.__errors)
    
    def get_errors(self) -> Error:
        return self.__errors
    
    def _add_error(self, error: Error):
        if not self.__errors:
            self.__errors = ErrorLocalizable(CommonErrorCodes.FORM_CONTAINS_ERRORS, CommonErrorCodes.FORM_CONTAINS_ERRORS, 'Form contains errors')
        self.__errors.add_error(error)

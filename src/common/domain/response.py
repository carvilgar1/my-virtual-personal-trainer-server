from enum import Enum
from typing import Iterator

from src.common.application.localizations import (LocalizableProperty,
                                                  LocalizableType)
from src.common.domain.errors import Error


class Status(Enum):
    SUCCESS = 'Success'
    ERROR = 'Error'


class Response:
    def __init__(self, status: Status, error: Error = None):
        self.status = status
        self.error = error

    def set_error_status(self, error: Error):
        self.error = error
        self.status = Status.ERROR

    def to_json(self):
        response = {
            'status': self.status.value
        }

        if self.error:
            response['error'] = self.error.to_json()

        return response


class ResponseLocalizable(Response, LocalizableType):

    def __init__(self, status: Status = Status.SUCCESS, error: Error = None):
        super().__init__(status, error)

    def get_localizable_properties(self) -> Iterator[LocalizableProperty]:
        if self.error and isinstance(self.error, LocalizableType):
            yield from self.error.get_localizable_properties()

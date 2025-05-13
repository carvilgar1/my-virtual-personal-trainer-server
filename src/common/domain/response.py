from enum import Enum


class Status(Enum):
    SUCCESS = 'Success'
    ERROR = 'Error'
    UPDATED = 'Updated'
    DELETED = 'Deleted'


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
            'code': self.code
        }

        if self.message:
            error['message'] = self.message

        if self.validation_field:
            error['validationField'] = self.validation_field

        if self.errors:
            error['errors'] = [error.to_json() for error in self.errors]

        return error


class Response:
    def __init__(self, status: Status, error: 'Error' = None):
        self.status = status
        self.error = error

    def set_error_status(self, error: 'Error'):
        self.error = error
        self.status = Status.ERROR

    def to_json(self):
        response = {
            'status': self.status.value
        }

        if self.error:
            response['error'] = self.error.to_json()

        return response

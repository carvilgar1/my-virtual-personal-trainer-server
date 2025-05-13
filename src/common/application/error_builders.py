from src.common.application.localizations import localize as _
from src.common.domain import Error
from src.constants import CommonErrorCodes


def init_missing_field_error(field_name: str, language: str):
    message = _(CommonErrorCodes.MISSING_MANDATORY_FIELD, language)
    if message:
        message = message.format(field_key=field_name)
    error = Error(CommonErrorCodes.MISSING_MANDATORY_FIELD,
                  message, validation_field=field_name)
    return error


def init_internal_server_error(exception):
    return Error(CommonErrorCodes.INTERNAL_SERVER_ERROR, str(exception))

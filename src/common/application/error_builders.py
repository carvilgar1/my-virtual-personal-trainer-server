from src.common.domain import (Error, ErrorLocalizable,
                               UserCredentialsFormFields)
from src.constants import CommonErrorCodes, SignUpErrorCodes, TokenErrorCodes


def init_server_exception_error(e: Exception) -> Error:
    return Error(CommonErrorCodes.INTERNAL_SERVER_ERROR, str(e))


def init_password_error(code: str, locale_id: str, default_message: str) -> Error:
    return init_form_field_error(code, locale_id, default_message, UserCredentialsFormFields.PASSWORD)


def init_email_error(code: str, locale_id: str, default_message: str) -> Error:
    return init_form_field_error(code, locale_id, default_message, UserCredentialsFormFields.EMAIL)


def init_username_error(code: str, locale_id: str, default_message: str) -> Error:
    return init_form_field_error(code, locale_id, default_message, UserCredentialsFormFields.USERNAME)


def init_form_field_error(code: str, locale_id: str, default_message: str, form_field: str) -> Error:
    return ErrorLocalizable(code, locale_id, default_message, form_field)


def init_password_too_short_error() -> Error:
    code = SignUpErrorCodes.PASSWORD_TOO_SHORT
    locale_id = SignUpErrorCodes.PASSWORD_TOO_SHORT
    default_message = 'Password must be at least 8 characters long'
    return init_password_error(code, locale_id, default_message)


def init_password_missing_lowercase_error() -> Error:
    code = SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE
    locale_id = SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE
    default_message = 'Password must contain at least one lowercase letter'
    return init_password_error(code, locale_id, default_message)


def init_password_missing_uppercase_error() -> Error:
    code = SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE
    locale_id = SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE
    default_message = 'Password must contain at least one uppercase letter'
    return init_password_error(code, locale_id, default_message)


def init_password_missing_digit_error() -> Error:
    code = SignUpErrorCodes.PASSWORD_MISSING_DIGIT
    locale_id = SignUpErrorCodes.PASSWORD_MISSING_DIGIT
    default_message = 'Password must contain at least one digit'
    return init_password_error(code, locale_id, default_message)


def init_password_missing_special_character_error() -> Error:
    code = SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR
    locale_id = SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR
    default_message = 'Password must contain at least one special character'
    return init_password_error(code, locale_id, default_message)


def init_email_format_error() -> Error:
    code = CommonErrorCodes.INVALID_EMAIL
    locale_id = CommonErrorCodes.INVALID_EMAIL
    default_message = 'Invalid email format'
    return init_email_error(code, locale_id, default_message)


def init_username_already_exists_error() -> Error:
    code = SignUpErrorCodes.USERNAME_ALREADY_EXISTS
    locale_id = SignUpErrorCodes.USERNAME_ALREADY_EXISTS
    default_message = 'Username already registered'
    return init_username_error(code, locale_id, default_message)


def init_email_already_exists_error() -> Error:
    code = SignUpErrorCodes.EMAIL_ALREADY_EXISTS
    locale_id = SignUpErrorCodes.EMAIL_ALREADY_EXISTS
    default_message = 'Email already registered'
    return init_email_error(code, locale_id, default_message)


def init_user_already_registered_error(errors: list[Error]) -> Error:
    code = SignUpErrorCodes.USER_ALREADY_REGISTERED
    locale_id = SignUpErrorCodes.USER_ALREADY_REGISTERED
    default_message = 'User already registered'
    return ErrorLocalizable(code, locale_id, default_message, errors=errors)


def init_form_contains_errors_error(errors: list[Error]) -> Error:
    code = CommonErrorCodes.FORM_CONTAINS_ERRORS
    locale_id = CommonErrorCodes.FORM_CONTAINS_ERRORS
    default_message = 'Form contains errors'
    return ErrorLocalizable(code, locale_id, default_message, errors=errors)


def init_missing_user_identifier_error(validation_field: str) -> Error:
    code = TokenErrorCodes.MISSING_USER_IDENTIFIER
    locale_id = TokenErrorCodes.MISSING_USER_IDENTIFIER
    default_message = 'Any of username or email should be provided'
    return ErrorLocalizable(code, locale_id, default_message, validation_field)


def init_missing_username_identifier_error() -> Error:
    return init_missing_user_identifier_error(UserCredentialsFormFields.USERNAME)


def init_missing_email_identifier_error() -> Error:
    return init_missing_user_identifier_error(UserCredentialsFormFields.EMAIL)


def build_missing_mandatory_field_error(validation_field: str) -> Error:
    return ErrorLocalizable(CommonErrorCodes.MISSING_MANDATORY_FIELD, CommonErrorCodes.MISSING_MANDATORY_FIELD, 'Mandatory field is missing', validation_field)

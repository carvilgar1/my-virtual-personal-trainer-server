from src.common.application.localizations import localize as _
from src.common.application.validations import (validate_content_length,
                                                validate_email_format,
                                                validate_mandatory_field)
from src.common.domain import Error, UserCredentialsFormFields
from src.constants import (MAX_USERNAME_CHARS, PASSWORD_ALLOWED_SYMBOLS,
                           PASSWORD_MIN_LENGTH, CommonErrorCodes,
                           SignUpErrorCodes)


def validate_password(password: str, lang: str, errors: list[Error]) -> bool:
    is_filled, error = validate_mandatory_field(
        password, UserCredentialsFormFields.PASSWORD, lang)
    if not is_filled:
        errors.append(error)
        return False

    valid_length, error = validate_content_length(
        password, lang)
    if not valid_length:
        error.validation_field = UserCredentialsFormFields.PASSWORD
        errors.append(error)
        return False

    valid_password = True
    if len(password) < PASSWORD_MIN_LENGTH:
        error = Error(SignUpErrorCodes.PASSWORD_TOO_SHORT, _(
            SignUpErrorCodes.PASSWORD_TOO_SHORT, lang), UserCredentialsFormFields.PASSWORD)
        valid_password = False
        errors.append(error)

    if not any(char.islower() for char in password):
        error = Error(SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE, _(
            SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE, lang), UserCredentialsFormFields.PASSWORD)
        valid_password = False
        errors.append(error)

    if not any(char.isupper() for char in password):
        error = Error(SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE, _(
            SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE, lang), UserCredentialsFormFields.PASSWORD)
        valid_password = False
        errors.append(error)

    if not any(char.isdigit() for char in password):
        error = Error(SignUpErrorCodes.PASSWORD_MISSING_DIGIT, _(
            SignUpErrorCodes.PASSWORD_MISSING_DIGIT, lang), UserCredentialsFormFields.PASSWORD)
        valid_password = False
        errors.append(error)

    if not any(char in PASSWORD_ALLOWED_SYMBOLS for char in password):
        error = Error(SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR, _(
            SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR, lang), UserCredentialsFormFields.PASSWORD)
        valid_password = False
        errors.append(error)

    return valid_password


def validate_email(email: str, lang: str, errors: list[Error]) -> bool:
    is_filled, error = validate_mandatory_field(
        email, UserCredentialsFormFields.EMAIL, lang)
    if not is_filled:
        errors.append(error)
        return False

    valid_length, error = validate_content_length(
        email, lang)
    if not valid_length:
        error.validation_field = UserCredentialsFormFields.EMAIL
        errors.append(error)
        return False

    if not validate_email_format(email):
        error = Error(CommonErrorCodes.INVALID_EMAIL, _(
            CommonErrorCodes.INVALID_EMAIL, lang), UserCredentialsFormFields.EMAIL)
        errors.append(error)
        return False

    return True


def validate_username(username: str, lang: str, errors: list[Error]) -> bool:
    is_filled, error = validate_mandatory_field(
        username, UserCredentialsFormFields.USERNAME, lang)
    if not is_filled:
        errors.append(error)
        return False

    valid_length, error = validate_content_length(
        username, lang, MAX_USERNAME_CHARS)
    if not valid_length:
        error.validation_field = UserCredentialsFormFields.USERNAME
        errors.append(error)
        return False

    return True

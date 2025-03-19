from bcrypt import gensalt, hashpw
from flask import Blueprint, current_app, jsonify, request

from src.common.application.localizations import Localizer
from src.common.domain import (Error, ErrorLocalizable, Response,
                               ResponseLocalizable, Status)
from src.constants import (DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM,
                           CommonErrorCodes, SignUpErrorCodes)
from src.sign_up.application.validations import SignUpValidator
from src.user_credentials.domain import (UserCredentials,
                                         UserCredentialsFormFields,
                                         UserCredentialsRepository)

sign_up_blueprint = Blueprint('sign_up', __name__, url_prefix='/sign-up')


@sign_up_blueprint.route('/', methods=['POST'])
def handle_sign_up_request():
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        localizer = current_app.config['LOCALIZER']
        user_credentials_repository = current_app.config[
            'APP_REPOSITORIES']['USER_CREDENTIALS_REPOSITORY']
        user_credentials = _get_user_credentials()

        response, status = sign_up(
            localizer, user_credentials_repository, user_credentials, language)
        return jsonify(response.to_json()), status
    except Exception as e:
        response = Response(Status.ERROR)
        response.error = Error(CommonErrorCodes.INTERNAL_SERVER_ERROR, str(e))
        return jsonify(response.to_json()), 500


def sign_up(localizer: Localizer, user_credentials_repository: UserCredentialsRepository, user_credentials: UserCredentials, language: str) -> tuple[Response, int]:
    response = ResponseLocalizable(Status.SUCCESS)

    validator = SignUpValidator(user_credentials)
    validator.validate()
    if validator.form_contains_errors():
        response.set_error_status(validator.get_error())
        return response, 400

    are_unique_credentials, error = __check_unique_credentials(
        user_credentials_repository, user_credentials)
    if not are_unique_credentials:
        response.set_error_status(error)
        return response, 400

    user_credentials.password = hashpw(
        user_credentials.password.encode('utf-8'), gensalt())
    user_credentials_repository.save(user_credentials)

    localizer.localize(response, language)
    return response, 201


def _get_user_credentials() -> UserCredentials:
    form = request.form
    email = form.get(UserCredentialsFormFields.EMAIL)
    username = form.get(UserCredentialsFormFields.USERNAME)
    password = form.get(UserCredentialsFormFields.PASSWORD)
    return UserCredentials(None, email, username, password)


def __check_unique_credentials(user_credentials_repository: UserCredentialsRepository, user_credentials: UserCredentials) -> tuple[bool, Error]:
    errors = []
    __check_unique_username(
        user_credentials_repository, user_credentials.username, errors)
    __check_unique_email(
        user_credentials_repository, user_credentials.email, errors)

    if not errors:
        return True, None

    error = ErrorLocalizable(SignUpErrorCodes.USER_ALREADY_REGISTERED,
                             SignUpErrorCodes.USER_ALREADY_REGISTERED,
                             'Non unique credentials', errors=errors)
    return False, error


def __check_unique_username(user_credentials_repository: UserCredentialsRepository, username: str, errors: list[Error]) -> None:
    user_credentials = user_credentials_repository.find_by_username(username)
    if user_credentials:
        error = ErrorLocalizable(SignUpErrorCodes.USERNAME_ALREADY_EXISTS,
                                 SignUpErrorCodes.USERNAME_ALREADY_EXISTS,
                                 'Username already exists',
                                 UserCredentialsFormFields.USERNAME)
        errors.append(error)


def __check_unique_email(user_credentials_repository: UserCredentialsRepository, email: str, errors: list[Error]) -> None:
    user_credentials = user_credentials_repository.find_by_email(email)
    if user_credentials:
        error = ErrorLocalizable(SignUpErrorCodes.EMAIL_ALREADY_EXISTS,
                                 SignUpErrorCodes.EMAIL_ALREADY_EXISTS,
                                 'Email already exists',
                                 UserCredentialsFormFields.EMAIL)
        errors.append(error)

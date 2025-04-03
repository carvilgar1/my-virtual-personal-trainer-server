from bcrypt import gensalt, hashpw
from flask import Blueprint, jsonify, request

from src.common.domain import (Error, Response, ResponseLocalizable, Status,
                               UserCredentials, UserCredentialsFormFields)
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM
from src.settings import localizer, user_credentials_repository
from src.sign_up.application.validations import (SignUpFormValidator,
                                                 UniqueUserValidator)

sign_up_blueprint = Blueprint('sign_up', __name__, url_prefix='/sign-up')


def _get_user_credentials() -> UserCredentials:
    form = request.form
    email = form.get(UserCredentialsFormFields.EMAIL)
    username = form.get(UserCredentialsFormFields.USERNAME)
    password = form.get(UserCredentialsFormFields.PASSWORD)
    return UserCredentials(None, email, username, password)


@sign_up_blueprint.route('/', methods=['POST'])
def handle_sign_up_request():
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        user_credentials = _get_user_credentials()

        response, status = sign_up(user_credentials)
        localizer.localize(response, language)

        return jsonify(response.to_json()), status
    except Exception as e:
        error = error_builders.init_server_exception_error(e)
        return ResponseLocalizable(Status.ERROR, error), 500


def sign_up(user_credentials: UserCredentials) -> tuple[Response, int]:
    form_validator = SignUpFormValidator(user_credentials)
    form_validator.validate()
    if form_validator.has_errors():
        error = form_validator.get_errors()
        return ResponseLocalizable(Status.ERROR, error), 400

    unique_user_validator = UniqueUserValidator(
        user_credentials_repository, user_credentials)
    unique_user_validator.validate()
    if unique_user_validator.has_errors():
        error = unique_user_validator.get_errors()
        return ResponseLocalizable(Status.ERROR, error), 400

    user_credentials.password = hashpw(
        user_credentials.password.encode('utf-8'), gensalt())

    user_credentials_repository.save(user_credentials)

    return Response(Status.SUCCESS), 201

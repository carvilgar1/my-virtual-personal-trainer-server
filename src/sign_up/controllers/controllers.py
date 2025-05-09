from bcrypt import gensalt, hashpw
from flask import Blueprint, jsonify, request

from src.common.application.localizations import localize as _
from src.common.domain import (Response, Status, UserCredentials,
                               UserCredentialsFormFields,
                               UserCredentialsRepository,
                               init_internal_server_error)
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM
from src.settings import user_credentials_repository
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

        response, status = sign_up(
            user_credentials_repository, user_credentials, language)

        return jsonify(response.to_json()), status
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


def sign_up(
        user_credentials_repository: UserCredentialsRepository,
        user_credentials: UserCredentials,
        lang: str
) -> tuple[Response, int]:
    form_validator = SignUpFormValidator(user_credentials, lang)
    form_validator.validate()
    if form_validator.has_errors():
        error = form_validator.errors
        return Response(Status.ERROR, error), 400

    unique_user_validator = UniqueUserValidator(
        user_credentials_repository, user_credentials, lang)
    unique_user_validator.validate()
    if unique_user_validator.has_errors():
        error = unique_user_validator.errors
        return Response(Status.ERROR, error), 400

    user_credentials.password = hashpw(
        user_credentials.password.encode('utf-8'), gensalt())

    user_credentials_repository.save(user_credentials)

    return Response(Status.SUCCESS), 201

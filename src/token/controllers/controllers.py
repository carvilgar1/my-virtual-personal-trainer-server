import bcrypt
from flask import Blueprint, jsonify, request

from src.common.application.localizations import localize as _
from src.common.application.validations import build_unexpeted_server_error
from src.common.domain import (Error, Response, Status, UserCredentials,
                               UserCredentialsFormFields,
                               UserCredentialsRepository)
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM, TokenErrorCodes
from src.settings import authentication_service, user_credentials_repository
from src.token.application.authentication import (AuthenticationService,
                                                  authorization_required)
from src.token.application.validations import TokenFormValidator

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


@token_blueprint.route('/new', methods=['POST'])
def handle_new_token_request():
    try:
        user_credentials = _get_user_credentials()
        lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

        response, status = generate_new_token(
            authentication_service, user_credentials_repository, user_credentials, lang)
        return jsonify(response.to_json()), status

    except Exception as e:
        response = Response(Status.ERROR, build_unexpeted_server_error(e))
        return jsonify(response.to_json()), 500


@token_blueprint.route('/refresh', methods=['POST'])
@authorization_required(authentication_service, 'refresh_token')
def handle_refresh_token_request(current_user: UserCredentials):
    try:
        lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

        response, status = refresh_token(
            authentication_service, user_credentials_repository, current_user, lang)
        return jsonify(response.to_json()), status

    except Exception as e:
        response = Response(Status.ERROR, build_unexpeted_server_error(e))
        return jsonify(response.to_json()), 500


def generate_new_token(
    authentication_service: AuthenticationService,
    user_credentials_repository: UserCredentialsRepository,
    user_credentials: UserCredentials,
    lang: str
) -> tuple[Response, int]:
    validator = TokenFormValidator(user_credentials, lang)
    validator.validate()
    if validator.has_errors():
        response = Response(Status.ERROR, validator.errors)
        return response, 400

    found_current_user = user_credentials_repository.find_by_username_or_email(
        user_credentials.username, user_credentials.email)
    if found_current_user and \
            bcrypt.checkpw(user_credentials.password.encode('utf-8'), found_current_user.password):
        jwt_response = authentication_service.grant_access(found_current_user)
        return jwt_response, 200

    error = Error(TokenErrorCodes.INVALID_USER_CREDENTIALS, _(
        TokenErrorCodes.INVALID_USER_CREDENTIALS, lang))
    response = Response(Status.ERROR, error)
    return response, 401


def refresh_token(
    authentication_service: AuthenticationService,
    user_credentials_repository: UserCredentialsRepository,
    current_user: UserCredentials,
    lang: str
) -> tuple[Response, int]:
    found_current_user = user_credentials_repository.find_by_username_or_email(
        current_user.username, current_user.email)
    if found_current_user:
        jwt_response = authentication_service.grant_access(found_current_user)
        return jwt_response, 200

    error = Error(TokenErrorCodes.INVALID_USER_CREDENTIALS, _(
        TokenErrorCodes.INVALID_USER_CREDENTIALS, lang))
    response = Response(Status.ERROR, error)
    return response, 403


def _get_user_credentials() -> UserCredentials:
    form = request.form
    email = form.get(UserCredentialsFormFields.EMAIL)
    username = form.get(UserCredentialsFormFields.USERNAME)
    password = form.get(UserCredentialsFormFields.PASSWORD)
    return UserCredentials(None, email, username, password)

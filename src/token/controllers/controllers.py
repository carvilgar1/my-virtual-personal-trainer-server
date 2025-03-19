import bcrypt
from flask import Blueprint, current_app, jsonify, request

from src.common.application.localizations import Localizer
from src.common.domain.errors import ErrorLocalizable
from src.common.domain.response import Response, ResponseLocalizable
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM, TokenErrorCodes
from src.settings import (AUTHENTICATION_SERVICE, LOCALIZER,
                          USER_CREDENTIALS_REPOSITORY)
from src.token.application.jwt_authentication_service import \
    JWTAuthenticationService
from src.token.application.validations import \
    TokenFormValidator
from src.token.domain.authentication_service import AuthenticationService
from src.token.domain.response import JwtTokenResponse
from src.user_credentials.domain.user_credentials import (
    UserCredentials, UserCredentialsFormFields)
from src.user_credentials.domain.user_credentials_repository import \
    UserCredentialsRepository

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


@token_blueprint.route('/new', methods=['POST'])
def handle_new_token_request():
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    user_credentials = _get_user_credentials()
    
    response = ResponseLocalizable()

    validator = TokenFormValidator(user_credentials)
    validator.validate()
    if validator.has_errors:
        response.set_error_status(validator.get_errors())
    
    current_user = USER_CREDENTIALS_REPOSITORY.find_by_username_or_email(
        user_credentials.username, user_credentials.email)
    if not current_user:
        error = ErrorLocalizable(TokenErrorCodes.USER_NOT_FOUND, TokenErrorCodes.USER_NOT_FOUND, 'User not found')
        response.set_error_status(error)
        return response

    if not bcrypt.checkpw(user_credentials.password.encode('utf-8'), current_user.password):
        error = ErrorLocalizable(TokenErrorCodes.WRONG_PASSWORD, TokenErrorCodes.WRONG_PASSWORD, 'Wrong password')
        response.set_error_status(error)
        return response

    return jsonify(AUTHENTICATION_SERVICE.grant_access(user_credentials).to_json()), 200


@token_blueprint.route('/refresh', methods=['POST'])
def handle_refresh_token_request():
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    refresh_token = request.headers.get('Authorization').replace('Bearer ', '')

    payload, error = AUTHENTICATION_SERVICE.authenticate({'refresh_token': refresh_token})
    if error:
        return jsonify({'error': error.message}), 401
    
    payload
    return jsonify(AUTHENTICATION_SERVICE.grant_access(payload).to_json()), 200


def _get_user_credentials() -> UserCredentials:
    form = request.form
    email = form.get(UserCredentialsFormFields.EMAIL)
    username = form.get(UserCredentialsFormFields.USERNAME)
    password = form.get(UserCredentialsFormFields.PASSWORD)
    return UserCredentials(None, email, username, password)

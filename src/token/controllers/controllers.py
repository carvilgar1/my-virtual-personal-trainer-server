import bcrypt
from flask import Blueprint, request

from src.common.domain.errors import ErrorLocalizable
from src.common.domain.response import Response, ResponseLocalizable, Status
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM, TokenErrorCodes
from src.settings import authentication_service, user_credentials_repository
from src.token.application.validations import TokenFormValidator
from src.common.domain.user_credentials import (
    UserCredentials, UserCredentialsFormFields)

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


def build_user_not_found_error():
    return ErrorLocalizable(
        TokenErrorCodes.USER_NOT_FOUND, TokenErrorCodes.USER_NOT_FOUND, 'User not found')


def build_wrong_password_error():
    return ErrorLocalizable(
        TokenErrorCodes.WRONG_PASSWORD, TokenErrorCodes.WRONG_PASSWORD, 'Wrong password')


@token_blueprint.route('/new', methods=['POST'])
def handle_new_token_request():
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    user_credentials = _get_user_credentials()

    response = ResponseLocalizable(language)
    validate_form(user_credentials, response)
    if response.error:
        return response, 400
    validate_user_exists(user_credentials, response)
    if response.error:
        return response, 401

    response = authentication_service.grant_access(user_credentials)
    return response, 200


def validate_form(user_credentials: UserCredentials, response: ResponseLocalizable):
    validator = TokenFormValidator(user_credentials)
    validator.validate()
    if validator.has_errors:
        response.set_error_status(validator.get_errors())


def validate_user_exists(user_credentials: UserCredentials, response: ResponseLocalizable):
    current_user = user_credentials_repository.find_by_username_or_email(
        user_credentials.username, user_credentials.email)
    if not current_user:
        error = build_user_not_found_error()
        response.set_error_status(error)
    elif not check_password_match(user_credentials, current_user):
        error = build_wrong_password_error()
        response.set_error_status(error)


def check_password_match(user_credentials: UserCredentials, current_user: UserCredentials):
    return not bcrypt.checkpw(user_credentials.password.encode('utf-8'), current_user.password)


@token_blueprint.route('/refresh', methods=['POST'])
def handle_refresh_token_request():
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    refresh_token = request.headers.get('Authorization').replace('Bearer ', '')

    payload, error = authentication_service.authenticate(
        {'refresh_token': refresh_token})
    if error:
        return ResponseLocalizable(language, Status.ERROR, error), 401

    return authentication_service.grant_access(payload), 200


def _get_user_credentials() -> UserCredentials:
    form = request.form
    email = form.get(UserCredentialsFormFields.EMAIL)
    username = form.get(UserCredentialsFormFields.USERNAME)
    password = form.get(UserCredentialsFormFields.PASSWORD)
    return UserCredentials(None, email, username, password)

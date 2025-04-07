import re

import bcrypt
from flask import Blueprint, jsonify, request

from src.common.domain.errors import ErrorLocalizable
from src.common.domain.response import (Error, Response, ResponseLocalizable,
                                        Status)
from src.common.domain.user_credentials import (UserCredentials,
                                                UserCredentialsFormFields)
from src.constants import (DEFAULT_LANGUAGE, EMAIL_PATTERN, LANGUAGE_GET_PARAM,
                           CommonErrorCodes, TokenErrorCodes)
from src.settings import authentication_service

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


@token_blueprint.route('/new', methods=['POST'])
def handle_new_token_request():
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    user_credentials = _get_user_credentials()
    form_validator = TokenFormValidator(user_credentials)
    form_validator.validate()
    if form_validator.errors:
        response = ResponseLocalizable(Status.ERROR, form_validator.errors)
        return jsonify(response.to_json()), 400

    response = authentication_service.grant_access(user_credentials)
    return response, 200


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

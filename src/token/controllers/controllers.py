
from flask import Blueprint, jsonify, request

from src.common.domain import UserCredentials, UserCredentialsFormFields
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM
from src.settings import (authentication_service, localizer,
                          user_credentials_repository)
from src.token.application.authentication import generate_new_token

token_blueprint = Blueprint('token', __name__, url_prefix='/token')


@token_blueprint.route('/new', methods=['POST'])
def handle_new_token_request():
    user_credentials = _get_user_credentials()
    lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

    response, status_code = generate_new_token(
        user_credentials_repository, authentication_service, user_credentials)
    localizer.localize(response, lang)

    return jsonify(response.to_json()), status_code


def _get_user_credentials() -> UserCredentials:
    form = request.form
    email = form.get(UserCredentialsFormFields.EMAIL)
    username = form.get(UserCredentialsFormFields.USERNAME)
    password = form.get(UserCredentialsFormFields.PASSWORD)
    return UserCredentials(None, email, username, password)

import re
import bcrypt
from flask import Blueprint, jsonify, request

from src.common.domain.errors import ErrorLocalizable
from src.common.domain.response import Response, ResponseLocalizable, Status, Error
from src.common.domain.user_credentials import (UserCredentials,
                                                UserCredentialsFormFields)
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM, TokenErrorCodes, EMAIL_PATTERN, CommonErrorCodes
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

class BaseFormValidator:
    def __init__(self):
        self.__errors: Error
    
    def has_errors(self) -> bool:
        return bool(self.__errors)
    
    def get_errors(self) -> Error:
        return self.__errors
    
    def _add_error(self, error: Error):
        if not self.__errors:
            self.__errors = ErrorLocalizable(CommonErrorCodes.FORM_CONTAINS_ERRORS, CommonErrorCodes.FORM_CONTAINS_ERRORS, 'Form contains errors')
        self.__errors.add_error(error)
    

class TokenFormValidator(BaseFormValidator):
    def __init__(self, user_credentials: UserCredentials):
        super.__init__()
        
        self.username = user_credentials.username
        self.email = user_credentials.email
        self.password = user_credentials.password

    def validate(self):
        self.validate_user_id()
        self.validate_password_field()

    def validate_password_field(self):
        if not self.password:
            error = self.build_empty_field_error()
            super._add_error(error)

            
    def validate_user_id(self):
        if self.username or self.email:
            if self.email:
                if not re.match(self.email, EMAIL_PATTERN):
                    error = ErrorLocalizable(CommonErrorCodes.INVALID_EMAIL, CommonErrorCodes.INVALID_EMAIL, 'Email is invalid')
                    self.errors.add_error(error)
        else:
            error = ErrorLocalizable(TokenErrorCodes.MISSING_USER_IDENTIFIER, TokenErrorCodes.MISSING_USER_IDENTIFIER, 'Yo must introduce any user identification')
            self.errors = error
    
            
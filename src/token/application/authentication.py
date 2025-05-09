from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

import jwt
from flask import jsonify, request

from src.common.application.localizations import localize as _
from src.common.domain import Error, Response, Status, UserCredentials
from src.constants import (DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM,
                           CommonErrorCodes, TokenErrorCodes)
from src.token.application.validations import validate_bearer_token
from src.token.domain import JwtTokenResponse


class AuthenticationService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def grant_access(self, credentials: UserCredentials) -> Optional[Any]:
        pass

    @abstractmethod
    def authenticate(self, auth_context: dict | Any) -> UserCredentials:
        pass


class JWTAuthenticationService(AuthenticationService):
    def __init__(self, secret_key: str, refresh_secret_key: str, access_token_expiration_hours: int, refresh_token_expiration_days: int, algorithm: str):
        self.secret_key = secret_key
        self.refresh_secret_key = refresh_secret_key
        self.access_token_expiration = access_token_expiration_hours * 3600
        self.refresh_token_expiration = refresh_token_expiration_days * 86400
        self.algorithm = algorithm

    def grant_access(self, user_credentials: UserCredentials) -> JwtTokenResponse:
        token_payload = {
            'sub': user_credentials.user_id,
            'username': user_credentials.username,
            'email': user_credentials.email
        }

        token_payload['iat'] = int(datetime.now().timestamp())
        token_payload['exp'] = int(token_payload['iat'] +
                                   self.access_token_expiration)
        access_token = jwt.encode(
            token_payload, self.secret_key, algorithm=self.algorithm)

        token_payload['iat'] = int(datetime.now().timestamp())
        token_payload['exp'] = int(token_payload['iat'] +
                                   self.refresh_token_expiration)
        refresh_token = jwt.encode(
            token_payload, self.refresh_secret_key, algorithm=self.algorithm)

        return JwtTokenResponse(access_token, refresh_token, self.access_token_expiration)

    def authenticate(self, auth_context: dict) -> UserCredentials:
        access_token = auth_context.get('access_token')
        refresh_token = auth_context.get('refresh_token')
        if access_token:
            return self.__decode_token(access_token, self.secret_key)
        elif refresh_token:
            return self.__decode_token(refresh_token, self.refresh_secret_key)
        else:
            raise AttributeError(
                'No valid AuthContext were provided for JWTAuthenticationService')

    def __decode_token(self, token: str, secret_key: str) -> UserCredentials:
        decoded_payload = jwt.decode(
            token, secret_key, algorithms=[self.algorithm])

        return UserCredentials(
            decoded_payload['sub'],
            decoded_payload['email'],
            decoded_payload['username'],
            None
        )


def authorization_required(authentication_service: AuthenticationService, required_secret='access_token'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                token = request.headers.get('Authorization')
                lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
                token, errors = validate_bearer_token(token, lang)
                if errors:
                    response = Response(Status.ERROR, errors)
                    return jsonify(response.to_json()), 400

                auth_context = {required_secret: token}
                current_user = authentication_service.authenticate(
                    auth_context)
                return func(current_user, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                response = Response(Status.ERROR, Error(
                    TokenErrorCodes.EXPIRED_TOKEN, _(TokenErrorCodes.EXPIRED_TOKEN, lang)))
                return jsonify(response.to_json()), 401
            except jwt.InvalidTokenError:
                response = Response(Status.ERROR, Error(
                    TokenErrorCodes.INVALID_TOKEN, _(TokenErrorCodes.INVALID_TOKEN, lang)))
                return jsonify(response.to_json()), 401
            except Exception as e:
                response = Response(Status.ERROR, Error(
                    CommonErrorCodes.INTERNAL_SERVER_ERROR, str(e)))
                return jsonify(response.to_json()), 500
        return wrapper
    return decorator

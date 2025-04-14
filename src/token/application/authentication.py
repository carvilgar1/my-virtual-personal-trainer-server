from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

import bcrypt
import jwt

from src.common.domain.errors import Error, ErrorLocalizable
from src.common.domain.response import ResponseLocalizable, Status
from src.common.domain.user_credentials import UserCredentials
from src.common.domain.user_credentials_repository import \
    UserCredentialsRepository
from src.constants import TokenErrorCodes
from src.token.application.validations import (TokenFormValidator,
                                               build_user_not_found_error,
                                               build_wrong_password_error)
from src.token.domain.response import JwtTokenResponse, TokenPayload


class AuthenticationService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def grant_access(self, credentials: UserCredentials) -> Optional[Any]:
        pass

    @abstractmethod
    def authenticate(self, auth_context: dict | Any) -> Tuple[UserCredentials, Error]:
        pass


class JWTAuthenticationService(AuthenticationService):
    def __init__(self, secret_key: str, refresh_secret_key: str, access_token_expiration_hours: int, refresh_token_expiration_days: int, algorithm: str):
        self.secret_key = secret_key
        self.refresh_secret_key = refresh_secret_key
        self.access_token_expiration = access_token_expiration_hours * 3600
        self.refresh_token_expiration = refresh_token_expiration_days * 86400
        self.algorithm = algorithm

    def grant_access(self, user_credentials: UserCredentials) -> JwtTokenResponse:
        token_payload = TokenPayload(
            user_credentials.username, user_credentials.username, user_credentials.email)

        token_payload.set_expiration(self.access_token_expiration)
        access_token = jwt.encode(token_payload.to_dict(
        ), self.secret_key, algorithm=self.algorithm)

        token_payload.set_expiration(self.refresh_token_expiration)
        refresh_token = jwt.encode(token_payload.to_dict(
        ), self.refresh_secret_key, algorithm=self.algorithm)

        return JwtTokenResponse(access_token, refresh_token, self.access_token_expiration)

    def authenticate(self, auth_context: dict) -> Tuple[Optional[UserCredentials], Optional[Error]]:
        try:
            if 'refresh_token' in auth_context:
                return self.__decode_refresh_token(auth_context), None
            else:
                return self.__decode_access_token(auth_context), None
        except jwt.ExpiredSignatureError:
            return None, build_expired_token_error()
        except jwt.InvalidTokenError:
            return None, build_invalid_token_error()
        except Exception as e:
            return None, build_unexpected_error(str(e))

    def __decode_access_token(self, auth_context: dict) -> UserCredentials:
        token = auth_context['access_token']
        return self.__decode_token(token, self.secret_key)

    def __decode_refresh_token(self, auth_context: dict) -> UserCredentials:
        token = auth_context['refresh_token']
        return self.__decode_token(token, self.refresh_secret_key)

    def __decode_token(self, token: str, secret_key: str) -> UserCredentials:
        decoded_payload = jwt.decode(
            token, secret_key, algorithms=[self.algorithm])
        return UserCredentials(
            id=decoded_payload['sub'],
            username=decoded_payload['username'],
            email=decoded_payload['email'],
            password=None
        )


def generate_new_token(
    user_credentials_repository: UserCredentialsRepository,
    authentication_service: AuthenticationService,
    user_credentials: UserCredentials
) -> Tuple[ResponseLocalizable, int]:
    form_validator = TokenFormValidator(user_credentials)
    form_validator.validate()
    if form_validator.has_errors():
        return ResponseLocalizable(Status.ERROR, form_validator.errors), 400

    current_user = user_credentials_repository.find_by_username_or_email(
        user_credentials.username, user_credentials.email)
    if not current_user:
        return ResponseLocalizable(Status.ERROR, build_user_not_found_error()), 404
    if not bcrypt.checkpw(user_credentials.password.encode('utf-8'), current_user.password):
        return ResponseLocalizable(Status.ERROR, build_wrong_password_error()), 401

    jwt_token = authentication_service.grant_access(user_credentials)
    return jwt_token, 200


def build_expired_token_error() -> Error:
    return ErrorLocalizable(TokenErrorCodes.EXPIRED_TOKEN, TokenErrorCodes.EXPIRED_TOKEN, 'Expired token')


def build_invalid_token_error() -> Error:
    return ErrorLocalizable(TokenErrorCodes.INVALID_TOKEN, TokenErrorCodes.INVALID_TOKEN, 'Invalid token')


def build_unexpected_error(message: str) -> Error:
    return Error(TokenErrorCodes.UNEXPECTED_ERROR, message)

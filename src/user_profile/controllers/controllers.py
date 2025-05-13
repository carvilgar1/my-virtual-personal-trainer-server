from flask import Blueprint, jsonify, request

from src.common.application.error_builders import init_internal_server_error
from src.common.application.localizations import localize as _
from src.common.domain.response import Error, Response, Status
from src.common.domain.user_credentials import UserCredentials
from src.constants import (DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM,
                           UserProfileErrorCodes)
from src.settings import authentication_service, user_profile_repository
from src.token_auth.application.authentication import authorization_required
from src.user_profile.application.validations import (
    SaveUserProfileFormValidator, UpdateUserProfileFormValidator)
from src.user_profile.domain.user_credentials_repository import \
    UserProfileRepository
from src.user_profile.domain.user_profile import UserProfileResponse

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/', methods=['POST'], endpoint='save_user_profile')
@authorization_required(authentication_service)
def handele_save_user_profile_request(current_user: UserCredentials):
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        form = request.json

        response, status_code = save_user_profile(
            current_user,
            user_profile_repository,
            language,
            form
        )

        return jsonify(response.to_json()), status_code
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


def save_user_profile(
    current_user: UserCredentials,
    user_profile_repository: UserProfileRepository,
    language: str,
    form: dict,
) -> tuple[Response, int]:
    user_profile_validator = SaveUserProfileFormValidator(form, language)
    user_profile_validator.validate()
    if user_profile_validator.has_errors():
        response = Response(Status.ERROR, user_profile_validator.errors)
        return jsonify(response.to_json()), 400

    user_profile = user_profile_validator.user_profile
    user_profile_repository.save(
        current_user.user_id,
        user_profile
    )

    response, status_code = get_user_profile(
        current_user, user_profile_repository, language)
    if status_code == 200:
        status_code = 201
    return response, status_code


@user_blueprint.route('/', methods=['PUT'], endpoint='update_user_profile')
@authorization_required(authentication_service)
def handele_update_user_profile_request(current_user: UserCredentials):
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        form = request.json

        response, status_code = update_user_profile(
            current_user,
            user_profile_repository,
            language,
            form
        )

        return jsonify(response.to_json()), status_code
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


def update_user_profile(
    current_user: UserCredentials,
    user_profile_repository: UserProfileRepository,
    language: str,
    form: dict,
) -> tuple[Response, int]:
    user_profile_validator = UpdateUserProfileFormValidator(form, language)
    user_profile_validator.validate()
    if user_profile_validator.has_errors():
        response = Response(Status.ERROR, user_profile_validator.errors)
        return response, 400

    user_profile_repository.update(
        current_user.user_id,
        user_profile_validator.user_profile
    )

    return get_user_profile(current_user, user_profile_repository, language)


@user_blueprint.route('/', methods=['GET'], endpoint='retrieve_user_profile')
@authorization_required(authentication_service)
def handele_retrieve_user_profile_request(current_user: UserCredentials):
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

        response, status_code = get_user_profile(
            current_user,
            user_profile_repository,
            language
        )
        return jsonify(response.to_json()), status_code
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


def get_user_profile(
    current_user: UserCredentials,
    user_profile_repository: UserProfileRepository,
    language: str
) -> tuple[Response, int]:
    user_profile = user_profile_repository.find(current_user.user_id)

    if not user_profile:
        error = Error(UserProfileErrorCodes.USER_PROFILE_NOT_FOUND, _(
            UserProfileErrorCodes.USER_PROFILE_NOT_FOUND, language))
        response = Response(Status.ERROR, error=error)
        return response, 404

    if not user_profile.is_completed():
        error = Error(UserProfileErrorCodes.USER_PROFILE_NOT_COMPLETED, _(
            UserProfileErrorCodes.USER_PROFILE_NOT_COMPLETED, language))
        response = Response(Status.ERROR, error=error)
        return response, 404

    response = UserProfileResponse(
        Status.UPDATED, user_profile=user_profile)
    return response, 200


@user_blueprint.route('/', methods=['DELETE'], endpoint='delete_user_profile')
@authorization_required(authentication_service)
def handle_delete_user_profile_request(current_user: UserCredentials):
    try:
        user_profile_repository.delete(current_user.user_id)

        response = Response(Status.DELETED)
        return jsonify(response.to_json()), 200
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500

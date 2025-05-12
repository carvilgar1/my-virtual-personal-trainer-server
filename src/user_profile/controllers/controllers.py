
from flask import Blueprint, jsonify, request

from src.common.application.error_builders import init_internal_server_error
from src.common.application.localizations import localize as _
from src.common.domain import Error, Response, Status, UserCredentials
from src.constants import (DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM,
                           UserProfileErrorCodes)
from src.settings import authentication_service, user_profile_repository
from src.token_auth.application.authentication import authorization_required
from src.user_profile.application.validations import (
    UserProfileFormValidator, UserProfileUpdateFormValidator)

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/retrieve', methods=['GET'], endpoint='user_retrieve')
@authorization_required(authentication_service)
def handle_user_profile_retrieval_request(current_user: UserCredentials):
    try:
        lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

        user_profile = user_profile_repository.find(current_user.user_id)
        if not user_profile:
            error = Error(UserProfileErrorCodes.USER_PROFILE_NOT_FOUND, _(
                UserProfileErrorCodes.USER_PROFILE_NOT_FOUND, lang))
            response = Response(Status.ERROR, error)
            return jsonify(response.to_json()), 404

        if not user_profile._profile_completed:
            error = Error(UserProfileErrorCodes.USER_PROFILE_NOT_COMPLETED, _(
                UserProfileErrorCodes.USER_PROFILE_NOT_COMPLETED, lang))
            response = Response(Status.ERROR, error)
            return jsonify(response.to_json()), 400

        return jsonify(user_profile.to_json()), 200
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


@user_blueprint.route('/save', methods=['POST'], endpoint='user_save')
@authorization_required(authentication_service)
def handle_user_profile_save_request(current_user: UserCredentials):
    try:
        lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        validator = UserProfileFormValidator(request.json, lang)
        validator.validate()
        if validator.has_errors():
            response = Response(Status.ERROR, validator.errors)
            return jsonify(response.to_json()), 400

        user_profile_repository.save(
            current_user.user_id, validator.user_profile)

        return jsonify(validator.user_profile.to_json()), 200
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


@user_blueprint.route('/update', methods=['PUT'], endpoint='user_update')
@authorization_required(authentication_service)
def handle_user_profile_update_request(current_user: UserCredentials):
    try:
        lang = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

        validator = UserProfileUpdateFormValidator(request.json, lang)
        validator.validate()
        if validator.has_errors():
            response = Response(Status.ERROR, validator.errors)
            return jsonify(response.to_json()), 400

        user_profile_repository.update(
            current_user.user_id, validator.user_profile)
        user_profile = user_profile_repository.find(current_user.username)

        return jsonify(user_profile.to_json()), 200
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


def update_contr():
    pass

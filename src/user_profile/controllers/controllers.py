

from flask import Blueprint, jsonify, request

from src.common.application.localizations import localize as _
from src.common.domain.response import Response, Status
from src.common.domain.user_credentials import UserCredentials
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM
from src.settings import authentication_service, user_profile_repository
from src.token_auth.application.authentication import authorization_required
from src.user_profile.application.validations import \
    SaveUserProfileFormValidator, UpdateUserProfileFormValidator

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/save', methods=['POST'], endpoint='save_user_profile')
@authorization_required(authentication_service)
def handele_save_user_profile_request(current_user: UserCredentials):
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    form = request.json

    user_profile_validator = SaveUserProfileFormValidator(form, language)
    user_profile_validator.validate()
    if user_profile_validator.has_errors():
        response = Response(Status.ERROR, user_profile_validator.errors)
        return jsonify(response.to_json()), 400

    user_profile_repository.save(
        current_user.user_id,
        user_profile_validator.user_profile
    )

    return jsonify(user_profile_validator.user_profile), 200

@user_blueprint.route('/update', methods=['PUT'], endpoint='update_user_profile')
@authorization_required(authentication_service)
def handele_update_user_profile_request(current_user: UserCredentials):
    language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
    form = request.json

    user_profile_validator = UpdateUserProfileFormValidator(form, language)
    user_profile_validator.validate()
    if user_profile_validator.has_errors():
        response = Response(Status.ERROR, user_profile_validator.errors)
        return jsonify(response.to_json()), 400

    user_profile_repository.save(
        current_user.user_id,
        user_profile_validator.user_profile
    )

    return jsonify(user_profile_validator.user_profile), 200

from flask import Blueprint, jsonify, request

from src.common.application.error_builders import init_internal_server_error
from src.common.application.localizations import localize as _
from src.common.domain.response import Response, Status
from src.common.domain.user_credentials import UserCredentials
from src.constants import DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM
from src.settings import authentication_service, workouts_repository
from src.token_auth.application.authentication import authorization_required
from src.workouts_recommendation.application.workouts_recommendations_service import (
    predict_next_for_user, train_for_user)

workouts_recommendation_blueprint = Blueprint(
    'workouts_recommendation', __name__, url_prefix='/workouts-recommendation')


@workouts_recommendation_blueprint.route('/', methods=['POST'], endpoint='train_model')
@authorization_required(authentication_service)
def handle_train_model_request(current_user: UserCredentials):
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        all_workouts = workouts_repository.retrieve_all_workouts(
            user_id=current_user.user_id
        )

        response, status = train_for_user(
            user_id=current_user.user_id,
            workouts=all_workouts,
            language=language,
            epochs=200
        )

        return jsonify(response.to_json()), status
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


@workouts_recommendation_blueprint.route('/', methods=['GET'], endpoint='predict_next')
@authorization_required(authentication_service)
def handle_predict_request(current_user: UserCredentials):
    try:
        lookback = 4
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)

        recent_workouts = workouts_repository.retrieve_last_n_workouts(
            user_id=current_user.user_id,
            n=lookback
        )

        response, status = predict_next_for_user(
            user_id=current_user.user_id,
            recent_workouts=recent_workouts,
            language=language,
            lookback=lookback
        )

        return jsonify(response.to_json()), status
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500

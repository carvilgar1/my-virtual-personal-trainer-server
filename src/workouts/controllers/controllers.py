from flask import Blueprint, jsonify, request

from src.common.application.error_builders import init_internal_server_error
from src.common.application.localizations import localize as _
from src.common.application.validations import validate_date
from src.common.domain.response import Error, Response, Status
from src.common.domain.user_credentials import UserCredentials
from src.constants import (DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM,
                           CommonErrorCodes, WorkoutsErrorCodes)
from src.settings import authentication_service, workouts_repository
from src.token_auth.application.authentication import authorization_required
from src.workouts.application.validations import (parse_workout,
                                                  validate_workout)
from src.workouts.domain.workouts import Warning, Workout, WorkoutResponse
from src.workouts.domain.workouts_repository import WorkoutsRepository

workouts_blueprint = Blueprint('workouts', __name__, url_prefix='/workouts')


def build_workout_response_with_warnings(workouts: list[Workout], warnings: list[Warning]) -> WorkoutResponse:
    return WorkoutResponse(Status.WARNING, workouts=workouts, warnings=warnings)


def build_workout_response_success(workouts: list[Workout]) -> WorkoutResponse:
    return WorkoutResponse(Status.SUCCESS, workouts=workouts)


def build_workout_response_with_errors(errors: Error, warnings: list[Warning] | None = None) -> WorkoutResponse:
    return WorkoutResponse(Status.ERROR, warnings=warnings,  errors=errors)


def build_bad_request_response(lang: str, errors: list[Error]) -> Response:
    error = Error(CommonErrorCodes.BAD_REQUEST, _(
        CommonErrorCodes.BAD_REQUEST, lang), errors=errors)
    response = Response(Status.ERROR, error=error)
    return response


@workouts_blueprint.route('/', methods=['POST'], endpoint='save_workouts')
@authorization_required(authentication_service)
def handle_save_workouts_request(current_user: UserCredentials):
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        workouts = request.json

        response, status_code = save_user_workouts(
            current_user,
            workouts_repository,
            workouts,
            language
        )
        return jsonify(response.to_json()), status_code
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


@workouts_blueprint.route('/', methods=['GET'], endpoint='get_workouts')
@authorization_required(authentication_service)
def handle_get_workouts_request(current_user: UserCredentials):
    try:
        language = request.args.get(LANGUAGE_GET_PARAM, DEFAULT_LANGUAGE)
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 1000, type=int)

        if date_from and date_to:
            response, status_code = retrieve_workouts_by_dates(
                current_user, date_from, date_to, language
            )
            return jsonify(response.to_json()), status_code

        response, status_code = retrieve_workouts_by_pages(
            current_user, workouts_repository, page, page_size)

        return jsonify(response.to_json()), status_code
    except Exception as e:
        response = Response(Status.ERROR, init_internal_server_error(e))
        return jsonify(response.to_json()), 500


def save_user_workouts(
    current_user: UserCredentials,
    workouts_repository: WorkoutsRepository,
    workouts_json: list[dict],
    language: str
) -> tuple[Response, int]:
    if not workouts_json or not isinstance(workouts_json, list):
        response = build_bad_request_response(language, None)
        return response, 400

    wrong_workouts = []
    accepted_workouts = []
    process_workout_data(language, workouts_json,
                         wrong_workouts, accepted_workouts)

    if accepted_workouts:
        workouts_repository.save_many(
            current_user.user_id, accepted_workouts)

        if wrong_workouts:
            response = build_workout_response_with_warnings(
                accepted_workouts, wrong_workouts)
            return response, 207

        response = build_workout_response_success(accepted_workouts)
        return response, 200

    fatal_save_error = Error(WorkoutsErrorCodes.FATAL_SAVING_ERROR, _(
        WorkoutsErrorCodes.FATAL_SAVING_ERROR, language))
    response = build_workout_response_with_errors(
        fatal_save_error, wrong_workouts)

    return response, 400


def process_workout_data(language: str, workouts: list[dict], wrong_workouts: list[Warning], accepted_workouts: list[Workout]) -> None:
    for workout_json in workouts:
        workout, errors = parse_workout(workout_json, language)
        if errors:
            wrong_workouts.append(errors)
        else:
            warnings = validate_workout(workout, language)
            if warnings:
                wrong_workouts.append(warnings)
            else:
                accepted_workouts.append(workout)


def retrieve_workouts_by_pages(
    current_user: UserCredentials,
    workouts_repository: WorkoutsRepository,
    page: int,
    page_size: int
) -> tuple[Response, int]:
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 1000:
        page_size = 1000

    workouts = workouts_repository.retrieve_workouts(
        current_user.user_id,
        page,
        page_size
    )

    response = build_workout_response_success(workouts)
    return response, 200


def retrieve_workouts_by_dates(
    current_user: UserCredentials,
    workouts_repository: WorkoutsRepository,
    date_from: str,
    date_to: str,
    lang: str
) -> tuple[Response, int]:
    errors = []

    date_from, date_from_errors = validate_date(date_from, lang)
    if date_from_errors:
        date_from_errors.validation_field = 'dateFrom'
        errors.append(date_from_errors)

    date_to, date_to_errors = validate_date(date_to, lang)
    if date_to_errors:
        date_to_errors.validation_field = 'dateTo'
        errors.append(date_to_errors)

    if errors:
        response = build_bad_request_response(lang, errors)
        return response, 400

    date_diff = date_to - date_from
    if date_diff.days > 365:
        errors = create_date_exceeded_errors(lang)

        response = build_bad_request_response(lang, errors)
        return response, 400

    workouts = workouts_repository.retrieve_workouts_by_dates(
        current_user.user_id,
        date_from,
        date_to
    )

    response = build_workout_response_success(workouts)
    return response, 200


def create_date_exceeded_errors(lang):
    errors = []
    error = Error(WorkoutsErrorCodes.DATES_RANGE_EXCEEDED, _(
        WorkoutsErrorCodes.DATES_RANGE_EXCEEDED, lang), validation_field='dateFrom')
    errors.append(error)
    error = Error(WorkoutsErrorCodes.DATES_RANGE_EXCEEDED, _(
        WorkoutsErrorCodes.DATES_RANGE_EXCEEDED, lang), validation_field='dateTo')
    errors.append(error)
    return errors

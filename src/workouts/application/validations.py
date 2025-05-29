from datetime import datetime

from src.common.application.localizations import localize as _
from src.common.application.validations import (validate_datetime,
                                                validate_float,
                                                validate_integer,
                                                validate_mandatory_field)
from src.common.domain.response import Error
from src.constants import (MAX_HEART_RATE, UserProfileErrorCodes,
                           WorkoutsErrorCodes)
from src.workouts.domain.workouts import Warning, Workout, WorkoutKeys


def validate_workout(workout: Workout, language: str) -> Warning | None:
    errors = []

    if workout.duration < 1:
        error = Error(WorkoutsErrorCodes.INVALID_DURATION, _(
            WorkoutsErrorCodes.INVALID_DURATION, language))
        errors.append(error)

    if workout.average_heart_rate < 1 or workout.average_heart_rate > MAX_HEART_RATE:
        error = Error(UserProfileErrorCodes.INVALID_MAX_HEART_RATE, _(
            UserProfileErrorCodes.INVALID_MAX_HEART_RATE, language))
        errors.append(error)

    if errors:
        warning = Warning(
            WorkoutsErrorCodes.SAVING_ERROR,
            _(WorkoutsErrorCodes.SAVING_ERROR, language),
            workout.to_json(),
            errors
        )
        return warning

    return None


def parse_workout(workout_json: dict[str, str], language: str) -> tuple[Workout, Warning]:
    errors = []

    start_time = parse_workout_start_time(workout_json, language, errors)
    duration = parse_workout_duration(workout_json, language, errors)
    average_heart_rate = parse_workout_average_heart_rate(
        workout_json, language, errors)

    if errors:
        warning = Warning(
            WorkoutsErrorCodes.SAVING_ERROR,
            _(WorkoutsErrorCodes.SAVING_ERROR, language),
            workout_json,
            errors
        )
        return None, warning

    workout = Workout(
        start=start_time,
        duration=duration,
        average_heart_rate=average_heart_rate
    )
    return workout, None


def parse_workout_start_time(workout_json: dict, language: str, errors: list[Error]) -> datetime | None:
    start_time = workout_json.get(WorkoutKeys.START)
    _, error = validate_mandatory_field(
        start_time, WorkoutKeys.START, language)
    if error:
        errors.append(error)
        return None

    start_time_parsed, error = validate_datetime(start_time, language)
    if error:
        errors.append(error)
        return None

    return start_time_parsed


def parse_workout_duration(workout_json: dict, language: str, errors: list[Error]) -> int | None:
    duration = workout_json.get(WorkoutKeys.DURATION)
    _, error = validate_mandatory_field(
        duration, WorkoutKeys.DURATION, language)
    if error:
        errors.append(error)
        return None

    duration_parsed, error = validate_integer(duration, language)
    if error:
        errors.append(error)
        return None

    return duration_parsed


def parse_workout_average_heart_rate(workout_json: dict, language: str, errors: list[Error]) -> float | None:
    average_heart_rate = workout_json.get(WorkoutKeys.AVERAGE_HEART_RATE)
    _, error = validate_mandatory_field(
        average_heart_rate, WorkoutKeys.AVERAGE_HEART_RATE, language)
    if error:
        errors.append(error)
        return None

    average_heart_rate_parsed, error = validate_float(
        average_heart_rate, language)
    if error:
        errors.append(error)
        return None

    return average_heart_rate_parsed

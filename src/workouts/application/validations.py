from datetime import datetime

from src.common.application.localizations import localize as _
from src.common.application.validations import (validate_datetime,
                                                validate_integer,
                                                validate_mandatory_field)
from src.common.domain.response import Error
from src.constants import (MAX_HEART_RATE, CommonErrorCodes,
                           UserProfileErrorCodes, WorkoutsErrorCodes)
from src.workouts.domain.workouts import Mood, Warning, Workout, WorkoutKeys


def validate_workout(workout: Workout, language: str) -> Warning | None:
    errors = []
    if workout.duration < 1:
        error = Error(WorkoutsErrorCodes.INVALID_DURATION, _(
            WorkoutsErrorCodes.INVALID_DURATION, language))
        errors.append(error)

    if workout.intensity < 1 or workout.intensity > 5:
        error = Error(WorkoutsErrorCodes.INVALID_INTENSITY, _(
            WorkoutsErrorCodes.INVALID_INTENSITY, language))
        errors.append(error)

    if workout.sleep_score < 1 or workout.sleep_score > 100:
        error = Error(WorkoutsErrorCodes.INVALID_SLEEP_SCORE, _(
            WorkoutsErrorCodes.INVALID_SLEEP_SCORE, language))
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
    mood = parse_workout_mood(workout_json, language, errors)
    sleep_score = parse_workout_sleep_score(workout_json, language, errors)
    intensity = parse_workout_intensity(workout_json, language, errors)

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
        intensity=intensity,
        sleep_score=sleep_score,
        mood=mood,
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


def parse_workout_mood(workout_json: dict, language: str, errors: list[Error]) -> Mood:
    mood = workout_json.get(WorkoutKeys.MOOD)
    if mood:
        mood = mood.strip()
        try:
            return Mood[mood]
        except KeyError:
            message = _(CommonErrorCodes.INVALID_VALUE, language)
            if message:
                message = message.format(
                    expected_values=', '.join([m.name for m in Mood]))
            error = Error(CommonErrorCodes.INVALID_VALUE,
                          message, WorkoutKeys.MOOD)
            errors.append(error)
            return Mood.NEUTRAL  # Default to NEUTRAL if invalid mood
    return Mood.NEUTRAL  # Default to NEUTRAL if mood is not provided


def parse_workout_sleep_score(workout_json: dict, language: str, errors: list[Error]) -> int | None:
    sleep_score = workout_json.get(WorkoutKeys.SLEEP_SCORE)
    _, error = validate_mandatory_field(
        sleep_score, WorkoutKeys.DURATION, language)
    if error:
        errors.append(error)
        return None

    sleep_score_parsed, error = validate_integer(sleep_score, language)
    if error:
        errors.append(error)
        return None

    return sleep_score_parsed


def parse_workout_intensity(workout_json: dict, language: str, errors: list[Error]) -> int | None:
    intensity = workout_json.get(WorkoutKeys.INTENSITY)
    _, error = validate_mandatory_field(
        intensity, WorkoutKeys.INTENSITY, language)
    if error:
        errors.append(error)
        return None

    intensity_parsed, error = validate_integer(intensity, language)
    if error:
        errors.append(error)
        return None

    return intensity_parsed

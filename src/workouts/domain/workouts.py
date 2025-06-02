from datetime import datetime

from src.common.domain import Error, Response, Status
from src.constants import DATE_TIME_FORMAT


class WorkoutKeys:
    START = "startTime"
    DURATION = "duration"
    AVERAGE_HEART_RATE = "averageHeartRate"


class Workout:
    def __init__(self, start: datetime, duration: int, average_heart_rate: float):
        self.start = start
        self.duration = duration
        self.average_heart_rate = average_heart_rate

    def to_json(self):
        return {
            WorkoutKeys.START: self.start.strftime(DATE_TIME_FORMAT),
            WorkoutKeys.DURATION: self.duration,
            WorkoutKeys.AVERAGE_HEART_RATE: self.average_heart_rate
        }


class Warning(Error):
    def __init__(self, code: str, message: str, workout: dict[str, str], errors: list[Error] | None = None):
        super().__init__(code, message, errors=errors)
        self.workout = workout

    def to_json(self):
        warning_json = super().to_json()
        warning_json['workout'] = self.workout
        return warning_json


class WorkoutResponse(Response):
    def __init__(self, status: Status, workouts: list[Workout] | None = None, warnings: list[Warning] | None = None, errors: Error | None = None):
        super().__init__(status, errors)
        self.workouts = workouts
        self.warnings = warnings

    def to_json(self):
        response_json = super().to_json()
        if self.warnings:
            response_json['warnings'] = [warning.to_json()
                                         for warning in self.warnings]
        if self.workouts:
            response_json['workouts'] = [workout.to_json()
                                         for workout in self.workouts]
        return response_json

from datetime import datetime
from enum import Enum

from src.common.domain import Error, Response, Status
from src.constants import DATE_TIME_FORMAT


class Mood(Enum):
    PROUD = 0                  # Euphoric, accomplished
    FRUSTRATED = 1             # Disappointed, annoyed
    CALM = 2                   # Serene, focused
    STRESSED = 3               # Anxious, pressured
    MOTIVATED = 4               # Happy, motivated, upbeat
    DEMOTIVATED = 5             # Apathetic, unmotivated
    VIGOROUS = 6               # Energetic, powerful
    DRAINED = 7                # Tired, fatigued
    NEUTRAL = 8                # No strong emotion
    INJURED = 9               # Physical discomfort


class WorkoutKeys:
    START = "startTime"
    DURATION = "duration"
    INTENSITY = "intensity"
    MOOD = "mood"
    SLEEP_SCORE = "sleepScore"


class Workout:
    def __init__(self, start: datetime, duration: int, intensity: int, sleep_score: int, mood: Mood):
        self.start = start
        self.duration = duration
        self.intensity = intensity
        self.sleep_score = sleep_score
        self.mood = mood

    def get_day_of_week(self) -> str:
        return self.start.strftime("%A").lower()

    def get_time_of_day(self) -> str:
        if self.start.hour < 12:
            return "early_morning"
        elif self.start.hour < 18:
            return "afternoon"
        else:
            return "evening"

    def to_json(self):
        return {
            WorkoutKeys.START: self.start.strftime(DATE_TIME_FORMAT),
            WorkoutKeys.DURATION: self.duration,
            WorkoutKeys.INTENSITY: self.intensity,
            WorkoutKeys.SLEEP_SCORE: self.sleep_score,
            WorkoutKeys.MOOD: self.mood.name}


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

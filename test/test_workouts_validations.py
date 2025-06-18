from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.workouts.application.validations import (
    parse_workout, validate_workout)
from src.workouts.domain.workouts import Workout, Mood

DUMMY_LANGUAGE = "en"
DUMMY_WORKOUT_JSON = {
    "startTime": "2025-07-09T14:48:00.000000+0000",
    "duration": 20,
    "intensity": 3,
    "mood": "NEUTRAL",
    "sleepScore": 80
}


class TestValidateWorkout(unittest.TestCase):
    
    def test_valid_workout(self):
        workout = Workout(
            start="2025-07-09T14:48:00.000000+0000",
            duration=20,
            intensity=3,
            mood=Mood.NEUTRAL,
            sleep_score=80
        )
        self.assertIsNone(validate_workout(workout, DUMMY_LANGUAGE))

    
    def test_invalid_duration(self):
        workout = Workout(
            start=datetime.strptime("2025-07-09T14:48:00.000000+0000", "%Y-%m-%dT%H:%M:%S.%f%z"),
            duration=0,
            intensity=3,
            mood=Mood.NEUTRAL,
            sleep_score=80
        )
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        self.assertTrue(
            any(error.code == "INVALID_DURATION" for error in result.errors))

    
    def test_invalid_intensity(self):
        workout = Workout(
            start=datetime.strptime("2025-07-09T14:48:00.000000+0000", "%Y-%m-%dT%H:%M:%S.%f%z"),
            duration=20,
            intensity=6,  # Invalid intensity
            mood=Mood.NEUTRAL,
            sleep_score=80
        )
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        self.assertTrue(
            any(error.code == "INVALID_INTENSITY" for error in result.errors))

    
    def test_invalid_sleep_score(self):
        workout = Workout(
            start=datetime.strptime("2025-07-09T14:48:00.000000+0000", "%Y-%m-%dT%H:%M:%S.%f%z"),
            duration=20,
            intensity=3,
            mood=Mood.NEUTRAL,
            sleep_score=101  # Invalid sleep score
        )
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        self.assertTrue(
            any(error.code == "INVALID_SLEEP_SCORE" for error in result.errors))

    
    def test_multiple_errors(self):
        workout = Workout(
            start=datetime.strptime("2025-07-09T14:48:00.000000+0000", "%Y-%m-%dT%H:%M:%S.%f%z"),
            duration=0,
            intensity=6,  # Invalid intensity
            mood=Mood.NEUTRAL,
            sleep_score=101  # Invalid sleep score
        )
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        codes = [error.code for error in result.errors]
        self.assertIn("INVALID_DURATION", codes)
        self.assertIn("INVALID_INTENSITY", codes)
        self.assertIn("INVALID_SLEEP_SCORE", codes)


class TestParseWorkout(unittest.TestCase):
    
    def test_parse_workout_valid(self):
        workout_json = DUMMY_WORKOUT_JSON
        workout, warning = parse_workout(workout_json, DUMMY_LANGUAGE)
        self.assertIsNotNone(workout)
        self.assertIsNone(warning)
        self.assertEqual(workout.duration, 20)
        self.assertEqual(workout.intensity, 3)
        self.assertEqual(workout.mood, Mood.NEUTRAL)
        self.assertEqual(workout.sleep_score, 80)

    def test_parse_workout_missing_fields(self):
        workout_json = {}
        workout, warning = parse_workout(workout_json, DUMMY_LANGUAGE)
        self.assertIsNone(workout)
        self.assertIsNotNone(warning)
        self.assertGreater(len(warning.errors), 0)

    def test_parse_workout_invalid_types(self):
        workout_json = {
            "startTime": "bad-date",
            "duration": "bad-int",
            "intensity": "bad-intensity",
            "mood": "INVALID_MOOD",
            "sleepScore": "bad-sleep-score"
        }
        workout, warning = parse_workout(workout_json, DUMMY_LANGUAGE)
        self.assertIsNone(workout)
        self.assertIsNotNone(warning)
        codes = [error.code for error in warning.errors]
        self.assertIn("INVALID_DATETIME", codes)
        self.assertIn("INVALID_INTEGER", codes)
        self.assertIn("INVALID_VALUE", codes)
        self.assertIn("INVALID_INTEGER", codes)


if __name__ == "__main__":
    unittest.main()

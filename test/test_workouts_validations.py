import unittest
from unittest.mock import Mock, patch

from src.workouts.application.validations import (
    parse_workout, parse_workout_average_heart_rate, parse_workout_duration,
    parse_workout_start_time, validate_workout)

DUMMY_LANGUAGE = "en"
DUMMY_WORKOUT_JSON = {"dummy": "data"}
MAX_HEART_RATE = 220


class TestValidateWorkout(unittest.TestCase):
    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.MAX_HEART_RATE", MAX_HEART_RATE)
    def test_valid_workout(self, mock_localize):
        workout = Mock()
        workout.duration = 30
        workout.average_heart_rate = 120
        workout.to_json.return_value = DUMMY_WORKOUT_JSON
        self.assertIsNone(validate_workout(workout, DUMMY_LANGUAGE))

    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.MAX_HEART_RATE", MAX_HEART_RATE)
    def test_invalid_duration(self, mock_localize):
        workout = Mock()
        workout.duration = 0
        workout.average_heart_rate = 120
        workout.to_json.return_value = DUMMY_WORKOUT_JSON
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        self.assertTrue(
            any(error.code == "INVALID_DURATION" for error in result.errors))

    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.MAX_HEART_RATE", MAX_HEART_RATE)
    def test_invalid_heart_rate_low(self, mock_localize):
        workout = Mock()
        workout.duration = 30
        workout.average_heart_rate = 0
        workout.to_json.return_value = DUMMY_WORKOUT_JSON
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        self.assertTrue(
            any(error.code == "INVALID_HEART_RATE" for error in result.errors))

    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.MAX_HEART_RATE", MAX_HEART_RATE)
    def test_invalid_heart_rate_high(self, mock_localize):
        workout = Mock()
        workout.duration = 30
        workout.average_heart_rate = MAX_HEART_RATE + 1
        workout.to_json.return_value = DUMMY_WORKOUT_JSON
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        self.assertTrue(
            any(error.code == "INVALID_HEART_RATE" for error in result.errors))

    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.MAX_HEART_RATE", MAX_HEART_RATE)
    def test_multiple_errors(self, mock_localize):
        workout = Mock()
        workout.duration = 0
        workout.average_heart_rate = 0
        workout.to_json.return_value = DUMMY_WORKOUT_JSON
        result = validate_workout(workout, DUMMY_LANGUAGE)
        self.assertIsNotNone(result)
        codes = [error.code for error in result.errors]
        self.assertIn("INVALID_DURATION", codes)
        self.assertIn("INVALID_HEART_RATE", codes)


class TestParseWorkout(unittest.TestCase):
    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.validate_mandatory_field", return_value=(None, None))
    @patch("src.workouts.application.validations.validate_datetime", return_value=("2024-01-01T10:00:00", None))
    @patch("src.workouts.application.validations.validate_integer", return_value=(30, None))
    @patch("src.workouts.application.validations.validate_float", return_value=(120.0, None))
    def test_parse_workout_valid(self, mock_float, mock_int, mock_datetime, mock_mandatory, mock_localize):
        workout_json = {
            "start": "2024-01-01T10:00:00",
            "duration": "30",
            "average_heart_rate": "120"
        }
        workout, warning = parse_workout(workout_json, DUMMY_LANGUAGE)
        self.assertIsNotNone(workout)
        self.assertIsNone(warning)
        self.assertEqual(workout.duration, 30)
        self.assertEqual(workout.average_heart_rate, 120.0)

    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.validate_mandatory_field", return_value=(None, Mock(code="MANDATORY_FIELD_MISSING")))
    def test_parse_workout_missing_fields(self, mock_mandatory, mock_localize):
        workout_json = {}
        workout, warning = parse_workout(workout_json, DUMMY_LANGUAGE)
        self.assertIsNone(workout)
        self.assertIsNotNone(warning)
        self.assertTrue(len(warning.errors) > 0)

    @patch("src.workouts.application.validations._", side_effect=lambda key, lang: f"localized-{key}")
    @patch("src.workouts.application.validations.validate_mandatory_field", return_value=(None, None))
    @patch("src.workouts.application.validations.validate_datetime", return_value=(None, Mock(code="INVALID_DATETIME")))
    @patch("src.workouts.application.validations.validate_integer", return_value=(None, Mock(code="INVALID_INTEGER")))
    @patch("src.workouts.application.validations.validate_float", return_value=(None, Mock(code="INVALID_FLOAT")))
    def test_parse_workout_invalid_types(self, mock_float, mock_int, mock_datetime, mock_mandatory, mock_localize):
        workout_json = {
            "start": "bad-date",
            "duration": "bad-int",
            "average_heart_rate": "bad-float"
        }
        workout, warning = parse_workout(workout_json, DUMMY_LANGUAGE)
        self.assertIsNone(workout)
        self.assertIsNotNone(warning)
        codes = [error.code for error in warning.errors]
        self.assertIn("INVALID_DATETIME", codes)
        self.assertIn("INVALID_INTEGER", codes)
        self.assertIn("INVALID_FLOAT", codes)


if __name__ == "__main__":
    unittest.main()

import math
import unittest
from datetime import datetime
from unittest.mock import patch

from src.common.application.error_builders import init_internal_server_error
from src.common.application.validations import (BaseFormValidator,
                                                validate_content_length,
                                                validate_date,
                                                validate_datetime,
                                                validate_email_format,
                                                validate_float,
                                                validate_integer,
                                                validate_mandatory_field)
from src.common.domain import Error
from src.constants import (DATE_FORMAT, DATE_TIME_FORMAT,
                           DEFAULT_MAX_VARCHAR_LENGTH, CommonErrorCodes)


class TestValidations(unittest.TestCase):
    def test_validate_mandatory_field_success(self):
        field_value = "test"
        field_key = "field_key"
        language = "en"
        result, error = validate_mandatory_field(
            field_value, field_key, language)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_validate_mandatory_field_failure(self):
        field_value = "   "
        field_key = "field_key"
        language = "en"
        expected_message = f"The field '{field_key}' is mandatory."
        result, error = validate_mandatory_field(
            field_value, field_key, language)
        self.assertFalse(result)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.MISSING_MANDATORY_FIELD)

    def test_validate_content_length_success(self):
        field_value = "short text"
        language = "en"
        result, error = validate_content_length(field_value, language)
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_validate_content_length_failure(self):
        field_value = "x" * (DEFAULT_MAX_VARCHAR_LENGTH + 1)
        language = "en"
        result, error = validate_content_length(field_value, language)
        self.assertFalse(result)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.FIELD_TOO_LARGE)

    def test_validate_email_format(self):
        self.assertTrue(validate_email_format("test@example.com"))
        self.assertFalse(validate_email_format("invalid-email"))

    def test_validate_integer(self):
        number, error = validate_integer("123", "en")
        self.assertEqual(number, 123)
        self.assertIsNone(error)

        number, error = validate_integer("abc", "en")
        self.assertIsNone(number)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_INTEGER)

    def test_validate_float(self):
        decimal, error = validate_float("123.45", "en")
        self.assertEqual(decimal, 123.45)
        self.assertIsNone(error)

        decimal, error = validate_float("abc", "en")
        self.assertIsNone(decimal)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_FLOAT)

    def test_validate_date(self):
        date_str = "2023-01-01"
        date, error = validate_date(date_str, "en")
        self.assertEqual(date, datetime.strptime(date_str, DATE_FORMAT))
        self.assertIsNone(error)

        date, error = validate_date("invalid-date", "en")
        self.assertIsNone(date)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATE)

    def test_validate_datetime(self):
        datetime_str = "2023-01-01T12:00:00.000000+00:00"
        dt, error = validate_datetime(datetime_str, "en")
        self.assertEqual(dt, datetime.strptime(datetime_str, DATE_TIME_FORMAT))
        self.assertIsNone(error)

        dt, error = validate_datetime("invalid-datetime", "en")
        self.assertIsNone(dt)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATETIME)

    def test_build_unexpected_server_error(self):
        exception = Exception("Unexpected error")
        error = init_internal_server_error(exception)
        self.assertEqual(error.code, CommonErrorCodes.INTERNAL_SERVER_ERROR)
        self.assertEqual(error.message, str(exception))

    def test_validate_email_format_edge_cases(self):
        self.assertFalse(validate_email_format(" test@example.com "))
        self.assertFalse(validate_email_format(""))
        with self.assertRaises(TypeError):
            validate_email_format(None)

    def test_validate_integer_edge_cases(self):
        number, error = validate_integer("", "en")
        self.assertIsNone(number)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_INTEGER)

        number, error = validate_integer("123.0", "en")
        self.assertIsNone(number)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_INTEGER)

        number, error = validate_integer(True, "en")
        self.assertEqual(number, 1)
        self.assertIsNone(error)

        with self.assertRaises(TypeError):
            validate_integer(None, "en")

    def test_validate_float_edge_cases(self):
        decimal, error = validate_float("", "en")
        self.assertIsNone(decimal)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_FLOAT)
        decimal, error = validate_float("NaN", "en")
        self.assertTrue(math.isnan(decimal))
        self.assertIsNone(error)

        decimal, error = validate_float(True, "en")
        self.assertEqual(decimal, 1.0)
        self.assertIsNone(error)

        with self.assertRaises(TypeError):
            validate_float(None, "en")

    def test_validate_date_edge_cases(self):
        date, error = validate_date("2023-02-29", "en")
        self.assertIsNone(date)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATE)

        date, error = validate_date("", "en")
        self.assertIsNone(date)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATE)

        with self.assertRaises(TypeError):
            validate_date(None, "en")

    def test_validate_datetime_edge_cases(self):
        dt, error = validate_datetime("2023-01-01 12:00:00", "en")
        self.assertIsNone(dt)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATETIME)

        dt, error = validate_datetime("", "en")
        self.assertIsNone(dt)
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATETIME)

        with self.assertRaises(TypeError):
            validate_datetime(None, "en")


class TestBaseFormValidator(unittest.TestCase):
    def test_base_form_validator_initial_state(self):
        validator = BaseFormValidator(language="en")
        self.assertFalse(validator.has_errors())
        self.assertIsNone(validator.errors)


if __name__ == "__main__":
    unittest.main()

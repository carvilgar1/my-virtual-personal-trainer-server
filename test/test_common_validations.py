import unittest
from datetime import datetime

from src.common.application.validations import (FieldValidator, validate_date,
                                                validate_datetime,
                                                validate_float,
                                                validate_integer,
                                                validate_mandatory_field)
from src.common.domain.response import Error
from src.constants import CommonErrorCodes


class TestFieldValidator(unittest.TestCase):
    def test_errors_initially_empty(self):
        validator = FieldValidator(field_value="test")
        self.assertEqual(validator.errors, [])

    def test_errors_with_initial_errors(self):
        initial_errors = [Error(code="code1", message="message1")]
        validator = FieldValidator(field_value="test", errors=initial_errors)
        self.assertEqual(validator.errors, initial_errors)

    def test_add_error(self):
        validator = FieldValidator(field_value="test")
        error = Error(code="code2", message="message2")
        validator.add_error(error)
        self.assertIn(error, validator.errors)

    def test_contains_error_initially_false(self):
        validator = FieldValidator(field_value="test")
        self.assertFalse(validator.contains_error)

    def test_contains_error_after_adding_error(self):
        validator = FieldValidator(field_value="test")
        error = Error(code="code2", message="message2")
        validator.add_error(error)
        self.assertTrue(validator.contains_error)


class TestValidations(unittest.TestCase):
    def test_validate_mandatory_field_success(self):
        result, error = validate_mandatory_field("test_field", "value")
        self.assertTrue(result)
        self.assertIsNone(error)

    def test_validate_mandatory_field_failure(self):
        result, error = validate_mandatory_field("test_field", "")
        self.assertFalse(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.code, CommonErrorCodes.MANDATORY_FIELD)

    def test_validate_integer_success(self):
        result, error = validate_integer("123")
        self.assertEqual(result, 123)
        self.assertIsNone(error)

    def test_validate_integer_failure(self):
        result, error = validate_integer("abc")
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_INTEGER)

    def test_validate_float_success(self):
        result, error = validate_float("123.45")
        self.assertEqual(result, 123.45)
        self.assertIsNone(error)

    def test_validate_float_failure(self):
        result, error = validate_float("abc")
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_FLOAT)

    def test_validate_date_success(self):
        result, error = validate_date("2023-10-01")
        self.assertIsInstance(result, datetime)
        self.assertIsNone(error)

    def test_validate_date_failure(self):
        result, error = validate_date("01-10-2023")
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATE)

    def test_validate_datetime_success(self):
        result, error = validate_datetime("2023-10-01T12:00:00.0000+03:00")
        self.assertIsInstance(result, datetime)
        self.assertIsNone(error)

    def test_validate_datetime_failure(self):
        result, error = validate_datetime("01-10-2023 12:00:00")
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(error.code, CommonErrorCodes.INVALID_DATETIME)


if __name__ == '__main__':
    unittest.main()

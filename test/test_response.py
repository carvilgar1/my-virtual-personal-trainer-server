import unittest

from src.common.domain.response import (Error, Response, Status,
                                        init_internal_server_error)
from src.constants import CommonErrorCodes


class TestResponseDomain(unittest.TestCase):

    def test_status_enum(self):
        self.assertEqual(Status.SUCCESS.value, 'Success')
        self.assertEqual(Status.ERROR.value, 'Error')

    def test_init_internal_server_error(self):
        exception = Exception("test error")
        err = init_internal_server_error(exception)
        self.assertEqual(err.code, CommonErrorCodes.INTERNAL_SERVER_ERROR)
        self.assertEqual(err.message, "test error")

    def test_error_raises_if_code_empty(self):
        with self.assertRaises(ValueError) as context:
            Error("", "some error")
        self.assertEqual(str(context.exception), "Error code must be set")

    def test_error_to_json_minimal(self):
        error = Error("code1", "error occurred")
        json_data = error.to_json()
        self.assertEqual(json_data["code"], "code1")
        self.assertEqual(json_data["message"], "error occurred")
        self.assertNotIn("validationField", json_data)
        self.assertNotIn("errors", json_data)

    def test_error_to_json_with_validation_field(self):
        error = Error("code2", "error occurred", validation_field="field1")
        json_data = error.to_json()
        self.assertEqual(json_data["validationField"], "field1")

    def test_error_add_error_and_nested_to_json(self):
        parent_error = Error("parentCode", "parent error")
        child_error = Error("childCode", "child error")
        parent_error.add_error(child_error)
        json_data = parent_error.to_json()
        self.assertIn("errors", json_data)
        self.assertEqual(len(json_data["errors"]), 1)
        self.assertEqual(json_data["errors"][0]["code"], "childCode")
        self.assertEqual(json_data["errors"][0]["message"], "child error")

    def test_response_to_json_without_error(self):
        response = Response(Status.SUCCESS)
        json_data = response.to_json()
        self.assertEqual(json_data["status"], Status.SUCCESS.value)
        self.assertNotIn("error", json_data)

    def test_response_set_error_status_and_to_json(self):
        error = Error("code4", "an error", validation_field="field2")
        response = Response(Status.SUCCESS)
        response.set_error_status(error)
        self.assertEqual(response.status, Status.ERROR)
        json_data = response.to_json()
        self.assertEqual(json_data["status"], Status.ERROR.value)
        self.assertIn("error", json_data)
        error_json = json_data["error"]
        self.assertEqual(error_json["code"], "code4")
        self.assertEqual(error_json["message"], "an error")
        self.assertEqual(error_json["validationField"], "field2")


if __name__ == "__main__":
    unittest.main()

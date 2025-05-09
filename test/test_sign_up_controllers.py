import json
import unittest
from unittest.mock import MagicMock

from flask import Flask

from src.common.domain import Response, Status, UserCredentials
from src.constants import (DEFAULT_LANGUAGE, LANGUAGE_GET_PARAM,
                           PASSWORD_MIN_LENGTH)
from src.sign_up.controllers.controllers import (handle_sign_up_request,
                                                 sign_up, sign_up_blueprint)


class TestSignUpControllers(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(sign_up_blueprint)
        self.client = self.app.test_client()
        self.mock_repo = MagicMock()
        self.mock_repo.find_by_username.return_value = None
        self.mock_repo.find_by_email.return_value = None
        self.mock_repo.save = MagicMock()

    def test_sign_up_success(self):
        pwd = "Valid1!"
        if len(pwd) < PASSWORD_MIN_LENGTH:
            pwd += "a" * (PASSWORD_MIN_LENGTH - len(pwd))
        user = UserCredentials("1", "test@example.com", "validuser", pwd)
        response, status = sign_up(self.mock_repo, user, DEFAULT_LANGUAGE)
        self.assertEqual(status, 201)
        self.assertEqual(response.status, Status.SUCCESS)
        self.assertNotEqual(user.password, pwd)
        self.mock_repo.save.assert_called_once_with(user)

    def test_sign_up_form_validation_error(self):
        user = UserCredentials("1", "   ", "validuser", "Valid1!")
        response, status = sign_up(self.mock_repo, user, DEFAULT_LANGUAGE)
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)
        self.mock_repo.save.assert_not_called()

    def test_sign_up_unique_error(self):
        pwd = "Valid1!"
        if len(pwd) < PASSWORD_MIN_LENGTH:
            pwd += "a" * (PASSWORD_MIN_LENGTH - len(pwd))
        user = UserCredentials("1", "test@example.com", "existinguser", pwd)
        existing_user = UserCredentials(
            "2", "other@example.com", "existinguser", "Pass1!")
        self.mock_repo.find_by_username.return_value = existing_user
        response, status = sign_up(self.mock_repo, user, DEFAULT_LANGUAGE)
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)
        self.mock_repo.save.assert_not_called()

    def test_handle_sign_up_request_success(self):
        from src.sign_up.controllers import controllers
        controllers.user_credentials_repository = self.mock_repo

        data = {
            "email": "test@example.com",
            "username": "validuser",
            "password": "Valid1!aaaaa"
        }
        with self.app.test_request_context(
            f'/sign-up/?{LANGUAGE_GET_PARAM}={DEFAULT_LANGUAGE}',
            method='POST',
            data=data,
            content_type='application/x-www-form-urlencoded'
        ):
            resp, status = handle_sign_up_request()
            resp_data = json.loads(resp.get_data(as_text=True))
            self.assertEqual(status, 201)
            self.assertEqual(resp_data.get("status"), Status.SUCCESS.value)
            self.mock_repo.save.assert_called_once()

    def test_handle_sign_up_request_exception(self):
        from src.sign_up.controllers import controllers
        original_get_user = controllers._get_user_credentials
        try:
            controllers._get_user_credentials = MagicMock(
                side_effect=Exception("test error"))
            with self.app.test_request_context(
                '/sign-up/', method='POST', content_type='application/x-www-form-urlencoded'
            ):
                resp, status = handle_sign_up_request()
                resp_data = json.loads(resp.get_data(as_text=True))
                self.assertEqual(status, 500)
                self.assertEqual(resp_data.get("status"), Status.ERROR.value)
        finally:
            controllers._get_user_credentials = original_get_user


if __name__ == "__main__":
    unittest.main()

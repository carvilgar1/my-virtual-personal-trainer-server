import unittest
from unittest.mock import MagicMock
from flask import Flask
from src.sign_up.controllers.controllers import sign_up_blueprint
from src.constants import DEFAULT_LANGUAGE

class TestSignUpIntegration(unittest.TestCase):

    def setUp(self):
        """Set up the Flask app and test client"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['LOCALIZER'] = MagicMock()
        self.app.config['APP_REPOSITORIES'] = {
            'USER_CREDENTIALS_REPOSITORY': MagicMock()
        }
        self.app.register_blueprint(sign_up_blueprint)
        self.client = self.app.test_client()

    def test_successful_signup_request(self):
        """Test successful signup request"""
        mock_repo = self.app.config['APP_REPOSITORIES']['USER_CREDENTIALS_REPOSITORY']
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = None

        response = self.client.post('/sign-up/', data={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Securepassword123#"
        })

        self.assertEqual(response.status_code, 201)
        self.assertIn("Success", str(response.json))

    def test_signup_with_existing_email(self):
        """Test signup request with an already registered email"""
        mock_repo = self.app.config['APP_REPOSITORIES']['USER_CREDENTIALS_REPOSITORY']
        mock_repo.find_by_email.return_value = MagicMock()  # Simulate existing user

        response = self.client.post('/sign-up/', json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Securepassword123#"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_signup_with_existing_username(self):
        """Test signup request with an already registered username"""
        mock_repo = self.app.config['APP_REPOSITORIES']['USER_CREDENTIALS_REPOSITORY']
        mock_repo.find_by_username.return_value = object()  # Simulate existing user

        response = self.client.post('/sign-up/', data={
            "email": "newemail@example.com",
            "username": "testuser",
            "password": "Securepassword123#"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_signup_missing_fields(self):
        """Test signup request with missing required fields"""
        response = self.client.post('/sign-up/', data={
            "email": "test@example.com",
            "password": "securepassword"
            # Missing username
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_internal_server_error_handling(self):
        """Test that the signup endpoint handles unexpected errors gracefully"""
        mock_repo = self.app.config['APP_REPOSITORIES']['USER_CREDENTIALS_REPOSITORY']
        mock_repo.find_by_username.return_value = None
        mock_repo.find_by_email.return_value = None
        mock_repo.save.side_effect = Exception("Unexpected database error")

        response = self.client.post('/sign-up/', data={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Securepassword1233#"
        })

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

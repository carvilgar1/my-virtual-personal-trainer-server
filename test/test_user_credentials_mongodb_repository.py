import unittest
from unittest.mock import MagicMock, patch

from pymongo.collection import Collection

from src.user_credentials.domain.user_credentials import UserCredentials
from src.user_credentials.infrastructure.user_credentials_mongodb_repository import \
    UserCredentialsMongoDBRepository


class TestUserCredentialsMongoDBRepository(unittest.TestCase):

    @patch('src.user_credentials.infrastructure.user_credentials_mongodb_repository.MongoClient')
    def setUp(self, mock_mongo_client):
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock(spec=Collection)
        self.mock_db.__getitem__.return_value = self.mock_collection
        mock_mongo_client.return_value.__getitem__.return_value = self.mock_db

        self.settings = {
            'uri': 'mongodb://localhost:27017',
            'database': 'test_db'
        }
        self.repository = UserCredentialsMongoDBRepository(self.settings)

    def test_save(self):
        user_credentials = UserCredentials(
            email='test@example.com', username='testuser', password='password123')
        self.repository.save(user_credentials)
        self.mock_collection.insert_one.assert_called_once_with({
            'credentials': {
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'password123'
            }
        })

    def test_find_by_username(self):
        self.mock_collection.find_one.return_value = {
            'credentials': {
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'password123'
            }
        }
        result = self.repository.find_by_username('testuser')
        self.mock_collection.find_one.assert_called_once_with(
            {'credentials.username': 'testuser'})
        self.assertEqual(result['credentials']['username'], 'testuser')

    def test_find_by_email(self):
        self.mock_collection.find_one.return_value = {
            'credentials': {
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'password123'
            }
        }
        result = self.repository.find_by_email('test@example.com')
        self.mock_collection.find_one.assert_called_once_with(
            {'credentials.email': 'test@example.com'})
        self.assertEqual(result['credentials']['email'], 'test@example.com')

    def test_find_by_username_or_email(self):
        self.mock_collection.find_one.return_value = {
            'credentials': {
                'email': 'test@example.com',
                'username': 'testuser',
                'password': 'password123'
            }
        }
        result = self.repository.find_by_username_or_email(
            'testuser', 'test@example.com')
        self.mock_collection.find_one.assert_called_once_with({
            '$or': [{'credentials.username': 'testuser'}, {'credentials.email': 'test@example.com'}]
        })
        self.assertEqual(result['credentials']['username'], 'testuser')
        self.assertEqual(result['credentials']['email'], 'test@example.com')


if __name__ == '__main__':
    unittest.main()

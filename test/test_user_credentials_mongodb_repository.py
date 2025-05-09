import unittest

import mongomock

from src.common.domain.user_credentials import UserCredentials
from src.common.infrastructure.user_credentials_mongodb_repository import \
    UserCredentialsMongoDBRepository


class TestUserCredentialsMongoDBRepository(unittest.TestCase):
    def setUp(self):
        # Patch the MongoClient in the module to use mongomock
        from src.common.infrastructure import \
            user_credentials_mongodb_repository
        user_credentials_mongodb_repository.MongoClient = mongomock.MongoClient

        self.settings = {
            'uri': 'mongodb://localhost:27017/test_db',
            'database': 'test_db'
        }
        self.repository = UserCredentialsMongoDBRepository(self.settings)
        # Clear the collection to ensure a clean test state.
        self.repository.collection.delete_many({})

    def test_save_and_find_by_username(self):
        user = UserCredentials("1", "test@example.com", "testuser", "password")
        self.repository.save(user)
        found = self.repository.find_by_username("testuser")
        self.assertIsNotNone(found)
        self.assertEqual(found.email, "test@example.com")
        self.assertEqual(found.username, "testuser")
        self.assertEqual(found.password, "password")

    def test_find_by_username_not_found(self):
        found = self.repository.find_by_username("nonexistent")
        self.assertIsNone(found)

    def test_save_and_find_by_email(self):
        user = UserCredentials("1", "email@example.com", "anotheruser", "pass")
        self.repository.save(user)
        found = self.repository.find_by_email("email@example.com")
        self.assertIsNotNone(found)
        self.assertEqual(found.email, "email@example.com")
        self.assertEqual(found.username, "anotheruser")
        self.assertEqual(found.password, "pass")

    def test_find_by_email_not_found(self):
        found = self.repository.find_by_email("notfound@example.com")
        self.assertIsNone(found)

    def test_find_by_username_or_email_by_username(self):
        user = UserCredentials("1", "email@example.com",
                               "uniqueuser", "secret")
        self.repository.save(user)
        found = self.repository.find_by_username_or_email(
            "uniqueuser", "nonexistent@example.com")
        self.assertIsNotNone(found)
        self.assertEqual(found.username, "uniqueuser")
        self.assertEqual(found.email, "email@example.com")

    def test_find_by_username_or_email_by_email(self):
        user = UserCredentials("1", "email@example.com", "user123", "secret")
        self.repository.save(user)
        found = self.repository.find_by_username_or_email(
            "nonexistent", "email@example.com")
        self.assertIsNotNone(found)
        self.assertEqual(found.email, "email@example.com")
        self.assertEqual(found.username, "user123")

    def test_find_by_username_or_email_not_found(self):
        found = self.repository.find_by_username_or_email(
            "nonexistent", "notfound@example.com")
        self.assertIsNone(found)


if __name__ == "__main__":
    unittest.main()

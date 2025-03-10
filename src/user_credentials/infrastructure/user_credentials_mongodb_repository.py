from typing import Optional

from pymongo import MongoClient

from src.user_credentials.domain.user_credentials import UserCredentials
from src.user_credentials.domain.user_credentials_repository import \
    UserCredentialsRepository


class UserCredentialsMongoDBRepository(UserCredentialsRepository):
    def __init__(self, settings: dict) -> None:
        self.client = MongoClient(settings['uri'])
        self.db = self.client[settings['database']]
        self.collection = self.db['users']

    def save(self, user_credentials: UserCredentials) -> None:
        self.collection.insert_one({
            'credentials': {
                'email': user_credentials.email,
                'username': user_credentials.username,
                'password': user_credentials.password
            }
        })

    def find_by_username(self, username: str) -> Optional[UserCredentials]:
        user_credentials = self.collection.find_one(
            {'credentials.username': username})
        return user_credentials

    def find_by_email(self, email: str) -> Optional[UserCredentials]:
        user_credentials = self.collection.find_one(
            {'credentials.email': email})
        return user_credentials

    def find_by_username_or_email(self, username: str, email: str) -> Optional[UserCredentials]:
        user_credentials = self.collection.find_one(
            {'$or': [{'credentials.username': username}, {'credentials.email': email}]})
        return user_credentials

from typing import Optional

from pymongo import MongoClient

from src.common.domain import UserCredentials, UserCredentialsRepository


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

        if validate_user_credentials(user_credentials):
            return build_user_credentials(user_credentials)
        return None

    def find_by_email(self, email: str) -> Optional[UserCredentials]:
        user_credentials = self.collection.find_one(
            {'credentials.email': email})

        if validate_user_credentials(user_credentials):
            return build_user_credentials(user_credentials)
        return None

    def find_by_username_or_email(self, username: str, email: str) -> Optional[UserCredentials]:
        user_credentials = self.collection.find_one(
            {'$or': [{'credentials.username': username}, {'credentials.email': email}]})

        if validate_user_credentials(user_credentials):
            return build_user_credentials(user_credentials)
        return None


def validate_user_credentials(user_credentials: dict) -> bool:
    if not user_credentials:
        return False

    credentials = user_credentials.get('credentials')
    if not credentials:
        return False

    mandatory_attrs = ('username', 'email', 'password')
    return all(attr in credentials for attr in mandatory_attrs)


def build_user_credentials(user_credentials: dict) -> UserCredentials:
    return UserCredentials(
        str(user_credentials['_id']),
        user_credentials['credentials']['email'],
        user_credentials['credentials']['username'],
        user_credentials['credentials']['password']
    )

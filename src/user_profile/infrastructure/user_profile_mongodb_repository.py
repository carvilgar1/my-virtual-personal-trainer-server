from typing import Optional

from pymongo import MongoClient

from src.user_profile.domain.user_credentials_repository import \
    UserProfileRepository
from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfile)


class UserProfileMongoDBRepository(UserProfileRepository):
    def __init__(self, settings: dict) -> None:
        self.client = MongoClient(settings['uri'])
        self.db = self.client[settings['database']]
        self.collection = self.db['users']

    def save(self, user_id: str, user_profile: UserProfile) -> None:
        self.update(user_id, user_profile)
        self.collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    '_profile_completed': True
                }
            }
        )

    def update(self, user_id: str, user_profile: UserProfile) -> None:
        self.collection.update_one(
            {'_id': user_id},
            {
                '$set': {
                    'name': user_profile.name,
                    'surname': user_profile.surname,
                    'birth_date': user_profile.birth_date,
                    'weight': user_profile.weight,
                    'height': user_profile.height,
                    'max_heart_rate': user_profile.max_heart_rate,
                    'gender': user_profile.gender.value,
                    'activity_level': user_profile.activity_level.value
                }
            }
        )

    def find(self, user_id: str) -> Optional[UserProfile]:
        user_data = self.collection.find_one({'_id': user_id})
        if not user_data:
            return None

        profile_completed = user_data.get('_profile_completed', False)
        name = user_data.get('name', None)
        surname = user_data.get('surname', None)
        birth_date = user_data.get('birth_date', None)
        weight = user_data.get('weight', 0)
        height = user_data.get('height', 0)
        max_heart_rate = user_data.get('max_heart_rate', 0)
        gender = user_data.get('gender', 0)
        activity_level = user_data.get('activity_level', 0)

        return UserProfile(
            profile_completed=profile_completed,
            name=name,
            surname=surname,
            birth_date=birth_date,
            weight=weight,
            height=height,
            max_heart_rate=max_heart_rate,
            gender=Gender(gender),
            activity_level=ActivityLevel(activity_level)
        )

from typing import Optional

from bson import ObjectId
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
        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                '$set': {
                    'birthDate': user_profile.birth_date,
                    'weight': user_profile.weight,
                    'height': user_profile.height,
                    'maxHeartRate': user_profile.max_heart_rate,
                    'gender': user_profile.gender.value,
                    'activityLevel': user_profile.activity_level.value
                }
            },
            upsert=True
        )

    def update(self, user_id: str, user_profile: UserProfile) -> None:
        if not user_profile:
            return
        
        update_data = {}
        if user_profile.birth_date:
            update_data['birthDate'] = user_profile.birth_date
        if user_profile.weight:
            update_data['weight'] = user_profile.weight
        if user_profile.height:
            update_data['height'] = user_profile.height
        if user_profile.max_heart_rate:
            update_data['maxHeartRate'] = user_profile.max_heart_rate
        if user_profile.gender:
            update_data['gender'] = user_profile.gender.value
        if user_profile.activity_level:
            update_data['activityLevel'] = user_profile.activity_level.value

        self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                '$set': update_data
            }
        )

    def find(self, user_id: str) -> Optional[UserProfile]:
        user_data = self.collection.find_one({"_id": ObjectId(user_id)})
        if not user_data:
            return None

        birth_date = user_data.get('birthDate', None)
        weight = user_data.get('weight', None)
        height = user_data.get('height', None)
        max_heart_rate = user_data.get('maxHeartRate', None)
        gender = user_data.get('gender', None)
        activity_level = user_data.get('activityLevel', None)

        user_profile = UserProfile(
            birth_date=birth_date,
            weight=weight,
            height=height,
            max_heart_rate=max_heart_rate,
            gender=Gender(gender) if gender is not None else None,
            activity_level=ActivityLevel(
                activity_level) if activity_level is not None else None
        )
        return user_profile

    def delete(self, user_id: str) -> None:
        self.collection.delete_one({"_id": ObjectId(user_id)})

from datetime import datetime
from enum import Enum

from src.common.domain import Error, Response, Status
from src.constants import DATE_FORMAT


class Gender(Enum):
    MALE = 0
    FEMALE = 1
    OTHER = 2
    UNSPECIFIED = 3


class ActivityLevel(Enum):
    SEDENTARY = 0
    LIGHTLY_ACTIVE = 1
    MODERATELY_ACTIVE = 2
    VERY_ACTIVE = 3
    EXTRA_ACTIVE = 4


class UserProfileFormKeys:
    AGE = 'age'
    BIRTH_DATE = 'birthDate'
    WEIGHT = 'weight'
    HEIGHT = 'height'
    MAX_HEART_RATE = 'maxHeartRate'
    GENDER = 'gender'
    ACTIVITY_LEVEL = 'activityLevel'


class UserProfile:
    def __init__(self, birth_date: datetime = None, weight: float = None, height: float = None, max_heart_rate: float = None, gender: Gender = None, activity_level: ActivityLevel = None):
        self.birth_date = birth_date
        self.weight = weight
        self.height = height
        self.max_heart_rate = max_heart_rate
        self.gender = gender
        self.activity_level = activity_level

    def is_completed(self) -> bool:
        return all([
            self.birth_date is not None,
            self.weight is not None,
            self.height is not None,
            self.max_heart_rate is not None,
            self.gender is not None,
            self.activity_level is not None
        ])

    def get_age(self) -> int:
        today = datetime.now()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def to_json(self) -> dict:
        return {
            UserProfileFormKeys.BIRTH_DATE: self.birth_date.strftime(DATE_FORMAT),
            UserProfileFormKeys.AGE: self.get_age(),
            UserProfileFormKeys.WEIGHT: self.weight,
            UserProfileFormKeys.HEIGHT: self.height,
            UserProfileFormKeys.MAX_HEART_RATE: self.max_heart_rate,
            UserProfileFormKeys.GENDER: self.gender.name,
            UserProfileFormKeys.ACTIVITY_LEVEL: self.activity_level.name
        }


class UserProfileResponse(Response):
    def __init__(self, status: Status, user_profile: UserProfile, errors: Error = None):
        super().__init__(status, errors)
        self.user_profile = user_profile

    def to_json(self) -> dict:
        json_response = super().to_json()
        if self.user_profile:
            json_response['userProfile'] = self.user_profile.to_json()
        return json_response

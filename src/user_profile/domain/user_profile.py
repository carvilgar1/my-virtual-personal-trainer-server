from datetime import datetime
from enum import Enum

from src.constants import DATE_FORMAT


class Gender(Enum):
    MALE = 0
    FEMALE = 1
    OTHER = 2


class ActivityLevel(Enum):
    SEDENTARY = 0
    LIGHTLY_ACTIVE = 1
    MODERATELY_ACTIVE = 2
    VERY_ACTIVE = 3
    EXTRA_ACTIVE = 4


class UserProfile:
    def __init__(self, profile_completed: bool, name: str, surname: str, birth_date: datetime, weight: float, height: float, max_heart_rate: float, gender: Gender, activity_level: ActivityLevel):
        self._profile_completed = profile_completed
        self.name = name
        self.surname = surname
        self.birth_date = birth_date
        self.weight = weight
        self.height = height
        self.max_heart_rate = max_heart_rate
        self.gender = gender
        self.activity_level = activity_level

    def get_age(self) -> int:
        today = datetime.now()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'surname': self.surname,
            'birth_date': self.birth_date.strftime(DATE_FORMAT),
            'age': self.get_age(),
            'weight': self.weight,
            'height': self.height,
            'max_heart_rate': self.max_heart_rate,
            'gender': self.gender.name,
            'activity_level': self.activity_level.name
        }

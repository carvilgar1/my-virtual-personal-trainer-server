import unittest
from datetime import datetime
from unittest.mock import patch

from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfile)


class TestUserProfile(unittest.TestCase):

    def test_initialization(self):
        birth_date = datetime(1990, 1, 1)
        user = UserProfile(
            name="Test",
            surname="User",
            birth_date=birth_date,
            weight=70.0,
            height=175.0,
            max_heart_rate=190.0,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )
        self.assertEqual(user.name, "Test")
        self.assertEqual(user.surname, "User")
        self.assertEqual(user.birth_date, birth_date)
        self.assertEqual(user.weight, 70.0)
        self.assertEqual(user.height, 175.0)
        self.assertEqual(user.max_heart_rate, 190.0)
        self.assertEqual(user.gender, Gender.MALE)
        self.assertEqual(user.activity_level, ActivityLevel.MODERATELY_ACTIVE)

    @patch('src.user_profile.domain.user_profile.datetime')
    def test_age_computation_on_same_birthday(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2025, 4, 13)

        birth_date = datetime(2000, 4, 13)
        user = UserProfile(
            name="",
            surname="",
            birth_date=birth_date,
            weight=0,
            height=0,
            max_heart_rate=0,
            gender=0,
            activity_level=0
        )
        age = user.get_age()
        self.assertEqual(age, 25)

    @patch('src.user_profile.domain.user_profile.datetime')
    def test_age_for_day_before_birthday(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2025, 4, 12)

        birth_date = datetime(2000, 4, 13)
        user = UserProfile(
            name="",
            surname="",
            birth_date=birth_date,
            weight=0,
            height=0,
            max_heart_rate=0,
            gender=0,
            activity_level=0
        )
        age = user.get_age()
        self.assertEqual(age, 24)

    @patch('src.user_profile.domain.user_profile.datetime')
    def test_get_age_for_birthday_in_future(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2026, 6, 18)

        birth_date = datetime(2000, 4, 13)
        user = UserProfile(
            name="",
            surname="",
            birth_date=birth_date,
            weight=0,
            height=0,
            max_heart_rate=0,
            gender=0,
            activity_level=0
        )
        age = user.get_age()
        self.assertEqual(age, 26)

    def test_to_json(self):
        birth_date = datetime(1990, 1, 1)
        user = UserProfile(
            name="Test",
            surname="User",
            birth_date=birth_date,
            weight=70.0,
            height=175.0,
            max_heart_rate=190.0,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )
        user_json = user.to_json()
        self.assertEqual(user_json['name'], "Test")
        self.assertEqual(user_json['surname'], "User")
        self.assertEqual(user_json['birth_date'], '1990-01-01')
        self.assertEqual(user_json['weight'], 70.0)
        self.assertEqual(user_json['height'], 175.0)
        self.assertEqual(user_json['max_heart_rate'], 190.0)
        self.assertEqual(user_json['gender'], "MALE")
        self.assertEqual(user_json['activity_level'], "MODERATELY_ACTIVE")

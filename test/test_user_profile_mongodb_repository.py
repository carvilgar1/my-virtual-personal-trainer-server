import unittest
from datetime import datetime
from unittest.mock import MagicMock, call, patch

from bson import ObjectId
from pymongo.collection import Collection

from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfile)
from src.user_profile.infrastructure.user_profile_mongodb_repository import \
    UserProfileMongoDBRepository


class TestUserProfileMongoDBRepository(unittest.TestCase):
    @patch('src.user_profile.infrastructure.user_profile_mongodb_repository.MongoClient')
    def test_partial_update(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock(spec=Collection)
        mock_db = {'users': mock_collection}
        mock_client = {'test_database': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017',
                    'database': 'test_database'}
        repository = UserProfileMongoDBRepository(settings)

        user_id = '682216745ea2078f68384d16'
        user_profile = UserProfile(
            birth_date='1990-01-01',
            weight=70,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )

        # Act
        repository.update(user_id, user_profile)

        # Assert
        mock_collection.update_one.assert_called_once_with(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'birthDate': user_profile.birth_date,
                    'weight': user_profile.weight,
                    'activityLevel': user_profile.activity_level.value
                }
            }
        )

    @patch('src.user_profile.infrastructure.user_profile_mongodb_repository.MongoClient')
    def test_full_update(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock(spec=Collection)
        mock_db = {'users': mock_collection}
        mock_client = {'test_database': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017',
                    'database': 'test_database'}
        repository = UserProfileMongoDBRepository(settings)

        user_id = '682216745ea2078f68384d16'
        user_profile = UserProfile(
            birth_date='1990-01-01',
            weight=70,
            height=175,
            max_heart_rate=190,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )

        # Act
        repository.update(user_id, user_profile)

        # Assert
        mock_collection.update_one.assert_called_once_with(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'birthDate': user_profile.birth_date,
                    'weight': user_profile.weight,
                    'height': user_profile.height,
                    'maxHeartRate': user_profile.max_heart_rate,
                    'gender': user_profile.gender.value,
                    'activityLevel': user_profile.activity_level.value
                }
            }
        )

    @patch('src.user_profile.infrastructure.user_profile_mongodb_repository.MongoClient')
    def test_save_calls_update_and_sets_profile_completed(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock(spec=Collection)
        mock_db = {'users': mock_collection}
        mock_client = {'test_database': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017',
                    'database': 'test_database'}
        repository = UserProfileMongoDBRepository(settings)

        user_id = '682216745ea2078f68384d16'
        user_profile = UserProfile(
            birth_date='1990-01-01',
            weight=70,
            height=175,
            max_heart_rate=190,
            gender=Gender.MALE,
            activity_level=ActivityLevel.MODERATELY_ACTIVE
        )

        # Act
        repository.save(user_id, user_profile)

        # Assert
        mock_collection.update_one.assert_has_calls([
            call(
                {'_id': ObjectId(user_id)},
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
        ])

    @patch('src.user_profile.infrastructure.user_profile_mongodb_repository.MongoClient')
    def test_find_uncompleted_profile_with_missng_fields(self, mock_mongo_client):
        user_id = '682216745ea2078f68384d16'

        mock_collection = MagicMock(spec=Collection)
        mock_collection.find_one.return_value = {
            '_id': user_id,
            '_profile_completed': False
        }
        mock_db = {'users': mock_collection}
        mock_client = {'test_database': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017',
                    'database': 'test_database'}
        repository = UserProfileMongoDBRepository(settings)

        result = repository.find(user_id)

        self.assertIsNotNone(result)
        self.assertIsNone(result.birth_date)
        self.assertIsNone(result.weight)
        self.assertIsNone(result.height)
        self.assertIsNone(result.max_heart_rate)
        self.assertIsNone(result.gender)
        self.assertIsNone(result.activity_level)

    @patch('src.user_profile.infrastructure.user_profile_mongodb_repository.MongoClient')
    def test_find_full_completed_profile(self, mock_mongo_client):
        user_id = '682216745ea2078f68384d16'

        mock_collection = MagicMock(spec=Collection)
        mock_collection.find_one.return_value = {
            '_id': user_id,
            'birthDate': datetime(1990, 1, 1),
            'weight': 70,
            'height': 175,
            'maxHeartRate': 190,
            'gender': 0,
            'activityLevel': 2
        }
        mock_db = {'users': mock_collection}
        mock_client = {'test_database': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017',
                    'database': 'test_database'}
        repository = UserProfileMongoDBRepository(settings)

        result = repository.find(user_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.birth_date, datetime(1990, 1, 1))
        self.assertEqual(result.weight, 70)
        self.assertEqual(result.height, 175)
        self.assertEqual(result.max_heart_rate, 190)
        self.assertEqual(result.gender, Gender.MALE)
        self.assertEqual(result.activity_level,
                         ActivityLevel.MODERATELY_ACTIVE)

    @patch('src.user_profile.infrastructure.user_profile_mongodb_repository.MongoClient')
    def test_find_missing_profile(self, mock_mongo_client):
        user_id = '682216745ea2078f68384d16'

        mock_collection = MagicMock(spec=Collection)
        mock_collection.find_one.return_value = None
        mock_db = {'users': mock_collection}
        mock_client = {'test_database': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017',
                    'database': 'test_database'}
        repository = UserProfileMongoDBRepository(settings)

        result = repository.find(user_id)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

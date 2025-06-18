import unittest
from datetime import datetime
from unittest.mock import MagicMock, call, patch

from src.workouts.domain.workouts import Mood, Workout
from src.workouts.infrastructure.workouts_mongodb_repository import \
    WorkoutsMongoDBRepository


class TestWorkoutsMongoDBRepository(unittest.TestCase):
    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_save_many_deletes_and_inserts(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        user_id = 'user123'
        workouts = [
            Workout(start='2025-07-09T14:48:00.000000+0000',
                    duration=20, intensity=3, mood=Mood.NEUTRAL, sleep_score=80),
            Workout(start='2025-07-10T14:48:00.000000+0000',
                    duration=30, intensity=4, mood=Mood.STRESSED, sleep_score=85)
        ]

        # Act
        repo.save_many(user_id, workouts)

        # Assert
        mock_collection.delete_many.assert_called_once_with(
            {'userId': user_id})
        # Should call insert_many once with both workouts
        inserted = [
            {
                'userId': user_id,
                'startTime': w.start,
                'duration': w.duration,
                'intensity': w.intensity,
                'mood': w.mood.value,
                'sleepScore': w.sleep_score
            }
            for w in workouts
        ]
        # insert_many is called with a generator, so convert to list for comparison
        args, _ = mock_collection.insert_many.call_args
        inserted_arg = list(args[0])
        self.assertEqual(inserted_arg, inserted)

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_save_many_batches(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        user_id = 'user456'
        # 1200 workouts to trigger batching (500 per batch)
        workouts = [
            Workout(start=f'2025-07-{i:02d}T14:48:00.000000+0000',
                    duration=i, intensity=3, mood=Mood.NEUTRAL, sleep_score=80)
            for i in range(1, 1201)
        ]

        # Act
        repo.save_many(user_id, workouts)

        # Assert
        mock_collection.delete_many.assert_called_once_with(
            {'userId': user_id})
        # Should call insert_many 3 times (500, 500, 200)
        self.assertEqual(mock_collection.insert_many.call_count, 3)
        # Check batch sizes
        batch_sizes = [len(list(call_args[0][0]))
                       for call_args in mock_collection.insert_many.call_args_list]
        self.assertEqual(batch_sizes, [500, 500, 200])

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_save_many_empty_list(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        user_id = 'user789'
        workouts = []

        # Act
        repo.save_many(user_id, workouts)

        # Assert
        mock_collection.delete_many.assert_called_once_with(
            {'userId': user_id})
        mock_collection.insert_many.assert_not_called()

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_retrieve_workouts_pagination(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        # Simulate .skip().limit() chain
        mock_collection.find.return_value.skip.return_value.limit.return_value = [
            {'startTime': '2025-07-09T14:48:00.000000+0000',
                'duration': 20, 'intensity': 3, 'mood': 8, 'sleepScore': 80},
            {'startTime': '2025-07-10T14:48:00.000000+0000',
                'duration': 30, 'intensity': 4, 'mood': 3, 'sleepScore': 85}
        ]
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        user_id = 'user123'

        # Act
        workouts_iter = repo.retrieve_workouts(user_id, page=2, page_size=2)
        workouts = list(workouts_iter)

        # Assert
        mock_collection.find.assert_called_once_with(
            {'userId': user_id},
            {'_id': 0, 'userId': 0}
        )
        mock_collection.find.return_value.skip.assert_called_once_with(2)
        mock_collection.find.return_value.skip.return_value.limit.assert_called_once_with(
            2)
        self.assertEqual(len(workouts), 2)
        self.assertEqual(workouts[0].duration, 20)
        self.assertEqual(workouts[1].mood, Mood.STRESSED)

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_retrieve_workouts_by_dates(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {'startTime': '2025-07-09T14:48:00.000000+0000',
                'duration': 20, 'intensity': 3, 'mood': 8, 'sleepScore': 80},
            {'startTime': '2025-07-10T14:48:00.000000+0000',
                'duration': 30, 'intensity': 4, 'mood': 3, 'sleepScore': 85}
        ]
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        user_id = 'user123'
        start = datetime(2025, 7, 9, 0, 0, 0)
        end = datetime(2025, 7, 10, 23, 59, 59)

        # Act
        workouts_iter = repo.retrieve_workouts_by_dates(user_id, start, end)
        workouts = list(workouts_iter)

        # Assert
        mock_collection.find.assert_called_once_with(
            {
                'userId': user_id,
                'startTime': {'$gte': start, '$lte': end}
            },
            {'_id': 0, 'userId': 0}
        )
        self.assertEqual(len(workouts), 2)
        self.assertEqual(workouts[0].duration, 20)
        self.assertEqual(workouts[1].mood, Mood.STRESSED)

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_build_workout(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        workout_data = {
            'startTime': '2025-07-09T14:48:00.000000+0000',
            'duration': 20,
            'intensity': 3,
            'mood': 8,
            'sleepScore': 80
        }

        # Act
        workout = repo.build_workout(workout_data)

        # Assert
        self.assertEqual(workout.start, '2025-07-09T14:48:00.000000+0000')
        self.assertEqual(workout.duration, 20)
        self.assertEqual(workout.intensity, 3)
        self.assertEqual(workout.mood, Mood.NEUTRAL)
        self.assertEqual(workout.sleep_score, 80)


if __name__ == '__main__':
    unittest.main()

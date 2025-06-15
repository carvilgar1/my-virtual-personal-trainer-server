import unittest
from unittest.mock import MagicMock, patch, call
from src.workouts.domain.workouts import Workout
from src.workouts.infrastructure.workouts_mongodb_repository import WorkoutsMongoDBRepository
from datetime import datetime

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
            Workout(start='2024-01-01T10:00:00', duration=30, average_heart_rate=120),
            Workout(start='2024-01-02T10:00:00', duration=40, average_heart_rate=130)
        ]

        # Act
        repo.save_many(user_id, workouts)

        # Assert
        mock_collection.delete_many.assert_called_once_with({'userId': user_id})
        # Should call insert_many once with both workouts
        inserted = [
            {
                'userId': user_id,
                'startTime': w.start,
                'duration': w.duration,
                'averageHeartRate': w.average_heart_rate
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
            Workout(start=f'2024-01-{i:02d}T10:00:00', duration=i, average_heart_rate=100+i)
            for i in range(1, 1201)
        ]

        # Act
        repo.save_many(user_id, workouts)

        # Assert
        mock_collection.delete_many.assert_called_once_with({'userId': user_id})
        # Should call insert_many 3 times (500, 500, 200)
        self.assertEqual(mock_collection.insert_many.call_count, 3)
        # Check batch sizes
        batch_sizes = [len(list(call_args[0][0])) for call_args in mock_collection.insert_many.call_args_list]
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
        mock_collection.delete_many.assert_called_once_with({'userId': user_id})
        mock_collection.insert_many.assert_not_called()

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_retrieve_workouts_pagination(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        # Simulate .skip().limit() chain
        mock_collection.find.return_value.skip.return_value.limit.return_value = [
            {'startTime': '2024-01-01T10:00:00', 'duration': 30, 'averageHeartRate': 120},
            {'startTime': '2024-01-02T10:00:00', 'duration': 40, 'averageHeartRate': 130}
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
        mock_collection.find.return_value.skip.return_value.limit.assert_called_once_with(2)
        self.assertEqual(len(workouts), 2)
        self.assertEqual(workouts[0].duration, 30)
        self.assertEqual(workouts[1].average_heart_rate, 130)

    @patch('src.workouts.infrastructure.workouts_mongodb_repository.MongoClient')
    def test_retrieve_workouts_by_dates(self, mock_mongo_client):
        # Arrange
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {'startTime': '2024-01-01T10:00:00', 'duration': 30, 'averageHeartRate': 120},
            {'startTime': '2024-01-02T10:00:00', 'duration': 40, 'averageHeartRate': 130}
        ]
        mock_db = {'workouts': mock_collection}
        mock_client = {'testdb': mock_db}
        mock_mongo_client.return_value = mock_client

        settings = {'uri': 'mongodb://localhost:27017', 'database': 'testdb'}
        repo = WorkoutsMongoDBRepository(settings)
        user_id = 'user123'
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 2, 23, 59, 59)

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
        self.assertEqual(workouts[0].duration, 30)
        self.assertEqual(workouts[1].average_heart_rate, 130)

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
            'startTime': '2024-01-01T10:00:00',
            'duration': 45,
            'averageHeartRate': 110
        }

        # Act
        workout = repo.build_workout(workout_data)

        # Assert
        self.assertEqual(workout.start, '2024-01-01T10:00:00')
        self.assertEqual(workout.duration, 45)
        self.assertEqual(workout.average_heart_rate, 110)
        
if __name__ == '__main__':
    unittest.main()
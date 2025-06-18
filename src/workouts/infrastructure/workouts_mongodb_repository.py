from datetime import datetime
from typing import Iterator

from pymongo import MongoClient

from src.workouts.domain.workouts import Mood, Workout
from src.workouts.domain.workouts_repository import WorkoutsRepository


class WorkoutsMongoDBRepository(WorkoutsRepository):
    def __init__(self, settings: dict) -> None:
        self.client = MongoClient(settings['uri'])
        self.db = self.client[settings['database']]
        self.collection = self.db['workouts']

    def save_many(self, user_id: str, workouts: list[Workout]) -> None:
        def build_query(workout: Workout) -> dict:
            return {
                'userId': user_id,
                'startTime': workout.start,
                'duration': workout.duration,
                'intensity': workout.intensity,
                'sleepScore': workout.sleep_score,
                'mood': workout.mood.value
            }

        batch_size = 500
        workouts_count = len(workouts)
        index = 0
        while index < workouts_count:
            batch = workouts[index:index + batch_size]
            self.collection.insert_many(
                (build_query(workout) for workout in batch))
            index += batch_size

    def retrieve_workouts(self, user_id: str, page: int, page_size: int) -> Iterator[Workout]:
        skip = (page - 1) * page_size
        workouts = (self.build_workout(workout) for workout in self.collection.find(
            {'userId': user_id},
            {'_id': 0, 'userId': 0}
        ).skip(skip).limit(page_size))
        return workouts

    def retrieve_last_n_workouts(self, user_id: str, n: int) -> Iterator[Workout]:
        workouts = (self.build_workout(workout) for workout in self.collection.find(
            {'userId': user_id},
            {'_id': 0, 'userId': 0}
        ).sort('startTime', -1).limit(n))
        return workouts

    def retrieve_all_workouts(self, user_id: str) -> Iterator[Workout]:
        workouts = (self.build_workout(workout) for workout in self.collection.find(
            {'userId': user_id},
            {'_id': 0, 'userId': 0}
        ))
        return workouts

    def retrieve_workouts_by_dates(self, user_id: str, start: datetime, end: datetime) -> Iterator[Workout]:
        workouts = (self.build_workout(workout) for workout in self.collection.find(
            {
                'userId': user_id,
                'startTime': {'$gte': start, '$lte': end}
            },
            {'_id': 0, 'userId': 0}
        ))
        return workouts

    def build_workout(self, workout_data: dict) -> Workout:
        return Workout(
            start=workout_data['startTime'],
            duration=workout_data['duration'],
            intensity=workout_data['intensity'],
            sleep_score=workout_data['sleepScore'],
            mood=Mood(workout_data['mood'])
        )

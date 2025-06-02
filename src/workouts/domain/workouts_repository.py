
from abc import ABC, abstractmethod
from datetime import datetime

from src.user_profile.domain.user_profile import UserProfile
from src.workouts.domain.workouts import Workout


class WorkoutsRepository(ABC):
    @abstractmethod
    def save_many(self, user_id: str, workouts: list[Workout]) -> None:
        pass

    @abstractmethod
    def retrieve_workouts(self, user_id: str, page: int, page_size) -> list[Workout]:
        pass

    @abstractmethod
    def retrieve_workouts_by_dates(self, user_id: str, start: datetime, end: datetime) -> list[Workout]:
        pass

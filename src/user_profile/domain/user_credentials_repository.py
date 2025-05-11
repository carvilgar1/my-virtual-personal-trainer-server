
from abc import ABC, abstractmethod
from typing import Optional

from src.user_profile.domain.user_profile import UserProfile


class UserProfileRepository(ABC):
    @abstractmethod
    def save(self, user_id: str, user_profile: UserProfile) -> None:
        pass

    @abstractmethod
    def update(self, user_id: str, user_profile: UserProfile) -> None:
        pass

    @abstractmethod
    def find(self, user_id: str) -> Optional[UserProfile]:
        pass


from abc import ABC, abstractmethod
from typing import Optional

from src.common.domain.user_credentials import UserCredentials


class UserCredentialsRepository(ABC):
    @abstractmethod
    def save(self, user_credentials: UserCredentials) -> None:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[UserCredentials]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserCredentials]:
        pass

    @abstractmethod
    def find_by_username_or_email(self, username: str, email: str) -> Optional[UserCredentials]:
        pass

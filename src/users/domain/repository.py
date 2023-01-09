from abc import abstractmethod, ABC
from users.domain.user import User

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def count_by_email(self, email: str) -> int:
        pass

    @abstractmethod
    def count_by_credentials(self, email: str, password: str) -> int:
        pass

    @abstractmethod
    def get_all_users(self) -> list[User]:
        pass

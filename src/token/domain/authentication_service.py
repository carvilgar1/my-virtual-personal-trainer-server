from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from src.common.domain import Error
from src.common.domain.response import Response
from src.user_credentials.domain.user_credentials import UserCredentials


class AuthenticationService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def grant_access(self, credentials: UserCredentials) -> Optional[Any]:
        pass

    @abstractmethod
    def authenticate(self, auth_context: dict | Any) -> Tuple[UserCredentials, Error]:
        pass

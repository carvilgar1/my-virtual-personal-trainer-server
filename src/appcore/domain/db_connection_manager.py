import os
from abc import abstractmethod, ABC

class DBConnectionManager(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBConnectionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.url = os.environ['URL']
        self.user = os.environ['USER']
        self.password = os.environ['PASSWORD']
        self.db_name = os.environ['DB_NAME']

    @abstractmethod
    def create_connection(self) -> None:
        pass

    @abstractmethod
    def close_connection(self) -> None:
        pass

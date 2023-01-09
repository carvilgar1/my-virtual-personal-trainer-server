from pymongo import MongoClient
from appcore.domain.db_connection_manager import DBConnectionManager


class MongoDBConnectionManagerImpl(DBConnectionManager):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.conn = None

    def create_connection(self) -> None:
        self.conn = MongoClient(self.url, username=self.user, password=self.password,
                            authSource=self.db_name, authMechanism='SCRAM-SHA-256')

    def close_connection(self) -> None:
        self.conn.close()

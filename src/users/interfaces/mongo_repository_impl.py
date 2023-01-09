from bson import ObjectId
from appcore.domain.db_connection_manager import DBConnectionManager
from users.domain.repository import UserRepository
from users.domain.user import User


class MongoDBUserRepositoryImpl(UserRepository):
    def __init__(self, base_repository: DBConnectionManager) -> None:
        super().__init__()
        self.base_repository = base_repository

    def save(self, user: User) -> None:
        user.id = ObjectId()
        self.base_repository.conn.get_database('my_virtual_personal_trainer') \
            .get_collection('user').insert_one(user.to_json())

    def get_all_users(self) -> list[User]:
        return [User(**obj) for obj in self.base_repository.conn
                .get_database('my_virtual_personal_trainer').get_collection('user').find({})]

    def count_by_email(self, email: str) -> int:
        return self.base_repository.conn.get_database('my_virtual_personal_trainer') \
            .get_collection('user').count_documents({'auth_credentials.email': email})

    def count_by_credentials(self, email: str, password: str) -> int:
        return self.base_repository.conn.get_database('my_virtual_personal_trainer') \
            .get_collection('user') \
            .count_documents({'auth_credentials.email': email,
                              'auth_credentials.password': password})

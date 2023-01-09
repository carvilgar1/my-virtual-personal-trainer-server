from users.domain.repository import UserRepository
from users.domain.user import User, AuthCredentials

class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def insert_user(self, form) -> None:
        auth_credentials = AuthCredentials(form['email'], form['password'])
        auth_credentials.encrypt_user_credentials()
        user = User(None, form['name'], form['sur_name'], form['birth_date'], auth_credentials,
                    form['weight'], form['height'], form['activity_level'])
        self.user_repository.save(user)

    def is_email_already_register(self, email):
        auth_credentials = AuthCredentials(email, "password")
        auth_credentials.encrypt_user_credentials()
        return self.user_repository.count_by_email(auth_credentials.email) > 0

    def are_valid_credentials(self, email: str, password: str):
        auth_credentials = AuthCredentials(email, password)
        auth_credentials.encrypt_user_credentials()
        return self.user_repository.count_by_credentials(auth_credentials.email, auth_credentials.password) > 0

    def get_all_users(self):
        return self.user_repository.get_all_users()

class UserCredentialsFormFields:
    EMAIL = 'email'
    PASSWORD = 'password'
    USERNAME = 'username'


class UserCredentials:
    def __init__(self, user_id: str, email: str, username: str, password: str):
        self.user_id = user_id
        self.email = email
        self.username = username
        self.password = password

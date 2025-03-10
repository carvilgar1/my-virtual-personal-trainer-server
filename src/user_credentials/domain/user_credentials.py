class UserCredentialsFormFields:
    EMAIL = 'email'
    PASSWORD = 'password'
    USERNAME = 'username'


class UserCredentials:
    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password = password

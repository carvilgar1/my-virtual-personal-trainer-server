class UserCredentialsFormFields:
    EMAIL = 'email'
    PASSWORD = 'password'
    USERNAME = 'username'


class UserCredentials:
    def __init__(self, id: str, email: str, username: str, password: str):
        self.id = id
        self.email = email
        self.username = username
        self.password = password

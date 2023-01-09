from datetime import datetime
from re import fullmatch
from hashlib import sha256

_EMAIL_REGEX = r"^\S+@\S+\.\S+$"
_DATE_REGEX = r"%d/%m/%Y"

class User():
    def __init__(self, _id, name, surname, birth_date, auth_credentials, weight, height, activity_level) -> None:
        self._id = _id
        self.name = name
        self.surname = surname
        self.auth_credentials = auth_credentials
        self.birth_date = birth_date
        self.weight = weight
        self.height = height
        self.activity_level = activity_level

    def get_user_age(self):
        today = datetime.now()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def get_BMI(self):
        return self.weight / self.height**2

    def to_json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "surname": self.surname,
            "birth_date": self.birth_date,
            "auth_credentials": self.auth_credentials.__dict__,
            "weight": self.weight,
            "height": self.height,
            "activity_level": self.activity_level
        }

    def _is_valid_name(self, name):
        if not (name or name.strip()):  # Name not empty or blank
            raise ValueError("name can't be empty or blank")
        return name

    def _is_valid_surname(self, surname):
        if not (surname or surname.strip()):
            raise ValueError("surname can't be empty or blank")
        return surname

    def _is_valid_birth_date(self, birth_date):
        if not (birth_date or birth_date.strip()):
            raise ValueError("birth_date can't be empty or blank")
        return datetime.strptime(birth_date, _DATE_REGEX)

    def _is_valid_weight(self, weight):
        weight = float(weight)
        if not (weight > 0.0 or weight <= 300.0):
            raise ValueError("weight must be a deecimal between 0 and 300.0")
        return weight

    def _is_valid_height(self, height):
        height = float(height)
        if not (height > 0.0 or height <= 3.0):
            raise ValueError("height must be a deecimal between 0 and 4")
        return height

    def _is_valid_activity_level(self, activity_level):
        activity_level = int(activity_level)
        if activity_level not in range(5):
            raise ValueError(
                "activity_level must be a integer between 0 and 4")
        return activity_level


class AuthCredentials():
    def __init__(self, email, password):
        self.email = self._is_valid_email(email)
        self.password = self._is_valid_password(password)

    def _is_valid_password(self, password):
        if not (password or password.strip()):
            raise ValueError("password can't be empty or blank")
        return password

    def _is_valid_email(self, email):
        if not (email or email.strip()):
            raise ValueError("email can't be empty or blank")
        if not fullmatch(_EMAIL_REGEX, email):
            raise ValueError(
                f"email {email} does not match format {_EMAIL_REGEX}")
        return email

    def encrypt_user_credentials(self):
        self.email = sha256(self.email.encode("utf-8")).hexdigest()
        self.password = sha256(self.password.encode("utf-8")).hexdigest()

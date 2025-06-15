import os

from dotenv import load_dotenv

from src import constants
from src.common.application.localizations import (PlaceHolderReplacer,
                                                  load_locales)
from src.common.domain import UserCredentialsFormFields
from src.common.infrastructure.user_credentials_mongodb_repository import \
    UserCredentialsMongoDBRepository
from src.token_auth.application.authentication import JWTAuthenticationService
from src.user_profile.infrastructure.user_profile_mongodb_repository import \
    UserProfileMongoDBRepository
from src.workouts.infrastructure.workouts_mongodb_repository import \
    WorkoutsMongoDBRepository

# ==============================================
# Environment variables
# ==============================================
load_dotenv()

# ==============================================
# Secret keys
# ==============================================
SECRET_KEY = os.getenv('SECRET_KEY')
REFRESH_KEY = os.getenv('REFRESH_KEY')

if not SECRET_KEY or not REFRESH_KEY:
    raise ValueError(
        "SECRET_KEY and REFRESH_KEY must be set in the environment variables")

# ==============================================
# Database settings
# ==============================================
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError(
        "Database configuration variables must be set in the environment variables")

DB_SETTINGS = {
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
    'database': DB_NAME,
    # Only support MongoDB for now
    'uri': f'mongodb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?authSource=admin'
}

# ==============================================
# Authentication service
# ==============================================
authentication_service = JWTAuthenticationService(
    SECRET_KEY, REFRESH_KEY, constants.ACCESS_TOKEN_EXPIRATION_HOURS, constants.REFRESH_TOKEN_EXPIRATION_DAYS, 'HS256')

# ==============================================
# Domain repositories
# ==============================================
user_credentials_repository = UserCredentialsMongoDBRepository(DB_SETTINGS)
user_profile_repository = UserProfileMongoDBRepository(DB_SETTINGS)
workouts_repository = WorkoutsMongoDBRepository(DB_SETTINGS)

# ==============================================
# Localizations configuration
# ==============================================


def init_placeholder_replacements():
    return {
        'username': UserCredentialsFormFields.USERNAME,
        'email': UserCredentialsFormFields.EMAIL,
        'password': UserCredentialsFormFields.PASSWORD,
        'password_min_length': str(constants.PASSWORD_MIN_LENGTH),
        'username_max_chars': str(constants.MAX_USERNAME_CHARS),
        'password_allowed_symbols': ''.join(constants.PASSWORD_ALLOWED_SYMBOLS),
        'min_height': str(constants.MIN_HEIGHT),
        'max_height': str(constants.MAX_HEIGHT),
        'min_weight': str(constants.MIN_WEIGHT),
        'max_weight': str(constants.MAX_WEIGHT),
        'min_heart_rate': str(constants.MIN_HEART_RATE),
        'max_heart_rate': str(constants.MAX_HEART_RATE),
    }


root_dir = os.path.dirname(os.path.abspath(__file__))
default_replacer = PlaceHolderReplacer(
    r'\{\{(.+?)\}\}', init_placeholder_replacements())
load_locales(root_dir, default_replacer)

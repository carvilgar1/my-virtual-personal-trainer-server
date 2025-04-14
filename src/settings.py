import os

from dotenv import load_dotenv

from src import constants
from src.common.application.localizations import LocalesAggregator, Localizer
from src.common.infrastructure.user_credentials_mongodb_repository import \
    UserCredentialsMongoDBRepository
from src.common.locales.locales import COMMON_LOCALES
from src.sign_up.locales.locales import SIGN_UP_LOCALES
from src.token.application.authentication import JWTAuthenticationService
from src.token.locales.locales import TOKEN_LOCALES

# Load environment variables from a .env file
load_dotenv(dotenv_path='.env.dev')

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

# ==============================================
# Localizations configuration
# ==============================================
localizer = Localizer(locales_aggregator.application_locales)

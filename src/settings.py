import os

from dotenv import load_dotenv

from src.common.application.localizations import LocalesAggregator, Localizer
from src.common.locales.locales import COMMON_LOCALES
from src.sign_up.locales.locales import SIGN_UP_LOCALES
from src.user_credentials.infrastructure.user_credentials_mongodb_repository import \
    UserCredentialsMongoDBRepository

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
# Domain repositories
# ==============================================
USER_CREDENTIALS_REPOSITORY = UserCredentialsMongoDBRepository(DB_SETTINGS)
APP_REPOSITORIES = {
    'USER_CREDENTIALS_REPOSITORY': USER_CREDENTIALS_REPOSITORY
}

# ==============================================
# Localizations configuration
# ==============================================
locales_aggregator = LocalesAggregator()
locales_aggregator.add_locales(COMMON_LOCALES)\
    .add_locales(SIGN_UP_LOCALES)

# Remove the locales from the global scope
del COMMON_LOCALES
del SIGN_UP_LOCALES

LOCALIZER = Localizer(locales_aggregator.application_locales)

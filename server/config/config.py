import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

is_production = os.environ.get('FLASK_ENV', 'development') == "production"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PASSWORD_HASH = os.environ.get('PASSWORD_HASH', 'pbkdf2:sha256:50000')

    APP_DEV_HOST = os.environ.get('APP_DEV_HOST')

    IMAGE_DIRECTORY = os.path.join(os.getcwd(), str(os.environ.get('IMAGE_DIRECTORY'))) if os.environ.get(
        'IMAGE_DIRECTORY').startswith('.') else os.environ.get('IMAGE_DIRECTORY')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    DRAMATIQ_BROKER = 'dramatiq.brokers.redis:RedisBroker'
    DRAMATIQ_BROKER_URL = os.environ.get('DRAMATIQ_BROKER_URL')
    WORKER_BACKEND_SERVER = os.environ.get('WORKER_BACKEND_SERVER')

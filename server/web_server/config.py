import os

is_production = os.environ.get('FLASK_ENV', 'development') == "production"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PASSWORD_HASH = os.environ.get('PASSWORD_HASH', 'pbkdf2:sha256:50000')

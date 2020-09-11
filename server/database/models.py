from .database import db
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """Data model for user accounts."""

    __tablename__ = 'users'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(64),
        index=True,
        unique=True,
        nullable=False
    )
    """
    email = db.Column(
        db.String(254),
        index=True,
        unique=True,
        nullable=False
    )
    """
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Image(db.Model):
    """Data model for images."""

    __tablename__ = 'images'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    owner = db.Column(
        db.Integer,
        ForeignKey('users.id'),
        index=True,
        unique=False,
        nullable=False
    )
    original_width = db.Column(
        db.Integer,
        index=True,
        unique=False,
        nullable=True
    )
    original_height = db.Column(
        db.Integer,
        index=True,
        unique=False,
        nullable=True
    )
    original_filename = db.Column(
        db.String(255),
        index=True,
        unique=False,
        nullable=False
    )
    extension = db.Column(
        db.String(255),
        index=True,
        unique=False,
        nullable=False
    )
    uuid_access_token = db.Column(
        db.String(36),
        index=False,
        unique=False,
        nullable=False
    )

    def __repr__(self):
        return f'<Image {self.id} {self.owner}>'

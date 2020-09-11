from database import User, Image, db
from urllib.parse import urlparse, urljoin
from flask import request, current_app, safe_join
from typing import BinaryIO
from worker import get_image_metadata
import os
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def create_user(username: str, password: str):
    if User.query.filter_by(username=username).first() is not None:
        return {
            'error': True,
            'error_message': 'User already exists'
        }
    new_user = User(
        username=username,
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return {
        'success': True,
    }


def handle_image(filename: str, image_stream: BinaryIO, owner_id: int) -> bool:
    filename, extension = os.path.splitext(filename)
    extension = extension[1:].lower()
    if extension.lower() not in ALLOWED_EXTENSIONS:
        return False
    image = Image(owner=owner_id, original_filename=filename,
                  extension=extension, uuid_access_token=str(uuid.uuid4()))
    db.session.add(image)
    db.session.commit()
    if not os.path.isdir(safe_join(current_app.config.get('IMAGE_DIRECTORY'), 'original')):
        os.makedirs(safe_join(current_app.config.get(
            'IMAGE_DIRECTORY'), 'original'))
    with open(safe_join(current_app.config.get('IMAGE_DIRECTORY'), 'original', f"{image.id}.{extension}"), 'wb') as f:
        f.write(image_stream.read())
    # Add image tasks
    get_image_metadata.delay(image.id, image.uuid_access_token)
    return True


TEST_USER_USERNAME = 'test'
TEST_IMAGE_DIRECTORY = './test_images'


def create_test_data(app):
    with app.app_context():
        if User.query.count() == 0:
            print("=> Creating test user")
            create_user(TEST_USER_USERNAME, TEST_USER_USERNAME)
        if Image.query.count() == 0:
            print(f"=> Creating test images")
            user_id = User.query.filter_by(
                username=TEST_USER_USERNAME).first().id
            for image_filename in os.listdir(TEST_IMAGE_DIRECTORY):
                with open(os.path.join(TEST_IMAGE_DIRECTORY, image_filename), 'rb') as f:
                    handle_image(image_filename, f, user_id)
                    print(image_filename)

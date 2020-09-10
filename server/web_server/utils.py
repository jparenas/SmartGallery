from database import User, db
from urllib.parse import urlparse, urljoin
from flask import request


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


def create_test_data(app):
    with app.app_context():
        if User.query.count() == 0:
            print("=> Creating test data")
            create_user('test', 'test')

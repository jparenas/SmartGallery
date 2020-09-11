from flask import current_app, Blueprint, send_from_directory, request, jsonify, redirect, url_for, safe_join, send_file
from flask import json
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from database import User, Image
from config import is_production, Config
from worker.utils import get_celery_queue_items
from .utils import create_user, is_safe_url, handle_image
import os
import io
import base64
from urllib.parse import unquote_plus


api_root = Blueprint('api', __name__)
root = Blueprint('root', __name__)


EXTENSION_TO_MIME_TYPE = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif'
}


@api_root.route('/api')
def api_base():
    return jsonify({
        'success': True,
    })


@api_root.route('/api/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        return jsonify(create_user(data['username'], data['password']))
    return jsonify({
        'error': True,
        'error_message': 'Did not send all fields: username, password'
    })


@api_root.route('/api/login', methods=['POST'])
def login():
    next_url = request.args.get('next')
    if not next_url or not is_safe_url(next_url):
        next_url = None
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'next': next_url or url_for('root.catch_all')
        })
    data = request.get_json()
    if 'username' in data and 'password' in data:
        user = User.query.filter_by(username=data['username']).first()
        if user is None or not user.check_password(data['password']):
            return jsonify({
                'error': True,
                'error_message': 'Wrong username or password'
            })
        login_user(user)
        return jsonify({
            'success': True,
            'next': next_url or url_for('root.catch_all')
        })
    return jsonify({
        'error': True,
        'error_message': 'Did not send all fields: username, password'
    })


@api_root.route('/api/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        return jsonify({
            'success': True,
        })
    return jsonify({
        'success': False,
    })


@api_root.route('/api/info', methods=['GET'])
@login_required
def info():
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'username': User.query.filter_by(id=current_user.id).first().username,
            'tasks': get_celery_queue_items('celery')
        })
    else:
        return jsonify({
            'success': False
        })


@api_root.route('/api/images', methods=['GET'])
@login_required
def find_images():
    images = Image.query.filter_by(owner=current_user.id).all()
    return jsonify(list(map(lambda image: {
        'id': image.id,
        'owner': User.query.filter_by(id=image.owner).first().username,
        'original_filename': f'{image.original_filename}.{image.extension}',
        'original_width': image.original_width,
        'original_height': image.original_height
    }, images)))


@api_root.route('/api/image/<string:quality>/<int:image_id>', methods=['GET'])
def get_image(quality: str, image_id: int):
    quality = quality.lower()
    image = Image.query.get(image_id)
    if image is None:
        return 'Image not found', 404
    uuid_access_token = request.args.get('uuid')
    if (current_user.is_authenticated and image.owner != current_user.id) or (uuid_access_token is not None and unquote_plus(uuid_access_token) != image.uuid_access_token):
        return 'User not authorized to see image', 401

    extension = 'jpg'
    if quality != 'original':
        if not os.path.exists(safe_join(str(current_app.config.get('IMAGE_DIRECTORY')), quality, f"{str(image.id)}.{extension}")):
            quality = 'original'

    if quality == 'original':
        extension = image.extension

    return send_file(safe_join(str(current_app.config.get('IMAGE_DIRECTORY')), quality, f"{str(image.id)}.{extension}"), attachment_filename=f"{image.original_filename}.{extension}", mimetype=EXTENSION_TO_MIME_TYPE[extension])


@api_root.route('/api/image/<string:quality>/<int:image_id>', methods=['PUT'])
def add_image_quality(quality: str, image_id: int):
    quality = quality.lower()
    if quality == 'original':
        return 'Cannot replace original image', 400
    image = Image.query.get(image_id)
    if image is None:
        return 'Image not found', 404
    uuid_access_token = request.args.get('uuid')
    if uuid_access_token is not None and unquote_plus(uuid_access_token) != image.uuid_access_token:
        return 'Request not authorized to replace image', 401

    data = request.get_json()
    if 'image' not in data:
        return 'Image not in data', 400

    image_stream = base64.b64decode(str.encode(data['image']))
    if not os.path.isdir(safe_join(current_app.config.get('IMAGE_DIRECTORY'), quality)):
        os.makedirs(safe_join(current_app.config.get(
            'IMAGE_DIRECTORY'), quality))
    with open(safe_join(current_app.config.get('IMAGE_DIRECTORY'), quality, f"{image.id}.jpg"), 'wb') as f:
        f.write(io.BytesIO(image_stream).read())

    return '', 200


@api_root.route('/api/image', methods=['PUT'])
@login_required
def upload_image():
    images = request.files.to_dict()
    for image in images:
        if not images[image].filename:
            continue
        filename = secure_filename(images[image].filename)
        handle_image(filename, images[image].stream, current_user.id)
    return jsonify({
        'success': True
    })


@root.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('root.catch_all'))

    if is_production:
        return send_from_directory(current_app.static_folder, "index.html")
    else:
        return redirect(f'{Config.APP_DEV_HOST}{request.path}')


@root.route('/', defaults={'path': ''})
@root.route("/<string:path>")
@root.route('/<path:path>')
@login_required
def catch_all(path):
    if is_production:
        return send_from_directory(current_app.static_folder, "index.html")
    else:
        return redirect(f'{Config.APP_DEV_HOST}{path}')

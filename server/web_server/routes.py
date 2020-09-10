from flask import current_app, Blueprint, send_from_directory, request, jsonify, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from database import User, db
from .config import is_production, Config
from .utils import create_user, is_safe_url

api_root = Blueprint('api', __name__)
root = Blueprint('root', __name__)


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
            'username': current_user.id
        })
    else:
        return jsonify({
            'success': False
        })


@api_root.route('/api/find')
@login_required
def find_user():
    username = request.args.get('user')
    if username:
        user = User.query.filter_by(username=username).first()
        return jsonify({
            'user': repr(user)
        })
    return "Not found"


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

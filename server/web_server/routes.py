from flask import current_app, Blueprint, send_from_directory, request, jsonify
from flask_login import login_required
from database import User, db

api_root = Blueprint('api', __name__)
root = Blueprint('', __name__)


@api_root.route('/api')
def api_base():
    return "Hello world!"


@api_root.route('/api/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()


@api_root.route('/api/create')
def create_user():
    username = request.args.get('user')
    email = request.args.get('email')
    password = request.args.get('password')
    if username and email and password:
        if User.query.filter_by(username=username).first() is not None:
            return 'User already exists'
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()
        return f"Hello {repr(new_user)}!"
    return "Not enough info"


@api_root.route('/api/find')
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
    return send_from_directory(current_app.static_folder, "index.html")


@root.route('/', defaults={'path': ''})
@root.route("/<string:path>")
@root.route('/<path:path>')
@login_required
def catch_all(path):
    return send_from_directory(current_app.static_folder, "index.html")

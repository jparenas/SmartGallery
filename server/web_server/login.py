
from flask_login import LoginManager
from flask import request, redirect, url_for, jsonify
from database import User

login_manager = LoginManager()


login_manager.login_view = ".login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_handler():
    if request.path.startswith('/api/'):
        return jsonify({
            'error': True,
            'error_message': 'Unauthorized'
        }), 401
    else:
        return redirect(url_for(login_manager.login_view))

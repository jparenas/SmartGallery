from web_server import Config, api_root, root, login_manager
from database import db
import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def create_app():
    app = Flask(__name__, static_url_path='/',
                static_folder=os.environ.get('APP_STATIC_DIR'))

    app.config.from_object('web_server.Config')

    login_manager.init_app(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(root)
    app.register_blueprint(api_root)

    return app

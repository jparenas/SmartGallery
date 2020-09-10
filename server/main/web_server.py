from web_server import Config, api_root, root, login_manager, is_production, create_test_data
from database import db
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import exc
import time


def create_app():
    app = Flask(__name__, static_url_path='/',
                static_folder=os.environ.get('APP_STATIC_DIR', './static'))

    app.config.from_object('web_server.Config')

    cors_resources = {}
    if not is_production:
        cors_resources = {r"/api/*": {"origins": Config.APP_DEV_HOST}}

    CORS(app, supports_credentials=True)

    login_manager.init_app(app)

    db.init_app(app)

    with app.app_context():
        while True:
            try:
                db.create_all()
                break
            except exc.OperationalError as e:
                print(e)
                time.sleep(1)

    app.register_blueprint(root)
    app.register_blueprint(api_root)

    if not is_production:
        create_test_data(app)

    return app

from web_server import api_root, root, login_manager, create_test_data, check_images
from config import Config, is_production
from database import db
from worker import dramatiq
import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
import time


def create_app():
    app = Flask(__name__, static_url_path='/',
                static_folder=os.environ.get('APP_STATIC_DIR', './static'))

    app.config.from_object('config.Config')

    cors_resources = {}
    if not is_production:
        cors_resources = {r"/api/*": {"origins": Config.APP_DEV_HOST}}

    CORS(app, supports_credentials=True)

    login_manager.init_app(app)

    db.init_app(app)
    dramatiq.init_app(app)

    if len(sys.argv) >= 2 and sys.argv[1].lower() != 'worker':
        with app.app_context():
            while True:
                try:
                    db.create_all()
                    check_images()
                    break
                except exc.OperationalError as e:
                    print(e)
                    time.sleep(1)

    app.register_blueprint(root)
    app.register_blueprint(api_root)

    if not is_production:
        create_test_data(app)

    return app

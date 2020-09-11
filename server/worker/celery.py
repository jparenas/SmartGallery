from celery import Celery
from database import db
import os
from flask import Flask
import time
from sqlalchemy import exc
from config import Config


def make_celery():
    app = Flask(__name__, static_url_path='/',
                static_folder=os.environ.get('APP_STATIC_DIR', './static'))

    app.config.from_object('config.Config')

    db.init_app(app)

    celery = Celery(
        backend=Config.CELERY_RESULT_BACKEND,
        broker=Config.CELERY_BROKER_URL
    )

    with app.app_context():
        while True:
            try:
                db.engine.execute('SELECT 1')
                break
            except exc.OperationalError as e:
                print(e)
                time.sleep(1)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery


worker_celery = make_celery()

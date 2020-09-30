from .celery import worker_celery
from config import Config
from database import Image as DBImage, db
from PIL import Image
from urllib.parse import quote_plus
import requests
import time
import io
import base64


@worker_celery.task(bind=True, ignore_result=True)
def get_image_annotations(self, image_id, uuid_access_token):
    print(f'Annotations {image_id}')
    # time.sleep(60)


@worker_celery.task(bind=True, ignore_result=True)
def get_image_metadata(self, image_id, uuid_access_token):
    print(f'Metadata and resizing {image_id}')
    image = None
    while image is None:
        try:
            image = Image.open(requests.get(
                f'{Config.WORKER_BACKEND_SERVER}/api/image/{image_id}/original?uuid={quote_plus(uuid_access_token)}', stream=True).raw)
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    width, height = image.size
    image_dao = DBImage.query.get(image_id)
    image_dao.original_width = width
    image_dao.original_height = height
    db.session.commit()
    print(f'Image width and height: {width} {height}')
    image.thumbnail((500, 500), Image.ANTIALIAS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='jpeg')
    image_bytes = image_bytes.getvalue()
    while True:
        try:
            response = requests.put(f'{Config.WORKER_BACKEND_SERVER}/api/image/{image_id}/large?uuid={quote_plus(uuid_access_token)}', json={
                'image': base64.b64encode(image_bytes).decode()
            })
            print(response.status_code)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    print(f'Saved 500x500 thumbnail from {image_id}')
    image.thumbnail((300, 300), Image.ANTIALIAS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='jpeg')
    image_bytes = image_bytes.getvalue()
    while True:
        try:
            requests.put(f'{Config.WORKER_BACKEND_SERVER}/api/image/{image_id}/small?uuid={quote_plus(uuid_access_token)}', json={
                'image': base64.b64encode(image_bytes).decode()
            })
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    print(f'Saved 300x300 thumbnail from {image_id}')

    get_image_annotations.delay(image_id, uuid_access_token)

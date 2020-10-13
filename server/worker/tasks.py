from flask.helpers import safe_join
from .celery import worker_celery
from .predictions import get_image_objects, get_image_description
from config import Config
from database import Image as DBImage, db, ImageObject
from PIL import Image
from urllib.parse import quote_plus
import requests
import time
import io
import os
import base64
import uuid
import shutil


def expand2square(pil_img, background_color='black') -> Image:
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


@worker_celery.task(bind=True, ignore_result=True)
def get_image_annotations(self, image_id, uuid_access_token):
    print(f'Annotations for image: {image_id}')
    image = None
    while image is None:
        try:
            image = Image.open(requests.get(
                f'{Config.WORKER_BACKEND_SERVER}/api/image/{image_id}/small?uuid={quote_plus(uuid_access_token)}', stream=True).raw)
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    assert(image.width == 320 or image.height == 320)
    padded_image = expand2square(image)
    folder_path = safe_join(os.getcwd(), 'tmp', str(uuid.uuid4()))
    image_path = safe_join(folder_path, 'image.jpg')
    if not os.path.isdir(os.path.join(os.getcwd(), 'tmp')):
        os.mkdir(os.path.join(os.getcwd(), 'tmp'))
    os.mkdir(folder_path)
    padded_image.save(image_path)
    objects = get_image_objects(padded_image)
    print(f"=> {image_id}: Found {len(objects)} objects")
    w_difference = (padded_image.width - image.width) // 2
    h_difference = (padded_image.height - image.height) // 2
    for obj in objects:
        obj["x1"] = ((obj["x1"] * padded_image.width) - w_difference) / image.width
        obj["x2"] = ((obj["x2"] * padded_image.width) - w_difference) / image.width
        obj["y1"] = ((obj["y1"] * padded_image.height) - h_difference) / image.height
        obj["y2"] = ((obj["y2"] * padded_image.height) - h_difference) / image.height
        image_object = ImageObject(image_id=image_id, x1=obj["x1"],
                  y1=obj["y1"], x2=obj["x2"], y2=obj["y2"], name=obj["class_name"])
        db.session.add(image_object)
        db.session.commit()
    description = get_image_description(folder_path)
    print(f"=> Description for image {image_id}: {description}")
    shutil.rmtree(folder_path)
    db_image = DBImage.query.get(image_id)
    db_image.description = description
    db.session.commit()


@worker_celery.task(bind=True, ignore_result=True)
def get_image_metadata(self, image_id, uuid_access_token):
    print(f'Metadata and resizing image: {image_id}')
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
    print(f'Saved {image.width}x{image.height} thumbnail from {image_id}')
    image.thumbnail((320, 320), Image.ANTIALIAS)
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
    print(f'Saved {image.width}x{image.height} thumbnail from {image_id}')

    get_image_annotations.delay(image_id, uuid_access_token)

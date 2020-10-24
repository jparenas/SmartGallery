from flask_dramatiq import Dramatiq
from flask.helpers import safe_join
from .predictions import get_image_objects, get_image_description
from config import Config
from database import Image as DBImage, db, ImageObject, User
from PIL import Image
from urllib.parse import quote_plus
from datetime import datetime
import requests
import time
import io
import os
import base64
import uuid
import shutil

dramatiq = Dramatiq()

def getImage(image_id: str, access_token: str, quality: str) -> Image: 
    image = None
    while image is None:
        try:
            response = requests.get(
                f'{Config.WORKER_BACKEND_SERVER}/api/image/{image_id}/{quality}?uuid={quote_plus(access_token)}', stream=True)
            if response.status_code >= 400 and response.status_code < 500:
                raise requests.exceptions.HTTPError()
            image = Image.open(response.raw)
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    return image


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


@dramatiq.actor
def get_image_annotations(image_id, access_token):
    print(f'Annotations for image: {image_id}')
    try:
        image = getImage(image_id, access_token, 'small')
    except requests.exceptions.HTTPError: 
        return
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
    if db_image:
        db_image.description = description
        user = User.query.get(db_image.owner)
        if user:
            user.last_update = datetime.now()
        db.session.commit()


@dramatiq.actor
def get_image_metadata(image_id, access_token):
    def putImage(quality: str, image: bytes) -> None:
        while True:
            try:
                response = requests.put(f'{Config.WORKER_BACKEND_SERVER}/api/image/{image_id}/{quality}?uuid={quote_plus(access_token)}', json={
                    'image': base64.b64encode(image).decode()
                })
                print(response.status_code)
                break
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)
    print(f'Metadata and resizing image: {image_id}')
    try:
        image = getImage(image_id, access_token, 'original')
    except requests.exceptions.HTTPError:
        return
    width, height = image.size
    image_dao = DBImage.query.get(image_id)
    image_dao.original_width = width
    image_dao.original_height = height
    user = User.query.get(image_dao.owner)
    if user:
        user.last_update = datetime.now()
    db.session.commit()
    print(f'Image width and height: {width} {height}')
    image.thumbnail((500, 500), Image.ANTIALIAS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='jpeg')
    image_bytes = image_bytes.getvalue()
    putImage('large', image_bytes)
    print(f'Saved {image.width}x{image.height} thumbnail from {image_id}')
    image.thumbnail((320, 320), Image.ANTIALIAS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='jpeg')
    image_bytes = image_bytes.getvalue()
    putImage('small', image_bytes)
    print(f'Saved {image.width}x{image.height} thumbnail from {image_id}')

    get_image_annotations.send(image_id, access_token)

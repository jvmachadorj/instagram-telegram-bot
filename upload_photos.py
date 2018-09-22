import ast
import datetime
import os
import time
from random import randint
import requests
from decouple import config

from models import Image

TAGS = ['travel', 'nature']
CATEGORY = ['nature', 'backgrounds']
URL = "https://pixabay.com/api/"
KEY = config('PIXA_BAY_KEY')
per_page = "100"


def upload_photos():
    global per_page
    query_tags = "+".join(TAGS)
    query_categories = ",".join(CATEGORY)

    querystring = {"key": KEY, "q": query_tags, "image_type": "photo",
                   "category": query_categories,
                   "safesearch": "true", "per_page": per_page}
    time.sleep(5)
    response = requests.request("GET", URL, params=querystring)

    result = ast.literal_eval(response.text)['hits']
    return result


def download_photo():
    global per_page
    global status
    n = randint(0, int(per_page) - 1)
    result = upload_photos()[n]
    image_obj = Image.get_or_none(pixabay_id=result['id'])
    error = True

    while error:
        if image_obj is None:
            try:
                url = result["largeImageURL"]
                print(url)
                filename = url.split('/')[-1]
                script_path = os.path.dirname(__file__)
                rel_path = 'images/{}'.format(filename)
                path = os.path.join(script_path, rel_path)
                time.sleep(5)
                r = requests.get(url, allow_redirects=True)
                open(path, 'wb').write(r.content)
                image = save_to_db(result, path, url)
                return image
            except IOError as e:
                return e

        if image_obj.status == "Posted":
            i = 0
            status = True
            while i <= int(per_page) and status:
                n = randint(0, int(per_page) - 1)
                result = upload_photos()[n]
                image_obj = Image.get_or_none(pixabay_id=result['id'])
                if image_obj.status == "Not Posted":
                    print("Image already downloaded and in database")
                    image = Image.get(pixabay_id=result['id'])
                    return image
                else:
                    i += 1
                    status = True
        per_page = int(per_page)+10


def treat_tags(tags):
    return "#exemplo"


def create_random_caption(tags):
    #TODO Tratar as tags e retornar como #
    treated_tags = treat_tags(tags)
    return "Que belo de um comentario {}".format(treated_tags)


def save_to_db(line, path, url):

    name = line["pageURL"].split('/')[-2]
    url = url
    path = path
    pixabay_id = line['id']
    created_at = datetime.datetime.now()
    status = "Not Posted"
    tags = line['tags']
    caption = create_random_caption(tags)

    image = Image.create(name=name, url=url, path=path, pixabay_id=pixabay_id,
                         created_at=created_at, status=status,
                         tags=tags, caption=caption)
    image.save()
    return image


def change_image_status(image):
    image.status = "Posted"
    image.save()


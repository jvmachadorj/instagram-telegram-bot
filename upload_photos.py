import ast
import datetime
import os
from random import randint
import requests

from models import Image


def upload_photos():
    tags = ['travel', 'nature']
    category = ['nature', 'backgrounds']
    url = "https://pixabay.com/api/"
    key = "8943266-b5890d7d36c17ce3d56bf0676"
    per_page = "50"

    query_tags = "+".join(tags)
    query_categories = ",".join(category)

    querystring = {"key": key, "q": query_tags, "image_type": "photo", "category": query_categories,
                   "safesearch": "true", "per_page": per_page}

    response = requests.request("GET", url, params=querystring)

    result = ast.literal_eval(response.text)['hits']
    return result


def download_photo():

    n = randint(0, 50)

    result = upload_photos()[n]

    if Image.get_or_none(pixabay_id=result['id']) is None:
        try:
            url = result["largeImageURL"]
            print(url)
            filename = url.split('/')[-1]
            script_path = os.path.dirname(__file__)
            rel_path = 'images/{}'.format(filename)
            path = os.path.join(script_path, rel_path)
            r = requests.get(url, allow_redirects=True)
            open(path, 'wb').write(r.content)
            image = save_to_db(result, path, url)
            return image

        except IOError as e:
            return e
    else:
        print("Image already downloaded and in database")
        image = Image.get(pixabay_id=result['id'])
        return image


def treat_tags(tags):
    return "#exemplo"


def create_random_caption(tags):
    #TODO Tratar as tags e retornar como #
    treated_tags = treat_tags(tags)
    return "Que bela de um comentario {}".format(treated_tags)


def save_to_db(line, path, url):

    name = line["pageURL"].split('/')[-2]
    url = url
    path = path
    pixabay_id = line['id']
    created_at = datetime.datetime.now()
    status = "Not Posted"
    tags = line['tags']
    caption = create_random_caption(tags)

    image = Image.create(name=name, url=url, path=path, pixabay_id=pixabay_id, created_at=created_at, status=status,
                         tags=tags, caption=caption)
    image.save()
    return image

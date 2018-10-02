import ast
import datetime
import json
import os
import time
from random import randint

import peewee
import requests
from decouple import config

from models import Image

try:
    Image.create_table()
except peewee.OperationalError:
    print('Tabela já existe')

TAGS = ['travel', 'nature', 'landscape', 'backpacker', 'tourist', 'mountain', 'view', 'hiking', 'trees', 'sunset']
CATEGORY = ['nature', 'backgrounds', 'people', 'places', 'travel', 'buildings']
URL = "https://pixabay.com/api/"
KEY = config('PIXA_BAY_KEY')
ORDER = ['popular', 'latest']
per_page = "100"
CAPTION = "What is your next destination? Travel smarter with @smartgeartravel and save on airline baggage fees.\n\n" \
          "Launching on #kickstarter in Q3 2018 - For more info follow link in Bio.\n\n{}"

CAPTION_TAGS = "#WhatIsYourNextDesination #smartgeartravel #onebagtravel #digitalnomad #travelphotography" \
               "#wanderlust #travelgram #instatravel #neverstopexploring #familytravel #travelcouple #worldschool" \
               "#gapyeartravel #backpacking #flashpacker #vagabond #backpacker #SaveBaggageFees"


def upload_photos():
    global per_page
    n = randint(0, len(TAGS)-1)
    i = 0
    random_tags = []
    while i < n:
        h = randint(0, n)
        if TAGS[h] not in random_tags:
            random_tags.append(TAGS[h])
            i += 1

    query_tags = "+".join(random_tags)
    query_categories = ",".join(CATEGORY)

    querystring = {"key": KEY, "q": query_tags, "image_type": "photo",
                   "category": query_categories,
                   "safesearch": "true", "per_page": per_page, "order": ORDER}
    response = requests.request("GET", URL, params=querystring)

    result = ast.literal_eval(response.text)['hits']
    return result


def download_photo():
    global per_page
    global status
    n = randint(0, int(per_page))
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
        error = False


def treat_tags(tags):
    tags_list = [x.strip() for x in CAPTION_TAGS.split('#')]
    print(len(tags_list))

    while len(tags_list) <= 30:
        for tag in tags.split(' '):
            if tag not in tags_list:
                tags_list.append(tag)
                if len(tags_list) >= 30:
                    break

        if len(tags_list) < 30:
            headers = {
                'Content-Type': 'text/html; charset=utf-8'
            }
            tags = tags.split(' ')
            n = randint(0, len(tags)-1)
            tag = tags[n]
            url = 'https://api.ritekit.com/v1/stats/hashtag-suggestions?text={}&client_id={}'.\
                format(tag, config('TAGS_ID'))
            request = requests.request("GET", url, headers=headers)

            print(request)

            result = json.loads(request.text)['data']
            print(result)

            for hashtag in result:
                external_tag = hashtag['hashtag']
                tags_list.append(external_tag)
                if len(tags_list) >= 30:
                    break
        break

    string_tags = ' #'.join(tags_list)

    return string_tags


def create_random_caption(tags):
    treated_tags = treat_tags(tags)

    caption = CAPTION.format(treated_tags)
    print(caption)
    return caption


def save_to_db(line, path, url):

    name = line["pageURL"].split('/')[-2]
    url = url
    path = path
    pixabay_id = line['id']
    created_at = datetime.datetime.now()
    status = "Not Posted"
    tags = line['tags'].replace(",", "")
    caption = create_random_caption(tags)

    image = Image.create(name=name, url=url, path=path, pixabay_id=pixabay_id,
                         created_at=created_at, status=status,
                         tags=tags, caption=caption)
    image.save()
    return image


def change_image_status(image):
    image.status = "Posted"
    image.save()


def post_on_instagram(image, login):

    # Upload Photo
    login.uploadPhoto(image.path, caption=image.caption, upload_id=None)
    print("Posted with caption {}".format(image.caption))

download_photo()
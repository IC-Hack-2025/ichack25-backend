import logging
import os
import requests
from dotenv import load_dotenv
import paths


load_dotenv(paths.ENV_PATH)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def search_google_images(search, limit=1):
    url = "https://google.serper.dev/images"
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'q': search,
        'tbm': 'isch',
        'num': limit
    }

    response = requests.post(url, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return []

    results = response.json()
    images_list = results.get('images', [])
    image_urls = [(image['title'], image['imageUrl'], image['link']) for image in images_list[:limit]]
    return image_urls


if __name__ == "__main__":
    # print(search_youtube_videos("quake 1 speedrun"))
    print(search_google_images("quake 1 gameplay"))

import vk_api
import os
import dotenv
import requests
from datetime import datetime as dt
from random import shuffle
from fake_headers import Headers


dotenv.load_dotenv()
token_vk = os.getenv("TOKEN_VK")
vk_session = vk_api.VkApi(token=token_vk)
vk = vk_session.get_api()
version_api_vk = "5.199"


def get_data_user(user_id: int) -> any:
    response = vk.users.get(
        access_token=token_vk,
        user_ids=user_id,
        v=version_api_vk,
        fields=["sex", "city", "bdate"],
    )
    info_user = response[0] if response else {}
    if info_user:
        city = info_user.get("city", {}).get("title")
        sex = info_user.get("sex")
        birthdate = info_user.get("bdate")
        if birthdate:
            date_object = dt.strptime(birthdate, "%d.%m.%Y")
            age = (
                dt.now().year
                - date_object.year
                - (
                    (dt.now().month, dt.now().day)
                    < (date_object.month, date_object.day)
                )
            )
        else:
            age = None
    else:
        return None
    return city, sex, age


def get_data_persons(
    city: str, age_from: int, age_to: int, sex: int
) -> tuple[str, str, int]:
    with vk_api.VkRequestsPool(vk) as pool:
        response = pool.method(
            "users.search",
            values={
                "hometown": city,
                "age_from": age_from,
                "age_to": age_to,
                "sex": sex,
                "count": "1000",
            },
        )
        pool.execute()
    if response.result["items"]:
        shuffle(response.result["items"])
        candidate = response.result["items"][0]
        first_name = candidate["first_name"]
        last_name = candidate["last_name"]
        user_id = candidate["id"]
        return first_name, last_name, user_id


def get_photos_person(user_id: int) -> dict:
    response = vk.photos.get(
        access_token=token_vk,
        owner_id=user_id,
        album_id="profile",
        v=version_api_vk,
        extended=1,
    )
    return response["items"]


def url_image_and_likes(list_url_image: list) -> list:
    type_picture = {
        "s": 0,
        "m": 1,
        "x": 2,
        "o": 3,
        "p": 4,
        "q": 5,
        "r": 6,
        "y": 7,
        "z": 8,
        "w": 9,
    }
    types_all = []
    for item_image in list_url_image:
        types = {}
        for image_size in item_image["sizes"]:
            types[image_size["url"]] = image_size["type"]
        largest_url = max(types.items(), key=lambda item: type_picture[item[1]])[0]
        types_all.append([largest_url, item_image["id"], item_image["likes"]["count"]])
    types_all.sort(key=lambda x: x[1], reverse=True)
    return types_all[:3]


def get_url_person(user_id: int) -> str:
    response = vk.users.get(
        access_token=token_vk, user_ids=user_id, v=version_api_vk, fields=["domain"]
    )
    return f'https://vk.com/{response[0]["domain"]}'


def check_city_exists(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=8c20632c8c75783d564abe2b90007bd7"
    response = requests.get(url, headers=Headers(browser="chrome", os="lin").generate())
    # print(response.json())
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        print(f"Произошла ошибка: {response.status_code}")

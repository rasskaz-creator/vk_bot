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


def get_data_user(user_id: int) -> tuple[str, str, int]:
    """
    Функция для получение данных о юзере.

    Параметры:
    -----------
    user_id: int
        Id пользователя в ВК

    Возвращает:
    -----------
    При откртых данных кортеж (город, пол, текущий возраст пользователя)
    Если какие то данные закрыты у пользователя возвращает None.
    """

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
    """
    функция для получения предположительного кандидата по параметрам пользователя.

    Параметры:
    -----------
    city: str
        Город в котором необходимо найти кандидатов
    sex: str
        Пол кандидата
    age_from: int
        Возраст от
    age_to: int
        Возврат до

    Возвращает
    -----------
    Кортеж (имя, фамилия, id кандидата)
    """

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
    """
    Функция для получения фотографий из профиля по id.

    Параметры:
    -----------
    user_id: int
        Id пользователя в ВК

    Возвращает
    -----------
    Словарь с данными по каждой фотографии пользователя
    """

    response = vk.photos.get(
        access_token=token_vk,
        owner_id=user_id,
        album_id="profile",
        v=version_api_vk,
        extended=1,
    )
    return response["items"]


def url_image_and_likes(list_url_image: list) -> list:
    """
    Опеределяет фотографию самого высокого качества, id фотографии и количество лайков.

    Параметры
    -----------
    list_url_image : list
        Список полученный из метода get_photos_person() по ключам словаря ['response']['items']

    Возвращает
    -----------
    Список из трех фотографий отсортированных по количеству лайков
    в формате [url фотографии, id фотографии, количество лайков].
    """

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
    types_all.sort(key=lambda x: x[2], reverse=True)
    return types_all[:3]


def get_url_person(user_id: int) -> str:
    """
    Функция для генерирования ссылки на страницу в ВК.

    Параметры:
    -----------
    user_id: int
        Id пользователя в ВК

    Возвращает:
    -----------
    Ссылку на страницу страницу в ВК.
    """
    response = vk.users.get(
        access_token=token_vk, user_ids=user_id, v=version_api_vk, fields=["domain"]
    )
    return f'https://vk.com/{response[0]["domain"]}'


def check_city_exists(city_name: str) -> bool:
    """
    Функция для проверки реального существования населенного пункта (город, поселок, деревня и т.д.).

    Параметры:
    -----------
    city_name: str
        Название предаполагаемого города
    """

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={os.getenv('TOKEN_OPENWEATHERMAP')}"
    response = requests.get(url, headers=Headers(browser="chrome", os="lin").generate())

    return response.status_code == 200

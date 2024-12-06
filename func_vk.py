import vk_api
import os
import dotenv
from datetime import  datetime
from random import shuffle




dotenv.load_dotenv()
token_vk = os.getenv('TOKEN_VK_GROUP')
version_api_vk = '5.199'
vk_session = vk_api.VkApi(token=token_vk)
vk = vk_session.get_api()


def get_data_user(user_id: int) -> any:
    response = vk.users.get(
        access_token=token_vk,
        user_ids=user_id,
        v=version_api_vk,
        fields=['sex', 'city', 'bdate']
    )
    info_user = response[0] if response else {}
    if info_user:
        city = info_user.get('city', {}).get('title')
        sex = info_user.get('sex')
        birthdate = info_user.get('bdate')
        if birthdate:
            date_object = datetime.strptime(birthdate, '%d.%m.%Y')
            age = datetime.now().year - date_object.year - ((datetime.now().month, datetime.now().day) < (date_object.month, date_object.day))
        else:
            age = None
    else:
        return None
    return city, sex, age

def get_data_persons(city: str, age_from: int, age_to: int, sex: int) -> int:
    with vk_api.VkRequestsPool(vk) as pool:
        response = pool.method('users.search', values={
            'hometown': city,
            'age_from': age_from,
            'age_to': age_to,
            'sex': sex
            }
        )
        pool.execute()
    shuffle(response.result['items'])
    return response.result['items'][0]['id']

def get_photos_person(user_id: int) -> dict:
    response = vk.photos.get(
                access_token=token_vk,
                owner_id=user_id,
                album_id='profile',
                v=version_api_vk,
                extended=1
    )
    return response['items']

def url_image_and_likes(list_url_image: list) -> list:
        type_picture = {
            's': 0,
            'm': 1,
            'x': 2,
            'o': 3,
            'p': 4,
            'q': 5,
            'r': 6,
            'y': 7,
            'z': 8,
            'w': 9
        }
        types_all = []
        for item_image in list_url_image:
            types = {}
            for image_size in item_image['sizes']:
                types[image_size['url']] = image_size['type']
            largest_url = max(types.items(), key=lambda item: type_picture[item[1]])[0]
            types_all.append(
                [largest_url,
                item_image['likes']['count']]
            )
        types_all.sort(key=lambda x: x[1], reverse=True)
        return types_all[:3]

def get_url_person(user_id: int) -> str:
    response = vk.users.get(
        access_token=token_vk,
        user_ids=user_id,
        v=version_api_vk,
        fields=['domain']
    )
    return f'https://vk.com/{response[0]['domain']}'
import vk_api
import os
import dotenv
from pprint import pprint
from datetime import  datetime



dotenv.load_dotenv()
token_vk = os.getenv('TOKEN_VK_GROUP')
version_api_vk = '5.199'
vk_session = vk_api.VkApi(token=token_vk)
vk = vk_session.get_api()


def get_data_user(user_id):
    response = vk.users.get(
        access_token=token_vk,
        user_ids=user_id,
        v=version_api_vk,
        fields=['sex', 'city', 'bdate']
    )
    id = response[0]['id']
    city = response[0]['city']['title']
    sex = response[0]['sex']
    birthdate = response[0]['bdate']
    date_object = datetime.strptime(birthdate, '%d.%m.%Y')
    age = datetime.now().year - date_object.year - ((datetime.now().month, datetime.now().day) < (date_object.month, date_object.day))
    return id, city, sex, age

def get_data_persons(city, age_from, age_to, sex):
    with vk_api.VkRequestsPool(vk) as pool:
        response = pool.method('users.search', values={
            'hometown': city,
            'age_from': age_from,
            'age_to': age_to,
            'sex': sex
            }
        )
        pool.execute()
    return response.result['items']

pprint(get_data_persons('Санкт-Петербург', 30, 30, 1))

def get_photos_person(user_id):
    response = vk.photos.get(
                access_token=token_vk,
                owner_id=user_id,
                album_id='profile',
                v=version_api_vk,
                extended=1
    )
    return response['items']

def url_image_and_likes(list_url_image: list):
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


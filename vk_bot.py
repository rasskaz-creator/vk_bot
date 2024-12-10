import os
import dotenv
import vk_api
from random import randrange
from models import Favourites
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from data_base import (
    add_or_save_param_user,
    add_favourite,
    add_blacklist,
    check_favourite_or_blacklist_db,
    session,
)
from func_vk import (
    get_data_persons,
    get_photos_person,
    url_image_and_likes,
    get_url_person,
    check_city_exists,
)


class VKBot:
    def __init__(self, token):
        self.session = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.session)
        self.vk = self.session.get_api()
        self.user_states = {}

    def write_msg(self, user_id, message, keyboard=None):
        post = {
            "user_id": user_id,
            "message": message,
            "random_id": randrange(10**7),
        }

        if keyboard:
            post["keyboard"] = keyboard.get_keyboard()

        self.session.method("messages.send", post)

    def create_keyboard_start(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Начать", VkKeyboardColor.PRIMARY)
        return keyboard

    def create_keyboard_options(self):
        keyboard = VkKeyboard()
        keyboard.add_button("В избранные", VkKeyboardColor.POSITIVE)
        keyboard.add_button("Пропустить", VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button("Избранные", VkKeyboardColor.PRIMARY)
        keyboard.add_button("Чёрный список", VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button("Сбросить", VkKeyboardColor.NEGATIVE)
        return keyboard

    def create_keyboard_reset(self):
        keyboard = VkKeyboard()
        keyboard.add_button("Сбросить", VkKeyboardColor.NEGATIVE)
        return keyboard

    def handle_user_input(self, event):
        user_id = event.user_id
        msg = event.text.lower()

        if user_id not in self.user_states:
            self.user_states[user_id] = {"state": "start", "data": {}}

        state = self.user_states[user_id]["state"]
        user_data = self.user_states[user_id]["data"]

        if msg == "сбросить":
            self.user_states[user_id] = {  # Полный сброс состояния
                "state": "start",
                "data": {},
            }
            keyboard = self.create_keyboard_start()
            self.write_msg(
                user_id, "Хорошо, начнём сначала. Нажмите 'Начать'.", keyboard
            )
            return

        if state == "start":
            self.write_msg(
                user_id,
                """
                           Привет! Для начала работы укажите город, пол и возраст кандидатов.
                           Укажите город.\n
                           """,
                self.create_keyboard_reset(),
            )
            self.user_states[user_id]["state"] = "city"

        elif state == "city":
            msg.lower()
            check_city = check_city_exists(msg)
            if check_city is True:
                self.user_states[user_id]["state"] = "sex"
                self.user_states[user_id]["data"]["city"] = msg.capitalize()
                self.write_msg(
                    user_id,
                    "Теперь укажите интересующий пол кандидата: мужской или женский",
                    self.create_keyboard_reset(),
                )
            else:
                self.write_msg(
                    user_id,
                    "Данный город не найден, введите существующий город",
                    self.create_keyboard_reset(),
                )

        elif state == "sex":
            msg.lower()
            if msg in ["мужской", "женский"]:
                self.user_states[user_id]["state"] = "age"
                self.user_states[user_id]["data"]["sex"] = 1 if msg == "женский" else 2
                self.write_msg(
                    user_id,
                    "Укажите возрастной диапазон (например, 18-25):",
                    self.create_keyboard_reset(),
                )

            else:
                self.write_msg(
                    user_id,
                    "Пожалуйста, напишите правильно пол кандидата мужской или женский",
                    self.create_keyboard_reset(),
                )

        elif state == "age":
            try:
                age_from, age_to = map(int, msg.split("-"))
                if (
                    age_from <= age_to and age_to <= 100
                ):  # Нижний порог возраста обрабатывается перехватом ошибки
                    self.user_states[user_id]["state"] = "search"
                    self.user_states[user_id]["data"]["age_from"] = age_from
                    self.user_states[user_id]["data"]["age_to"] = age_to

                    add_or_save_param_user(
                        user_id,
                        self.user_states[user_id]["data"]["city"],
                        self.user_states[user_id]["data"]["sex"],
                        self.user_states[user_id]["data"]["age_from"],
                        self.user_states[user_id]["data"]["age_to"],
                    )

                    self.write_msg(
                        user_id,
                        "Отлично! Сейчас найду подходящих кандидатов.",
                        self.create_keyboard_options(),
                    )
                    self.show_candidate(user_id)
                else:
                    self.write_msg(
                        user_id, "Возраст введен не верно", self.create_keyboard_reset()
                    )
            except ValueError:
                self.write_msg(
                    user_id,
                    "Укажите возрастной диапазон в формате 18-25",
                    self.create_keyboard_reset(),
                )

        elif state == "search":
            if msg == "в избранные":
                candidate_id = user_data.get("current_candidate")
                if candidate_id:
                    add_favourite(user_id, candidate_id)
                    self.write_msg(user_id, "Кандидат добавлен в избранное.")
                    self.show_candidate(user_id)

            elif msg == "пропустить":
                self.write_msg(user_id, "Ищу следующего кандидата...")
                self.show_candidate(user_id)

            elif msg == "избранные":
                self.show_favourites(user_id)

            elif msg == "чёрный список":
                candidate_id = user_data.get("current_candidate")
                if candidate_id:
                    add_blacklist(user_id, candidate_id)
                    self.write_msg(user_id, "Кандидат добавлен в чёрный список.")
                else:
                    self.write_msg(user_id, "Кандидат не найден.")
                self.show_candidate(user_id)

            else:
                self.write_msg(
                    user_id,
                    """Я вас не понял. Используйте кнопки для управления,
                                если их нет напишите 'пропустить' или 'сбросить'.""",
                )

    def show_candidate(self, user_id):
        user_data = self.user_states[user_id]["data"]
        candidates = get_data_persons(
            user_data["city"],
            user_data["age_from"],
            user_data["age_to"],
            user_data["sex"],
        )
        if candidates:
            candidate_id = candidates[2]
            check_candidates = check_favourite_or_blacklist_db(candidate_id)
            if check_candidates is False:
                return self.show_candidate(user_id)
            candidates_first_name = candidates[0]
            candidates_last_name = candidates[1]
            photos = get_photos_person(candidate_id)
            top_photos = url_image_and_likes(photos)
            photo_id = [photo[1] for photo in top_photos]
            photo_urls = ",".join(
                [f"photo{candidate_id}_{photo_id}" for photo_id in photo_id]
            )
            candidate_url = get_url_person(candidate_id)
            user_data["current_candidate"] = candidate_id

            self.write_msg(
                user_id,
                f"Имя: {candidates_first_name} {candidates_last_name}\n"
                f"Ссылка: {candidate_url}",
                self.create_keyboard_options(),
            )
            if photo_urls:
                self.vk.messages.send(
                    user_id=user_id, attachment=photo_urls, random_id=randrange(10**7)
                )
        else:
            self.write_msg(
                user_id, "Кандидаты не найдены. Попробуйте изменить критерии поиска."
            )

    def show_favourites(self, user_id):
        favourites = (
            session.query(Favourites).filter_by(vk_user_id=user_id, chosen=True).all()
        )
        if favourites:
            for favourite in favourites:
                candidate_url = get_url_person(favourite.favourite_id)
                self.write_msg(user_id, f"Избранный: {candidate_url}")
        else:
            self.write_msg(user_id, "У вас пока нет избранных кандидатов.")


def run_bot(bot):
    print("Бот запущен. Ожидание сообщений...")
    while True:
        try:
            for event in bot.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    bot.handle_user_input(event)
        except Exception as ex:
            print(f"Ошибка: {ex}")


if __name__ == "__main__":
    dotenv.load_dotenv()
    community_token = os.getenv("COMMUNITY_TOKEN")
    bot = VKBot(token=community_token)
    run_bot(bot)

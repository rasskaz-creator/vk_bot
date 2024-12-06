from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from models import Users, Favourites, create_tables
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

DSN = "postgresql://postgres:Mb20041995@localhost:5432/VK_Bot_team"
engine: Engine = sqlalchemy.create_engine(DSN)

try:
    create_tables(engine)  # Создаём таблицы
    Session = sessionmaker(bind=engine)
    session = Session()


except SQLAlchemyError as e:
    print(f"Ошибка базы данных: {e}")
finally:
    session.close()


Session = sessionmaker(bind=engine)
session = Session()

def add_user(vk_user_id): #создание пользователя
    user = Users(vk_user_id=vk_user_id)
    session.add(user)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении пользователя: {e}")

def add_favourite(vk_user_id, favourite_id, chosen=True): #добавление в избр-е
    favourite = Favourites(vk_user_id=vk_user_id, favourite_id=favourite_id, chosen=chosen)
    session.add(favourite)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении в избранное: {e}")

def add_blacklist(vk_user_id, favourite_id, chosen=False): # добавление в ЧС
    blacklist = Favourites(vk_user_id=vk_user_id, favourite_id=favourite_id, chosen=chosen)
    session.add(blacklist)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении в черный список: {e}")
session.close()



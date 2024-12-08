import sqlalchemy
import dotenv
import os
from sqlalchemy.orm import sessionmaker
from models import Users, Favourites, create_tables
from sqlalchemy.exc import SQLAlchemyError


dotenv.load_dotenv()
DSN = f"postgresql://postgres:{os.getenv('PASSWORD_DB')}]@localhost:5432/{os.getenv('NAME_DB')}"
engine = sqlalchemy.create_engine(DSN)


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


def check_favourite_db(favourite_id):  # Проверка человека в списке избранных
    result = (
        session.query(Favourites)
        .filter(Favourites.favourite_id == favourite_id, Favourites.chosen == True)
        .first()
    )
    if result is not None:
        return True
    else:
        return False


def check_blacklist_db(favourite_id):  # Проверка человека в черном списке
    result = (
        session.query(Favourites)
        .filter(Favourites.favourite_id == favourite_id, Favourites.chosen == False)
        .first()
    )
    if result is not None:
        return True
    else:
        return False


def add_favourite(vk_user_id, favourite_id, chosen=True):  # добавление в избр-е
    check_favourite = check_favourite_db(favourite_id)
    if check_favourite:
        return
    else:
        favourite = Favourites(
            vk_user_id=vk_user_id, favourite_id=favourite_id, chosen=chosen
        )
        session.add(favourite)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении в избранное: {e}")


def add_blacklist(vk_user_id, favourite_id, chosen=False):  # добавление в ЧС
    blacklist = Favourites(
        vk_user_id=vk_user_id, favourite_id=favourite_id, chosen=chosen
    )
    session.add(blacklist)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении в черный список: {e}")


def add_or_save_param_user(vk_user_id, city, sex, age_from, age_to):
    user = session.query(Users).filter_by(vk_user_id=vk_user_id).first()

    if user is None:
        user = Users(
            vk_user_id=vk_user_id,
            param_city=city,
            param_sex=sex,
            param_age_from=age_from,
            param_age_to=age_to,
        )
        session.add(user)
    else:
        user = (
            session.query(Users)
            .filter_by(vk_user_id=vk_user_id)
            .update(
                {
                    Users.param_city: city,
                    Users.param_sex: sex,
                    Users.param_age_from: age_from,
                    Users.param_age_to: age_to,
                }
            )
        )

    session.commit()


session.close()

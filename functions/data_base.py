import sqlalchemy
import dotenv
import os
from sqlalchemy.orm import sessionmaker
from models import Users, Favourites, create_tables
from sqlalchemy.exc import SQLAlchemyError


dotenv.load_dotenv()
DSN = f"postgresql://postgres:{os.getenv('PASSWORD_DB')}@localhost:5432/{os.getenv('NAME_DB')}"
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


def check_favourite_or_blacklist_db(favourite_id: int) -> bool:
    """
    Функция для проверки находится кандидат в избранных или в черном списке.

    Параметры:
    -----------
    favourite_id: int
        Id страницы кандидата в ВК

    Возвращает:
    -----------
    True если кандидат находится в избранных, False если в черном списке,
    None если отсутствует в обеих списках.
    """

    result = (
        session.query(Favourites.chosen)
        .filter(Favourites.favourite_id == favourite_id)
        .first()
    )
    try:
        if result.chosen:
            return True
        elif result.chosen is False:
            return False
    except AttributeError:
        return None


def add_favourite_or_blacklist(
    vk_user_id: int, favourite_id: int, chosen=None
) -> None:  # добавление в избр-е
    """
    Функция добавляет кандидата в избранные или в черный список.

    Параматеры:
    -----------
    vk_user_id: int
        Id пользователя в ВК
    favourite_id: int
        Id страницы кандидата в ВК
    chosen: bool
        Флаг кандидата True, если в избранные и False если в черный список
    """

    favourite = Favourites(
        vk_user_id=vk_user_id, favourite_id=favourite_id, chosen=chosen
    )
    session.add(favourite)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении в избранное: {e}")


def add_or_save_param_user(
    vk_user_id: int, city: str, sex: str, age_from: int, age_to: int
) -> None:
    """
    Функция добавляет или обновляет параметры поиска кандидатов.

    Параметры:
    -----------
    vk_user_id: int
        Id пользователя в ВК
    city: str
        Город в котором необходимо найти кандидатов
    sex: str
        Пол кандидата
    age_from: int
        Возраст от
    age_to: int
        Возврат до
    """

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
        user.param_city = city
        user.param_sex = sex
        user.param_age_from = age_from
        user.param_age_to = age_to

    session.commit()


session.close()

import sqlalchemy as sq
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__= 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_user_id = sq.Column(sq.Integer, unique=True, nullable=False)

class Favourites(Base):
    __tablename__= 'favourites'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_user_id = sq.Column (sq.Integer, sq.ForeignKey('users.vk_user_id'))
    favourite_id = sq.Column(sq.Integer,  unique=True)
    chosen = sq.Column(sq.Boolean, nullable=True)

def create_tables(engine):
    try:
        # Base.metadata.drop_all(engine) # Удалить все таблицы
        Base.metadata.create_all(engine)
        print("Таблицы успешно созданы")
    except SQLAlchemyError as e:
        print(f"Произошла ошибка при создании таблиц: {e}")
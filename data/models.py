import sqlalchemy as sq
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__= 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_user_id = sq.Column(sq.Integer, unique=True, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    gender = sq.Column(sq.String(length=10), nullable=False)
    city = sq.Column(sq.String(length=30), nullable=False)

class Candidates(Base):
    __tablename__ = 'candidates'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    vk_id = sq.Column(sq.Integer, unique=True, nullable=False)
    full_name = sq.Column(sq.String(length=100), nullable=False)
    link_vk = sq.Column(sq.String(length=400), nullable=False)
    photo_1 = sq.Column(sq.String(length=400), nullable=False)
    photo_2 = sq.Column(sq.String(length=400), nullable=True)
    photo_3 = sq.Column(sq.String(length=400), nullable=True)

class Favourites(Base):
    __tablename__= 'favourites'

    id = sq.Column(sq.Integer, primary_key=True)
    favourite_id = sq.Column(sq.Integer, sq.ForeignKey('candidates.id'))
    user_id = sq.Column (sq.Integer, sq.ForeignKey('users.id'))
    chosen = sq.Column(sq.Boolean, nullable=True)

def create_tables(engine):
    try:
        Base.metadata.drop_all(engine) # Удалить все таблицы
        Base.metadata.create_all(engine)
        print("Таблицы успешно созданы")
    except SQLAlchemyError as e:
        print(f"Произошла ошибка при создании таблиц: {e}")
import sqlalchemy as sq
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    vk_user_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    param_city: Mapped[str] = mapped_column(nullable=True)
    param_sex: Mapped[str] = mapped_column(nullable=True)
    param_age_from: Mapped[str] = mapped_column(nullable=True)
    param_age_to: Mapped[str] = mapped_column(nullable=True)


class Favourites(Base):
    __tablename__ = "favourites"

    id: Mapped[int] = mapped_column(primary_key=True)
    vk_user_id: Mapped[int] = mapped_column(sq.ForeignKey("users.vk_user_id"))
    favourite_id: Mapped[int] = mapped_column(unique=True)
    chosen: Mapped[bool] = mapped_column(nullable=True)


def create_tables(engine):
    try:
        # Base.metadata.drop_all(engine) # Удалить все таблицы
        Base.metadata.create_all(engine)
        print("Таблицы успешно созданы")
    except SQLAlchemyError as e:
        print(f"Произошла ошибка при создании таблиц: {e}")

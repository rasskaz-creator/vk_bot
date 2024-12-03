from sqlalchemy.orm import sessionmaker
from models import Users, Candidates, Favourites, create_tables
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

DSN = "postgresql://postgres:Mb20041995@localhost:5432/VK_Bot_team"
engine = sqlalchemy.create_engine(DSN)

try:
    create_tables(engine)  # Создаём таблицы
    Session = sessionmaker(bind=engine)
    session = Session()

    # Здесь можно выполнять операции с сессией

    # Закрытие сессии
except SQLAlchemyError as e:
    print(f"Ошибка базы данных: {e}")
finally:
    session.close()
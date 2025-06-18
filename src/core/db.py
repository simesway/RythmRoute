from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.config import DBConfig as DB


def connection_string():
  return f'postgresql+psycopg2://{DB.username}:{DB.password}@{DB.host}:{DB.port}/{DB.name}'

engine = create_engine(connection_string(), echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


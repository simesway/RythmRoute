import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base


def connection_string():
  from dotenv import load_dotenv
  load_dotenv()

  username = os.getenv("DB_USERNAME")
  password = os.getenv("DB_PASSWORD")
  host = os.getenv("DB_HOST")
  port = os.getenv("DB_PORT")
  database_name = os.getenv("DB_NAME")

  return f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_name}'

engine = create_engine(connection_string(), echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


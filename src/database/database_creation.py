from sqlalchemy import text
from src.database.models import Base
from src.core.db import engine

def create_tables():
  Base.metadata.create_all(engine)

def drop_tables():
  with engine.connect() as conn:
    conn.execute(text("DROP TABLE genre CASCADE"))
    conn.execute(text("DROP TABLE genre_genre CASCADE"))
    conn.execute(text("DROP TABLE artist CASCADE"))
    conn.execute(text("DROP TABLE artist_genre CASCADE"))
    conn.execute(text("DROP TABLE image_object CASCADE"))
    conn.commit()

def drop_types():
  with engine.connect() as conn:
    conn.execute(text("DROP TYPE relationshiptypeenum"))
    conn.commit()

def create_types():
  with engine.connect() as conn:
    rel_type = "CREATE TYPE relationship_type AS ENUM ('SUBGENRE_OF', 'INFLUENCED_BY', 'FUSION_OF');"
    conn.execute(text(rel_type))
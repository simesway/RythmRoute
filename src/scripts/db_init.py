from src.database.database_creation import create_types, create_tables


def create_all():
  create_types()
  create_tables()

if __name__ == "__main__":
  create_all()
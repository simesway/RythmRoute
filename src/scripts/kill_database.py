from src.database.database_creation import drop_tables, drop_types


def drop_all():
  drop_tables()
  drop_types()

if __name__ == '__main__':
  drop_all()
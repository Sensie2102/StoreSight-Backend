from .database import get_engine
from .db_schema import Base

def create_all_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created.")
from sqlmodel import SQLModel, create_engine, Session
from config import SQLITE_URL, DEBUG

connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_URL, echo=DEBUG, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

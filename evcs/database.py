from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from evcs.settings import Settings

engine = create_engine(Settings().DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    database = SessionLocal()
    # with Session(engine) as session:
    #     yield session
    try:
        yield database
    finally:
        database.close()

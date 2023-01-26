from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db import Database, DeclarativeBase


engine = create_engine(environ["DB_URL"])

Session = sessionmaker(bind=engine)
db = Database(Session)
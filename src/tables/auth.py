from sqlalchemy import Column, Integer, String

from src.db import DeclarativeBase


class UserAuth(DeclarativeBase):
    __tablename__ = "users_auth"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    hashed_password = Column(String)
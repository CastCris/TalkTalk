from sqlalchemy import Column, String, Integer
from .base import Base

USER_NAME_LEN = 80
USER_EMAIL_LEN = 240
USER_PASSWORD_LEN = 50
USER_STATUS_LEN = 20

class User(Base):
    __tablename__ = 'User'

    name = Column(String(USER_NAME_LEN), primary_key = True)
    email = Column(String(USER_EMAIL_LEN))
    password = Column(String(USER_PASSWORD_LEN))
    status = Column(String(USER_STATUS_LEN))

    connections = Column(Integer)

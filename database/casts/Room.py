from sqlalchemy import Column, String, ForeignKey
from .base import Base
from .User import User

ROOM_NAME_LEN = 100

class Room(Base):
    __tablename__ = 'Room'

    name = Column(String(ROOM_NAME_LEN), primary_key=True)
    user_admin = Column(String(USER_NAME_LEN), ForeignKey('User.name'))

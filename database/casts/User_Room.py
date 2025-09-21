from sqlalchemy import Column, String, ForeignKey, Integer
from .base import Base

from .User import USER_NAME_LEN
from .Room import ROOM_NAME_LEN

##
class User_Room(Base):
    __tablename__ = 'User_Room'

    room_name = Column(String(ROOM_NAME_LEN), ForeignKey('Room.name'), primary_key=True)
    user_name = Column(String(USER_NAME_LEN), ForeignKey('User.name'), primary_key=True)

    connections = Column(Integer)


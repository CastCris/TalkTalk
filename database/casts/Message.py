from sqlalchemy import Column, String, Integer, Float, CHAR, ForeignKey
from .base import Base
from .User import User
from .Room import Room

MESSAGE_ID_LEN = 20
MESSAGE_CONTENT_LEN = 2000

class Message(Base):
    __tablename__ = 'Message'

    id = Column(CHAR(MESSAGE_ID_LEN))
    date = Column(Float)

    user_name = Column(String(USER_NAME_LEN), ForeignKey('User.name'))
    room_name = Column(String(ROOM_NAME_LEN), ForeignKey('Room.name'))

    content = Column(String(MESSAGE_CONTENT_LEN))

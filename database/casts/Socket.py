from sqlalchemy import Column, String, ForeignKey
from .base import Base

from .Room import ROOM_NAME_LEN

##
SOCKET_ID_LENGTH = 10

class Socket(Base):
    __tablename__ = "Socket"

    id = Column(String(SOCKET_ID_LENGTH), primary_key=True)

    room = Column(String(ROOM_NAME_LEN))
    highlight = Column(String(100))

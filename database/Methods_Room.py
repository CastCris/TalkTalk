from .xtensions import *

from .session import session
from .casts import Room

##
def room_get()->list:
    room_able = [ room_name[0] for room_name in session.query(Room.name).all()]

    return room_able

def room_insert(room_name: str, user_name: str)->None:
    room_new = Room(name=room_name, user_admin=user_name)
    session.add(room_new)
    session.commit()



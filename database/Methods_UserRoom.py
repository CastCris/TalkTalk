from .xtensions import *

from .session import session
from .casts import User_Room

##
def userRoom_get(user_name:str, room_name:str)->object:
    userRoom_instance = session.query(User_Room) \
            .filter(User_Room.room_name==room_name, User_Room.user_name==user_name) \
            .first()

    return userRoom_instance

def userRoom_insert(user_name:str, room_name:str)->None:
    userRoom_new = User_Room(user_name=user_name, room_name=room_name, connections=0)
    session.add(userRoom_new)

    session.commit()

def userRoom_delete(user_name:str, room_name)->None:
    userRoom = userRoom_get(user_name, room_name)

    session.delete(userRoom)
    session.commit()


def userRoom_connections_get(user_name:str, room_name:str)->int:
    userRoom = userRoom_get(user_name, room_name)
    if not userRoom:
        return 0

    return userRoom.connections

def userRoom_connections_add(user_name:str, room_name:str)->None:
    userRoom = userRoom_get(user_name, room_name)

    try:
        userRoom.connections += 1
    except Exception as e:
        print('userRoom_connections_add ERROR', e)
        session.rollback()

        return

    session.commit()

def userRoom_connections_minus(user_name:str, room_name:str)->None:
    userRoom = userRoom_get(user_name, room_name)

    try:
        userRoom.connections -= 1
    except Exception as e:
        print('userRoom_connections_minus ERROR', e)
        session.rollback()
        
        return

    session.commit()


def userRoom_user_online_get(room_name:str)->list:
    userRoom_instances = session.query(User_Room.user_name) \
            .filter(User_Room.room_name==room_name) \
            .all()

    result = [ i[0] for i in userRoom_instances ]
    return result

def userRoom_user_connections_get(user_name:str)->int:
    userRoom_instances = session.query(User_Room.connections) \
            .filter(User_Room.user_name==user_name) \
            .all()

    result = [ i[0] for i in userRoom_instances ]
    return sum(result)


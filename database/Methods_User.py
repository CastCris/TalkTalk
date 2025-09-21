from .xtensions import *

from .session import session
from .casts import User

##
def user_get(user_name:str)->object:
    try:
        user = session.query(User).filter(User.name == user_name).first()
    except:
        session.rollback()
        return None

    return user

def user_insert(name:str, email:str, status:str, password: str, room_home:str)->None:
    user_new = User(name=name, email=email, status=status, password=password, room_home=room_home)

    session.add(user_new)
    session.commit()

def user_status_update(user_name:str, status_new:str)->None:
    user = user_get(user_name)
    if not user:
        return

    user.status = status_new

    session.commit()

def user_room_home_get(user_name:str)->str:
    user = user_get(user_name)
    if not user:
        return ''

    return user.room_home


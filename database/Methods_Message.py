from .xtensions import *

from .session import session
from .casts import Message

import time

##
def message_insert(message_id:str, content:str, user_name:str, room_name:str)->None:
    message_new = Message(id=message_id, date=time.time(), user_name=user_name, room_name=room_name, content=content)
    session.add(message_new)

    session.commit()

def message_fetch_newest(date_offset:int, room_name:str, limit:int)->set:
    messages = session.query(Message.content, Message.date, Message.user_name) \
            .filter(Message.date > date_offset, Message.room_name == room_name) \
            .order_by(sqlalchemy.desc(Message.date)) \
            .limit(limit) \
            .all()

    messages_list = [
        {'message_content': str(message[0]),
         'message_offset': float(message[1]),
         'message_user_name': str(message[2])
        }
        for message in messages
    ]

    # print('message_list: ', messages_list)

    return messages_list

def message_fetch_oldest(date_offset:int, room_name:str, limit:int)->set:
    messages = session.query(Message.content, Message.date, Message.user_name) \
            .filter(Message.date < date_offset, Message.room_name == room_name) \
            .order_by(sqlalchemy.desc(Message.date)) \
            .limit(limit) \
            .all()

    messages_list = [
        {'message_content': str(message[0]),
         'message_offset': float(message[1]),
         'message_user_name': str(message[2])
        }
        for message in messages
    ]

    # print('message_list: ', messages_list)

    return messages_list

def message_date_get(message_id:str)->float:
    message_offset = session.query(Message.date).filter(Message.id == message_id).first()[0]

    return message_offset


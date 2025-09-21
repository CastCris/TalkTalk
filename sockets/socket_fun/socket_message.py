from begin import *
from database import *

import sqlalchemy

##
def message_server_id()->str:
    global SYSTEM_MESSAGE_OFFSET_COUNT 
    global SYSTEM_MESSAGE_OFFSET

    SYSTEM_MESSAGE_OFFSET_COUNT += 1

    return SYSTEM_MESSAGE_OFFSET+str(SYSTEM_MESSAGE_OFFSET_COUNT)


def message_insert_system(message_content:str, room_name:str)->None:
    message_id = message_server_id()
    message_insert(message_id, message_content, SUPER_ADMIN, room_name)


def message_send_user(message_content:str, message_offset:str, user_name:str)->None:
    flask_socketio.emit(
            'message',
            {
                'message_content': message_content,
                'message_offset': message_offset,

                'message_user_name': user_name
            }
    )

def message_send_room(message_content:str, message_offset:list, user_name:str, room_name:str)->None:
    flask_socketio.emit(
            'message',
            {
                'message_content': message_content,
                'message_offset': message_offset,

                'message_user_name': user_name
            },
            to = room_name
    )

def message_send_system(message_content:str, room_name:str)->None:
    message_id = message_server_id()
    try:
        message_insert(message_id, message_content, SUPER_ADMIN, room_name)
    except sqlalchemy.exc.IntegrityError:
        flask_socketio.emit('user_invalid')
        print('Message send system ERROR: ', e)
        return
    except Exception as e:
        print('Message send system ERROR: ', e)

    message_date = message_date_get(message_id)

    message_send_room(message_content, message_date, SUPER_ADMIN, room_name)

##
def message_handler(data)->None:
    message_content = data["message_content"]
    message_id = data["message_id"]

    print('message: ',data)

    room_name = data["room"]
    user_name = flask.request.cookies["user_name"]

    try:
        message_insert(message_id, message_content, user_name, room_name) 
    except sqlalchemy.exc.IntegrityError as e:
        flask_socketio.emit('user_invalid')
        print('Handler_message Error: ', e)

        return
    except Exception as e:
        message_content = "Error in message loading"
        session.rollback()

        print('Handler_mesaage Error: ', e)

        return

    message_date = message_date_get(message_id)
    print('message_date: ', message_date)
    #

    message_send_room(message_content, message_date, user_name, room_name)

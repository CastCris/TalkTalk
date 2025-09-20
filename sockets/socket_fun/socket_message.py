from begin import *
from database import *

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

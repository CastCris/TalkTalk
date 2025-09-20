from begin import *
from database import *

import zlib
import json

###
def data_recovery_message(room_name:str, message_offset:float, message_recovery_method:object)->None:
    message_needed = None

    try:
        message_needed = message_recovery_method(message_offset, room_name, MESSAGE_SCROLLOFF)
    except Exception as e:
        message_needed = [{
            "message_content": "An error occurs while recovery messages...",
            "user_name": SUPER_ADMIN,
            "message_offset": time.time()
        }]
        session.rollback();

        print('Error in message recovery:', e)

    message_needed_str = json.dumps(message_needed)
    message_needed_zip = zlib.compress(message_needed_str.encode('utf-8'))

    print('message_needed: ', message_needed)
    flask_socketio.emit('message_recovery',{
        "messages": message_needed_zip,
        "scroll_off": len(message_needed)
    })

def data_recovery_room()->None:
    romms_needed = None

    try:
        rooms_needed = room_get()
    except Exception as e:
        rooms_needed = ["Error"]
        session.rollback();

        print('Error room recovery: ', e)

    flask_socketio.emit('room_recovery', {'rooms': rooms_needed})

##
def data_recovery(room_name:str, message_offset:float, message_recovery_method:object)->None:
    data_recovery_message(room_name, message_offset, message_recovery_method)
    data_recovery_room()

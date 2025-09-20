from begin import *
from database import *

from .socket_room import room_leave
from .socket_message import message_send_system

def disconnect()->None:
    print('socket_data: ', socket_data)

    socket_id = flask.request.sid
    server_room = socket_data[socket_id]["room"]

    #
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies.get("user_name", None)
    user_connections = userRoom_user_connections_get(user_name)

    if not user_name:
        flask_socketio.emit('user_invalid')
        return

    room_leave({
        "room": server_room
    })

    message_index = f"User disconnect: { user_name }, { user_ip }"
    if user_connections > 1:
        message_index = f"User disconnect device: { user_name }, { user_ip }"

    message_send_system(message_index, ROOM_INITIAL)
    message_room = f"User { user_name } leave the room"
    # print('disconnect message index: ', message_index)


    if user_connections == 1:
        user_status_update(user_name, STATUS_OFFLINE)

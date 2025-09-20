from begin import *
from database import *

from .socket_room import room_join
from .socket_message import message_send_system

##
def connect_room(auth:object)->None:
    socket_id = flask.request.sid
    message_offset = auth.get('messageNewOffset') if auth else 0
    server_room = auth.get('serverRoom') if auth else 'index'

    ###
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies.get("user_name", None);
    user_connections = userRoom_user_connections_get(user_name)

    user_status_update(user_name, STATUS_ONLINE)

    print('user_get: ', user_get(user_name))

    if not user_name or not user_get(user_name):
        flask_socketio.emit('user_invalid')
        return

    print('user_name: ', user_name)
    print('user_connections: ', user_connections)

    ###
    if not socket_id in socket_data:
        socket_data[socket_id] = {}

    room_able = []
    try:
        room_able = room_get()
    except sqlalchemy.exc.OperationalError as e:
        flask_socektio.emit('user_invalid')
        print('Connect Error: ', e)

        return

    if not server_room in room_able:
        server_room = user_room_home_get(user_name)
        server_room = server_room if server_room in room_able else ROOM_INITIAL

        flask_socketio.emit('room_change',{
            "room": server_room
        })

    ###
    message_index = f"User connection: { user_name }, { user_ip }"
    if user_connections:
        message_index = f"User connection device: { user_name }, { user_ip }"
    
    message_room = f"User { user_name } join to room"

    message_send_system(message_index, ROOM_INITIAL)

    ###
    room_join({
        "room": server_room,
        "message_offset": message_offset
    })

    ###
    flask_socketio.emit('server_status_highlight', {
        "highlight": SERVER_STATUS_HIGHLIGHTS
    })

def connect_room_manager()->None:
    pass

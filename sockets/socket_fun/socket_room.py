from begin import *
from database import *

from .socket_message import message_send_system
from .socket_recovery import *

##
def room_join(data)->None:
    room_name = data["room"]
    if not room_name:
        return

    user_name = flask.request.cookies["user_name"]
    user_connections = userRoom_connections_get(user_name, room_name)

    if not user_connections:
        userRoom_insert(user_name, room_name)
    userRoom_connections_add(user_name, room_name)

    #
    message_content = f"User { user_name } joined to this room" # +room_name
    message_send_system(message_content, room_name)

    socket_id = flask.request.sid
    socket_data[socket_id]["room"] = room_name

    flask_socketio.join_room(room_name)

    #
    flask_socketio.emit('output_clean')
    flask_socketio.emit('output_room_clean');

    #
    message_offset = 0
    data_recovery(room_name, message_offset, message_fetch_newest)

    flask_socketio.emit('room_joined', {
        "room": room_name
    })

def room_leave(data)->None:
    room_name = data["room"]
    if not room_name:
        return

    user_name = flask.request.cookies["user_name"]
    user_connections = userRoom_connections_get(user_name, room_name)

    userRoom_connections_minus(user_name, room_name)
    if user_connections == 1:
        userRoom_delete(user_name, room_name)

    message_content = f"User { user_name } get out of this room" # +room_name
    message_send_system(message_content, room_name)

    flask_socketio.emit('room_leaved', {
        "room": room_name
    })

    flask_socketio.leave_room(room_name)

def room_change(data)->None:
    room_name_old = data["room_name_old"]
    room_name_new = data["room_name_new"]

    print('room_name_old: ', room_name_old)
    print('room_name_new: ', room_name_new)

    room_leave({
        "room": room_name_old
    })

    room_join({
        "room": room_name_new
    })


def room_recovery(rooms:list)->None:
    rooms_copy = rooms.copy()
    rooms_copy.sort()
    flask_socketio.emit('room_recovery', rooms_copy)


def room_create(data)->None:
    room_name = data["room_name"]
    room_able = room_get()

    print('room_able: ', room_able)
    room_able.append(room_name)
    room_able.sort()

    flask_socketio.emit(
        'room_create',
        {
            "room_able": room_able
        },
        broadcast = True
    )

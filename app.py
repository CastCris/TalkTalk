import flask
import flask_socketio

import sqlalchemy

import string
import secrets

from database import *
from routers import *

import time
import datetime

import zlib
import json

###
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.register_blueprint(main_routers)

socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
socket_data = {}


ROOM_INITIAL = 'index'

SYSTEM_MESSAGE_OFFSET = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
SYSTEM_MESSAGE_OFFSET_COUNT  = 0

SUPER_ADMIN = 'super_admin'

MESSAGE_SCROLLOFF = 250

try:
    user_insert(SUPER_ADMIN, 'thisemaildoesntexists@email', STATUS_DIE, '')
    room_insert(ROOM_INITIAL, SUPER_ADMIN)
except Exception as e:
    session.rollback()
    print('Setup server error: ',e)

###
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

def message_data_recovery(room_name:str, message_offset:float, message_recovery_method:object)->None:
    message_needed = None

    try:
        message_needed = message_recovery_method(message_offset, room_name, MESSAGE_SCROLLOFF)
    except Exception and e:
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

def room_data_recovery()->None:
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
    message_data_recovery(room_name, message_offset, message_recovery_method)
    room_data_recovery()


###
def connect_room(auth:object)->None:
    socket_id = flask.request.sid
    message_offset = auth.get('messageNewOffset') if auth else 0
    server_room = auth.get('serverRoom') if auth else 'index'

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
        server_room = ROOM_INITIAL

        flask_socketio.emit('room_change',{
            "room": server_room
        })

    ###
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies.get("user_name", None);
    user_connections = user_connections_get(user_name)

    print('user_get: ', user_get(user_name))

    if not user_name or not user_get(user_name):
        flask_socketio.emit('user_invalid')
        return

    print('user_name: ', user_name)

    user_connections_add(user_name)
    user_status_update(user_name, STATUS_ONLINE)

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

def connect_room_manager()->None:
    pass


@socketio.on('connect')
def handler_connect(auth:object)->None:
    connection_type = auth.get("typeConnection", "null")

    if connection_type == "room":
        connect_room(auth)


@socketio.on('disconnect')
def handler_disconnect()->None:
    socket_id = flask.request.sid
    server_room = socket_data[socket_id]["room"]

    #
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies.get("user_name", None)

    if not user_name:
        flask_socketio.emit('user_invalid')
        return

    user_connections = user_connections_get(user_name)
    user_connections_minus(user_name)

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

###
def room_join(data)->None:
    room_name = data["room"]
    user_name = flask.request.cookies["user_name"]

    message_offset = 0

    socket_id = flask.request.sid
    if not room_name:
        return

    message_content = f"User { user_name } joined to this room" # +room_name
    message_send_system(message_content, room_name)

    socket_data[socket_id]["room"] = room_name

    flask_socketio.join_room(room_name)

    #
    flask_socketio.emit('output_clean')
    flask_socketio.emit('output_room_clean');

    #
    data_recovery(room_name, message_offset, message_fetch_newest)

    flask_socketio.emit('room_joined', {
        "room": room_name
    })


def room_leave(data)->None:
    room_name = data["room"]
    user_name = flask.request.cookies["user_name"]
    if not room_name:
        return

    message_content = f"User { user_name } get out of this room" # +room_name
    message_send_system(message_content, room_name)

    flask_socketio.emit('room_leaved', {
        "room": room_name
    })

    flask_socketio.leave_room(room_name)

def room_recovery(rooms:list)->None:
    rooms_copy = rooms.copy()
    rooms_copy.sort()
    flask_socketio.emit('room_recovery', rooms_copy)


@socketio.on('room_change')
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


@socketio.on('room_create')
def room_create_handler(data)->None:
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


##
@socketio.on('message')
def handler_message(data)->None:
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

@socketio.on('message_load')
def handler_message_load(auth)->None:
    message_old_offset = auth.get('messageOldOffset', 0)
    server_room = auth.get('serverRoom', 'index')

    message_data_recovery(server_room, message_old_offset, message_fetch_oldest)


if __name__=='__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

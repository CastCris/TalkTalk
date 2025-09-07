import os
import flask
import flask_socketio

import string
import secrets

from database import *
from routers import *

SECRET_KEY_LEN = 26

###
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(SECRET_KEY_LEN)
app.register_blueprint(main_routers)

socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


ROOM_INITIAL = 'index'
ROOM_INITIAL_CLIENT_OFFSET = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
ROOM_INITIAL_COUNTER = 0

MESSAGE_MAX = 500
MESSAGE_SCROLLOFF = 25

SUPER_ADMIN = 'super_admin'

try:
    user_insert(SUPER_ADMIN, 'thisemaildoesntexists@email', STATUS_DIE, '')
    room_insert(ROOM_INITIAL, SUPER_ADMIN)
except Exception as e:
    session.rollback()
    print('Setup server error: ',e)


###
def message_send_room(message_content:str, message_offset:list, user_name:str, room_name:str)->None:
    flask_socketio.emit(
            'message',
            {
                'message_content': message_content,
                'message_offset': message_offset,

                'user_name': user_name
            },
            to = room_name
    )

def message_send(message_content, message_offset, user_name)->None:
    flask_socketio.emit(
            'message',
            {
                'message_content': message_content,
                'message_offset': message_offset,

                'user_name': user_name
            }
    )

##
def data_recovery(room_name:str, message_offset:str)->None:
    rooms_needed = None
    message_needed = None
    
    # rooms_needed = room_get()
    # message_needed  = message_fetch(message_offset, room_name)
    try:
        rooms_needed = room_get()
        message_needed  = message_fetch(message_offset, room_name)
    except Exception as e:
        message_needed = [("Error in message recovery", 0, SUPER_ADMIN)]
        rooms_needed = ["Error in rooms recovery"]
        session.rollback()

        print('Data_recovery ERROR: \n', e)
        return

    print('message_needed: ', message_needed)
    print('rooms_needed: ', rooms_needed)
    for i in message_needed:
        message_content = i[0]
        message_offset = i[1]
        message_user = i[2]

        print(i)

        message_send(message_content, message_offset, message_user)

    flask_socketio.emit('room_recovery', {'rooms': rooms_needed})

@socketio.on('connect')
def handler_connect(auth)->None:
    global ROOM_INITIAL
    global ROOM_INITIAL_COUNTER

    message_offset = auth.get('messageOffset') if auth else 0
    server_room = auth.get('serverRoom') if auth else 'index'

    ###
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies["user_name"];
    user_connections = user_connections_get(user_name)

    user_connections_add(user_name)
    user_status_update(user_name, STATUS_ONLINE)

    ###
    message = f"User connection: { user_name }, { user_ip }"
    if user_connections:
        message = f"User connection device: { user_name }, { user_ip }"

    handler_message({
        'message_content' : message,
        'message_id' : ROOM_INITIAL_CLIENT_OFFSET+str(ROOM_INITIAL_COUNTER),
        'user_name' : SUPER_ADMIN,

        'room' : ROOM_INITIAL
    })

    ROOM_INITIAL_COUNTER += 1

    flask_socketio.join_room(server_room)

    data_recovery(server_room, message_offset)

@socketio.on('disconnect')
def handler_disconnect()->None:
    global ROOM_INITIAL_CLIENT_OFFSET
    global ROOM_INITIAL_COUNTER

    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies["user_name"]
    user_connections = user_connections_get(user_name)

    user_connections_minus(user_name)

    message = f"User disconnect: { user_name }, { user_ip }"
    if user_connections > 1:
        message = f"User disconnect device: { user_name }, { user_ip }"

    handler_message({
        'message_content' : message,
        'message_id': ROOM_INITIAL_CLIENT_OFFSET+str(ROOM_INITIAL_COUNTER),
        'user_name': SUPER_ADMIN,

        'room' : ROOM_INITIAL
    })

    user_status_update(user_name, STATUS_OFFLINE)

    ROOM_INITIAL_COUNTER += 1

@socketio.on('room_join')
def room_join(data)->None:
    room_name = data["room"]
    if not room_name:
        return

    flask_socketio.join_room(room_name)
    flask_socketio.emit(
            'room_joined',
            {"room_name": room_name}
    )

@socketio.on('room_recovery')
def room_recovery(rooms:list)->None:
    rooms_copy = rooms.copy()
    rooms_copy.sort()
    flask_socketio.emit('room_recovery', rooms_copy)

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
            "room_able": room_able,
        },
        broadcast = True
    )

@socketio.on('room_change')
def room_change(data)->None:
    room_name_old = data["room_name_old"]
    room_name_new = data["room_name_new"]

    flask_socketio.leave_room(room_name_old)
    flask_socketio.join_room(room_name_new)

    data_recovery(room_name_new, 0)


@socketio.on('message')
def handler_message(data)->None:
    message_content = data["message_content"]
    message_id = data["message_id"]

    print('message: ',data)

    room_name = data["room"]
    user_name = flask.request.cookies["user_name"]

    try:
        message_insert(message_id, message_content, user_name, room_name) 
    except Exception as e:
        message_content = "Error in message loading"
        print('Message error: ', e)
        return

    message_date = session.query(Message.date).filter(Message.id == message_id).first()[0]
    print('message_date: ', message_date)
    #

    message_send_room(message_content, message_date, user_name, room_name)


if __name__=='__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

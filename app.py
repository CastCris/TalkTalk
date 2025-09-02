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

# user
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        name VARCHAR(80) PRIMARY KEY,
        email VARCHAR(254),
        status VARCHAR(50),
        password VARCHAR(50),

        connections INTEGER
    );
""")

try:
    cursor.execute("""
    INSERT INTO user VALUES('super_admin', 'thisemaildoesntexist@email.com', 'die', '')
    """)
except:
    print('An error occurs in super_admin creation')

# room
cursor.execute("""
    CREATE TABLE IF NOT EXISTS room (
        name VARCHAR(100) PRIMARY KEY,
        user_admin VARCHAR(80),

        CONSTRAINT FK_user_admin
            FOREIGN KEY(user_admin) REFERENCES user(name)
    );
"""
)

try:
    cursor.execute("""
    INSERT INTO room VALUES('index', 'super_admin')
    """)
except:
    print('An error occurs in index room creation')

# message
cursor.execute("""
    CREATE TABLE IF NOT EXISTS message(
        id CHAR(20) PRIMARY KEY,
        data REAL,

        user_name VARCHAR(80),
        room_name VARCHAR(80),

        content VARCHAR,

        CONSTRAINT FK_room_name
            FOREIGN KEY(room_name) REFERENCES room(name)
    );
""")

db.commit()


###
def room_fetch()->set:
    rooms = cursor.execute("""
    SELECT name FROM room
    """)

    rooms = rooms.fetchall()

    return rooms

def message_fetch(date_offset:int, room_name:str)->set:
    messages = cursor.execute(f"""
    SELECT content, data, user_name FROM message WHERE data > { date_offset } AND room_name = '{ room_name }'
    """)

    messages = messages.fetchall()

    return messages

def message_send_room(message_content:str, message_offset:str, user_name:str, room_name:str)->None:
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
    
    # rooms_needed = room_fetch()
    # message_needed  = message_fetch(message_offset, room_name)
    try:
        rooms_needed = room_fetch()
        message_needed  = message_fetch(message_offset, room_name)
    except:
        messqage_needed = [("Error in message recovery", 0, "system")]
        rooms_needed = ["Error in rooms recovery"]
        return

    print(message_needed,'inteligencia visionaria')
    for i in message_needed:
        message_content = i[0]
        message_offset = i[1]
        message_user = i[2]


        # print(i)

        message_send(message_content, message_offset, message_user)

    flask_socketio.emit('room_recovery', {'rooms': rooms_needed})

@socketio.on('connect')
def handler_connect()->None:
    global ROOM_INITIAL
    global ROOM_INITIAL_COUNTER

    socket = flask.request.namespace
    message_offset = flask.request.args.get('messageOffset', default=0, type=int)
    server_room = flask.request.args.get('serverRoom', default='index', type=str)

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
        'user_name' : 'system',

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
        'user_name': 'system',

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

@socketio.on('room_change')
def room_change(data)->None:
    room_name = data["room_name"]
    room_join({"room": room_name})

    data_recovery(room_name, 0)


@socketio.on('message')
def handler_message(data)->None:
    # print(data)
    message_content = data["message_content"]
    message_id = data["message_id"]

    room_name = data["room"]
    user_name = flask.request.cookies["user_name"]
    if 'user_name' in data:
        user_name = data['user_name']

    try:
        message_insert(message_id, message_content, user_name, room_name) 
    except:
        message_content = "Error in message loading"
        print('ERROR')

    message_date = cursor.execute(f"SELECT data FROM message WHERE id = '{ message_id }'")
    message_date = message_date.fetchall()
    #

    print(user_name)
    message_send_room(message_content, message_date, user_name, room_name)


if __name__=='__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

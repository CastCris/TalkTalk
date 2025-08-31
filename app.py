import os
import flask
import flask_socketio

from database import *

SECRET_KEY_LEN = 26

###
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(SECRET_KEY_LEN)

socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


ROOM_INITIAL = 'index'

STATUS_DIE = 'die'
STATUS_ONLINE = 'online'
STATUS_OFFLINE = 'offline'

MESSAGE_MAX = 500
MESSAGE_SCROLLOFF = 25

# user
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        name VARCHAR(80) PRIMARY KEY,
        email VARCHAR(254),
        status VARCHAR(50),
        password VARCHAR(50)
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_offset CHAR(20) UNIQUE,

        room_name VARCHAR(80),
        content VARCHAR,

        CONSTRAINT FK_room_name
            FOREIGN KEY(room_name) REFERENCES room(name)
    );
""")

db.commit()

###
@app.before_request
def before_request()->None:
    if "user_name" in flask.request.cookies:
        flask.session["user_name"] = flask.request.cookies["user_name"]

###
@app.route('/')
def index()->object:
    print(flask.session)
    if not "user_name" in flask.session or not flask.session["user_name"]:
        return flask.redirect('/sign/display')
    return flask.render_template('index.html')


@app.route('/login/display')
def login_display()->object:
    return flask.render_template('login.html')

@app.route('/login/auth', methods=['POST'])
def login_auth()->object:
    if flask.request.method != 'POST':
        return

    user_name = flask.request.form['user_name']
    user_email = flask.request.form['user_email']
    user_password = flask.request.form['user_password']

    result = user_insert(user_name, user_email, user_password)
    try:
        result = user_insert(user_name, user_email, user_password)
    except sqlite3.OperationalError:
        flask.session["message"]="An error occurs..."
        return flask.redirect(flask.url_for('login_display'))

    if result == 1:
        flask.session["message"]="Unavailable user name"
        return flask.redirect(flask.url_for('login_display'))


    flask.session['message'] = ''
    flask.session['user_name'] = user_name

    response = flask.make_reponse(flask.redirect('/'))
    response.set_cookie('user_name', user_name)

    return response


@app.route('/sign/display')
def sign_display()->object:
    return flask.render_template('sign.html')

@app.route('/sign/auth', methods=['POST'])
def sign_auth()->object:
    if flask.request.method != 'POST':
        return

    user_name = flask.request.form['user_name']
    user_password = flask.request.form['user_password']

    result = cursor.execute(f"SELECT name, password, status FROM user WHERE name = '{ user_name }'")
    # print(result,'-')
    rows = result.fetchone()

    if not rows:
        flask.session['message'] = "Unavaible user name"
        return flask.redirect(flask.url_for('sign_display'))

    if rows[2]==STATUS_DIE:
        flask.session['message'] = "This user is unactive"
        return flask.redirect(flask.url_for('sign_display'))

    print(rows)
    if rows[1] != user_password:
        flask.session['message'] = "Incorrect password"
        return flask.redirect(flask.url_for('sign_display'))

    flask.session['message'] = ''
    flask.session["user_name"] = user_name

    response = flask.make_response(flask.redirect('/'))
    response.set_cookie('user_name', user_name)

    return response


@app.route('/logout')
def logout()->object:
    response = flask.make_response(flask.redirect('/'))
    response.set_cookie('user_name', '', expires=0)
    flask.session["user_name"] = None

    return response


@app.route('/room_manager/create')
def room_create()->object:
    return flask.render_template('room_create.html')

@app.route('/room_manager/create/auth', methods = ['POST'])
def room_create_auth()->object:
    if flask.request.method != 'POST':
        return

    room_name = flask.request.form['room_name']

    result = 0
    try:
        result = insert_room(room_name)
    except:
        flask.session["message"]="An error occurs..."
        return flask.redirect(flask.url_for('room_create'))

    if result == 1:
        flask.session["message"]="Room name already exists"
        return flask.redirect(flask.url_for('room_create'))

    flask.session["message"]=''

    # socketio.send(

    return flask.redirect(flask.url_for('index'))

##
@app.route('/load_home_page')
def home_page()->None:
    return flask.redirect("/")

###
def room_fetch()->set:
    rooms = cursor.select("""
    SELECT name FROM room
    """)

    rooms = rooms.fetchall()
    if not rooms:
        return None

    return rooms

def message_fetch(offset, room_name)->set:
    messages = cursor.select(f"""
    SELECT content, id FROM message WHERE id > { offset } AND room = '{ room_name }'
    """)

    messages = messages.fetchall()
    if not messages:
        return None

    return messages


@socketio.on('connect')
def connect()->None:
    global ROOM_INITIAL

    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies["user_name"];

    flask_socketio.join_room(ROOM_INITIAL)

    if ROOM_INITIAL in flask.request.cookies:
        ROOM_INITIAL = flask.request.cookies["room_index"]

    flask_socketio.emit(
            'message',
            f"User connection: { user_name }, { user_ip }",
            broadcast = True
    )

@socketio.on('disconnect')
def disconnect()->None:
    user_ip = flask.request.remote_addr;
    user_name = flask.request.cookies["user_name"]

    flask_socketio.emit(
            'message',
            f"User disconnect: { user_name }, { user_ip }",
            to = ROOM_INITIAL
    )


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

@socketio.on('message')
def handler_message(data)->None:
    message = data["message"]
    room_name = data["room"]

    flask_socketio.emit(
            'message',
            {"message": message},
            to = room_name
    )


if __name__=='__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

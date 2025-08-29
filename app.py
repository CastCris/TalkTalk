import flask
import flask_socketio

from database import *

cursor.execute("""
    CREATE TABLE IF NOT EXISTS room (
        name VARCHAR(100) PRIMARY KEY AUTOINCREMENT,
        user_admin VARCHAR(80)
    );
"""
)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        name VARCHAR(80) PRIMARY KEY,
        email VARCHAR(254),
        password VARCHAR(200)
    );
""")

INITIAL_ROOM = 0
ROOMS_ABLE = set()

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = '234567890-='
socketio = flask_socketio.SocketIO(app)

user = None


###
@app.route('/')
def index()->object:
    user = flask.request.cookies.get('user_name')
    if not user:
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('index.html')

@app.route('/login')
def login()->object:
    return flask.render_template('login.html')

@app.route('/login_auth', methods=['POST'])
def login_auth()->object:
    if flask.request.method != 'POST':
        return

    user_name = flask.request.form['user_name']
    user_email = flask.request.form['user_email']
    user_password = flask.request.form['user_password']

    try:
        create_user(user_name, user_email, user_password)
    except sqlite3.OperationalError:
        flask.g.message = 'User name invalid'
        return flask.redirect(flask.url_for('login'))

    flask.g.message=''

    response = make_response(flask.redirect(flask.url_for('index')))
    response.set_cooekie('user_name')
    return response


@app.route('/sign')
def sign()->object:
    return flask.render_template('sign.html')

@app.route('/sign_auth')
def sign_auth()->object:
    pass


@app.route('/room_create')
def room_create()->object:
    return flask.redirect('room_create.html')

@app.route('/room_create_auth', methods = ['POST'])
def room_create_auth()->object:
    if flask.request.method != 'POST':
        return

    room_name = flask.request.form['room_name']

    try:
        create_room(room_name)
    except:
        flask.g.message = 'Invalid room name'
        return flask.redirect(flask.url_for('room_create'))

    flask.g.message = ''
    return flask.redirect(flask.url_for('index'))


###

@socketio.on('connect')
def handler_connect()->None:
    ip = flask.request.remote_addr;
    flask_socketio.send('New user found: '+ip, to=INITIAL_ROOM)

@socketio.on('room_join')
def room_join(data)->None:
    room = data["room"]

@socketio.on('message')
def handler_message(data)->None:
    message = data["message"]
    room = data["room"]

    flask_socketio.send(message, to=room)


if __name__=='__main__':
    socketio.run(app, debug=True)

import os
import flask
import flask_socketio

from database import *

INITIAL_ROOM = 0
SECRET_KEY_LEN = 26

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(SECRET_KEY_LEN)
socketio = flask_socketio.SocketIO(app)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS room (
        name VARCHAR(100) PRIMARY KEY,
        user_admin VARCHAR(80)
    );
"""
)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        name VARCHAR(80) PRIMARY KEY,
        email VARCHAR(254),
        status VARCHAR(50),
        password VARCHAR(50)
    );
""")

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
        return flask.redirect('/login/display')
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

    try:
        result = user_insert(user_name, user_email, user_password)
    except sqlite3.OperationalError:
        flask.session["message"]="An error occurs..."
        return flask.redirect(flask.url_for('login'))

    if result == 1:
        flask.session["message"]="Unavailable user name"
        return flask.redirect(flask.url_for('login'))


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

    result = cursor.execute(f"SELECT name, password FROM user WHERE name = '{ user_name }'")
    rows = result.fetchone()

    if not rows:
        flask.session['message'] = "Unavaible user name"
        return flask.redirect(flask.url_for('sign'))

    print(rows)
    if rows[1] != user_password:
        flask.session['message'] = "Incorrect password"
        return flask.redirect(flask.url_for('sign'))

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

    return flask.redirect(flask.url_for('index'))

##
@app.route('/load_home_page')
def home_page()->None:
    return flask.redirect("/")

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

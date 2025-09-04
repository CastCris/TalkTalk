import flask
import sqlite3
from database import *

STATUS_DIE = 'die'
STATUS_ONLINE = 'online'
STATUS_OFFLINE = 'offline'

main_routers = flask.Blueprint('main', __name__)

###
@main_routers.before_request
def before_request()->None:
    if "user_name" in flask.request.cookies:
        flask.session["user_name"] = flask.request.cookies["user_name"]
        return

    flask.redirect('/')

###
@main_routers.route('/')
def index()->object:
    print(flask.session)
    if not "user_name" in flask.session or not flask.session["user_name"]:
        return flask.redirect('/sign/display')
    return flask.render_template('index.html')


@main_routers.route('/login/display')
def login_display()->object:
    return flask.render_template('login.html')

@main_routers.route('/login/auth', methods=['POST'])
def login_auth()->object:
    if flask.request.method != 'POST':
        return

    user_name = flask.request.form['user_name']
    user_email = flask.request.form['user_email']
    user_password = flask.request.form['user_password']

    # result = user_insert(user_name, user_email, user_password)
    try:
        result = user_insert(user_name, user_email, STATUS_ONLINE, user_password)
    except sqlite3.OperationalError:
        flask.session["message"]="An error occurs..."
        return flask.redirect(flask.url_for('main.login_display'))

    if result == 1:
        flask.session["message"]="Unavailable user name"
        return flask.redirect(flask.url_for('main.login_display'))


    flask.session['message'] = ''
    flask.session['user_name'] = user_name

    response = flask.make_response(flask.redirect('/'))
    response.set_cookie('user_name', user_name)

    return response


@main_routers.route('/sign/display')
def sign_display()->object:
    return flask.render_template('sign.html')

@main_routers.route('/sign/auth', methods=['POST'])
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
        return flask.redirect(flask.url_for('main.sign_display'))

    if rows[2]==STATUS_DIE:
        flask.session['message'] = "This user is unactive"
        return flask.redirect(flask.url_for('main.sign_display'))

    print(rows)
    if rows[1] != user_password:
        flask.session['message'] = "Incorrect password"
        return flask.redirect(flask.url_for('main.sign_display'))

    flask.session['message'] = ''
    flask.session["user_name"] = user_name

    response = flask.make_response(flask.redirect('/'))
    response.set_cookie('user_name', user_name)

    return response


@main_routers.route('/logout')
def logout()->object:
    response = flask.make_response(flask.redirect('/'))
    response.set_cookie('user_name', '', expires=0)
    flask.session["user_name"] = None

    return response


@main_routers.route('/room_manager/create')
def room_create()->object:
    return flask.render_template('room_create.html')

@main_routers.route('/room_manager/create/auth', methods = ['POST'])
def room_create_auth()->object:
    if flask.request.method != 'POST':
        return

    room_name = flask.request.form['room_name']
    user_name = flask.request.cookies["user_name"]

    result = 0
    try:
        result = room_insert(room_name, user_name)
    except Exception as e:
        flask.session["message"] = "An error occurs"
        print('Room create ERRO: ', e)
        return flask.redirect(flask.url_for('main.room_create'))

    if result == 1:
        flask.session["message"] = "Room name already exists"
        return flask.redirect(flask.url_for('main.room_create'))

    flask.session["message"]=''

    return flask.redirect(flask.url_for('main.index'))

##
@main_routers.route('/load_home_page')
def home_page()->None:
    return flask.redirect("/")

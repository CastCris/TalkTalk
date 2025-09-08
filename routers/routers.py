import os
import flask

import hmac
import hashlib

import sqlalchemy
from database import *

SECRET_KEY_LEN = 26
SECRET_KEY = os.urandom(SECRET_KEY_LEN)

STATUS_DIE = 'die'
STATUS_ONLINE = 'online'
STATUS_OFFLINE = 'offline'

main_routers = flask.Blueprint('main', __name__)

"""
def cookie_hash_get(cookie_value:str)->object:
    return hmac.new(SECRET_KEY, value.encode(), hashlib.sha256).hexdigest()

def cookie_set(cookie_object:object, cookie_name:str, cookie_value)->None:
    cookie_value_hash = cookie_hash_get(cookie_value)
    cookie_object.set_cookie(cookie_name, cookie_value_hash, secure=True, httponly=True, samesite='Strict')
"""

###
@main_routers.before_request
def before_request()->None:
    user_name = None
    if "user_name" in flask.request.cookies:
        user_name = flask.request.cookies["user_name"]

    user = None
    try:
        user = user_get(user_name)
    except sqlalchemy.exc.OperationalError:
        pass

    if user_name and user:
        flask.session["user_name"] = flask.request.cookies["user_name"]
        return

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
    except sqlalchemy.exc.IntegrityError:
        flask.session["message"]="Unavailable user name"
        session.rollback()

        return flask.redirect(flask.url_for('main.login_display'))
    except:
        flask.session["message"]="An error occurs..."
        session.rollback()

        return flask.redirect(flask.url_for('main.login_display'))

    flask.session['message'] = ''
    flask.session['user_name'] = user_name

    response = flask.make_response(flask.redirect('/'))
    response.set_cookie('user_name', user_name, secure=True, httponly=True, )

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

    result = session.query(User.name, User.password, User.status).filter(User.name == user_name).first()
    # print(result,'-')
    print(result)

    if not result:
        flask.session['message'] = "Unavaible user name"
        return flask.redirect(flask.url_for('main.sign_display'))

    if result[2]==STATUS_DIE:
        flask.session['message'] = "This user is unactive"
        return flask.redirect(flask.url_for('main.sign_display'))

    if result[1] != user_password:
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

    try:
        result = room_insert(room_name, user_name)
    except sqlalchemy.exc.IntegrityError:
        flask.session["message"] = "Room name already exists"
        session.rollback()

        return flask.redirect(flask.url_for('main.room_create'))
    except Exception as e:
        flask.session["message"] = "An error occurs"
        session.rollback()
        print('Room create ERRO: ', e)

        return flask.redirect(flask.url_for('main.room_create'))

    flask.session["message"]=''

    return flask.redirect(flask.url_for('main.index'))

##
@main_routers.route('/load_home_page')
def home_page()->None:
    return flask.redirect("/")

import flask
import flask_socketio

import sqlalchemy

import string
import secrets

import os

# Global vars
SECRET_KEY_LEN = 26
SECRET_KEY = os.urandom(SECRET_KEY_LEN)

STATUS_DIE = 'die'
STATUS_ONLINE = 'online'
STATUS_OFFLINE = 'offline'

SUPER_ADMIN = 'super_admin'
ROOM_INITIAL = 'index'

SYSTEM_MESSAGE_OFFSET = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
SYSTEM_MESSAGE_OFFSET_COUNT  = 0

MESSAGE_SCROLLOFF = 250

SERVER_STATUS_HIGHLIGHTS = ['Users online', 'Test1', 'Test2', 'Test3']

ROUTER_REGISTER_IGNORE = ['__pycache__', '__init__.py', 'router_register.py']

# Flask
app = None

# Flask_socketio
socketio = flask_socketio.SocketIO()
socket_data = {}

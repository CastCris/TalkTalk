from begin import *

from routers import *
from sockets import *

###
# Flask
app = flask.Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
router_register(app, 'routers')

# Flask_socketio
socketio.init_app(app)
socket_register_events(socketio)

###
try:
    user_insert(SUPER_ADMIN, 'thisemaildoesntexists@email', STATUS_DIE, '', ROOM_INITIAL)
    room_insert(ROOM_INITIAL, SUPER_ADMIN)
except Exception as e:
    session.rollback()
    print('Setup server error: ',e)

###
if __name__=='__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

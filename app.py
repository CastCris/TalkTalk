import flask
import socketio
import eventlet
import eventlet.wsgi

sio = socketio.Server()
app = flask.Flask(__name__)

@app.route('/')
def index()->object:
    return flask.render_template('/index.html')

@sio.event
def connect(sid, environ):
    print('Client {} connect'.format(sid))

@sio.event
def disconnect(sid, data):
    print('Client {} disconnet'.format(sid))

eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

"""
if __name__=='__main__':
    app.run(debug=True)
"""

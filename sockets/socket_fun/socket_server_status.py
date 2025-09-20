from begin import *

def server_status_data_get(data)->None:
    highlight_name = data["highlight_name"]
    room_name = socket_data[flask.request.sid]["room"]

    data = None

    # User Online
    if highlight_name == SERVER_STATUS_HIGHLIGHTS[0]:
        data = userRoom_user_online_get(room_name)

    flask_socketio.emit('server_status_data', {
        'highlight_name': highlight_name,
        'data': data
    })

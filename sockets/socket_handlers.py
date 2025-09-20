from begin import *

from .socket_fun import *

def socket_register_events(socketio: object)->None:
    ##
    @socketio.on('connect')
    def handler_connect(auth:object)->None:
        connection_type = auth.get("typeConnection", "null")

        if connection_type == "room":
            connect_room(auth)

    @socketio.on('disconnect')
    def handler_disconnect()->None:
        disconnect()

    ##
    @socketio.on('message')
    def handler_message(data)->None:
        message_content = data["message_content"]
        message_id = data["message_id"]

        print('message: ',data)

        room_name = data["room"]
        user_name = flask.request.cookies["user_name"]

        try:
            message_insert(message_id, message_content, user_name, room_name) 
        except sqlalchemy.exc.IntegrityError as e:
            flask_socketio.emit('user_invalid')
            print('Handler_message Error: ', e)

            return
        except Exception as e:
            message_content = "Error in message loading"
            session.rollback()

            print('Handler_mesaage Error: ', e)

            return

        message_date = message_date_get(message_id)
        print('message_date: ', message_date)
        #

        message_send_room(message_content, message_date, user_name, room_name)

    @socketio.on('message_load')
    def handler_message_load(auth)->None:
        message_old_offset = auth.get('messageOldOffset', 0)
        server_room = auth.get('serverRoom', 'index')

        data_recovery_message(server_room, message_old_offset, message_fetch_oldest)

    ##
    @socketio.on('room_change')
    def handler_room_change(data)->None:
        room_change(data)

    @socketio.on('room_create')
    def handler_room_create(data)->None:
        room_create(data)

    ##
    @socketio.on('server_status_data_get')
    def handler_server_status_data_get(data)->None:
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

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
        message_handler(data)

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
        server_status_data_get(data)

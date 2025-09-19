# from casts import *
from .casts import *
import sqlalchemy
import time

def foreign_key_enable(conn, branch)->None:
    conn.execute('PRAGMA foreign_keys = ON')

engine = sqlalchemy.create_engine("sqlite:///data.db", echo=True)

sqlalchemy.event.listen(engine, 'connect', foreign_key_enable)

Base.metadata.create_all(engine)

Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

def room_get()->list:
    room_able = [ room_name[0] for room_name in session.query(Room.name).all()]

    return room_able

def room_insert(room_name: str, user_name: str)->None:
    room_new = Room(name=room_name, user_admin=user_name)
    session.add(room_new)
    session.commit()


###
def user_get(user_name:str)->object:
    try:
        user = session.query(User).filter(User.name == user_name).first()
    except:
        session.rollback()
        return None

    return user

def user_insert(name:str, email:str, status:str, password: str, room_home:str)->None:
    user_new = User(name=name, email=email, status=status, password=password, room_home=room_home)

    session.add(user_new)
    session.commit()

def user_status_update(user_name:str, status_new:str)->None:
    user = user_get(user_name)
    if not user:
        return

    user.status = status_new

    session.commit()

def user_room_home_get(user_name:str)->str:
    user = user_get(user_name)
    if not user:
        return ''

    return user.room_home

###
def message_insert(message_id:str, content:str, user_name:str, room_name:str)->None:
    message_new = Message(id=message_id, date=time.time(), user_name=user_name, room_name=room_name, content=content)
    session.add(message_new)

    session.commit()

def message_fetch_newest(date_offset:int, room_name:str, limit:int)->set:
    messages = session.query(Message.content, Message.date, Message.user_name) \
            .filter(Message.date > date_offset, Message.room_name == room_name) \
            .order_by(sqlalchemy.desc(Message.date)) \
            .limit(limit) \
            .all()

    messages_list = [
        {'message_content': str(message[0]),
         'message_offset': float(message[1]),
         'message_user_name': str(message[2])
        }
        for message in messages
    ]

    # print('message_list: ', messages_list)

    return messages_list

def message_fetch_oldest(date_offset:int, room_name:str, limit:int)->set:
    messages = session.query(Message.content, Message.date, Message.user_name) \
            .filter(Message.date < date_offset, Message.room_name == room_name) \
            .order_by(sqlalchemy.desc(Message.date)) \
            .limit(limit) \
            .all()

    messages_list = [
        {'message_content': str(message[0]),
         'message_offset': float(message[1]),
         'message_user_name': str(message[2])
        }
        for message in messages
    ]

    # print('message_list: ', messages_list)

    return messages_list

def message_date_get(message_id:str)->float:
    message_offset = session.query(Message.date).filter(Message.id == message_id).first()[0]

    return message_offset

###
def userRoom_get(user_name:str, room_name:str)->object:
    userRoom_instance = session.query(User_Room) \
            .filter(User_Room.room_name==room_name, User_Room.user_name==user_name) \
            .first()

    return userRoom_instance

def userRoom_insert(user_name:str, room_name:str)->None:
    userRoom_new = User_Room(user_name=user_name, room_name=room_name, connections=0)
    session.add(userRoom_new)

    session.commit()

def userRoom_delete(user_name:str, room_name)->None:
    userRoom = userRoom_get(user_name, room_name)

    session.delete(userRoom)
    session.commit()


def userRoom_connections_get(user_name:str, room_name:str)->int:
    userRoom = userRoom_get(user_name, room_name)
    if not userRoom:
        return 0

    return userRoom.connections

def userRoom_connections_add(user_name:str, room_name:str)->None:
    userRoom = userRoom_get(user_name, room_name)

    try:
        userRoom.connections += 1
    except Exception as e:
        print('userRoom_connections_add ERROR', e)
        session.rollback()

        return

    session.commit()

def userRoom_connections_minus(user_name:str, room_name:str)->None:
    userRoom = userRoom_get(user_name, room_name)

    try:
        userRoom.connections -= 1
    except Exception as e:
        print('userRoom_connections_minus ERROR', e)
        session.rollback()
        
        return

    session.commit()


def userRoom_user_online_get(room_name:str)->list:
    userRoom_instances = session.query(User_Room.user_name) \
            .filter(User_Room.room_name==room_name) \
            .all()

    result = [ i[0] for i in userRoom_instances ]
    return result

def userRoom_user_connections_get(user_name:str)->int:
    userRoom_instances = session.query(User_Room.connections) \
            .filter(User_Room.user_name==user_name) \
            .all()

    result = [ i[0] for i in userRoom_instances ]
    return sum(result)

"""
try:
    user_insert("Agnaldo", "abcd@gmail.com", "online", "password")
except sqlalchemy.exc.IntegrityError:
    session.rollback()
    print("This user already exists!")

jose = user_get("Jose")
agnaldo = user_get("Agnaldo")

print(jose,'-')
print(agnaldo.name,'-')
print(user_connections_get("Agnaldo"))

result = session.query(User.name, User.status).all()
print(type(result[0]))
"""

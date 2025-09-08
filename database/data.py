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


def user_get(user_name:str)->object:
    try:
        user = session.query(User).filter(User.name == user_name).first()
    except:
        session.rollback()
        return None

    return user

def user_insert(name:str, email:str, status:str, password: str)->None:
    user_new = User(name=name, email=email, status=status, password=password, connections=0)

    session.add(user_new)
    session.commit()

def user_status_update(user_name:str, status_new:str)->None:
    user = user_get(user_name)
    if not user:
        return

    user.status = status_new

    session.commit()

def user_connections_add(user_name:str)->None:
    user = user_get(user_name)
    if not user:
        return

    user.connections += 1

    session.commit()

def user_connections_minus(user_name:str)->None:
    user = user_get(user_name)
    if not user:
        return

    user.connections -= 1

    session.commit()

def user_connections_get(user_name:str)->int:
    user = user_get(user_name)
    if not user:
        return 0

    return user.connections


def message_insert(message_id:str, content:str, user_name:str, room_name:str)->None:
    message_new = Message(id=message_id, date=time.time(), user_name=user_name, room_name=room_name, content=content)
    session.add(message_new)

    session.commit()

def message_fetch(date_offset:int, room_name:str)->set:
    messages = session.query(Message.content, Message.date, Message.user_name) \
            .filter(Message.date > date_offset, Message.room_name == room_name) \
            .all()

    messages_list = [message for message in messages]

    return messages

def message_date_get(message_id:str)->float:
    message_offset = session.query(Message.date).filter(Message.id == message_id).first()[0]

    return message_offset

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

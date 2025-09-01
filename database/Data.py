import sqlite3

db = sqlite3.connect('data.db', check_same_thread=False)
cursor = db.cursor()

def room_able()->set:
    result = cursor.execute("""
    SELECT name FROM room
    """)

    result = result.fetchone()
    return result

def room_insert(room_name: str, user_name: str)->object:
    room_avaible = room_able()
    if room_avaible and room_name in room_avaible:
        return 1

    result = cursor.execute(f"""
    INSERT INTO room(name, user_admin) VALUES('{ room_name }', '{ user_name }');
    """)

    db.commit()

    return 0


def user_insert(name:str, email:str, password: str)->object:
    result = cursor.execute(f"SELECT (name) FROM user WHERE (name = '{ name }')")
    result = result.fetchone()
    print(result,'mil acasos me dizem o que sou')
    if result:
        return 1

    cursor.execute(f"""
    INSERT INTO user(name, email, password, status) VALUES('{ name }', '{ email }', '{ password }', 'online');
    """)

    db.commit()

    return 0


def message_insert(message_id:str, content:str, room_name:str)->object:
    print(message_id, content, room_name)
    result = cursor.execute(f"""
    INSERT INTO message VALUES('{ message_id }', (SELECT unixepoch('subsec')), '{ room_name }', '{ content }') 
    """)

    db.commit()
    
    return result

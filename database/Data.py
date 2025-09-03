import sqlite3

db = sqlite3.connect('data.db', check_same_thread=False)
cursor = db.cursor()

def room_get()->set:
    result = cursor.execute("""
    SELECT name FROM room
    """)

    result = result.fetchall()
    room_able = []
    for i in result:
        room_able.append(i[0])

    return room_able

def room_insert(room_name: str, user_name: str)->int:
    room_avaible = room_get()
    if room_name in room_avaible:
        return 1


    cursor.execute(
        "INSERT INTO room VALUES(?, ?)",
        (room_name, user_name)
    )

    db.commit()

    return 0


def user_insert(name:str, email:str, status:str, password: str)->int:
    result = cursor.execute(f"SELECT (name) FROM user WHERE (name = '{ name }')")
    result = result.fetchone()
    # print(result,'mil acasos me dizem o que sou')

    if result:
        return 1

    cursor.execute(
        "INSERT INTO user VALUES(?, ?, ?, ?, ?)",
        (name, email, status, password, 0)
    )

    db.commit()

    return 0

def user_status_update(user_name:str, status_new:str)->object:
    result = cursor.execute(
        "UPDATE user SET status = ? WHERE name = ?",
        (status_new, user_name)
    )

    db.commit()

    return result

def user_connections_add(user_name:str)->object:
    result = cursor.execute(
        "UPDATE user SET connections = connections + 1 WHERE name = ?",
        (user_name, )
    )

    return result

def user_connections_minus(user_name:str)->object:
    result = cursor.execute(
        "UPDATE user SET connections = connections - 1 WHERE name = ?",
        (user_name, )
    )

    return result

def user_connections_get(user_name:str)->object:
    result = cursor.execute(
        "SELECT connections FROM user WHERE name = ?",
        (user_name, )
    )

    result = result.fetchone()

    if not result:
        return 0
    return result[0]


def message_insert(message_id:str, content:str, user_name:str, room_name:str)->object:
    print(message_id, content, room_name)
    result = cursor.execute(
        "INSERT INTO message VALUES(?, (SELECT unixepoch()), ?, ?, ?)",
        (message_id, user_name, room_name, content, )
    )

    db.commit()
    
    return result

import sqlite3

db = sqlite3.connect('data.db')
cursor = db.cursor()

ROOMS_ABLE = cursor.execute('SELECT (name) FROM room').fetchone()
if ROOMS_ABLE:
    ROOMS_ABLE = set(ROOMS_ABLE.split(' '))

def create_room(id_code: str, user_name: str)->object:
    result = cursor.execute(f"""
    INSERT INTO room(user_admin) VALUE({ user_name });
    """)

    return result


def create_user(name:str, email:str, password: str)->object:
    result = cursor.execute(f"""
    INSERT INTO user VALUES({ name }, { email }, { password });
    """)

    return result

from .casts import Base

import sqlalchemy

##
def foreign_key_enable(conn, branch)->None:
    conn.execute('PRAGMA foreign_keys = ON')


engine = sqlalchemy.create_engine("sqlite:///data.db", echo=True)

sqlalchemy.event.listen(engine, 'connect', foreign_key_enable)

Base.metadata.create_all(engine)

Session = sqlalchemy.orm.sessionmaker(bind=engine)
session = Session()

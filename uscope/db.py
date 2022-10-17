from flask import current_app
from flask.cli import with_appcontext

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE as dbstring

engine = create_engine(dbstring, echo=True, future=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from ..config import DATABASE as dbstring
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()


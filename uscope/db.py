from sys import modules
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE as dbstring


engine = create_engine(dbstring, echo=True, future=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    current_app.logger.debug(__name__)
    import models
    Base.metadata.create_all(bind=engine)

def update_tables():
    current_app.logger.debug(__name__)
    import models
    classes = [cls_obj for cls_name, cls_obj in inspect.getmembers(modules['models']) if inspect.isclass(cls_obj)]
    for my_class in classes:
        if not engine.dialect.has_table(engine, my_class):
            table = Table(my_class)



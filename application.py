import os
from flask import Flask, session, render_template
from flask_user import UserManager
from flask_sqlalchemy import SQLAlchemy
#from flask.ext.session import Session

import uscope.gsearch
import uscope.configure
import uscope.linkedin.lnkedin
from uscope.models import User

def create_app(test_config=None):
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_pyfile('./config.py', silent=False)
    else:
        app.config.from_pyfile('/tests/config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from uscope.db import db_session

    user_manager = UserManager(app, SQLAlchemy(app), UserClass=User)
    
    @app.route('/')
    def hello_world():
        return render_template('index.html')

    app.register_blueprint(uscope.gsearch.bp)
    app.register_blueprint(uscope.configure.bp)
    app.register_blueprint(uscope.linkedin.lnkedin.bp)

    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
    return app

if __name__ == "__main__":
    app = create_app()
    app.debug = True
    app.run()


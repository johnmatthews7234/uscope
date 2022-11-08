
from flask import Blueprint, flash, redirect, render_template, request, current_app
from .models import ConfigKeys
from .db import db_session, init_db
from .helper import log

bp = Blueprint('config', __name__, url_prefix='/config')

@bp.route('/', methods=('GET', 'POST',))
def configure():
    current_app.logger.debug(__name__)
    config_records = ConfigKeys.query.all()
    if request.method == 'POST':
        for config_record in config_records:
            if request.form[config_record.keyname] is not None:
                config_record.keyvalue = request.form[config_record.keyname]
        db_session.commit()
        flash('Configuration saved.  :-)')
    config_list = []
    for config_record in config_records:
        config_list.append({'keyname' : config_record.keyname, 'keyvalue' : config_record.keyvalue})
    return render_template('/configure/configure.html', configs=config_list)


@bp.route('/delete/<string:keyname>', methods=('GET',))
def delete(keyname):
    current_app.logger.debug(__name__)
    config_record = ConfigKeys.query.filter(ConfigKeys.keyname == keyname).first()
    db_session.delete(config_record)
    db_session.commit
    flash('Config key deleted.')
    redirect('/config')

@bp.route('/add', methods=('GET','POST',))
def add():
    current_app.logger.debug(__name__)
    if request.method == 'POST':
        if ConfigKeys.query.filter(ConfigKeys.keyname == request.form['keyname']).first() is None:
            db_session.add(ConfigKeys(request.form['keyname'], request.form['keyvalue']))
            db_session.commit()
        return redirect('/config')
    return  render_template('/configure/add.html')
    
@bp.route('/database', methods=('GET', 'POST',))
def database_admin():
    #TODO: Need to flesh this out with update tables.
    current_app.logger.debug(__name__)

    if request.method == 'POST':
        match request.form['action']:
            case 'create':
                init_db()

        


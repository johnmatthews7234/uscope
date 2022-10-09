from urllib import response
import urllib.request
import json
from flask import request, current_app

from .db import db_session
from .models import ConfigKeys, KeyWords

def data_from_url(full_url):
    request = urllib.request.Request(full_url)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.URLError as e:
        raise Exception('Unexpected Error while opening ' + full_url)
    json_data = json.loads(response.read())
    return json_data

def get_key(key_name):
    ck = ConfigKeys.query.filter(ConfigKeys.keyname == key_name).first()
    if ck is not None:
        return ck.keyvalue
    else:
        return ""

def set_key(key_name, key_value):
    ck = ConfigKeys.query.filter(ConfigKeys.keyname == key_name).first()
    if ck is not None:
        ck.keyvalue = str(key_value)
    else:
        ck = ConfigKeys(str(key_name), str(key_value))
        db_session.add(ck)
    db_session.commit()


def get_refresh_place_days():
    refresh_place_days = ConfigKeys.query.filter(ConfigKeys.keyname == 'refreshplacedays').first()
    if refresh_place_days is None:
        refresh_place_days = '90'
        my_record = ConfigKeys('refreshplacedays', refresh_place_days)
        db_session.add(my_record)
        db_session.commit()
    return int(refresh_place_days.keyvalue)

def log(log_text, level='debug'):
    if level == 'debug':
        current_app.logger.debug(log_text)
    elif level == 'info':
        current_app.logger.info(log_text)
    else:
        current_app.logger.debug(f'{level} is not a logging level.  {log_text}')


    




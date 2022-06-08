import json
import random
import requests
import string
from urllib.parse import urlparse, parse_qs
from  datetime import datetime 
from uscope.helper import get_key, set_key


def auth(credentials):
    creds = read_creds(credentials)
    print(creds)
    client_id = get_key('linkedin_client_id')
    client_secret = get_key('linkedin_client_secret')
    redirect_uri = get_key('linkedin_redirect_uri')
    api_url = 'https://www.linkedin.com/oauth/v2'
    if datetime(get_key('linkedin_timeout')) < datetime.now():
        args = client_id, client_secret, redirect_uri
        auth_code = authorize(api_url, *args)
        access_token = refresh_token(auth_code, *args)
        set_key('linkedin_access_token', access_token['access_token'])
        set_key('linkedin_timeout', str(datetime.now() + datetime.timedelta(seconds=int(access_token['expires_in']))))
    else:
        access_token = get_key('linkedin_access_token')
    return access_token

def headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'cache_control': 'no-cache',
        'X-Restli-Protocol-Version' : '2.0.0'
    }

def create_CSRF_token():
    letters = string.ascii_lowercase
    token = ''.join(random.choice(letters) for i in range(20))
    return token

def open_url(url):
    '''probably want to turn this into a blueprint with a click here thingy.'''
    import webbrowser
    print(url)
    webbrowser.open(url)

def parse_redirect_uri(redirect_response):
    url = parse_qs(urlparse(redirect_response).query)
    return url['code'][0]

def authorize(api_url, client_id, client_secret, redirect_uri):
    csrf_token = create_CSRF_token()
    params = {
        'response_type': 'code',
        'client_id' : client_id,
        'redirect_uri' : redirect_uri,
        'state' : csrf_token,
        'scope' : 'r_liteprofile,remailaddress,w_membersocial' 
    }
    response = requests.get(f'{api_url}/authorization', params=params)
    open_url(response.url)
    redirect_response = input('Paste the full url here:')
    auth_code = parse_redirect_uri(redirect_response)
    return auth_code


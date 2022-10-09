
from crypt import methods
from datetime import datetime, timedelta
from urllib import request
from urllib.parse import urldefrag
from flask import Blueprint, redirect, flash, request, render_template, current_app
from flask_user import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from flask_user import current_user
#from linkedin.linkedin import LinkedInAuthentication, LinkedInApplication, PERMISSIONS
import requests
import urllib
import json

from ..models import LinkedInTokens
from ..helper import data_from_url, get_key, log
from ..db import db_session

url = "https://linkedin.com"
driver = webdriver.Chrome()

bp = Blueprint('linkedin', __name__, url_prefix='/linkedin')

@bp.route('getcode', methods=('GET', 'POST',))
@login_required
def send_code_request():
    log('hello world')
    if request.method == 'GET':
        return render_template('/linkedin/login.html')
    if not test_login(request.form['li_un'],request.form['li_pw']):
        flash('Error: Username or password is not working for me')
        return render_template('/linkedin/login.html')
    my_LinkedIn_record = LinkedInTokens.query.filter(LinkedInTokens.user_id == current_user.user_id).first()
    if my_LinkedIn_record is None:
        my_LinkedIn_record = LinkedInTokens(current_user.user_id)
    my_LinkedIn_record.username = request.form['li_un']
    my_LinkedIn_record.password = generate_password_hash(request.form['li_pw'])
    db_session.commit()
    header_string = f"?response_type=code&client_id={get_key('linkedin_api_key')}&redirect_uri={urllib.parse.quote(get_key('linkedin_return_url'))}&state={get_key('linkedin_csrf')}&scope=r_liteprofile%20r_emailaddress%20w_member_social"
    return redirect ('https://www.linkedin.com/oauth/v2/authorization' + header_string)


@bp.route('code', methods=('GET',))
@login_required
def get_code_request():
    args = request.args.to_dict()
    if 'error' in args:
        flash(f"Error: {args['error']}.  {args['error_description']}")
    elif args['state'] is not get_key('linkedin_csrf'):
            flash("Error: State string is invalid.")
    else:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        header_string = f"grant_type=authorization_code&code={args['code']}&client_id={get_key('linkedin_api_key')}&client_secret={get_key('linkedin_api_secret')}&redirect_uri={urllib.parse.quote(get_key('linkedin_return_url'))}"
        reply = requests.post('https://www.linkedin.com/oauth/v2/accessToken?' + header_string, headers=headers)
        reply_dict = json.loads(reply.text)
        my_LinkedIn_record = LinkedInTokens.query.filter(LinkedInTokens.user_id == current_user.user_id).first()
        if my_LinkedIn_record is None:
            my_LinkedIn_record = LinkedInTokens(current_user.user_id)
        my_LinkedIn_record.token = generate_password_hash(reply_dict['access_token'])
        my_LinkedIn_record.expires = datetime.now() + datetime.timedelta(seconds=reply_dict['expires_in'])
        db_session.commit()

        
def test_login(username, password):
    output = False
    url = 'https://www.linkedin.com/'
    driver.delete_all_cookies()
    driver.get(url)
    if "Log In" in driver.title:
        username_input = driver.find_element(By.ID, "session_key")
        username_input.clear()
        username_input.send_keys(username)
        password_input = driver.find_element(By.ID, "session_password")
        password_input.clear()
        password_input.send_keys(password)
        password_input.submit()
        driver.implicitly_wait(10)
        if 'feed' in driver.current_url:
            output = True
        driver.get(url + 'm/logout')
    return output


class linkedin_search:
    logged_in = False
    
    def __init__(self, company_name, url ):
        self.login()
        for company in self.search_company(company_name):
            urllist = self.get_company_url(company)

    def login(self):
        if self.logged_in:
            return
        driver.get(url)
        if "Log in" not in driver.title:
            username = get_key("linkedin_user")
            password = get_key("linkedin_password")
            if (username == "") or (password == ""):
                raise Exception('No LinkedIn login data was found.  Go configure that')
            username_input = driver.find_element(By.ID, "session_key")
            username_input.clear()
            username_input.send_keys(username)
            password_input = driver.find_element(By.ID, "session_password")
            password_input.clear()
            password_input.send_keys(password)
            password_input.submit()
        else:
            log
        self.logged_in = True 

    def search_companies(self, companyname):
        driver.get(url + "/feed/")
        search_button = driver.find_element(By.CLASS_NAME, "search-global-typehead__collapsed-search-button")
        search_button.click()
        search_input = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input always-show-placeholder always-show-paceholder")
        search_input.clear()
        search_input.send_keys(companyname)
        search_input.send_keys(Keys.RETURN)
        company_filter = driver.find_element(By.XPATH, '//button[text()="Companies"]')
        company_filter.click()
        soup = BeautifulSoup(driver.page_source)
        urns = []
        for elem in soup.findall('div', class_='entity-result'):
            urns.append(elem['data-chameleon-result-urn'])
        return urns

'''
    def pick_closest_company(urnlist):
        urn_text = ','.join(urnlist)
        GET https://api.linkedin.com/rest/organizationBrandsLookup?ids=List(5025865,35625943)
    #Now for beautiful soup.





    grab list of companies
    for company in list
        grab url
    use fuzzywuzzy for picking the closest url aove 80%
    populate company linkedin data_from_url
'''
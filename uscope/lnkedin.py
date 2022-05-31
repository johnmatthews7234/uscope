
from .helper import data_from_url, get_key
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
url = "https://linkedin.com"
driver = webdriver.Chrome()



class linkedin_search:
    logged_in = False
    
    def __init__(self, company_name, url ):
        self.login()
        for company in search_company(company_name):
            urllist = get_company_url(company)

    def login(self):
        if self.logged_in:
            return
        driver.get(url)
        if "Log in" in driver.title:
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
        self.logged_in = True 

    def search_company(self, companyname):
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
        soup.findall('div',class='entity-result')


    #Now for beautiful soup.



    grab list of companies
    for company in list
        grab url
    use fuzzywuzzy for picking the closest url aove 80%
    populate company linkedin data_from_url




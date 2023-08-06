# -*- coding: UTF-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from django.test.testcases import LiveServerTestCase

class Selenium(LiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(Selenium, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(Selenium, cls).tearDownClass()

    def login(self, username, password, url='/', login_verification_text='Logout'):
        self.selenium.get('%s%s' % (self.live_server_url, url))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//input[@value="login"]').click()
        WebDriverWait(self.selenium, 10).until(lambda driver: \
                    driver.find_element_by_link_text(login_verification_text))


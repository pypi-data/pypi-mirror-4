from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.firefox.webdriver import WebDriver

class TinymceTests(LiveServerTestCase):
    #fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(TinymceTests, cls).setUpClass()
        user = User.objects.create(username="testuser", is_staff=True)
        user.set_password('testpassword')
        TinymceTests.test_username = user.username
        TinymceTests.test_password = 'testpassword'

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TinymceTests, cls).tearDownClass()

    def test_tinymce_loading(self):
        username = TinymceTests.test_username
        password = TinymceTests.test_password

        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(user.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(user.password)
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

        self.selenium.get('%s%s' % (self.live_server_url, '/admin/testapp/testpage/add/'))
        dir(self.selenium)
        self.selenium.executeScript("return false")

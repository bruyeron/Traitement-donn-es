from selenium.webdriver.common.by import By
from .base_page import BasePage
from utils.config import USER_NAME_VOCALCOM, PASSWORD

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://tapp1240wv.corp.telma.mg/hermes360/Admin/Launcher/login"
        self.username_input = (By.ID, "usrID")
        self.password_input = (By.ID, "usrPWD")
        self.login_button = (By.CSS_SELECTOR, "Input.send")

        # Affichage pour debug
        print(f"my user name => {USER_NAME_VOCALCOM}")

    def login(self):
        self._open_url(self.url)
        self._type_text(self.username_input, USER_NAME_VOCALCOM)
        self._click(self.login_button)
        self._type_text(self.password_input, PASSWORD)
        self._click(self.login_button)

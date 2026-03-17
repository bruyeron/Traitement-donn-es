from selenium.webdriver.common.by import By
from .base_page import BasePage

class DashboardPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://tapp1240wv.corp.telma.mg/hermes360/Admin/Launcher/dashboard"
        self.workspace_button = (By.CSS_SELECTOR, "#hermes .workspace")
        self.reporting_button = (By.CSS_SELECTOR, ".button-panel.reporting .button-name")

    def go_to_page(self):
        self._open_url(self.url)

    def click_workspace(self):
        self._click(self.workspace_button)

    def click_reporting(self):
        self._click(self.reporting_button)

    def verify_reporting_page(self):
        try:
            # Vérifier le titre de la page
            title = self.driver.title
            print(f"Titre de la page de reporting: {title}")

            # Vérifier que nous sommes sur la bonne page
            expected_url = "https://tapp1240wv.corp.telma.mg/hermes360/Admin/Launcher/Start.aspx"
            if not self.driver.current_url.startswith(expected_url):
                raise Exception(f"URL incorrecte: attendu {expected_url}, obtenu {self.driver.current_url}")

            return True
        except Exception as e:
            print(f"Erreur de vérification de la page: {str(e)}")
            return False

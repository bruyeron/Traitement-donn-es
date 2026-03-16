from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.poll_frequency = 0.5
        self.original_tab = None

    def _open_url(self, url):
        self.driver.get(url)

    def _click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def _type_text(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def switch_to_new_tab(self):
        # Stocker l'onglet actuel
        self.original_tab = self.driver.current_window_handle

        # Attendre que le nouvel onglet s'ouvre
        self.wait.until(lambda d: len(d.window_handles) > 1)

        # Obtenir tous les onglets
        all_tabs = self.driver.window_handles

        # Switcher vers le nouvel onglet
        for tab in all_tabs:
            if tab != self.original_tab:
                self.driver.switch_to.window(tab)
                break

        # Vérifier que nous sommes bien dans le nouvel onglet
        current_url = self.driver.current_url
        print(f"URL du nouvel onglet: {current_url}")

        return current_url

    def switch_to_original_tab(self):
        if self.original_tab:
            self.driver.switch_to.window(self.original_tab)
            print(f"Retour à l'onglet original: {self.driver.current_url}")
        else:
            raise Exception("Aucun onglet original enregistré")

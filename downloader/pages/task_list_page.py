import json
from .base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlencode
import time

class TaskListPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "https://tdbp519wv.corp.telma.mg/hermes360/Reporting/TasksList.aspx"
        # selector plus général : on ne dépend plus de l'attribut style exact
        self.sablier = (By.CSS_SELECTOR, '[id*="sablier"]')
        self.open_button = (
            By.CSS_SELECTOR,
            "[id='content'] [style*='index: 8'] [class='Cell'] a:not([onclick*='del'])[href*='xls']"
        )
        self.delete_history_button = (
            By.CSS_SELECTOR,
            "[class*='delete'][title='Supprimer une liste de rapports']"
        )
        self.delete_all = (
            By.CSS_SELECTOR,
            "[class='dialogFooter'] [class*='delete']"
        )

    def go_to_page(self, extra_params=None):
        if extra_params:
            query_string = urlencode(extra_params)
            url = f"{self.base_url}?{query_string}"
        else:
            url = self.base_url

        self._open_url(url)
        print(f"Page ouverte: {url}")

    def wait_for_download(self, timeout=420):
        """
        Attend que le sablier disparaisse.
        - timeout en secondes (WebDriverWait utilise des secondes).
        """
        # crée un WebDriverWait local avec le timeout demandé
        local_wait = WebDriverWait(self.driver, timeout, poll_frequency=getattr(self, "poll_frequency", 0.5))

        try:
            # méthode simple : invisibility_of_element_located gère display:none / visibility:hidden / disparition du DOM
            local_wait.until(EC.invisibility_of_element_located(self.sablier))
            print("✅ Téléchargement terminé ")
            return True
        except TimeoutException:
            # fallback si EC a échoué : interroger computed style via JS jusqu'à timeout
            end_time = time.time() + timeout
            while time.time() < end_time:
                try:
                    visible = self.driver.execute_script(
                        "let el = document.querySelector('[id*=\"sablier\"]');"
                        "if(!el) return false;"  # pas d'élément => invisible
                        "let cs = window.getComputedStyle(el);"
                        "return !(cs.visibility === 'hidden' || cs.display === 'none' || el.offsetParent === null);"
                    )
                except Exception:
                    visible = False

                if not visible:
                    print("✅ Téléchargement terminé (JS fallback).")
                    return True

                time.sleep(getattr(self, "poll_frequency", 0.5))

            # debug: afficher l'état des éléments sablier trouvés (utile pour investigation)
            try:
                elems = self.driver.find_elements(*self.sablier)
                for e in elems:
                    print("DEBUG sablier style:", e.get_attribute("style"),
                          "display:", e.value_of_css_property("display"),
                          "is_displayed():", e.is_displayed())
            except Exception:
                pass

            raise Exception(f"⏳ Le sablier est resté visible après {timeout} secondes.")

    def download_file(self):
        self._click(self.open_button)
    
    def download_file_1(self, section_title: str = "Rapport détaillé"):
        """
        Télécharge un fichier à partir de la cellule associée à `section_title`.
        """

        # Sérialiser la chaîne pour être sûre qu'elle soit valide en JS
        js_section_title = json.dumps(section_title)  # exemple => "Rapport détaillé"

        script = f"""
            let section_title = {js_section_title};
            console.log("Recherche du titre :", section_title);

            let cells = Array.from(document.querySelectorAll('[title="Rapport"] ~ div[class*="Cell"]'));
            let index = cells.findIndex(cell => cell.getAttribute('title') === section_title);

            if (index === -1) {{
                console.error(`Le titre "${{section_title}}" n'a pas été trouvé.`);
            }} else {{
                let download_elem = document.querySelectorAll('[title="Actions"] ~ div[class*="Cell"]');
                let tmp = download_elem[index];
                if (tmp) {{
                    let link = tmp.querySelector('a[href*=".xls"]');
                    if (link) {{
                        console.log("Lien trouvé :", link.href);
                        link.click();
                    }} else {{
                        console.error("Aucun lien trouvé avec le sélecteur : a[href*='.xls']");
                    }}
                }} else {{
                    console.error("Aucun élément trouvé à l'index " + index);
                }}
            }}
        """
        self.driver.execute_script(script)
        print(f"Téléchargement du fichier '{section_title}' lancé.")
        
    def click_delete_history_button(self):
        self._click(self.delete_history_button)
        
    def click_delete_all(self):
        self._click(self.delete_all)


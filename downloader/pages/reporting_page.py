import time
from .base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert



class ReportingPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://tapp1240wv.corp.telma.mg/hermes360/Admin/Launcher/Start.aspx"
        self.report_facturation_par_agent = (
            By.CSS_SELECTOR,
            "[id='Menu_ReportAgent'] [onclick=\"return parent.menu.select('AgentBillingReport2')\"]"
        )

    def go_to_page(self):
        self._open_url(self.url)

    def open_saved_reports(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            let menuGeneral = iframeDoc.querySelector("#Mnu_General");
            if (menuGeneral) menuGeneral.click();
            let listesRapportsSauvegardes = iframeDoc.querySelector('[onclick="return ShowLoadDialog()"]');
            if (listesRapportsSauvegardes) listesRapportsSauvegardes.click();
        """
        self.driver.execute_script(script)

    def click_rapport_detaille(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;          
            let iframe2 = iframeDoc.querySelector("iframe#scheduleListFrame");
            let iframeDoc2 = iframe2.contentDocument || iframe2.contentWindow.document;
            let rapportDetaille = iframeDoc2.querySelector(`[title="RD j-1"] span`)
            if(rapportDetaille) rapportDetaille.click()
        """
        self.driver.execute_script(script)

    def click_ouvrir(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            let loadButton = iframeDoc.querySelector(`[id="ButtonLoad"]`)
            if(loadButton) loadButton.click()  
        """
        self.driver.execute_script(script)

    def click_onglet_agent(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            let ongletAgent = iframeDoc.querySelector(`[value="Agents"]`)
            if(ongletAgent) ongletAgent.click() 
        """
        self.driver.execute_script(script)

    def select_all_agent(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            let selectAllAgent = iframeDoc.querySelector(`[id="select_Agents"]`)
            if(selectAllAgent) selectAllAgent.click() 
            if(selectAllAgent) selectAllAgent.click() 
        """
        self.driver.execute_script(script)

    def generate_button(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            let generateButton = iframeDoc.querySelector(`[id="generateButton"]`)
            if(generateButton) generateButton.click()   
        """
        self.driver.execute_script(script)
        
    def choose_date(self, date_from:str , date_to:str):
        script = f"""
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

            // Récupérer les éléments input pour "De" et "À"
            let input1 = iframeDoc.querySelector('.dateFrom .treeInput input');
            let input2 = iframeDoc.querySelector('.dateTo .treeInput input');

            // Mettre à jour la valeur de l'input
            // format de la date dd/mm/yyyy: 11/10/2025
            input1.value = "{date_from}"; 
            input2.value = "{date_to}";

            // Créer un événement 'change' (ou 'input', selon ce que l'application attend)
            let event = new Event('change', {{
                'bubbles': true,
                'cancelable': true
            }});

            // Déclencher l'événement sur les deux champs de date pour simuler une interaction utilisateur
            input1.dispatchEvent(event);
            input2.dispatchEvent(event);
        
        """
        try:
            self.driver.execute_script(script)
        except UnexpectedAlertPresentException:
            alert = Alert(self.driver)
            print("⚠️ Alerte détectée :", alert.text)
            alert.accept()  # ou .dismiss() selon ton besoin

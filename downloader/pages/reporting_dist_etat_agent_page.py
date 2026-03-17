from .base_page import BasePage


class ReportingDistEtatAgentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        
    def click_dist_etat_agent(self):
        script = """
            let iframe = document.querySelector("iframe#main");
            let iframeDoc = iframe.contentDocument || iframe.contentWindow.document;          
            let iframe2 = iframeDoc.querySelector("iframe#scheduleListFrame");
            let iframeDoc2 = iframe2.contentDocument || iframe2.contentWindow.document;
            let rapportDetaille = iframeDoc2.querySelector(`[title="EA j-1"] span`)
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
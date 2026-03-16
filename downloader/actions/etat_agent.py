import time
from downloader.pages.login_page import LoginPage
from downloader.pages.dashboard_page import DashboardPage
from downloader.pages.reporting_page import ReportingPage
from downloader.pages.task_list_page import TaskListPage
from downloader.pages.reporting_dist_etat_agent_page import ReportingDistEtatAgentPage
from urllib.parse import urlparse, parse_qs

def get_url_params(driver):
    current_url = driver.current_url
    parsed = urlparse(current_url)
    return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}

def run(driver):
    """Scénario : Télécharger un rapport"""
    login_page = LoginPage(driver)
    login_page.login()
    time.sleep(5)
    
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_page()
    dashboard_page.click_workspace()
    time.sleep(6)
    dashboard_page.click_reporting()
    time.sleep(30)
    dashboard_page.switch_to_new_tab()
    
    dist_etat_agent = ReportingDistEtatAgentPage(driver)
    reporting_page = ReportingPage(driver)
    reporting_page.open_saved_reports()
    time.sleep(2)
    dist_etat_agent.click_dist_etat_agent()
    time.sleep(2)
    reporting_page.click_ouvrir()
    time.sleep(2)
    dist_etat_agent.click_onglet_agent()
    time.sleep(2)
    dist_etat_agent.select_all_agent()
    time.sleep(4)
    dist_etat_agent.generate_button()
    
    params = get_url_params(driver)
    print("Paramètres récupérés:", params)

    # Ouvrir TaskListPage avec les mêmes paramètres
    task_list_page = TaskListPage(driver)
    task_list_page.go_to_page(extra_params=params)
    time.sleep(5)
    
    task_list_page.wait_for_download(timeout=300)
    
    task_list_page.download_file()
    time.sleep(15)
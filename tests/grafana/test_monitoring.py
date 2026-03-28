import allure
import pytest

from pages.grafana.dashboard_page_grafana import DashboardPageGrafana
from pages.locators.grafana.home_elements_grafana import HomeGrafanaElements


@allure.epic("Мониторинг EMON3")
@allure.suite("Мониторинг EMON3")
@pytest.mark.grafana
@pytest.mark.regress
class TestMonitoring:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_grafana) -> None:
        self.home_page = HomeGrafanaElements()
        self.dashboard_page = DashboardPageGrafana()
        self.names_logs = ["Count by code", "Elapsed time by code", "Elapsed time by method", "Table"]
        self.MONITORING_PRODUCTS = [
            "ZOOKEEPER",
            "MBUS",
            "KAFKA",
            "SLS TNT",
            "PIC",
            "OSA",
            "REFDATA",
            "WPSEC",
            "UNIBLP",
            "API GATEWAY",
            "CRAB",
            "GUS",
            "CNC",
            "SSO",
            "LIS",
            "EMON",
            "REPORT ENGINE",
            "SAM",
            "CPM",
            "EPM",
            "DGS",
            "UDB",
            "DMS",
            "PRAIM",
            "PSC",
            "PM",
            "FPM",
            "NBSS PORTAL",
            "APC",
            "CSM",
            "LAM",
            "NLM",
            "PASS",
            "NSG",
            "DLM",
            "OAPI",
            "NGINX",
            "APACHE",
            "TOMCAT",
            "ACCOUNTS TX",
            "ACCOUNTS BACKEND",
            "BALANCE BACKEND",
            "BALANCE MONITOR",
            "CDR SERVER",
            "CHF",
            "CHF CDS",
            "COUNTER TX",
            "HTTP GATEWAY",
            "INDENTIFICATION",
            "RECURRING CHARGE",
            "RESOURCE PROVIDER",
            "SUBS CACHE",
            "SUBS BACKEND",
            "RSC",
            "NMS",
            "NORD",
            "CLICKHOUSE",
            "TARANTOOL",
            "NEXYLLA",
        ]

    @allure.title("Проверка алертов")
    @allure.id(832741)
    def test_check_alerts(self):
        self.home_page.ALERTS_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.home_page.PRODUCTS_ALERTS.to_contain_text_in_any("Alerts: AIM")
        for index in range(self.home_page.PRODUCTS_ALERTS.elements_len()):
            self.home_page.PRODUCTS_ALERTS.to_contain_text_in_any("Alerts: AIM")
            self.home_page.PRODUCTS_ALERTS[index].click()
            self.dashboard_page.locators.ROW_DASHBOARD.wait_to_be_visible()
            self.dashboard_page.locators.NAV_MENU[0].click()

    @allure.title("Проверка логирования")
    @allure.id(832739)
    def test_check_logs(self):
        self.home_page.LOGS_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.home_page.PRODUCTS_LOGS[0].click()
        self.dashboard_page.locators.NAME_GRAPH.wait_for_text_in_all(self.names_logs)
        self.dashboard_page.locators.FILTER_BTN.wait_to_be_visible()
        self.dashboard_page.open_filter_and_choose_option_by_index(1, 0)
        self.dashboard_page.open_filter_and_choose_option_by_index(2, 0)
        self.dashboard_page.locators.NAV_MENU[0].click()
        self.home_page.PRODUCTS_LOGS.wait_to_be_visible(timeout=15000)
        self.home_page.PRODUCTS_LOGS[1].click()
        self.dashboard_page.locators.CONTENT_PANEL.wait_to_be_visible(timeout=15000)
        self.dashboard_page.locators.LOG_MENU.wait_to_be_visible(timeout=80000)
        self.dashboard_page.locators.FILTER_PRODUCT_LOGS.select_by_value("GUS")
        self.dashboard_page.locators.FILTER_APPLICATION_LOGS.select_by_value("GUS_RERATING")
        self.dashboard_page.locators.FILTER_LVL_LOGS.select_by_value("INFO")
        self.dashboard_page.locators.BACKWARD_TIME.click()
        self.dashboard_page.locators.LOG_MENU.wait_to_be_visible(timeout=80000)

    @allure.title("Проверка мониторинга k8s")
    @allure.id(832740)
    def test_check_k8s(self):
        self.home_page.K8S_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.home_page.PRODUCTS_K8S.to_contain_text_in_any("Kubernetes / System / CoreDNS")
        for index in range(self.home_page.PRODUCTS_K8S.elements_len()):
            self.home_page.PRODUCTS_K8S.to_contain_text_in_any("Kubernetes / System / CoreDNS")
            self.home_page.PRODUCTS_K8S[index].click()
            self.dashboard_page.locators.NAME_GRAPH.wait_to_be_visible()
            self.dashboard_page.locators.NAV_MENU[0].click()

    @allure.title("Проверка мониторинга инфраструктуры")
    @allure.id(832737)
    def test_check_monitoring(self):
        self.home_page.SOLUTION_MONITORING_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.home_page.PRODUCTS_MONITORING[1].click()
        self.dashboard_page.locators.NAME_GRAPH.wait_to_be_visible()
        self.dashboard_page.locators.NAME_GRAPH.to_have_text_list(self.MONITORING_PRODUCTS)
        self.dashboard_page.open_product_on_link_and_close_tab(0)
        self.dashboard_page.open_product_on_link_and_close_tab(15)
        self.dashboard_page.open_product_on_link_and_close_tab(1)

    @allure.title("Проверка мониторинга приложений")
    @allure.id(832742)
    def test_monitoring_application(self):
        self.home_page.APPLICATION_MONITORING_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.home_page.APPLICATION_MONITORING_PRODUCTS.to_contain_text_in_any("Apache")
        for index in range(self.home_page.APPLICATION_MONITORING_PRODUCTS.elements_len()):
            self.home_page.APPLICATION_MONITORING_PRODUCTS.to_contain_text_in_any("Apache")
            self.home_page.APPLICATION_MONITORING_PRODUCTS[index].click()
            self.dashboard_page.locators.ROW_DASHBOARD.wait_to_be_visible()
            self.dashboard_page.locators.NAV_MENU[0].click()

    @allure.title("Проверка мониторинга хостов")
    @allure.id(832738)
    def test_monitoring_hosts(self):
        self.home_page.MONITORING_HOSTS_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.home_page.MONITORING_HOSTS_PRODUCT[2].click()
        self.dashboard_page.locators.ROW_DASHBOARD.wait_to_be_visible(timeout=15000)
        self.dashboard_page.open_setting_host_monitoring_and_choose_type(0)
        self.dashboard_page.open_setting_host_monitoring_and_choose_type(1)
        self.dashboard_page.open_setting_host_monitoring_and_choose_type(2)

import allure

from pages.base_page import BasePage
from pages.locators.grafana.dashboard_elements_grafana import DashboardGrafanaElements


class DashboardPageGrafana(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.locators = DashboardGrafanaElements()

    @allure.step("Открыть продукт с индексом {index_product} и проверить наличие графиков")
    def open_product_on_link_and_close_tab(self, index_product: int) -> None:
        self.locators.LINK_PRODUCT[index_product].click()
        self.locators.NAME_GRAPH.wait_to_be_visible()
        self.close_page_by_index(1)

    @allure.step("Открыть настройка с выбором хоста мониторинга и выбрать вариант с индексом {index_type}")
    def open_setting_host_monitoring_and_choose_type(self, index_type: int) -> None:
        self.locators.HOST_MONITORING.click()
        self.locators.TYPE_HOST_MONITORING[index_type].wait_to_be_visible()
        self.locators.TYPE_HOST_MONITORING[index_type].click()
        self.locators.ROW_DASHBOARD.wait_to_be_visible()
        self.close_page_by_index(1)

    @allure.step("Открыть фильтр с индексом {filter_index} и выбрать опцию с индексом {option_index}")
    def open_filter_and_choose_option_by_index(self, filter_index: int, option_index: int) -> None:
        self.locators.FILTER_BTN[filter_index].click()
        self.locators.NAMES_PRODUCT_FILTER[option_index].click()
        self.locators.CONFIRM_FILTER_BTN.click()

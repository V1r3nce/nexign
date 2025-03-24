from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import Element, ElementsList


class Consumption(DynamicForms):
    """Страница 'Потребление'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.SUBSCRIBER_NUM = Element("div.scrollable-body:nth-child(2) div>p", "Номер абонента", self.page)

        # TABS
        self.TABS_LIST = ElementsList(".ant-tabs-nav-list .ant-tabs-tab", "Список вкладок абонента", self.page)

        self.REMAINING_VOLUMES_LIST = ElementsList("div.scrollable-body:nth-child(3) div:nth-child(1)>p:nth-child(1)",
                                                   "Значение остатков объёмов абонента", self.page)

        # TRAFFIC
        self.SWITCH_BTN_LIST = ElementsList("button[role='switch']", "Список кнопок-переключателей", self.page)

        # ACCRUALS
        self.ACCRUALS_TABPANEL_BTNS = ElementsList("[role='tabpanel'] div:nth-child(1)>div>button",
                                                   "Список кнопок 'Начисления'", self.page)
        self.SWITCH_LIST = ElementsList("ul li button", "Список переключателей", self.page)
        self.ACCRUALS_TITLE_LIST = ElementsList(".ant-table-column-title", "Список наименований столбцов", self.page)
        self.ACCRUALS_SPINNING = ElementsList(".ant-spin-nested-loading .ant-spin-spinning svg", "Лоадер", self.page)

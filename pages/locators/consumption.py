from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class Consumption(BaseElements):
    """Страница 'Потребление'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SUBSCRIBER_NUM = ElementsList("[class*=scrollable-body] p", "Номер абонента", self.page)
        self.TABS_LIST = ElementsList(".ant-tabs-nav-list .ant-tabs-tab", "Список вкладок абонента", self.page)

        # VOLUMES
        self.VOLUME = ElementsList("[id*=panel-volumes] div:not([class]):not([style])", "Объем абонента", self.page)
        self.VOLUME_REMAINING = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(1)>p:nth-child(1)",
            "Значение остатка объёма абонента",
            self.page,
        )
        self.VOLUME_ACTIVE_PERIOD = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(1)>p:nth-child(3)",
            "Срок действия объёма",
            self.page,
        )
        self.VOLUME_NAME = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(2):not([color])>div:nth-child(1)",
            "Название сервиса объёма (Интернет/Минуты/SMS)",
            self.page,
        )
        self.VOLUME_PRODUCT = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(2)>p",
            "Название продукта объёма",
            self.page,
        )

        self.TITLE_VOLUME_NAME = Element("[id*=panel-volumes] h4", "Заголовок - Название объема", self.page)
        self.VOLUME_PROPERTY = ElementsList(
            "[id*=panel-volumes] div:nth-child(2) .platform-scrollable > div > div",
            "Свойство объёма",
            self.page,
        )

        # TRAFFIC
        self.SWITCH_BTN_LIST = ElementsList("button[role='switch']", "Список кнопок-переключателей", self.page)

        # ACCRUALS
        self.ACCRUALS_TABPANEL_BTNS = ElementsList(
            "//*[contains(@class, 'custom-table')]/div[1] //button", "Список кнопок 'Начисления'", self.page
        )
        self.UPDATE_ACCRUAL_LIST_BTN = Element(
            "(//*[contains(@class, 'custom-table')]/div[1] //button)[2]", "Кнопка 'Обновить начисления'", self.page
        )
        self.CLEAR_FILTER_BTN = Element(
            "(//*[contains(@class, 'custom-table')]/div[1] //button)[3]", "Кнопка 'Очистить все фильтры'", self.page
        )
        self.LINKED_INQUIRES_BTN = Element(
            "(//*[contains(@class, 'custom-table')]/div[1] //button)[5]", "Кнопка 'Связать с заявкой'", self.page
        )
        self.SWITCH_LIST = ElementsList("ul li button", "Список переключателей", self.page)
        self.ACCRUALS_TITLE_LIST = ElementsList(".ant-table-column-title", "Список наименований столбцов", self.page)
        self.ACCRUAL_LIST = ElementsList("[role='tabpanel'] tbody tr", "Список начислений", self.page)
        self.ACCRUAL_CHECKBOXES = ElementsList("[role='tabpanel'] tr td:nth-child(1)", "Чекбоксы начислений", self.page)
        self.LINKED_INQUIRES = ElementsList("[role='tabpanel'] tr td:nth-child(12)", "Связанные заявки", self.page)
        self.LINKED_INQUIRES_LIST_BTN = ElementsList(
            "[role='tabpanel'] tr td:nth-child(12) a", "Кнопка 'Список связанных заявок'", self.page
        )
        self.ACCRUALS_SPINNING = ElementsList(".ant-spin-nested-loading .ant-spin-spinning svg", "Лоадер", self.page)

        self.CHARGES_BILLING_NUM_LIST = ElementsList(
            "tr>td:nth-child(19)>div", "Список значений поля 'Поле биллингового счета' начислений", self.page
        )
        self.CHARGES_INVOICE_DATE_LIST = ElementsList(
            "tr>td:nth-child(20)>div", "Список значений поля 'Дата выставления счета' начислений", self.page
        )
        self.TRAFFIC_BILLING_NUM_LIST = ElementsList(
            "tr>td:nth-child(28)>div", "Список значений поля 'Поле биллингового счета'", self.page
        )
        self.TRAFFIC_INVOICE_DATE_LIST = ElementsList(
            "tr>td:nth-child(29)>div", "Список значений поля 'Дата выставления счета абоненту'", self.page
        )

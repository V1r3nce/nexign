from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class BillingAccounts(BaseElements):
    """Страница 'Биллинговые счета'"""

    def __init__(self, page: Page):
        super().__init__(page)

        # LEFT_NAV
        self.REFRESH_BTN = Element(
            "(//*[contains(@class, 'platform-scrollable')]/div/div[2]/div[1] //button)[1]",
            "Кнопка 'Обновить'",
            self.page,
        )
        self.BILLING_LAUNCH_BTN = Element(
            "button[variant='default']:nth-child(6)", "Кнопка 'Запуск биллинга'", self.page
        )
        self.BILLING_TASKS_BTN = Element(
            "button[title='Список заданий биллинга']", "Кнопка 'Список заданий биллинга'", self.page
        )
        self.ACCOUNT_NUMS_LIST = ElementsList(
            ".scrollable-body>div div:first-child>p", "Список биллинговых счетов", self.page
        )

        # BILLING_ACCOUNT
        self.BILLING_BTNS = ElementsList(
            ".platform-scrollable div:nth-child(1)>div>div:nth-of-type(2) [variant='default']",
            "Список кнопок биллинга",
            self.page,
        )
        self.BILLING_PROPERTIES = ElementsList(
            "//*[@role='tabpanel'] //*[@overflow='scroll']/div/div/div[1]",
            "Список наименований свойств биллинга",
            self.page,
        )
        self.PROPERTIES_TAB = Element("[id*=tab-properties]", "Таб 'Свойства'", self.page)
        self.DETAILS_TAB = Element("[id*=tab-details]", "Таб 'Детали'", self.page)

        # PROPERTIES
        self.BILLING_PROPERTY_VALUES = ElementsList(
            "//*[@role='tabpanel'] //*[@overflow='scroll']/div/div/div[2]", "Список значений свойств биллинга", self.page
        )
        self.LINKED_CLAIM_LIST_BTN = Element("//*[@role='tabpanel'] //a", "Кнопка 'Список связанных заявок'", self.page)

        # DETAILS
        self.UPDATE_DETAILS_LIST_BTN = Element(
            "(//*[contains(@id, 'panel-details')] //button)[2]", "Кнопка 'Обновить детали'", self.page
        )
        self.LINKED_INQUIRES_BTN = Element(
            "(//*[contains(@id, 'panel-details')] //button)[4]", "Кнопка 'Связать с заявкой'", self.page
        )
        self.DETAIL = ElementsList("[id*=panel-details] tbody tr", "Деталь биллингового счета", self.page)
        self.DETAIL_CHECKBOX = ElementsList(
            "[id*=panel-details]  tr td:nth-child(1)", "Чекбокс выбора детали", self.page
        )
        self.LINKED_INQUIRES = ElementsList("[id*=panel-details]  tr td:nth-child(13)", "Связанные заявки", self.page)
        self.LINKED_INQUIRES_LIST_BTN = ElementsList(
            "[id*=panel-details]  tr td:nth-child(13) a", "Кнопка 'Список связанных заявок'", self.page
        )

        # BILLING_TASKS
        self.TASK_TYPE_LIST = ElementsList("tr td:nth-child(2) div", "Список типов заданий", self.page)
        self.TASK_STATUS_LIST = ElementsList("tr td:nth-child(4) p", "Список статусов", self.page)
        self.TASKS_CLOSE_BTN = Element("#_cancel-button", "Кнопка 'Закрыть'", self.page)

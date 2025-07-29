from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class Consumption(BaseElements):
    """Страница 'Потребление'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SUBSCRIBER_NUM = ElementsList("[class*=scrollable-body] div:not([class]) p", "Номер абонента", self.page)
        self.TABS_LIST = ElementsList(
            "[id*=panel-consuming] [class*=tabs-nav-list] [role=tab]", "Список вкладок абонента", self.page
        )

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
        self.TRAFFIC_LOADER = Element(
            "[id*=panel-calls] [data-icon=Spinner]", "Лоадер на странице 'Начисления'", self.page
        )
        self.SWITCH_BTN_LIST = ElementsList(
            "[id*=panel-calls] button[role='switch']", "Список кнопок-переключателей", self.page
        )
        self.TRAFFIC_TITLE_LIST = ElementsList(
            "[id*=panel-calls] [class*=table-header-column-title] div", "Список наименований столбцов", self.page
        )
        self.TRAFFIC_BILLING_NUM_LIST = ElementsList(
            "[id*=panel-calls] tr td:nth-child(28)", "Список значений поля 'Номер биллингового счета'", self.page
        )
        self.TRAFFIC_INVOICE_DATE_LIST = ElementsList(
            "[id*=panel-calls] tr td:nth-child(29)", "Список значений поля 'Дата выставления счета абоненту'", self.page
        )

        # ACCRUALS
        self.ACCRUAL_LOADER = Element(
            "[id*=panel-charges] [data-icon=Spinner]", "Лоадер на странице 'Начисления'", self.page
        )
        self.UPDATE_ACCRUAL_LIST_BTN = Element(
            "[id*=panel-charges] [data-icon=Refresh]", "Кнопка 'Обновить начисления'", self.page
        )
        self.CLEAR_FILTER_BTN = Element(
            "[id*=panel-charges] [data-icon=FilterRemove]", "Кнопка 'Очистить все фильтры'", self.page
        )
        self.LINKED_INQUIRES_BTN = Element(
            "[id*=panel-charges] [data-icon=AddLink]", "Кнопка 'Связать с заявкой'", self.page
        )
        self.MORE_ACTIONS_BTN = Element(
            "[id*=panel-charges] [data-icon=MoreVert]", "Кнопка меню выпадающего списка", self.page
        )
        self.SWITCH_SHOW_BILLING = Element(
            "ul li[data-menu-id*=showBilling] button", "Переключатель 'Показать данные о биллинге'", self.page
        )

        self.ACCRUALS_TITLE_LIST = ElementsList(
            "[id*=panel-charges] [class*=table-header-column-title] div", "Список наименований столбцов", self.page
        )
        self.ACCRUAL_LIST = ElementsList("[id*=panel-charges] [class*=table-row]", "Список начислений", self.page)
        self.ACCRUAL_CHECKBOXES = ElementsList(
            "[id*=panel-charges] tr td:nth-child(1) label", "Чекбоксы начислений", self.page
        )
        self.ACCRUAL_SUM = ElementsList("[id*=panel-charges] tr td:nth-child(3)", "Значение столбца 'Сумма'", self.page)
        self.ACCRUAL_TYPE = ElementsList(
            "[id*=panel-charges] tr td:nth-child(8)", "Значение столбца 'Тип начисления'", self.page
        )
        self.LINKED_INQUIRES = ElementsList("[id*=panel-charges] tr td:nth-child(12)", "Связанные заявки", self.page)
        self.LINKED_INQUIRES_LIST_BTN = ElementsList(
            "[id*=panel-charges] tr td:nth-child(12) a", "Кнопка 'Список связанных заявок'", self.page
        )

        self.CHARGES_BILLING_NUM_LIST = ElementsList(
            "[id*=panel-charges] tr td:nth-child(19)",
            "Список значений поля 'Номер биллингового счета' начислений",
            self.page,
        )
        self.CHARGES_INVOICE_DATE_LIST = ElementsList(
            "[id*=panel-charges] tr td:nth-child(20)",
            "Список значений поля 'Дата выставления счета' начислений",
            self.page,
        )

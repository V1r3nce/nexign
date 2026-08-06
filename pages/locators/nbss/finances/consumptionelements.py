from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList, SelectDifferentRoot


class ConsumptionElements(BaseElements):
    """Страница 'Потребление'"""

    def __init__(self) -> None:
        super().__init__()

        self.SUBSCRIBER_SWITCH = ElementsList("label[class*=radio-button]", "Переключатель 'Абоненты/Без абонента'")
        self.SUBSCRIBER_VIEW_MODE = SelectDifferentRoot(
            "[data-testid*=Consuming][data-testid*=select]:has(input[id*=rc_select])", "Дропдаун Режим"
        )
        self.SUBSCRIBER_NUM = ElementsList("[class*=scrollable-body] div:not([class]) p", "Номер абонента")
        self.TABS_LIST = ElementsList(
            "[id*=panel-consuming] [class*=tabs-nav-list] [role=tab]", "Список вкладок абонента"
        )
        self.CHARGES_TAB = Element("[data-node-key*=charges][class*=tab] > div", "Таб Начисления")
        self.TRAFFIC_TAB = Element("[data-node-key*=calls][class*=tab] > div", "Таб Трафик")
        self.VOLUMES_TAB = Element("[data-node-key*=volumes][class*=tab] > div", "Таб Объемы")

        # VOLUMES
        self.VOLUME = ElementsList("[id*=panel-volumes] div:not([class]):not([style])", "Объем абонента")
        self.VOLUME_REMAINING = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(1)>p:nth-child(1)",
            "Значение остатка объёма абонента",
        )
        self.VOLUME_ACTIVE_PERIOD = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(1)>p:nth-child(3)",
            "Срок действия объёма",
        )
        self.VOLUME_NAME = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(2):not([color])>div:nth-child(1)",
            "Название сервиса объёма (Интернет/Минуты/SMS)",
        )
        self.VOLUME_PRODUCT = ElementsList(
            "[id*=panel-volumes] div:not([class]):not([style]) div:nth-child(2)>p",
            "Название продукта объёма",
        )

        self.TITLE_VOLUME_NAME = Element("[id*=panel-volumes] h4", "Заголовок - Название объема")
        self.VOLUME_PROPERTY = ElementsList(
            "[id*=panel-volumes] div:nth-child(2) .platform-scrollable > div > div",
            "Свойство объёма",
        )

        # TRAFFIC
        self.TRAFFIC_LOADER = Element("[id*=panel-calls] [data-icon=Spinner]", "Лоадер на странице 'Начисления'")
        self.SWITCH_BTN_LIST = ElementsList("[id*=panel-calls] button[role='switch']", "Список кнопок-переключателей")
        self.TRAFFIC_TITLE_LIST = ElementsList(
            "[id*=panel-calls] [class*=table-header-column-title] div", "Список наименований столбцов"
        )
        self.TRAFFIC_BILLING_NUM_LIST = ElementsList(
            "[id*=panel-calls] tr td:nth-child(28)", "Список значений поля 'Номер биллингового счета'"
        )
        self.TRAFFIC_INVOICE_DATE_LIST = ElementsList(
            "[id*=panel-calls] tr td:nth-child(29)", "Список значений поля 'Дата выставления счета абоненту'"
        )

        # ACCRUALS
        self.ACCRUAL_LOADER = ElementsList("[id*=panel-charges] [data-icon=Spinner]", "Лоадер на странице 'Начисления'")
        self.UPDATE_ACCRUAL_LIST_BTN = Element("[id*=panel-charges] [data-icon=Refresh]", "Кнопка 'Обновить начисления'")
        self.CLEAR_FILTER_BTN = Element("[id*=panel-charges] [data-icon=FilterRemove]", "Кнопка 'Очистить все фильтры'")
        self.LINKED_INQUIRES_BTN = Element("[id*=panel-charges] [data-icon=AddLink]", "Кнопка 'Связать с заявкой'")
        self.MORE_ACTIONS_BTN = Element("[id*=panel-charges] [data-icon=MoreVert]", "Кнопка меню выпадающего списка")
        self.SWITCH_SHOW_BILLING = Element(
            "ul li[data-menu-id*=showBilling] button", "Переключатель 'Показать данные о биллинге'"
        )

        self.ACCRUALS_TITLE_LIST = ElementsList(
            "[id*=panel-charges] [class*=table-header-column-title] div", "Список наименований столбцов"
        )
        self.ACCRUAL_LIST = ElementsList("div[class*=tbody] [class*=table-row]", "Список начислений")
        self.ACCRUAL_CHECKBOXES = ElementsList("div[class*=tbody] input[class*=checkbox-input]", "Чекбоксы начислений")
        self.ACCRUAL_DATES = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(2)", "'Дата события' начисления"
        )
        self.ACCRUAL_SUMS = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(3)", "Значение столбца 'Сумма'"
        )
        self.ACCRUAL_PRODUCT_NAMES = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(8)", "Значение столбца 'Продукт'"
        )
        self.ACCRUAL_TYPE = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(7)", "Значение столбца 'Тип начисления'"
        )
        self.LINKED_INQUIRES = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(13)", "Связанные заявки"
        )

        self.CHARGES_BILLING_NUM_LIST = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(17)",
            "Список значений поля 'Номер биллингового счета' начислений",
        )
        self.CHARGES_INVOICE_DATE_LIST = ElementsList(
            "div[class*=tbody] [class*=table-row] [class*=table-cell]:nth-child(18)",
            "Список значений поля 'Дата выставления счета' начислений",
        )

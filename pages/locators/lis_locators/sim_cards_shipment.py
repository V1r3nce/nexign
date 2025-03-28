from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class SimCardShipmentElementsLis(BaseElementsLis):
    """Страница Отгрузка SIM-карт LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.TITLE = Element("h2.content-section-header", "Заголовок страницы", self.page)

        # Верхние кнопки
        self.SHIPMENT_BTN = Element("ps-button[icon='shipping-sim-inverted']", "Кнопка 'Отгрузить'", self.page)
        self.SHIPMENT_BY_IMSI_RANGE_BTN = Element(
            "ps-list-item[ng-click*='IMSIFromForm']", "Кнопка 'Отгрузить/Отгрузить на ГС по диапазону IMSI'", self.page
        )
        self.SHIPMENT_BY_IMSI_FILE_BTN = Element(
            "ps-list-item[ng-click*='IMSIFromFile']",
            "Кнопка 'Отгрузить/Отгрузить на ГС по списку IMSI из файла'",
            self.page,
        )
        self.SHIPMENT_BACK_BTN = Element("ps-button[icon='shipping-sim-back']", "Кнопка 'Вернуть на ГС'", self.page)
        self.REFRESH_BTN = Element("ps-button[ng-click*='refreshGrid']", "Кнопка 'Обновить'", self.page)
        self.EXPORT_BTN = Element("ps-button[ng-click*='csvExport']", "Кнопка 'Выгрузить в файл'", self.page)

        # Строки таблицы
        self.OPERATIONS_IDS = ElementsList(
            "tr.n-grid__row td:nth-child(2) a", "Значения столбца 'ID операции'", self.page
        )
        self.OPERATIONS_TYPES = ElementsList(
            "tr.n-grid__row td:nth-child(3)", "Значения столбца 'Тип операции'", self.page
        )
        self.PROCES_START_FIELDS = ElementsList(
            "tr.n-grid__row td:nth-child(4)", "Значения столбца 'Начало выполнения'", self.page
        )
        self.PROCES_END_FIELDS = ElementsList(
            "tr.n-grid__row td:nth-child(5)", "Значения столбца 'Конец выполнения'", self.page
        )
        self.STATUS_FIELDS = ElementsList("tr.n-grid__row td:nth-child(6)", "Значения столбца 'Статус'", self.page)

        # Модальное окно 'Отгрузка SIM'
        self.QUANTITY_INPUT = Element("[ng-model*='localModel.count']", "Поле ввода 'Количество штук'", self.page)
        self.IMSI_START_INPUT = Element(
            "[ng-model*='localModel.startIMSI']", "Поле ввода 'Начальное значение IMSI'", self.page
        )
        self.IMSI_END_INPUT = Element(
            "[ng-model*='localModel.endIMSI']", "Поле ввода 'Конечное значение IMSI'", self.page
        )
        self.TYPE_DROP_DOWN_BTN = Element(
            "[ng-if*='PARTNER_2_PARTNER'] ps-button[ng-if*='options.showDropDownButton']",
            "Открыть выбор 'Тип'",
            self.page,
        )
        self.TEST_TYPE_OPTION = Element("ps-list-item[user-value*='TEST']", "Опция 'Тип' Тестовая", self.page)
        self.PARTNER_NAME_BLOCK = Element("[simple-model*='partnerModel']", "Блок 'Наименование партнера'", self.page)
        self.PARTNER_NAME_DROP_DOWN_BTN = Element(
            "[simple-model*='partnerModel'] ps-button[ng-if*='options.showDropDownButton']",
            "Открыть выбор 'Наименование партнера'",
            self.page,
        )
        self.PARTNER_NAMES_OPTIONS = ElementsList(
            "ps-list-item[ng-repeat-start*='item.agentId']", "Опции 'Наименование партнера'", self.page
        )
        self.MOVE_BTN = Element("ps-button[on-submit*='createSimMovement']", "Кнопка 'Переместить'", self.page)
        self.CANCEL_BTN = Element("ps-button[ng-click*='dialogHide']", "Кнопка 'Отменить'", self.page)

        # Подробности операции
        self.OPERATION_DETAIL_TYPE = Element(
            "[ng-bind*='model.tasks.current.type.name']", "Тип операции 'Подробности операции'", self.page
        )
        self.OPERATION_DETAIL_PARTNER = Element(
            "[ng-bind*='model.tasks.current.params.partner.name']",
            "Наименование партнера 'Подробности операции'",
            self.page,
        )

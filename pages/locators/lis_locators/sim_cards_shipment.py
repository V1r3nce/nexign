from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class SimCardShipmentElementsLis(BaseElementsLis):
    """Страница Отгрузка SIM-карт LIS"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER
        self.TITLE = Element("h2.content-section-header", "Заголовок страницы")

        # Верхние кнопки
        self.SHIPMENT_BTN = Element("ps-button[icon='shipping-sim-inverted']", "Кнопка 'Отгрузить'")
        self.SHIPMENT_BY_IMSI_RANGE_BTN = Element(
            "ps-list-item[ng-click*='IMSIFromForm']", "Кнопка 'Отгрузить/Отгрузить на ГС по диапазону IMSI'"
        )
        self.SHIPMENT_BY_IMSI_FILE_BTN = Element(
            "ps-list-item[ng-click*='IMSIFromFile']",
            "Кнопка 'Отгрузить/Отгрузить на ГС по списку IMSI из файла'",
        )
        self.SHIPMENT_BACK_BTN = Element("ps-button[icon='shipping-sim-back']", "Кнопка 'Вернуть на ГС'")
        self.REFRESH_BTN = Element("ps-button[ng-click*='refreshGrid']", "Кнопка 'Обновить'")
        self.EXPORT_BTN = Element("ps-button[ng-click*='csvExport']", "Кнопка 'Выгрузить в файл'")

        # Строки таблицы
        self.OPERATIONS_IDS = ElementsList("tr.n-grid__row td:nth-child(2) a", "Значения столбца 'ID операции'")
        self.OPERATIONS_TYPES = ElementsList("tr.n-grid__row td:nth-child(3)", "Значения столбца 'Тип операции'")
        self.PROCES_START_FIELDS = ElementsList("tr.n-grid__row td:nth-child(4)", "Значения столбца 'Начало выполнения'")
        self.PROCES_END_FIELDS = ElementsList("tr.n-grid__row td:nth-child(5)", "Значения столбца 'Конец выполнения'")
        self.STATUS_FIELDS = ElementsList("tr.n-grid__row td:nth-child(6)", "Значения столбца 'Статус'")

        # Модальное окно 'Отгрузка SIM'
        self.QUANTITY_INPUT = Element("[ng-model*='localModel.count']", "Поле ввода 'Количество штук'")
        self.IMSI_START_INPUT = Element("[ng-model*='localModel.startIMSI']", "Поле ввода 'Начальное значение IMSI'")
        self.IMSI_END_INPUT = Element("[ng-model*='localModel.endIMSI']", "Поле ввода 'Конечное значение IMSI'")
        self.TYPE_DROP_DOWN_BTN = Element(
            "[ng-if*='PARTNER_2_PARTNER'] ps-button[ng-if*='options.showDropDownButton']",
            "Открыть выбор 'Тип'",
        )
        self.TEST_TYPE_OPTION = Element("ps-list-item[user-value*='TEST']", "Опция 'Тип' Тестовая")
        self.PARTNER_NAME_BLOCK = Element("[simple-model*='partnerModel']", "Блок 'Наименование партнера'")
        self.PARTNER_NAME_DROP_DOWN_BTN = Element(
            "[simple-model*='partnerModel'] ps-button[ng-if*='options.showDropDownButton']",
            "Открыть выбор 'Наименование партнера'",
        )
        self.PARTNER_NAMES_OPTIONS = ElementsList(
            "ps-list-item[ng-repeat-start*='item.agentId']", "Опции 'Наименование партнера'"
        )
        self.MOVE_BTN = Element("ps-button[on-submit*='createSimMovement']", "Кнопка 'Переместить'")
        self.CANCEL_BTN = Element("ps-button[ng-click*='dialogHide']", "Кнопка 'Отменить'")

        # Подробности операции
        self.OPERATION_DETAIL_TYPE = Element(
            "[ng-bind*='model.tasks.current.type.name']", "Тип операции 'Подробности операции'"
        )
        self.OPERATION_DETAIL_PARTNER = Element(
            "[ng-bind*='model.tasks.current.params.partner.name']",
            "Наименование партнера 'Подробности операции'",
        )

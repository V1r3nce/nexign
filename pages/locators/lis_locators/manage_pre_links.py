from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element


class ManagePreLinksLis(BaseElementsLis):
    """Страница Управление предсвязками LIS"""

    def __init__(self) -> None:
        super().__init__()

        # TAB Изготовление SIM-карт
        self.CREATE_BTN = Element("div[icon*='plus'] ps-button", "Кнопка 'Создать'")
        self.BY_IMSI_RANGE_BTN = Element("[ng-click*=\"showMaster('IMSIFromForm')\"]", "Кнопка 'по диапазону IMSI'")
        self.BY_IMSI_RANGE_FROM_FILE_BTN = Element(
            "[ng-click*=\"showMaster('IMSIFromFile')\"]", "Кнопка 'по списку IMSI из файла'"
        )
        self.BY_IMSI_MSISDN_FROM_FILE_BTN = Element(
            "[ng-click*='IMSI_MSISDNFromFile']", "Кнопка 'по списку IMSI-MSISDN из файла'"
        )
        self.CANCEL_TASK_BTN = Element("[icon*='block-white'] ps-button", "Кнопка 'Аннулировать'")
        self.CANCEL_BY_IMSI_RANGE_BTN = Element(
            "[ng-click*=\"showUndoMaster('IMSIFromForm')\"]", "Кнопка 'Аннулировать по диапазону IMSI'"
        )
        self.CANCEL_BY_IMSI_RANGE_FROM_FILE_BTN = Element(
            "[ng-click*=\"showUndoMaster('IMSIFromFile')\"]", "Кнопка 'Аннулировать по списку IMSI из файла'"
        )
        self.REFRESH_BTN_CREATE_SIM = Element("[ng-click*='refreshGrid']", "Кнопка 'Обновить'")

        # Модальное окно Создание предсвязок
        self.TAKE_CITY_LINKED_ONLY_CHECKBOX = Element(
            "[ng-model*='localModel.params.linkedWithLandlineOnly'] > span:first-child",
            "Чекбокс 'Брать номера только с состоянием Связан с городским'",
        )

        # Подробности операции
        self.DETAILS_COMMUTATOR = Element("[ng-bind*='params.equipment.name']", "Коммутатор 'Подробности операции'")
        self.DETAILS_NUMS_TYPE = Element("[ng-bind*='phoneNumberType.name']", "Тип нумерации 'Подробности операции'")
        self.DETAILS_GOAL = Element("[ng-bind*='phoneNumberPurpose.name']", "Цель использования 'Подробности операции'")

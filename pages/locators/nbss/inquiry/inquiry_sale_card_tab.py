from pages.base_page import BasePage
from pages.ui_elements import Element, ElementsList, SelectWithId


class InquirySaleCardTab(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.ATTRIBUTE_GROUP_TITLES = ElementsList(
            ".ant-tabs-tabpane-active h4, .ant-tabs-tabpane-active [class*=collapse-header-text]",
            "Заголовки групп атрибутов и коллапсов активной вкладки заявки",
        )
        self.ATTRIBUTES_EDIT_BTN = Element(
            "[data-testid*=InquiryAttributes][data-testid*=editButton]", "Кнопка 'Редактировать' атрибутов заявки"
        )
        self.ATTRIBUTES_SAVE_BTN = Element(
            ".ant-tabs-tabpane-active button[class*=btn-primary]", "Кнопка 'Сохранить' атрибутов заявки"
        )
        self.ATTRIBUTES_DESCRIPTION = Element("textarea[id$=description]", "Поле 'Описание' атрибутов заявки")
        self.ATTRIBUTES_DESCRIPTION_VALUE = Element(
            ".ant-tabs-tabpane-active [class*=collapse-item]:first-child [class*=collapse-content]",
            "Значение поля 'Описание' атрибутов заявки",
        )
        self.ATTRIBUTES_AGREEMENT = SelectWithId("saleAgreement", "Поле 'Договор' атрибутов заявки")
        self.ATTRIBUTES_ACCOUNT = SelectWithId("saleAccount", "Поле 'Лицевой счет' атрибутов заявки")

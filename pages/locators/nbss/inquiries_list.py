from pages.locators.nbss.inquiries_elements import InquiriesElements
from pages.ui_elements import Element, ElementsList


class InquiriesListElements(InquiriesElements):
    """Страница "Заявки" /inquiry-list/"""

    def __init__(self) -> None:
        super().__init__()
        self.TABLE_VIEW = Element("(//div[contains(@class, 'ant-radio-group')])[1] /label[1]", "Таблицей")
        self.LIST_VIEW = Element("(//div[contains(@class, 'ant-radio-group')])[1] /label[2]", "Списком")

        self.ALL_INQUIRIES_BTN = Element("(//div[contains(@class, 'ant-radio-group')])[2] /label[1]", "Все заявки")
        self.IN_PROCESS_BTN = Element("(//div[contains(@class, 'ant-radio-group')])[2] /label[2]", "В обработке")
        self.IN_QUEUE_BTN = Element("(//div[contains(@class, 'ant-radio-group')])[2] /label[3]", "В очередях")

        self.SEARCH_FIELD = Element(
            ".platform-custom-list-extra-tools .platform-toolbar > div:nth-child(1) input[placeholder]",
            "Поиск по номеру заявки",
        )
        self.FOUNDED_INQUIRIES = ElementsList(
            "//div[contains(@class, 'platform-custom-list-scrollable-body')] //div[not(@class)]/div",
            "Найденные заявки",
        )

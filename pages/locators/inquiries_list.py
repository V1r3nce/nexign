from playwright.sync_api import Page

from pages.locators.inquiries_elements import InquiriesElements
from pages.ui_elements import Element, ElementsList


class InquiriesList(InquiriesElements):
    """Страница "Заявки" /inquiry-list/"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.TABLE_VIEW = Element("(//div[contains(@class, 'ant-radio-group')])[1] /label[1]", "Таблицей", self.page)
        self.LIST_VIEW = Element("(//div[contains(@class, 'ant-radio-group')])[1] /label[2]", "Списком", self.page)

        self.ALL_INQUIRIES_BTN = Element(
            "(//div[contains(@class, 'ant-radio-group')])[2] /label[1]", "Все заявки", self.page
        )
        self.IN_PROCESS_BTN = Element(
            "(//div[contains(@class, 'ant-radio-group')])[2] /label[2]", "В обработке", self.page
        )
        self.IN_QUEUE_BTN = Element("(//div[contains(@class, 'ant-radio-group')])[2] /label[3]", "В очередях", self.page)

        self.NEXT_STEP_BTN = Element(
            "(//button[contains(@class, 'ant-dropdown-trigger')])[1]", "Кнопка 'Далее'", self.page
        )

        self.SEARCH_FIELD = Element('[placeholder="Номер заявки"]', "Поиск по номеру заявки", self.page)
        self.FOUNDED_INQUIRIES = ElementsList(
            "//div[contains(@class, 'platform-scrollable scrollable-body')] /div /div /div[not(contains(@style, 'display: none'))]",
            "Найденные заявки",
            self.page,
        )

from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element

class InquiriesPage(BaseElements):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT = Element("//a[contains(@href, 'overview')]/span", "Клиент", self.page)
        self.INQUIRY_ID = Element("//a[contains(@href, 'inquiries/')]/span", "Номер заявки", self.page)
        self.INQUIRY_NAME = Element("//a[contains(@href, 'customer-hierarchy-management')]/..//h2", "Название заявки", self.page)
        self.INQUIRY_STATUS = Element("//div[@display='inline-block']/p", "Статус заявки", self.page)

        self.ACTIVE_STEP_TAB = Element(".ant-tabs-tab-active", "Вкладка 'Активный шаг'",
                                       self.page)
        self.LOCATOR_SALE = Element(".platform-empty-box__container", "Элемент о текущих продуктах",
                                    self.page)
        self.LOAD_SPIN = Element(".ant-spin-dot", "Лоадер",
                            self.page)
        self.ADD_SALE_BTN = Element("#add", "Кнопка 'Добавить'",
                                    self.page)
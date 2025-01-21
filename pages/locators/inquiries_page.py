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
from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class HomePage(BaseElements):
    """Страница /welcome Домашняя"""
    def __init__(self, page: Page):
        super().__init__(page)

        #HEADER PANEL
        self.CUSTOMER_NAME = Element("#customerName", "Клиент", self.page)
        self.INN = Element("#taxIdentificationNumber", "ИНН", self.page)

        #WORK_TABLE
        self.WIDGET = ElementsList(".react-grid-layout > div", "Виджеты", self.page)
        self.WIDGET_LABEL = ElementsList(".react-grid-layout > div h4", "Название виджета", self.page)

        #QUICK_ACTIONS_WIDGET
        self.CREATE_ORG_BTN = Element("#createOrganization", "Создать клиент ЮЛ", self.page)
        self.CREATE_CUSTOMER_BTN = Element("#createIndividual", "Создать клиент ФЛ", self.page)
        self.CREATE_ENTREPRENEUR_BTN = Element("#createEntrepreneur", "Создать клиента ИП", self.page)
        self.LAST_INQUIRY_BTN = Element("#lastInquiry", "Последняя заявка", self.page)
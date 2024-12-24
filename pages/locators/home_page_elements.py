from pages.locators.base_elements import BaseElements
from playwright.sync_api import Page
from pages.locators.ui_elements import Element, ElementsList


class HomePage(BaseElements):
    def __init__(self, page: Page):
        super().__init__(page)

        """Страница /welcome Домашняя"""
        #footer panel
        CUSTOMER_NAME = "#customerName"
        INN = "#taxIdentificationNumber"

        #WORK_TABLE
        WIDGET = ".react-grid-layout > div:nth-child({widget_num})"
        WIDGET_LABEL = ".react-grid-layout > div:nth-child({widget_num}) h4"

        #QUICK_ACTIONS_WIDGET
        CREATE_ORG_BTN = "#createOrganization"
        self.CREATE_CUSTOMER_BTN = Element("#createIndividual", "Создать ФЛ", self.page)
        CREATE_ENTREPRENEUR_BTN = "#createEntrepreneur"
        LAST_INQUIRY_BTN = "#lastInquiry"
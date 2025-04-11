from playwright.sync_api import Page

from pages.ui_elements import Element


class BaseElementsPsc:
    def __init__(self, page: Page):
        self.page = page

        self.APP_LOGO = Element("a[href='/ProductCatalog/ui/']", "Логотип сервиса", self.page)

        # FORM ELEMENTS
        self.SECOND_BTN_FORM = Element(".footer-actions > button:last-child", "Вторая кнопка формы", self.page)

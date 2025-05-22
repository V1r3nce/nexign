from playwright.sync_api import Page

from pages.ui_elements import Dropdown, Element, ElementsList


class BaseElementsRfd:
    def __init__(self, page: Page):
        self.page = page

        self.REFDATA_LOGO = Element('h1[class="app-title"]', "Логотип сервиса", self.page)
        self.SAVE_OK_BTN = ElementsList('ps-button[icon="ok"]', "Кнопка 'Сохранить'", self.page)
        self.NEXT_BNT_RFD = Element(
            'ps-button[icon="ok"][ng-click="ctrl.apply($event);"]', "Кнопка 'Продолжить'", self.page
        )
        # LEFT MENU
        self.LEFT_MENI_ITEM = ElementsList('li[class="app-menu-list__item"]', "Кнопки навигации меню слева", self.page)


class SelectRFD(Dropdown):
    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)

    @property
    def options(self) -> dict:
        for item in self.page.locator(".ps-list-drop-option").all():
            self.options_dict[item.text_content()] = item
        return self.options_dict

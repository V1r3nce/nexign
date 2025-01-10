from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList


class BaseElements:
    def __init__(self, page: Page):
        self.page = page
        #header
        self.BURGER_MENU_BTN = Element(".sc-gFCCrQ.bEnxbF.cWFlmk", "Бургер Меню", self.page) # возможно, нестабильный
        self.HOME_BTN = Element('a[href="/rm-ui/all/welcome"]', "Главная", self.page)
        PAGE_TITLE = "[class='sc-guDLey RHMsq'] > h4" # возможно, нестабильный

        HEADER_ACCOUNT_NUM = "#accountNumber"
        HEADER_SUBSCRIBER = "#subscriptionIdentification"
        self.HEADER_SEARCH_BTN = Element(".ant-form-inline > button", "Поиск", self.page)
        USER_DROPDOWN_BTN = "p.ant-dropdown-trigger"

        #USER_DROPDOWN
        ENGLISH_LANG_BTN = "li[data-menu-id*='ru']"
        RUSSIAN_LANG_BTN = "li[data-menu-id*='en']"
        DARK_THEME_BTN = "li[data-menu-id*='dark']"
        DEFAULT_THEME_BTN = "li[data-menu-id*='default']"
        LOGOUT_BTN = "li[data-menu-id*='logout']"

        #BURGER_MENU
        BURGER_MENU_PARTITION = ".ant-drawer-body div:nth-child({partition_num}"
        BURGER_MENU_EL_BTN = ".ant-drawer-body a:nth-child({element_num})"

        #RIGHT_SIDE_MENU
        self.RIGHT_SIDE_BTN = ElementsList("//div[contains(@class, 'ant-drawer-inline')]/following-sibling::div[1]/div[2]//button", "Кнопка правого меню", self.page) # возможно, нестабильный

        #MODAL
        self.MODAL = Element(".ant-modal-content", "Модальное окно", self.page)
        self.MODAL_X_BTN = Element(".ant-modal-close-x", "Кнопка Х закрыть модального окна", self.page)
        self.MODAL_COPY_DETAILS_BTN = Element(".ant-modal-content .ant-modal-footer > div > button",
                                              "Кнопка 'Копировать детали' модального окна", self.page)
        self.MODAL_CLOSE_BTN = Element(".ant-modal-content div:nth-child(2) button",
                                       "Кнопка 'Закрыть' модального окна", self.page)
        self.MODAL_TITLE = Element(".ant-modal-title", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = Element(".ant-modal-body", "Текст модального окна", self.page)
        self.COPY_DETAILS_BTN = Element(".ant-modal-footer > div > button", "", self.page)
        self.FOOTER_CLOSE_BTN = Element(".ant-modal-footer > div > div > button", "", self.page)

from playwright.sync_api import Page

from pages.ui_elements import BurgerMenu, Dropdown, Element, ElementsList


class BaseElements:
    def __init__(self, page: Page):
        self.page = page

        # header
        self.BURGER_MENU = BurgerMenu(".platform-root-limited-container > div > div > span", "Бургер Меню", self.page)
        self.HOME_BTN = Element('a[href="/nbss/welcome"]', "Главная", self.page)
        self.PAGE_TITLE = Element(
            ".platform-root-limited-container > div > div:nth-child(3) > h4", "Заголовок", self.page
        )

        self.HEADER_ACCOUNT_NUM = Element("#accountNumber", "Лицевой счет", self.page)
        self.HEADER_SUBSCRIBER = Element("#subscriptionIdentification", "Абонент", self.page)
        self.HEADER_SEARCH_BTN = Element(".ant-form-inline > button", "Поиск", self.page)
        self.USER_DROPDOWN_BTN = Element("p[class*='dropdown-trigger']", "Кнопка пользователя (выпадашка)", self.page)

        # USER_DROPDOWN
        self.ENGLISH_LANG_BTN = Element("li[data-menu-id*='en']", "Английский язык", self.page)
        self.RUSSIAN_LANG_BTN = Element("li[data-menu-id*='ru']", "Русский язык", self.page)
        self.DARK_THEME_BTN = Element("li[data-menu-id*='dark']", "Темная тема", self.page)
        self.DEFAULT_THEME_BTN = Element("li[data-menu-id*='default']", "Стандартная тема", self.page)
        self.LOGOUT_BTN = Element("li[data-menu-id*='logout']", "Выйти", self.page)

        # CONTEXT
        self.CONTEXT_ELEMENT = ElementsList(
            "//*[@class='platform-link-content']/../../p", "Элементы контекста", self.page
        )
        self.LINK_IN_CONTEXT = ElementsList(".platform-link-content", "Ссылки в контексте пользователя", self.page)

        # BURGER_MENU
        self.BURGER_MENU_PARTITION = ElementsList(".ant-drawer-body div", "Раздел бокового меню", self.page)
        self.BURGER_MENU_EL_BTN = ElementsList(".ant-drawer-body a", "Кнопка бокового меню", self.page)

        # RIGHT_SIDE_MENU
        self.RIGHT_SIDE_BTN = ElementsList(
            "//div/*[(count(button) = 2) or (count(button) = 3 and count(span) = 1)]/*",
            "Кнопка правого меню",
            self.page,
        )
        self.CREATE_REQUEST = Element(
            '//*[@id="root"]/div/div/div[3]/div[2]/div/div[1]/button[1]', "Кнопка 'Создать заявку'", self.page
        )
        self.CREATE_APPLICATION = Element(
            '//*[@id="root"]/div/div/div[3]/div[2]/div/div[1]/button[2]',
            "Кнопка 'Создание продажи и управление услугами'",
            self.page,
        )

        # MODAL
        self.MODAL = ElementsList(".ant-modal-content", "Модальное окно", self.page)
        self.MODAL_X_BTN = Element(".ant-modal-close-x", "Кнопка Х закрыть модального окна", self.page)
        self.MODAL_COPY_DETAILS_BTN = Element(
            ".ant-modal-content .ant-modal-footer > div > button",
            "Кнопка 'Копировать детали' модального окна",
            self.page,
        )
        self.MODAL_CLOSE_BTN = Element(
            ".ant-modal-content div:nth-child(2) button", "Кнопка 'Закрыть' модального окна", self.page
        )
        self.MODAL_DONT_SAVE_BTN = Element(
            ".ant-modal-content div:nth-child(2) button:first-child", "Кнопка 'Не сохранять' модального окна", self.page
        )
        self.MODAL_TITLE = ElementsList(".ant-modal-title", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = ElementsList(".ant-modal-body", "Текст модального окна", self.page)
        self.COPY_DETAILS_BTN = Element(".ant-modal-footer > div > button", "", self.page)
        self.FOOTER_CLOSE_BTN = ElementsList(
            ".ant-modal-footer > div > div > button", "Кнопка 'Закрыть' модального окна", self.page
        )
        self.FIRST_BTN = Element(".ant-modal-content div button:first-child", "Первая кнопка модального окна", self.page)
        self.SECOND_BTN = Element(".ant-modal-content div button:last-child", "Вторая кнопка модального окна", self.page)
        self.INFO_MESSAGE = Element(
            "//div[contains(@class,'platform-snackbar')]/span/following-sibling::p",
            "Информационное сообщение",
            self.page,
        )
        self.INFO_MESSAGE_2 = Element("div[role='alert'] p p", "Информационное сообщение", self.page)
        self.INFO_MESSAGE_3 = Element(
            "//div[contains(@class,'platform-snackbar')]//span/following-sibling::p",
            "Информационное сообщение",
            self.page,
        )
        self.INFO_MESSAGE_LINK = Element("div[role='alert'] p a", "Кнопка ссылки в Информационном сообщении", self.page)

        # DROPDOWN_MENU
        self.DROPDOWN_MENU = Dropdown("ul[role=menu]", "Меню", self.page)

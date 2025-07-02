from playwright.sync_api import Page

from pages.ui_elements import BurgerMenu, Element, ElementsList


class BaseElements:
    def __init__(self, page: Page):
        self.page = page

        # header
        self.BURGER_MENU = BurgerMenu("[data-icon=Menu]", "Бургер Меню", self.page)
        self.HOME_BTN = Element("[data-icon=Home]", "Главная", self.page)
        self.PAGE_TITLE = Element(".platform-root-limited-container > div h4", "Заголовок", self.page)

        self.HEADER_ACCOUNT_NUM = Element("#accountNumber", "Лицевой счет", self.page)
        self.HEADER_SUBSCRIBER = Element("#subscriptionIdentification", "Абонент", self.page)
        self.HEADER_SEARCH_BTN = Element("[class*=form-inline] > button", "Поиск", self.page)
        self.USER_DROPDOWN_BTN = Element(
            "button[class*='dropdown-trigger'] p", "Кнопка пользователя (выпадашка)", self.page
        )

        # USER_DROPDOWN
        self.ENGLISH_LANG_BTN = Element("li[data-menu-id*='en']", "Английский язык", self.page)
        self.RUSSIAN_LANG_BTN = Element("li[data-menu-id*='ru']", "Русский язык", self.page)
        self.DARK_THEME_BTN = Element("li[data-menu-id*='dark']", "Темная тема", self.page)
        self.DEFAULT_THEME_BTN = Element("li[data-menu-id*='default']", "Стандартная тема", self.page)
        self.LOGOUT_BTN = Element("li[data-menu-id*='logout']", "Выйти", self.page)

        # CONTEXT
        self.CONTEXT_ELEMENT = ElementsList(
            "//*[contains(@class, 'platform-root-scrollable-container')]/../div[1] //p", "Элементы контекста", self.page
        )
        self.LINK_IN_CONTEXT = ElementsList(
            "//*[contains(@class, 'platform-root-scrollable-container')]/../div[1] //*[contains(@class, 'platform-text-link')]",
            "Ссылки в контексте пользователя",
            self.page,
        )

        # BURGER_MENU
        self.BURGER_MENU_PARTITION = ElementsList(".ant-drawer-body div", "Раздел бокового меню", self.page)
        self.BURGER_MENU_EL_BTN = ElementsList(".ant-drawer-body a", "Кнопка бокового меню", self.page)

        # RIGHT_SIDE_MENU
        self.RIGHT_SIDE_BTN = ElementsList(
            "div:has(> button >span  [data-icon=CreateTicket]) > *",
            "Кнопка правого меню",
            self.page,
        )
        self.CREATE_REQUEST = Element("[data-icon=CreateTicket]", "Кнопка 'Создать заявку'", self.page)
        self.CREATE_APPLICATION = Element(
            "[data-icon=CreateOrder]", "Кнопка 'Создание продажи и управление услугами'", self.page
        )
        self.VIEW_COMMENTS = Element("[data-icon=ForumIcon]", "Кнопка 'Просмотр комментариев'", self.page)

        # MODAL
        self.MODAL = ElementsList("[class*=modal-content]", "Модальное окно", self.page)
        self.MODAL_X_BTN = Element("[class*=modal-close-x]", "Кнопка Х закрыть модального окна", self.page)
        self.MODAL_COPY_DETAILS_BTN = Element(
            ".ant-modal-content .ant-modal-footer > div > button",
            "Кнопка 'Копировать детали' модального окна",
            self.page,
        )
        self.MODAL_CLOSE_BTN = Element(
            "[class*=modal-content] div:nth-child(2) button", "Кнопка 'Закрыть' модального окна", self.page
        )
        self.MODAL_DONT_SAVE_BTN = Element(
            ".ant-modal-content div:nth-child(2) button:first-child", "Кнопка 'Не сохранять' модального окна", self.page
        )
        self.MODAL_TITLE = ElementsList("[class*=modal-title]", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = ElementsList("[class*=modal-body]", "Текст модального окна", self.page)
        self.COPY_DETAILS_BTN = Element(".ant-modal-footer > div > button", "", self.page)
        self.FOOTER_CLOSE_BTN = ElementsList(
            ".ant-modal-footer > div > div > button", "Кнопка 'Закрыть' модального окна", self.page
        )
        self.MODAL_FIRST_BTN = Element(
            "[class*=modal-content] div button:first-child", "Первая кнопка модального окна", self.page
        )
        self.MODAL_SECOND_BTN = Element(
            "[class*=modal-content] div button:last-child", "Вторая кнопка модального окна", self.page
        )

        # NOTIFICATION
        self.INFO_MESSAGE = ElementsList(
            "//div[@role='alert' and contains(@class, 'notice')]/*[contains(@class, 'notice-message')]",
            "Информационное сообщение",
            self.page,
        )
        self.INFO_MESSAGE_CLOSE_BTN = Element(
            "//div[@role='alert' and contains(@class, 'notice')] /.. /.. //a[contains(@class, 'notice-close')]",
            "Крестик закрытия информационного сообщения",
            self.page,
        )
        self.INFO_MESSAGE_LINK = Element(
            "//div[@role='alert' and contains(@class, 'notice')] //p //a",
            "Кнопка ссылки в Информационном сообщении",
            self.page,
        )
        self.INFO_MESSAGE_ACTION_BUTTON = Element(
            "//div[@role='alert' and contains(@class, 'notice')] //div[contains(@class, 'notice-action')]//a",
            "Активная кнопка в Информационном сообщении",
            self.page,
        )

        # TAB
        self.SELECTED_TAB_TITLE = Element("[role=tab][aria-selected=true]", "Название активной вкладки", self.page)
        self.TAB = ElementsList("[role=tab]", "Вкладка", self.page)

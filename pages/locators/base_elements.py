from pages.ui_elements import BurgerMenu, Element, ElementsList


class BaseElements:
    def __init__(self) -> None:
        # header
        self.BURGER_MENU = BurgerMenu("[data-icon=Menu]", "Бургер Меню")
        self.HOME_BTN = Element("[data-icon=Home]", "Главная")
        self.PAGE_TITLE = Element(".platform-root-limited-container > div h4", "Заголовок")

        self.HEADER_ACCOUNT_NUM = Element("#accountNumber", "Лицевой счет")
        self.HEADER_SUBSCRIBER = Element("#subscriptionIdentification", "Абонент")
        self.HEADER_SEARCH_BTN = Element("[class*=form-inline] > button", "Поиск")
        self.USER_DROPDOWN_BTN = Element("button[class*='dropdown-trigger'] p", "Кнопка пользователя (выпадашка)")

        # USER_DROPDOWN
        self.ENGLISH_LANG_BTN = Element("li[data-menu-id*='en']", "Английский язык")
        self.RUSSIAN_LANG_BTN = Element("li[data-menu-id*='ru']", "Русский язык")
        self.DARK_THEME_BTN = Element("li[data-menu-id*='dark']", "Темная тема")
        self.DEFAULT_THEME_BTN = Element("li[data-menu-id*='default']", "Стандартная тема")
        self.LOGOUT_BTN = Element("li[data-menu-id*='logout']", "Выйти")

        # CONTEXT
        self.CONTEXT_ELEMENT = ElementsList(
            "//*[contains(@class, 'platform-root-scrollable-container')]/../div[1] //p", "Элементы контекста"
        )
        self.LINK_IN_CONTEXT = ElementsList(
            "//*[contains(@class, 'platform-root-scrollable-container')]/../div[1] //*[contains(@class, 'platform-text-link')]",
            "Ссылки в контексте пользователя",
        )

        # BURGER_MENU
        self.BURGER_MENU_PARTITION = ElementsList(".ant-drawer-body div", "Раздел бокового меню")
        self.BURGER_MENU_EL_BTN = ElementsList(".ant-drawer-body a", "Кнопка бокового меню")

        # RIGHT_SIDE_MENU
        self.RIGHT_SIDE_BTN = ElementsList(
            "div:has(> button >span  [data-icon=CreateTicket]) > *",
            "Кнопка правого меню",
        )
        self.CREATE_REQUEST = Element("[data-icon=CreateTicket]", "Кнопка 'Создать заявку'")
        self.CREATE_APPLICATION = Element("[data-icon=CreateOrder]", "Кнопка 'Создание продажи и управление услугами'")
        self.CREATE_SELL_EQUIPMENT = Element("[data-icon=Devices]", "Кнопка 'Продажа товаров/оборудования'")
        self.VIEW_COMMENTS = Element("[data-icon=ForumIcon]", "Кнопка 'Просмотр комментариев'")
        self.AUTHORIZATION = Element("[data-icon=VisibilityOnOutlined]", "Кнопка 'Авторизация'")

        # MODAL
        self.MODAL = ElementsList("[class*=modal-content]", "Модальное окно")
        self.MODAL_X_BTN = Element("[class*=modal-close-x]", "Кнопка Х закрыть модального окна")
        self.MODAL_COPY_DETAILS_BTN = Element(
            ".ant-modal-content .ant-modal-footer > div > button",
            "Кнопка 'Копировать детали' модального окна",
        )
        self.MODAL_CLOSE_BTN = Element(
            "[class*=modal-content] div:nth-child(2) button", "Кнопка 'Закрыть' модального окна"
        )
        self.MODAL_TITLE = ElementsList("[class*=modal-title]", "Заголовок модального окна")
        self.MODAL_BODY_TEXT = ElementsList("[class*=modal-body]", "Текст модального окна")
        self.COPY_DETAILS_BTN = Element(".ant-modal-footer > div > button", "")
        self.FOOTER_CLOSE_BTN = ElementsList(
            ".ant-modal-footer > div > div > button", "Кнопка 'Закрыть' модального окна"
        )
        self.MODAL_FIRST_BTN = Element("[class*=modal-content] div button:first-child", "Первая кнопка модального окна")
        self.MODAL_SECOND_BTN = Element("[class*=modal-content] div button:last-child", "Вторая кнопка модального окна")

        # NOTIFICATION
        self.INFO_MESSAGE = ElementsList(
            "//div[@role='alert' and contains(@class, 'notice')]/*[contains(@class, 'notice-message')]",
            "Информационное сообщение",
        )
        self.INFO_MESSAGE_CLOSE_BTN = Element(
            "//div[@role='alert' and contains(@class, 'notice')] /.. /.. //a[contains(@class, 'notice-close')]",
            "Крестик закрытия информационного сообщения",
        )
        self.INFO_MESSAGE_LINK = Element(
            "//div[@role='alert' and contains(@class, 'notice')] //a",
            "Кнопка ссылки в Информационном сообщении",
        )
        self.INFO_MESSAGE_ACTION_BUTTON = Element(
            "//div[@role='alert' and contains(@class, 'notice')] //div[contains(@class, 'notice-action')]//a",
            "Активная кнопка в Информационном сообщении",
        )

        # TAB
        self.SELECTED_TAB_TITLE = Element("[role=tab][aria-selected=true]", "Название активной вкладки")
        self.TAB = ElementsList("[role=tab]", "Вкладка")

        # LOAD
        self.LOAD_SPINS = ElementsList('[class*="spin"][class*="spin-spin"]', "Лоадер")

        # TOOLTIP
        self.TOOLTIP = Element("[class*=tooltip-content] p", "Подсказка при наведении")

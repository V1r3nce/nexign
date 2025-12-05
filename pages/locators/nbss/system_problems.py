from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import Element, ElementsList


class SystemProblems(DynamicForms):
    """Страница /common-faults-list/all 'Системные проблемы'"""

    def __init__(self) -> None:
        super().__init__()

        # OPTION_BTNS
        self.ADD_PROBLEM_BTN = Element(
            "//div[contains(@class, 'platform-toolbar')]/div[1] //span[@data-icon='Add']", "Кнопка 'Добавить'"
        )
        self.EDIT_PROBLEM_BTN = Element(".ant-tabs-content-holder button", "Кнопка 'Редактировать'")
        self.PROCESSING_DEFAULT_BTN = ElementsList(
            "div:nth-child(2) > div:first-child > .ant-btn-default", "Кнопка 'Обработка'"
        )
        self.PROCESSING_OPTION = ElementsList(
            "//*[contains(@data-menu-id, 'menu-uuid')]//*[contains(@class, 'dropdown-menu-title-content')]",
            "Вариант 'Обработки'",
        )
        self.REFRESH_SYSTEM_PROBLEM = Element(
            "(//*[contains(@class, 'spin-container')]//*[contains(@class, platform-root-scrollable-container))//*[contains(@class, 'spin-container')]//div[1]//div[last()]//button)[1]",
            "Кнопка 'Обновить'",
        )
        self.PROBLEM_CLOSE_DEFAULT_BTN = Element(".ant-btn-default:nth-of-type(2)", "Кнопка 'Закрыть проблему'")

        # TABS
        self.PROCESSING_HISTORY_TAB = Element(".ant-tabs-tab:nth-of-type(6)", "Таб 'История обработки'")

        # REVIEW_TAB
        self.REVIEW_PROBLEM_TYPE = Element("[data-testid='attribute-commonFaultType'] p+p", "Тип проблемы")
        self.REVIEW_REASON_TYPE = Element("[data-testid='attribute-reasonType'] p+p", "Тип причины")
        self.REVIEW_INFLUENCE_POTENTIAL = Element("[data-testid='attribute-potential'] p+p", "Потенциал влияния")
        self.REVIEW_EXPERTS = Element(
            "[data-testid='attribute-onlyExpertLink']>label>span:last-child", "Привязывают только эксперты"
        )
        self.REVIEW_OPERATOR_DESCRIPTION = Element(
            "[data-testid='attribute-descriptionForOperator'] p+p", "Описание для оператора"
        )
        self.REVIEW_TECH_DESCRIPTION = Element("[data-testid='attribute-description'] p+p", "Техническое описание")
        self.REVIEW_NOTIFY_CLIENT = Element("[data-testid='attribute-messageToSubscriber'] p+p", "Сообщить клиенту")
        self.REVIEW_SOLUTION_PLANNED_DURATION = Element(
            "[data-testid='attribute-CF_DEDLINE'] p+p", "Планируемый срок решения"
        )
        self.REVIEW_CON_SOLUTION_PLANNED_DURATION = Element(
            "[data-testid='attribute-CF_DEDLINE'] p+p", "Планируемый срок решения"
        )
        self.REVIEW_PROBLEM_REGION = Element(
            "[data-testid=attribute-CF_REGION]  p:nth-child(2)", "Регион возникновения проблемы"
        )

        self.REVIEW_ATTEMPTS_NUM = Element(
            "//div[@data-testid='attribute-TEST_6']",
            "Количество попыток_число",
        )
        self.REVIEW_ADJUSTMENT_REQUIRED = Element(
            "//div[@data-testid='attribute-TEST_4']",
            "Требуется корректировка?",
        )
        self.REVIEW_PROBLEMATIC_SERVICE = Element(
            "//div[@data-testid='attribute-TEST_5']",
            "Проблемный сервис",
        )
        self.REVIEW_CHARGES_AMOUNT = Element(
            "//div[@data-testid='attribute-TEST_7']",
            "Сумма начислений",
        )

        self.REVIEW_PROBLEM_OCCURANCE_DATE = Element(
            "//div[@data-testid='attribute-TEST_3']", "Дата возникновения проблемы"
        )
        self.REVIEW_SERVICE_NAME = Element("//div[@data-testid='attribute-TEST_1']", "Название услуги")
        self.REVIEW_CLIENT_CONTACT_AGAIN = Element(
            "//div[@data-testid='attribute-TEST_2']", "Клиент обращается повторно?"
        )

        self.REVIEW_CLIENT_TYPE = Element("[data-testid='attribute-CF_CLNT_TYPE'] p+p", "Тип клиента")

        self.REVIEW_PROCESS_BEFORE = Element("[data-testid='attribute-finishDate'] div>div", "Обработать до")
        self.REVIEW_PRIORITY = Element("[data-testid='attribute-priority'] p+p", "Приоритет")
        self.REVIEW_CREATION_DATE = Element("[data-testid='attribute-createDate'] p+p", "Дата создания")
        self.REVIEW_REGISTERED = Element("[data-testid='attribute-createUser'] p+p", "Зарегистрировал")
        self.REVIEW_PLANNED_END_DATE = Element("[data-testid='attribute-planCloseDate'] p+p", "Дата закрытия (план)")
        self.REVIEW_FACT_END_DATE = Element("[data-testid='attribute-factCloseDate'] p+p", "Дата закрытия (факт)")
        self.REVIEW_ORIGIN_DATE = Element("[data-testid='attribute-raiseDate'] p+p", "Дата возникновения")

        self.EXPAND_ICON_LIST = ElementsList(
            ".ant-collapse .ant-collapse-expand-icon", "Список кнопок разворачивания списка"
        )

        # HISTORY_TAB
        self.HISTORY_STEP_NAME_LIST = ElementsList(
            ".ant-tabs-tabpane-active .platform-custom-list-scrollable-body div:nth-child(1) > p",
            "Список наименований шагов",
        )
        self.HISTORY_STEP_NAME = Element(".platform-scrollable h3", "Наименование шага")
        self.HISTORY_STEP_CREATION_DATE = Element(".platform-scrollable h3 + p", "Время создания шага")
        self.HISTORY_PLANNED_END_DATE = Element(
            "((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[1]/p[2]",
            "Дата завершения (план)",
        )
        self.HISTORY_END_DATE = Element(
            "((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[2]/p[2]",
            "Дата завершения (факт)",
        )
        self.HISTORY_QUEUE = Element(
            "((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[3]/p[2]",
            "Очередь",
        )
        self.HISTORY_DURATION = Element(
            "((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[4]/p[2]",
            "Продолжительность",
        )

        self.PROCESSING_REPORT = Element(".platform-scrollable>div>div>div:nth-child(2)>div>p", "Отчет об обработке")
        self.HISTORY_STEP_EVENTS = ElementsList(
            ".platform-scrollable h4 + div p:nth-child(1)", "Список наименований событий на шаге"
        )
        self.HISTORY_STEP_DATE_AND_USER = ElementsList(
            ".platform-scrollable h4 + div p:nth-child(1)", "Список дат и юзеров для событий шагов"
        )

        # FILTERS
        self.FILTER_PROBLEM_NUMBER_FIELD = Element(
            "div:first-child>.platform-toolbar-item div>span span+input",
            "Поле фильтра 'Номер СП'",
        )
        self.FILTER_PROBLEM_NAME_FIELD = Element(
            "div:first-child>.platform-toolbar-item:nth-child(2) span span+input",
            "Поле фильтра 'Наименование СП'",
        )

        # MODAL
        self.MODAL_FIELD = Element(".ant-modal-content textarea", "Поле 'Отчет по обработке'")
        self.MODAL_CLOSE_PROBLEM_BTN = Element(".ant-modal-content .ant-btn-primary", "Кнопка 'Закрыть")

        # SYSTEM_PROBLEMS_LIST
        self.PROBLEM_NUMBERS_LIST = ElementsList(".platform-scrollable a", "Список номеров системных проблем")
        self.PROBLEM_CLEAR_BTN = ElementsList(".ant-input-clear-icon", "Кнопка сброса фильтра")
        self.PROBLEM_NAME = ElementsList(".platform-scrollable a + p", "Наименование системной проблемы")
        self.PROBLEM_STATUS_COLOR_LIST = ElementsList(
            ".platform-scrollable>div>div:first-child>div>div>div>div:first-child",
            "Список цветов статусов системных проблем",
        )
        self.PROBLEM_NAMES_LIST = ElementsList(".platform-scrollable a + p", "Список наименований системных проблем")
        self.SWITCHER_ACTIVE = Element(
            "//div[contains(@class, 'radio-group')]/label[2]", "Значение переключателя 'Активные'"
        )
        self.PROBLEM_LIST_FILTER_SWITCHES = ElementsList(
            "span.ant-radio-button + span", "Переключатели фильтра списка системных проблем"
        )
        self.PROBLEM_FILTER_SETTINGS_BTN = Element(
            ".platform-toolbar>div:first-child>.platform-toolbar-item:nth-child(3)",
            "Кнопка настройки фильтра",
        )

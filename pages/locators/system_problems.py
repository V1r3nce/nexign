from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import Element, ElementsList


class SystemProblems(DynamicForms):
    """Страница /common-faults-list/all 'Системные проблемы'"""
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        #OPTION_BTNS
        self.ADD_PROBLEM_BTN = Element("[variant=primary]", "Кнопка 'Добавить'", self.page)
        self.EDIT_PROBLEM_BTN = Element(".ant-tabs-content-holder button", "Кнопка 'Редактировать'", self.page)
        self.PROCESSING_DEFAULT_BTN = ElementsList("h2 button:nth-child(1)", "Кнопка 'Обработка'", self.page)
        self.PROCESSING_OPTION = ElementsList("[data-menu-id*='rc-menu-uuid'] .ant-dropdown-menu-title-content", "Вариант 'Обработки'", self.page)
        self.PROBLEM_CLOSE_DEFAULT_BTN = Element('((//h2[@justifycontent="space-between"]) //button)[3]', "Кнопка 'Закрыть проблему'", self.page)

        #TABS
        self.PROCESSING_HISTORY_TAB = Element(".ant-tabs-tab:nth-of-type(6)", "Таб 'История обработки'", self.page)

        #REVIEW_TAB
        self.REVIEW_PROBLEM_TYPE = Element("[data-testid=attribute-commonFaultType] p:nth-child(2)", "Тип проблемы", self.page)
        self.REVIEW_REASON_TYPE = Element("[data-testid=attribute-reasonType] p:nth-child(2)", "Тип причины", self.page)
        self.REVIEW_INFLUENCE_POTENTIAL = Element("[data-testid=attribute-potential] p:nth-child(2)", "Потенциал влияния", self.page)
        self.REVIEW_EXPERTS = Element("[data-testid=attribute-onlyExpertLink] input", "Привязывают только эксперты", self.page)
        self.REVIEW_OPERATOR_DESCRIPTION = Element("[data-testid=attribute-descriptionForOperator] p:nth-child(2)", "Описание для оператора", self.page)
        self.REVIEW_TECH_DESCRIPTION = Element("[data-testid=attribute-description] p:nth-child(2)", "Техническое описание", self.page)
        self.REVIEW_NOTIFY_CLIENT = Element("[data-testid=attribute-messageToSubscriber] p:nth-child(2)", "Сообщить клиенту", self.page)
        self.REVIEW_SOLUTION_PLANNED_DURATION = Element("[data-testid=attribute-CF_DEDLINE] p:nth-child(2)", "Планируемый срок решения", self.page)
        self.REVIEW_PROBLEM_REGION = Element("[data-testid=attribute-CF_REGION] p:nth-child(2)", "Регион возникновения проблемы", self.page)

        self.REVIEW_ATTEMPTS_NUM = Element("[data-testid=attribute-TEST_6] p:nth-child(2)", "Количество попыток_число", self.page)
        self.REVIEW_ADJUSTMENT_REQUIRED = Element("[data-testid=attribute-TEST_4] p:nth-child(2)", "Требуется корректировка?", self.page)
        self.REVIEW_PROBLEMATIC_SERVICE = Element("[data-testid=attribute-TEST_5] p:nth-child(2)", "Проблемный сервис", self.page)
        self.REVIEW_CHARGES_AMOUNT = Element("[data-testid=attribute-TEST_7] p:nth-child(2)", "Сумма начислений", self.page)

        self.REVIEW_PROBLEM_OCCURANCE_DATE = Element("[data-testid=attribute-TEST_3] p:nth-child(2)", "Дата возникновения проблемы", self.page)
        self.REVIEW_SERVICE_NAME = Element("[data-testid=attribute-TEST_1] p:nth-child(2)", "Название услуги", self.page)
        self.REVIEW_CLIENT_CONTACT_AGAIN = Element("[data-testid=attribute-TEST_2] p:nth-child(2)", "Клиент обращается повторно?", self.page)

        self.REVIEW_CLIENT_TYPE = Element("[data-testid=attribute-CF_CLNT_TYPE] p:nth-child(2)", "Тип клиента",
                                          self.page)

        self.REVIEW_PROCESS_BEFORE = Element("[data-testid=attribute-finishDate] div", "Обработать до", self.page)
        self.REVIEW_PRIORITY = Element("[data-testid=attribute-priority] p:nth-child(2)", "Приоритет", self.page)
        self.REVIEW_CREATION_DATE = Element("[data-testid=attribute-createDate] p:nth-child(2)", "Дата создания", self.page)
        self.REVIEW_REGISTERED = Element("[data-testid=attribute-createUser] p:nth-child(2)", "Зарегистрировал", self.page)
        self.REVIEW_PLANNED_END_DATE = Element("[data-testid=attribute-planCloseDate] p:nth-child(2)", "Дата закрытия (план)", self.page)
        self.REVIEW_FACT_END_DATE = Element("[data-testid=attribute-factCloseDate] p:nth-child(2)", "Дата закрытия (факт)", self.page)
        self.REVIEW_ORIGIN_DATE = Element("[data-testid=attribute-raiseDate] p:nth-child(2)", "Дата возникновения", self.page)

        #HISTORY_TAB
        self.HISTORY_STEP_NAME_LIST = ElementsList(".ant-tabs-tabpane-active .scrollable-body div:nth-child(1) > p", "Список наименований шагов", self.page)
        self.HISTORY_STEP_NAME = Element(".platform-scrollable h3", "Наименование шага", self.page)
        self.HISTORY_STEP_CREATION_DATE = Element(".platform-scrollable h3 + p", "Время создания шага", self.page)
        self.HISTORY_PLANNED_END_DATE = Element("((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[1]/p[2]", "Дата завершения (план)", self.page)
        self.HISTORY_END_DATE = Element("((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[2]/p[2]", "Дата завершения (факт)", self.page)
        self.HISTORY_QUEUE = Element("((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[3]/p[2]", "Очередь", self.page)
        self.HISTORY_DURATION = Element("((//div[contains(@id, 'panel-history')]//div[contains(@class, 'platform-scrollable')])[2] //div[contains(@class, 'platform-grid-item')])[4]/p[2]", "Продолжительность", self.page)

        self.PROCESSING_REPORT = Element(".platform-scrollable h4 + p", "Отчет об обработке", self.page)
        self.HISTORY_STEP_EVENTS = ElementsList(".platform-scrollable h4 + div p:nth-child(1)", "Список наименований событий на шаге", self.page)
        self.HISTORY_STEP_DATE_AND_USER = ElementsList(".platform-scrollable h4 + div p:nth-child(1)", "Список дат и юзеров для событий шагов", self.page)

        #FILTERS
        self.FILTER_PROBLEM_NUMBER_FIELD = Element("(//span[contains(@class, 'ant-input-affix-wrapper-borderless')])[1]/input", "Поле фильтра 'Номер СП'", self.page)
        self.FILTER_PROBLEM_NAME_FIELD = Element("(//span[contains(@class, 'ant-input-affix-wrapper-borderless')])[2]/input", "Поле фильтра 'Наименование СП'", self.page)

        #MODAL
        self.MODAL_FIELD = Element(".ant-modal-content textarea", "Поле 'Отчет по обработке'", self.page)
        self.MODAL_CLOSE_PROBLEM_BTN = Element(".ant-modal-content [variant=primary]", "Кнопка 'Закрыть", self.page)

        #SYSTEM_PROBLEMS_LIST
        self.PROBLEM_NUMBERS_LIST = ElementsList(".scrollable-body a", "Список номеров системных проблем", self.page)
        self.PROBLEM_CLEAR_BTN = ElementsList(".ant-input-clear-icon", "Кнопка сброса фильтра", self.page)
        self.PROBLEM_NAME = ElementsList(".scrollable-body a + p", "Наименование системной проблемы", self.page)
        self.PROBLEM_STATUS_COLOR_LIST = ElementsList(".scrollable-body [size='12']", "Список цветов статусов системных проблем", self.page)
        self.PROBLEM_NAMES_LIST = ElementsList(".scrollable-body a + p", "Список наименований системных проблем", self.page)
        self.PROBLEM_LIST_FILTER_SWITCHES = ElementsList("span.ant-radio-button + span", "Переключатели фильтра списка системных проблем", self.page)
        self.PROBLEM_FILTER_SETTINGS_BTN = Element("button[title='Настройки фильтра']", "Кнопка настройки фильтра", self.page)
        

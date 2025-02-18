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
        self.REVIEW_PROBLEM_TYPE = Element("(//form[@id='additional_values']//div[contains(@class, 'platform-grid-item')])[1]/p[2]", "Тип проблемы", self.page)
        self.REVIEW_REASON_TYPE = Element("(//form[@id='additional_values']//div[contains(@class, 'platform-grid-item')])[2]/p[2]", "Тип причины", self.page)
        self.REVIEW_INFLUENCE_POTENTIAL = Element("(//form[@id='additional_values']//div[contains(@class, 'platform-grid-item')])[3]/p[2]", "Потенциал влияния", self.page)
        self.REVIEW_EXPERTS = Element("(//form[@id='additional_values']//div[contains(@class, 'platform-grid-item')])[4]/span/input", "Привязывают только эксперты", self.page)
        self.REVIEW_OPERATOR_DESCRIPTION = Element("(//form[@id='additional_values']//div[contains(@class, 'platform-grid-item')])[5]/p[2]", "Описание для оператора", self.page)
        self.REVIEW_TECH_DESCRIPTION = Element("(//form[@id='additional_values']//div[contains(@class, 'platform-grid-item')])[6]/p[2]", "Техническое описание", self.page)
        self.REVIEW_NOTIFY_CLIENT = Element("//p[contains(text(), 'Сообщить клиенту')]/following-sibling::p", "Сообщить клиенту", self.page)
        self.REVIEW_SOLUTION_PLANNED_DURATION = Element("//p[contains(text(), 'Планируемый срок решения')]/following-sibling::p", "Планируемый срок решения", self.page)
        self.REVIEW_PROBLEM_REGION = Element("//p[contains(text(), 'Регион возникновения проблемы')]/following-sibling::p", "Регион возникновения проблемы", self.page)

        self.REVIEW_ATTEMPTS_NUM = Element("//p[contains(text(), 'Количество попыток_число')]/following-sibling::p", "Количество попыток_число", self.page)
        self.REVIEW_ADJUSTMENT_REQUIRED = Element("//p[contains(text(), 'Требуется корректировка?')]/following-sibling::p", "Требуется корректировка?", self.page)
        self.REVIEW_PROBLEMATIC_SERVICE = Element("//p[contains(text(), 'Проблемный сервис')]/following-sibling::p", "Проблемный сервис", self.page)
        self.REVIEW_CHARGES_AMOUNT = Element("//p[contains(text(), 'Сумма начислений')]/following-sibling::p", "Сумма начислений", self.page)

        self.REVIEW_CLIENT_TYPE = Element("//p[contains(text(), 'Тип клиента')]/following-sibling::p", "Тип клиента", self.page)
        self.REVIEW_SERVICE_NAME = Element("//p[contains(text(), 'Название услуги')]/following-sibling::p", "Название услуги", self.page)
        self.REVIEW_CLIENT_CONTACT_AGAIN = Element("//p[contains(text(), 'Клиент обращается повторно?')]/following-sibling::p", "Клиент обращается повторно?", self.page)
        self.REVIEW_PROBLEM_OCCURANCE_DATE = Element("//p[contains(text(), 'Дата возникновения проблемы')]/following-sibling::p", "Дата возникновения проблемы", self.page)
        self.REVIEW_CLIENT_TYPE = Element("//p[contains(text(), 'Тип клиента')]/following-sibling::p", "Тип клиента", self.page)

        self.REVIEW_PROCESS_BEFORE = Element(".ant-collapse-content-box .platform-grid-item:nth-child(1)>div>div", "Обработать до", self.page)
        self.REVIEW_PRIORITY = Element(".ant-collapse-content-box .platform-grid-item:nth-child(2)", "Приоритет", self.page)
        self.REVIEW_CREATION_DATE = Element(".ant-collapse-content-box .platform-grid-item:nth-child(3) p:nth-child(2)", "Дата создания", self.page)
        self.REVIEW_REGISTERED = Element(".ant-collapse-content-box .platform-grid-item:nth-child(4)", "Зарегистрировал", self.page)
        self.REVIEW_PLANNED_END_DATE = Element(".ant-collapse-content-box .platform-grid-item:nth-child(5) p:nth-child(2)", "Дата закрытия (план)", self.page)
        self.REVIEW_FACT_END_DATE = Element(".ant-collapse-content-box .platform-grid-item:nth-child(6)  p:nth-child(2)", "Дата закрытия (факт)", self.page)
        self.REVIEW_ORIGIN_DATE = Element(".ant-collapse-content-box .platform-grid-item:nth-child(7) p:nth-child(2)", "Дата возникновения", self.page)

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
        

from playwright.sync_api import Page

from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import Element, ElementsList


class SystemProblems(DynamicForms):
    """Страница /common-faults-list/all
    'Системные проблемы'"""
    def __init__(self, page: Page):
        self.page = page

        #OPTION_BTNS
        self.ADD_PROBLEM_BTN = Element("[variant=primary]", "Кнопка 'Добавить'", self.page)
        self.EDIT_PROBLEM_BTN = Element(".ant-tabs-content-holder button", "Кнопка 'Редактировать'", self.page)
        self.PROCESSING_DEFAULT_BTN = ElementsList("h2 button:nth-child(1)", "Кнопка 'Обработка'", self.page)
        self.PROCESSING_OPTION = ElementsList("[data-menu-id*='rc-menu-uuid'] .ant-dropdown-menu-title-content", "Выбор 'Передачи на обработку'", self.page)
        self.PROBLEM_CLOSE_DEFAULT_BTN = Element("[variant=default]:nth-child(5) div", "Кнопка 'Обработка'", self.page)

        #TABS
        self.PROCESSING_HISTORY_TAB = Element(".ant-tabs-tab:nth-of-type(6)", "Таб 'История обработки'", self.page)

        #REVIEW_TAB
        self.REVIEW_PROBLEM_TYPE = Element("//p[contains(text(), 'Тип проблемы')]/following-sibling::p", "Тип проблемы", self.page)
        self.REVIEW_REASON_TYPE = Element("//p[contains(text(), 'Тип причины')]/following-sibling::p", "Тип причины", self.page)
        self.REVIEW_INFLUENCE_POTENTIAL = Element("//p[contains(text(), 'Потенциал влияния')]/following-sibling::p", "Потенциал влияния", self.page)
        self.REVIEW_EXPERTS = Element("//p[contains(text(), 'Привязывают только эксперты')]/following-sibling::span/input", "Привязывают только эксперты", self.page)
        self.REVIEW_OPERATOR_DESCRIPTION = Element("//p[contains(text(), 'Описание для оператора')]/following-sibling::p", "Описание для оператора", self.page)
        self.REVIEW_TECH_DESCRIPTION = Element("//p[contains(text(), 'Техническое описание')]/following-sibling::p", "Техническое описание", self.page)
        self.REVIEW_NOTIFY_CLIENT = Element("//p[contains(text(), 'Сообщить клиенту')]/following-sibling::p", "Сообщить клиенту", self.page)

        self.REVIEW_PROBLEMATIC_SERVICE = Element("//p[contains(text(), 'Проблемный сервис')]/following-sibling::p", "Проблемный сервис", self.page)
        self.REVIEW_ADJUSTMENT_REQUIRED = Element("//p[contains(text(), 'Требуется корректировка?')]/following-sibling::p", "Требуется корректировка?", self.page)
        self.REVIEW_ATTEMPTS_NUM = Element("//p[contains(text(), 'Количество попыток_число')]/following-sibling::p", "Количество попыток_число", self.page)
        self.REVIEW_CHARGES_AMOUNT = Element("//p[contains(text(), 'Сумма начислений')]/following-sibling::p", "Сумма начислений", self.page)

        self.REVIEW_CLIENT_TYPE = Element("//p[contains(text(), 'Тип клиента')]/following-sibling::p", "Тип клиента", self.page)
        self.REVIEW_SOLUTION_PLANNED_DURATION = Element("//p[contains(text(), 'Планируемый срок решения')]/following-sibling::p", "Планируемый срок решения", self.page)
        self.REVIEW_SERVICE_NAME = Element("//p[contains(text(), 'Название услуги')]/following-sibling::p", "Название услуги", self.page)
        self.REVIEW_CLIENT_CONTACT_AGAIN = Element("//p[contains(text(), 'Клиент обращается повторно?')]/following-sibling::p", "Клиент обращается повторно?", self.page)
        self.REVIEW_PROBLEM_OCCURANCE_DATE = Element("//p[contains(text(), 'Дата возникновения проблемы')]/following-sibling::p", "Дата возникновения проблемы", self.page)
        self.REVIEW_CLIENT_TYPE = Element("//p[contains(text(), 'Тип клиента')]/following-sibling::p", "Тип клиента", self.page)
        self.REVIEW_PROBLEM_REGION = Element("//p[contains(text(), 'Регион возникновения проблемы')]/following-sibling::p", "Регион возникновения проблемы", self.page)

        self.REVIEW_PROCESS_BEFORE = Element("//p[contains(text(), 'Обработать до')]/following-sibling::div/div", "Обработать до", self.page)
        self.REVIEW_CREATION_DATE = Element("//p[contains(text(), 'Дата создания')]/following-sibling::p", "Дата создания", self.page)
        self.REVIEW_PLANNED_END_DATE = Element("//p[contains(text(), 'Дата закрытия (план)')]/following-sibling::p", "Дата закрытия (план)", self.page)
        self.REVIEW_ORIGIN_DATE = Element("//p[(text() = 'Дата возникновения')]/following-sibling::p", "Дата возникновения", self.page)
        self.REVIEW_PRIORITY = Element("//p[contains(text(), 'Приоритет')]/following-sibling::p", "Приоритет", self.page)
        self.REVIEW_REGISTERED = Element("//p[contains(text(), 'Зарегистрировал')]/following-sibling::p", "Зарегистрировал", self.page)
        self.REVIEW_FACT_END_DATE = Element("//p[contains(text(), 'Дата закрытия (факт)')]/following-sibling::p", "Дата закрытия (факт)", self.page)
        
        #HISTORY_TAB
        self.HISTORY_STEP_NAME_LIST = ElementsList(".ant-tabs-tabpane-active .scrollable-body div:nth-child(1) > p", "Список наименований шагов", self.page)
        self.HISTORY_STEP_NAME = Element(".platform-scrollable h3", "Наименование шага", self.page)
        self.HISTORY_STEP_CREATION_DATE = Element(".platform-scrollable h3 + p", "Время создания шага", self.page)
        self.HISTORY_PLANNED_END_DATE = Element("//p[contains(text(), 'Дата завершения (план)')]/following-sibling::p", "Дата завершения (план)", self.page) 
        self.HISTORY_END_DATE = Element("//p[contains(text(), 'Дата завершения (факт)')]/following-sibling::p", "Дата завершения (факт)", self.page)
        self.HISTORY_QUEUE = Element("//p[contains(text(), 'Очередь')]/following-sibling::p", "Очередь", self.page)
        self.HISTORY_DURATION = Element("//p[contains(text(), 'Продолжительность')]/following-sibling::p", "Продолжительность", self.page)

        self.PROCESSING_REPORT = Element(".platform-scrollable h4 + p", "Отчет об обработке", self.page)
        self.HISTORY_STEP_EVENTS = ElementsList(".platform-scrollable h4 + div p:nth-child(1)", "Список наименований событий на шаге", self.page)
        self.HISTORY_STEP_DATE_AND_USER = ElementsList(".platform-scrollable h4 + div p:nth-child(1)", "Список дат и юзеров для событий шагов", self.page)

        #FILTERS
        self.FILTER_PROBLEM_NUMBER_FIELD = Element("input[placeholder='Номер СП']", "Поле фильтра 'Номер СП'", self.page)
        self.FILTER_PROBLEM_NAME_FIELD = Element("input[placeholder='Наименование СП']", "Поле фильтра 'Наименование СП'", self.page)

        #MODAL
        self.MODAL_FIELD = Element(".ant-modal-content textarea", "Поле 'Отчет по обработке'", self.page)
        self.MODAL_CLOSE_PROBLEM_BTN = Element(".ant-modal-content [variant=primary]", "Кнопка 'Закрыть", self.page)

        #SYSTEM_PROBLEMS_LIST
        self.PROBLEM_NUMBER = Element(".scrollable-body>div>div>div:nth-of-type(1) a", "Номер системной проблемы", self.page)
        self.PROBLEM_NUMBERS_LIST = ElementsList(".scrollable-body a", "Список номеров системных проблем", self.page)
        self.PROBLEM_NUMBERS_LIST_TEST = ElementsList(".scrollable-body a", "Список номеров системных проблем", self.page)
        self.PROBLEM_CLEAR_BTN = ElementsList(".ant-input-clear-icon", "Кнопка сброса фильтра", self.page)
        self.PROBLEM_NAME = Element(".scrollable-body a + p:nth-of-type(1)", "Наименование системной проблемы", self.page)
        self.PROBLEM_STATUS_COLOR_LIST = ElementsList(".scrollable-body [size='12']", "Список цветов статусов системных проблем", self.page)
        self.PROBLEM_NAMES_LIST = ElementsList(".scrollable-body a + p", "Список наименований системных проблем", self.page)
        self.PROBLEM_NAME_CLEAR_BTN = Element(".ant-input-clear-icon:nth-child(2)", "Кнопка сброса фильтра по наименованию", self.page)
        self.PROBLEM_LIST_FILTER_SWITCHES = ElementsList("span.ant-radio-button + span", "Переключатели фильтра списка системных проблем", self.page)
        self.PROBLEM_FILTER_SETTINGS_BTN = Element("button[title='Настройки фильтра']", "Кнопка настройки фильтра", self.page)
        

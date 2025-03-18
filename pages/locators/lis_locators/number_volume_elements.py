from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList, SelectLIS


class NumberVolumeElementsLis(BaseElementsLis):
    """Страница Номерная емкость LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER
        self.TITLE = Element("div.content-section-header__left", "Заголовок страницы", self.page)
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы", self.page)

        # TAB Список MSISDN верхние кнопки
        self.RESERVE_BTN = Element("[ng-click*='reserveDialog']", "Кнопка 'Зарезервировать'", self.page)
        self.HISTORY_BTN = Element("[ng-click*='historyDialog']", "Кнопка 'История'", self.page)
        self.SET_IN_USE_BTN = Element("[ng-click*='setNumbersAsInUse']", "Кнопка 'В эксплуатацию'", self.page)
        self.ADD_NUMBER_BTN = Element("[ng-click*='dialogs.addNumberDialog.show()']", "Кнопка 'Добавление номера'",
                                      self.page)
        self.EDIT_NUM_BTN = Element("[ng-click*='dialogs.editNumberDialog.show()']",
                                    "Кнопка 'Редактирование номера'", self.page)
        self.GROUP_EDIT_BTN = Element("[ng-disabled*='massEditNumbersDisabled'] div ps-button",
                                      "Кнопка 'Массовое редактирование'", self.page)
        self.GROUP_EDIT_NUM_ATTRIBUTE_BTN = Element("ps-list-item[ng-click*='massEditNumbersAttributes']",
                                                    "Кнопка 'Редактировать атрибуты номеров'", self.page)
        self.GROUP_EDIT_BUSY_NUM_ATTRIBUTE_BTN = Element("ps-list-item[ng-click*='massEditBusyNumbersAttributes']",
                                                         "Кнопка 'Редактировать атрибуты занятых номеров'", self.page)
        self.CHANGE_NUM_CLASS_BTN = Element("[ng-click*='massEditNumberClassDialog']",
                                            "Кнопка 'Изменить класс номера'", self.page)
        self.LINK_DEF_TO_ABC_BTN = Element("[ng-click*='dialogs.linkingNumberDialog']",
                                           "Кнопка 'Связывание номеров DEF и ABC'", self.page)
        self.UNLINK_BTN = Element("[ng-click*='massActions.unLinkNumbers']", "Кнопка 'Развязать'", self.page)
        self.SET_OUT_USE_BTN = Element("[ng-click*='setNumbersAsOutUse']", "Кнопка 'Исключить'", self.page)
        self.SET_OUT_OF_ISOLATION_BTN = Element("[ng-click*='outOfIsolation']", "Кнопка 'Вывод из карантина'",
                                                self.page)
        self.LINK_NUMBER_BTN = Element("[ng-click*='linkingNumberDialog']", "Кнопка 'Связывание номеров DEF и ABC'",
                                       self.page)
        self.DOWNLOAD_BTN = Element("[ng-click*='massActions.csvExport']", "Кнопка 'Выгрузить в Excel'", self.page)
        self.REFRESH_BTN = Element("[ng-click*='search'][icon='refresh']", "Кнопка 'Обновить'", self.page)
        self.SEARCH_BTN = Element("a.lis-toolbar-search__link", "Кнопка 'Поиск'", self.page)
        self.NUMBERS_COUNTER = Element("div.toolbar-right a.toolbar-quick-filter__item_active", "Счетчик номеров",
                                       self.page)
        self.ZONE_TYPE = ElementsList("[ng-click*='numZoneSwitch']", "Кнопки 'Код зоны нумерации'", self.page)

        # TAB Список MSISDN заголовки столбцов таблицы
        self.DATE_CHANGE_STATUS_HEADER = Element("//table//tr/th[contains(@class, 'n-grid__title')][7]",
                                                 "Заголовок/Кнопка 'Дата смены статуса'", self.page)
        self.MSISDN_HEADER = Element("//ps-grid[contains(@rows, 'model.phoneNumbers.rows')]//tr/th[contains(@class,"
                                     " 'n-grid__title')][3]", "Заголовок/Кнопка 'MSISDN'", self.page)

        # TAB Список MSISDN Таблица Общая часть + DEF
        self.CHECK_ALL_BTN = Element("//ps-tabs//tr/th[2]", "Кнопка 'Выбрать все'", self.page)
        self.TABLE_LINE = ElementsList("tr.n-grid__row", "Строки таблицы", self.page)
        self.PHONE_NUMBERS_COLOUR = ElementsList("tr.n-grid__row td:nth-child(1)", "Цвета статусов номер телефонов",
                                                 self.page)
        self.LINE_CHECKBOXES = ElementsList("tr.n-grid__row span.n-check-checkbox", "Чекбоксы строк таблицы", self.page)
        self.PHONE_NUMBERS = ElementsList("tr.n-grid__row td:nth-child(3)", "Номера телефонов", self.page)
        self.PHONE_NUMBERS_CLASS = ElementsList("tr.n-grid__row td:nth-child(5)", "Классы номеров телефонов",
                                                self.page)
        self.PHONE_NUMBERS_STATUS = ElementsList("tr.n-grid__row td:nth-child(6)", "Статусы номеров телефонов",
                                                 self.page)
        self.PHONE_NUMBERS_STATE = ElementsList("tr.n-grid__row td:nth-child(8)", "Состояния номеров телефонов",
                                                self.page)
        self.PHONE_NUMBERS_BLOCKING = ElementsList("tr.n-grid__row td:nth-child(11)", "Блокировки номеров телефонов",
                                                   self.page)
        self.PHONE_NUMBERS_COMMUTATORS = ElementsList("tr.n-grid__row td:nth-child(12)", "Коммутатор номеров телефонов",
                                                      self.page)
        self.PHONE_NUMBERS_STANDARDS = ElementsList("tr.n-grid__row td:nth-child(13)", "Стандарт номеров телефонов",
                                                    self.page)
        self.PHONE_NUMBERS_OPERATORS = ElementsList("tr.n-grid__row td:nth-child(14)", "Оператор номеров телефонов",
                                                    self.page)
        self.PHONE_NUMBERS_TYPES = ElementsList("tr.n-grid__row td:nth-child(15)", "Тип операции номеров телефонов",
                                                self.page)
        self.COMMENTS = ElementsList("tr.n-grid__row td:nth-child(20)", "Комментарии номеров телефонов",
                                     self.page)
        self.NO_MSISDN_OR_LOADER = Element(
            "[rows='model.phoneNumbers.rows'] [ps-link-element='elements.loader.center']",
            "Окно 'Нет данных' или 'Загрузка...' в списке MSISDN", self.page)

        # TAB Список MSISDN Таблица ABC
        self.PHONE_NUMBERS_COMMUTATORS_ABC = ElementsList("tr.n-grid__row td:nth-child(13)",
                                                          "Коммутатор номеров телефонов", self.page)
        self.PHONE_NUMBERS_STANDARDS_ABC = ElementsList("tr.n-grid__row td:nth-child(14)", "Стандарт номеров телефонов",
                                                        self.page)
        self.PHONE_NUMBERS_OPERATORS_ABC = ElementsList("tr.n-grid__row td:nth-child(15)", "Оператор номеров телефонов",
                                                        self.page)
        self.PHONE_NUMBERS_TYPES_ABC = ElementsList("tr.n-grid__row td:nth-child(16)", "Тип операции номеров телефонов",
                                                    self.page)
        self.COMMENTS_ABC = ElementsList("tr.n-grid__row td:nth-child(21)", "Комментарии номеров телефонов",
                                         self.page)

        # Модалка История по номеру
        self.REFRESH_HISTORY_BTN = Element("[ng-click*='refreshGrid()']", "Кнопка 'Обновить данные'", self.page)
        self.HISTORY_TYPE_BTN = ElementsList("[ng-click*='historyDialog.setActive']", "Кнопка 'Обновить данные'",
                                             self.page)

        # Поиск
        self.MSISDN_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][1]//div[contains(@class,"
                                         " 'button')]", "Кнопка открыть фильтр 'MSISDN'", self.page)
        self.MSISDN_OPTION_INTERVAL = Element("//*[count(ps-list-item) = 7]/ps-list-item[contains(@user-value,"
                                              " 'INTERVAL')]", "Опция фильтра 'MSISDN' По диапазону", self.page)
        self.MSISDN_OPTION_VALUE = Element("//*[count(ps-list-item) = 7]/ps-list-item[contains(@user-value, 'VALUE')]",
                                           "Опция фильтра 'MSISDN' Точное значение", self.page)
        self.MSISDN_SELECTED_OPTIONS = Element("//div[@class='lis-search-numbers-params__item'][1]"
                                               "//div[contains(@ps-link-element, 'elements.value')]",
                                               "Выбранное значение 'MSISDN'", self.page)
        self.MSISDN_FILTER_INPUT = Element("//div[@class='lis-search-numbers-params__item'][1]//input",
                                           "Поле ввода фильтр 'MSISDN'", self.page)
        self.MSISDN_FILTER_INPUT_FROM = Element("[ng-model*='searchParameters.MSISDN.startValue']",
                                                "Поле ввода фильтр 'MSISDN' Начальное значение", self.page)
        self.MSISDN_FILTER_INPUT_TO = Element("[ng-model*='searchParameters.MSISDN.endValue']",
                                              "Поле ввода фильтр 'MSISDN' Конечное значение", self.page)
        self.CATEGORY_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][2]//div[contains(@class,"
                                           " 'button')]", "Кнопка открыть фильтр 'Категория'", self.page)
        self.CLASS_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][3]//div[contains(@class,"
                                        " 'button')]", "Кнопка открыть фильтр 'Класс'", self.page)
        self.CLASS_FILTER_OPTIONS = ElementsList("//*[@user-value='item.numberClassId']",
                                                 "Опции фильтр 'Класс'", self.page)
        self.STATUS_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][4]//div[contains(@class,"
                                         " 'button')]", "Кнопка открыть фильтр 'Статус'", self.page)
        self.STATUS_OPTION_BUSY = Element("//span[contains(text(), 'Занят')]",
                                         "Фильтр 'Статус' опция 'Занят'", self.page)
        self.STATUS_OPTION_UNAVAILABLE = Element("//span[contains(text(), 'Недоступен')]",
                                                 "Фильтр 'Статус' опция 'Недоступен'", self.page)
        self.STATUS_OPTION_FREE = Element("//span[contains(text(), 'Свободен')]",
                                          "Фильтр 'Статус' опция 'Свободен'", self.page)
        self.CHANGE_STATUS_DATE_BTN = Element("//div[@class='lis-search-numbers-params__item'][5]//div[contains(@class,"
                                              " 'button')]", "Кнопка открыть фильтр 'Дата смены статуса'", self.page)
        self.STATE_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][6]//div[contains(@class,"
                                        " 'button')]", "Кнопка открыть фильтр 'Состояние'", self.page)
        self.STATE_FILTER_OPTIONS = ElementsList("//*[@user-value='item.phoneNumberStateId']",
                                                 "Опции фильтр 'Состояние'", self.page)
        self.OPERATOR_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][7]//div[contains(@class,"
                                           " 'button')]", "Кнопка открыть фильтр 'Оператор'", self.page)
        self.USER_FILTER_FIELD = Element("//div[@class='lis-search-numbers-params__item'][8]//input",
                                         "Поле ввода 'Пользователь'", self.page)
        self.NUMBER_TYPE_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][9]//div[contains(@class,"
                                              " 'button')]", "Кнопка открыть фильтр 'Тип нумерации'", self.page)
        self.STANDARD_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][10]//div[contains(@class,"
                                           " 'button')]", "Кнопка открыть фильтр 'Стандарт'", self.page)
        self.COMMUTATOR_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][11]//div[contains(@class,"
                                             " 'button')]/ps-button[2]", "Кнопка открыть фильтр 'Коммутатор'",
                                             self.page)
        self.BLOCKING_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][12]//div[contains(@class,"
                                           " 'button')]", "Кнопка открыть фильтр 'Блокировка'", self.page)
        self.BLOCKED_OPTION = Element("//ps-list-item//span[contains(text(), 'Установлена')]",
                                          "Фильтр 'Блокировка' вариант 'Установлена'", self.page)
        self.NOT_BLOCKED_OPTION = Element("//ps-list-item//span[contains(text(), 'Не установлена')]",
                                          "Фильтр 'Блокировка' вариант 'Не установлена'", self.page)
        self.LINK_NUMBER_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][13]//div[contains("
                                              "@class, 'button')]", "Кнопка открыть фильтр 'Связанный номер'",
                                              self.page)
        self.LINK_NUMBER_OPTION_INTERVAL = Element("//*[count(ps-list-item) = 5]/ps-list-item[contains(@user-value,"
                                                   " 'INTERVAL')]", "Опция фильтра 'Связанный номер' По диапазону",
                                                   self.page)
        self.LINK_NUMBER_SELECTED_OPTIONS = Element("//div[@class='lis-search-numbers-params__item'][13]//div[contains"
                                                    "(@ps-link-element, 'elements.value')]",
                                                    "Выбранное значение 'Связанный номер'", self.page)
        self.GOAL_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][14]//div[contains(@class,"
                                       " 'button')]", "Кнопка открыть фильтр 'Цель использования'", self.page)
        self.BILLING_CONNECTION_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][15]"
                                                     "//div[contains(@class, 'button')]",
                                                     "Кнопка открыть фильтр 'Принадлежность к биллингу'", self.page)
        self.COMMENT_FILTER_BTN = Element("//div[@class='lis-search-numbers-params__item'][16]//div[contains("
                                          "@class, 'button')]", "Кнопка открыть фильтр 'Комментарий'",
                                          self.page)
        self.COMMENT_OPTION_NOT_FILLED = Element("//*[count(ps-list-item) = 3]/ps-list-item[contains(@user-value,"
                                                 " 'true')]", "Опция фильтра 'Комментарий' Не заполнен", self.page)
        self.COMMENT_SELECTED_OPTIONS = Element("//div[@class='lis-search-numbers-params__item'][16]//div[contains"
                                                "(@ps-link-element, 'elements.value')]",
                                                "Выбранное значение 'Комментарий'", self.page)

        self.FILTER_SEARCH_BTN = Element(".lis-search-numbers-view [ng-click*='search()']", "Кнопка 'Найти'",
                                         self.page)
        self.CLEAR_FILTER_BTN = Element(".lis-search-numbers-view [ng-click*='numValueSearchClear()']",
                                        "Кнопка 'Очистить фильтры'", self.page)

        # Модальное окно Добавление номера
        self.MODAL_ADD_NUMBER = Element("//body/div[contains(@class, 'n-popup')][1]", "Окно 'Добавление номера'",
                                        self.page)
        self.MODAL_ADD_NUMBER_TITLE = Element("//body/div[contains(@class, 'n-popup')][1]/div[1]/div[1]",
                                              "Заголовок окна 'Добавление номера'", self.page)
        self.LOAD_NUMBER_BUTTON = Element("//body/div[contains(@class, 'n-popup')][1]//ps-button[@icon='open']",
                                          "Кнопка 'Загрузить номера'", self.page)
        self.UPLOADED_FILE_NAME = Element("//body/div[contains(@class, 'n-popup')][1]//span[@ng-if='addNumberDialog.file']",
                                          "Название загруженного файла", self.page)
        self.DELETE_FILE_BUTTON = Element("//body/div[contains(@class, 'n-popup')][1]//ps-button[@icon='trash-inverted']",
                                          "Кнопка 'Удалить файл'", self.page)
        self.START_PHONE_NUMBER = Element("[name*='startPhoneNumber']", "Поле ввода 'Начальный MSISDN'", self.page)
        self.COUNT_PHONE_NUMBER = Element("[name*='countPhoneNumber']", "Поле ввода 'Количество MSISDN'", self.page)
        self.CHOOSE_COMMUTATOR_BTN = Element(".n-popup [ng-model*='equipmentId'] ps-button:last-child",
                                             "Кнопка выбора 'Коммутатор'", self.page)
        self.CHOOSE_COMMUTATOR_BLOCK = Element(".n-popup [ng-model*='.equipmentId']", "Блок 'Коммутатор'", self.page)
        self.CHOSEN_CATEGORY_FIELD = Element("[ng-model*='numberCategoryId'] > div > div",
                                             "Поле 'Категория'", self.page)
        self.CHOSEN_CATEGORY_BLOCK = Element("[ng-model*='numberCategoryId']", "Блок 'Категория'", self.page)
        self.CHOSEN_STATUS_FIELD = Element("[ng-model*='status']", "Поле 'Статус'", self.page)
        self.NUMBER_TYPE_FIELD = Element("[ng-model*='phoneNumberTypeId'] > div > div", "Поле 'Тип нумерации'",
                                         self.page)
        self.NUMBER_TYPE_BLOCK = Element("[ng-model*='phoneNumberTypeId']", "Блок 'Тип нумерации'", self.page)
        self.NUMBER_TYPE_OPTIONS = ElementsList("//ps-list-item[contains(@user-value, 'type.phoneNumberTypeId')]",
                                                "Варианты списка 'Тип нумерации'", self.page)
        self.OPERATOR_FIELD_BLOCK = Element("[ng-model*='operatorId']", "Блок 'Оператор'", self.page)
        self.OPERATOR_FIELD = Element("[ng-model*='operatorId'] > div > div", "Поле 'Оператор'", self.page)
        self.OPERATOR_OPTIONS = ElementsList("//ps-list-item[contains(@user-value, 'operator.operatorId')]",
                                             "Варианты списка 'Оператор'", self.page)
        self.AVAILABLE_TO_LINK = Element(".n-popup [ng-model*='phoneNumberTypeLinkId'] > div > div",
                                         "Поле 'Доступность для связки'", self.page)
        self.USE_GOAL_FIELD = Element("[ng-model*='phoneNumberPurposeId'] > div > div",
                                      "Поле 'Цель использования'", self.page)
        self.COMMENT_FIELD = Element(".n-popup [ng-model*='note']", "Поле 'Комментарий'", self.page)
        self.NUMBER_TYPE_LINE = ElementsList("//body/div[contains(@class, 'n-popup')][1] //td/..",
                                             "Строки таблицы 'Разметка классов'", self.page)
        self.NUMBER_TYPE_CLASSES = ElementsList("//body/div[contains(@class, 'n-popup')][1]//tr/td[2]",
                                              "Классы 'Разметка классов'", self.page)
        self.NUMBER_TYPE_CHECKBOXES = ElementsList("//body/div[contains(@class, 'n-popup')][1]//tr/td[1]",
                                                   "Чекбоксы 'Разметка классов'", self.page)
        self.NUMBER_TYPE_ALL_CHECKBOX = Element("//body/div[contains(@class, 'n-popup')][1]//tr/th[1]",
                                                "Выбрать все чекбоксы 'Разметка классов'", self.page)
        self.CANCEL_ADD_NUMBER = Element("//ps-button[contains(@ng-click, 'addNumberDialog.close()')]",
                                         "Кнопка 'Отменить' добавление номера", self.page)

        # Модальное окно Связывание номеров
        self.TEMPLATE_INPUT = Element("[ng-model*='templateSearch']", "Поле ввода 'Шаблон отбора'", self.page)
        self.ABC_START_INPUT = Element("[ng-model*='startPhoneNumberABC']", "Поле ввода 'Начальное значение ABC'",
                                       self.page)
        self.ABC_END_INPUT = Element("[ng-model*='endPhoneNumberABC']", "Поле ввода 'Конечное значение ABC'", self.page)
        self.DEF_START_INPUT = Element("[ng-model*='startPhoneNumberDEF']", "Поле ввода 'Начальное значение ABC'",
                                       self.page)
        self.DEF_END_INPUT = Element("[ng-model*='endPhoneNumberDEF']", "Поле ввода 'Конечное значение ABC'", self.page)

        # Модальное окно Изменение класса номера
        self.CHOOSE_CLASS_TITLE = Element("//*[contains(@ng-model, 'editNumber.numberClassId')]/../div[1]",
                                          "Заголовок 'Класс номера'", self.page)
        self.CHOOSE_CLASS_FIELD = SelectLIS("[ng-model*='editNumber.numberClassId'] [ps-link-element='elements.value']",
                                          "Поле выбора класса", self.page)
        self.CLASS_OPTIONS = ElementsList("ps-list-item[user-value='item.numberClassId']", "Опции выбора класса",
                                          self.page)
        self.CONFIRM_CHANGE_CLASS_BTN = Element("[on-submit*='updateNumberClass']", "Кнопка 'Сохранить'",
                                                self.page)
        self.CANCEL_CHANGE_CLASS_BTN = Element("[ng-click*='massEditNumberClassDialog.close']",
                                               "Кнопка 'Отменить'", self.page)

        # TAB Шаблоны классов номеров Кнопки для работы с шаблонами
        self.ADD_TEMPLATE_BTN = Element("[ng-click*=addTemplate]", "Кнопка 'Добавить шаблон'", self.page)
        self.EDIT_TEMPLATE_BTN = Element("[ng-click*=editTemplate]", "Кнопка 'Редактировать шаблон'", self.page)
        self.DELETE_TEMPLATE_BTN = Element("[ng-click*=deleteTamplates]", "Кнопка 'Удалить шаблон'", self.page)
        self.UPDATE_TEMPLATE_BTN = Element("[ng-click*='refreshGrid(model.templates)']",
                                           "Кнопка 'Обновить список шаблонов'", self.page)

        # TAB Шаблоны классов номеров Таблица шаблонов
        self.TEMPLATE_TABLE_COLUMN_NAMES = ElementsList("[rows='model.templates.rows'] tr.n-grid__head-row th>div",
                                               "Названия столбцов таблицы шаблонов", self.page)
        self.TEMPLATE_TABLE_LINE = ElementsList("[rows='model.templates.rows'] tr.n-grid__row",
                                       "Строки таблицы шаблонов", self.page)
        self.TEMPLATE_NAME = ElementsList("[rows='model.templates.rows'] tr.n-grid__row td:nth-child(2)",
                                           "Наименование шаблона", self.page)
        self.TEMPLATE_CLASS = ElementsList("[rows='model.templates.rows'] tr.n-grid__row td:nth-child(3)",
                                           "Класс шаблона", self.page)
        self.TEMPLATE_PRIORITY = ElementsList("[rows='model.templates.rows'] tr.n-grid__row td:nth-child(4)",
                                           "Приоритет шаблона", self.page)
        self.TEMPLATE_IS_DEFAULT = ElementsList("[rows='model.templates.rows'] tr.n-grid__row td:nth-child(5)",
                                           "Используется шаблон 'по умолчанию'", self.page)

        # Модальное окно Добавление шаблона класса
        self.TEMPLATE_NAME_INPUT_TITLE = Element("//*[contains(@ng-model, 'addTemplate.values.name')]/../div[1]",
                                           "Название поля 'Наименование шаблона'", self.page)
        self.TEMPLATE_NAME_INPUT = Element("input[ng-model*='addTemplate.values.name']",
                                           "Поле ввода 'Наименование шаблона'", self.page)
        self.CHOOSE_CLASS_BLOCK_TITLE = Element(
            "//*[contains(@ng-model, 'addTemplate.values.numberClassId')]/../div[1]",
            "Название поля 'Класс'", self.page)
        self.CHOOSE_CLASS_BLOCK = SelectLIS("[ng-model*='addTemplate.values.numberClassId']",
                                          "Блок выбора 'Класс'", self.page)
        self.TEMPLATE_PRIORITY_INPUT_TITLE = Element(
            "//*[contains(@ng-model, 'addTemplate.values.priority')]/../div[1]",
            "Название поля 'Приоритет'", self.page)
        self.TEMPLATE_PRIORITY_INPUT = Element("input[ng-model*='addTemplate.values.priority']",
                                               "Поле ввода 'Приоритет'", self.page)
        self.TEMPLATE_IS_DEFAULT_CHECKBOX = Element("[ng-model*='addTemplate.values.isDefault'] span.n-check-checkbox",
                                                    "Чекбокс 'Использовать как Шаблон по умолчанию'", self.page)
        self.ADD_TEMPLATE_MODAL_BTN = Element("[on-submit*=addClassTemplate]", "Кнопка 'Добавить'", self.page)
        self.CLOSE_ADD_TEMPLATE_BTN = Element("[ng-click*='addTemplate.close']", "Кнопка 'Отменить'", self.page)

        # Модальное окно Редактирование шаблона класса
        self.EDIT_TEMPLATE_NAME_INPUT = Element("input[ng-model*='editTemplate.values.name']",
                                                "Поле ввода 'Наименование шаблона'", self.page)
        self.EDIT_CHOOSE_CLASS_BLOCK = SelectLIS("[ng-model*='editTemplate.values.numberClass.numberClassId']",
                                                 "Блок выбора 'Класс'", self.page)
        self.EDIT_TEMPLATE_PRIORITY_INPUT = Element("input[ng-model*='editTemplate.values.priority']",
                                                    "Поле ввода 'Приоритет'", self.page)
        self.EDIT_TEMPLATE_IS_DEFAULT_CHECKBOX = Element(
            "[ng-model*='editTemplate.values.isDefault'] span.n-check-checkbox",
            "Чекбокс 'Использовать как Шаблон по умолчанию'", self.page)
        self.EDIT_TEMPLATE_MODAL_BTN = Element("[on-submit*=editClassTemplate]", "Кнопка 'Добавить'", self.page)
        self.CLOSE_EDIT_TEMPLATE_BTN = Element("[ng-click*='editTemplate.close']", "Кнопка 'Отменить'", self.page)

        # TAB Шаблоны классов номеров Кнопки для работы с условиями
        self.ADD_RULE_BTN = Element("[ng-click*=addRules]", "Кнопка 'Добавить условие'", self.page)
        self.EDIT_RULE_BTN = Element("[ng-click*=editRules]", "Кнопка 'Редактировать условие'", self.page)
        self.DELETE_RULE_BTN = Element("[ng-click*=deleteRules]", "Кнопка 'Удалить условие'", self.page)

        # TAB Шаблоны классов номеров Таблица условий
        self.RULE_TABLE_COLUMN_NAMES = ElementsList("[rows='model.templatesRules.rows'] tr.n-grid__head-row th>div",
                                                    "Названия столбцов таблицы условий", self.page)
        self.RULE_TABLE_LINE = ElementsList("[rows='model.templatesRules.rows'] tr.n-grid__row",
                                            "Строки таблицы условий", self.page)
        self.RULE_NAME = ElementsList("[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(1)",
                                      "Наименование условия", self.page)
        self.RULE_CONDITION = ElementsList("[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(2)",
                                           "Условие", self.page)
        self.RULE_IS_ACTIVE = ElementsList("[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(3)",
                                           "Активность условия", self.page)
        self.RULE_TEST_NUMBER = ElementsList("[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(4)",
                                             "Тестовый номер", self.page)

        # Модальное окно Добавление условия шаблона
        self.RULE_NAME_INPUT_TITLE = Element("//*[contains(@ng-model, 'addRules.values.name')]/../div[1]",
                                             "Название поля 'Наименование условия'", self.page)
        self.RULE_NAME_INPUT = Element("input[ng-model*='addRules.values.name']",
                                       "Поле ввода 'Наименование условия'", self.page)
        self.RULE_CONDITION_INPUT_TITLE = Element("//*[contains(@ng-model, 'addRules.values.condition')]/../div[1]",
                                                  "Название поля 'Условие'", self.page)
        self.RULE_CONDITION_INPUT = Element("*[ng-model*='addRules.values.condition']",
                                            "Поле ввода 'Условие'", self.page)
        self.RULE_TEST_NUMBER_INPUT = Element("input[ng-model*='addRules.values.testMSISDN']",
                                              "Поле ввода 'Тестовый номер'", self.page)
        self.RULE_IS_ACTIVE_CHECKBOX = Element("[ng-model*='addRules.values.isActive'] span.n-check-checkbox",
                                               "Чекбокс 'Активировать условие'", self.page)
        self.ADD_RULE_MODAL_BTN = Element("[on-submit*=addRulesTemplate]", "Кнопка 'Добавить'", self.page)
        self.CLOSE_ADD_RULE_BTN = Element("[ng-click*='addRules.close']", "Кнопка 'Отменить'", self.page)

        # Модальное окно Редактирование условия шаблона
        self.EDIT_RULE_NAME_INPUT = Element("input[ng-model*='editRules.values.name']",
                                            "Поле ввода 'Наименование условия'", self.page)
        self.EDIT_RULE_CONDITION_INPUT = Element("*[ng-model*='editRules.values.condition']",
                                                 "Поле ввода 'Условие'", self.page)
        self.EDIT_RULE_TEST_NUMBER_INPUT = Element("input[ng-model*='editRules.values.testMSISDN']",
                                                   "Поле ввода 'Тестовый номер'", self.page)
        self.EDIT_RULE_IS_ACTIVE_CHECKBOX = Element("[ng-model*='editRules.values.isActive'] span.n-check-checkbox",
                                                    "Чекбокс 'Активировать условие'", self.page)
        self.EDIT_RULE_MODAL_BTN = Element("[on-submit*=editRulesTemplate]", "Кнопка 'Добавить'", self.page)
        self.CLOSE_EDIT_RULE_BTN = Element("[ng-click*='editRules.close']", "Кнопка 'Отменить'", self.page)

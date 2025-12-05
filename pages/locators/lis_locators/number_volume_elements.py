from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList, SelectLIS


class NumberVolumeElementsLis(BaseElementsLis):
    """Страница Номерная емкость LIS"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER
        self.TITLE = Element("div.content-section-header__left", "Заголовок страницы")
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы")

        # TAB Список MSISDN верхние кнопки
        self.RESERVE_BTN = Element("[ng-click*='reserveDialog']", "Кнопка 'Зарезервировать'")
        self.HISTORY_BTN = Element("[ng-click*='historyDialog']", "Кнопка 'История'")
        self.SET_IN_USE_BTN = Element("[ng-click*='setNumbersAsInUse']", "Кнопка 'В эксплуатацию'")
        self.ADD_NUMBER_BTN = Element("[ng-click*='dialogs.addNumberDialog.show()']", "Кнопка 'Добавление номера'")
        self.EDIT_NUM_BTN = Element("[ng-click*='dialogs.editNumberDialog.show()']", "Кнопка 'Редактирование номера'")
        self.GROUP_EDIT_BTN = Element(
            "[ng-disabled*='massEditNumbersDisabled'] div ps-button", "Кнопка 'Массовое редактирование'"
        )
        self.GROUP_EDIT_NUM_ATTRIBUTE_BTN = Element(
            "ps-list-item[ng-click*='massEditNumbersAttributes']", "Кнопка 'Редактировать атрибуты номеров'"
        )
        self.GROUP_EDIT_BUSY_NUM_ATTRIBUTE_BTN = Element(
            "ps-list-item[ng-click*='massEditBusyNumbersAttributes']",
            "Кнопка 'Редактировать атрибуты занятых номеров'",
        )
        self.CHANGE_NUM_CLASS_BTN = Element("[ng-click*='massEditNumberClassDialog']", "Кнопка 'Изменить класс номера'")
        self.LINK_DEF_TO_ABC_BTN = Element(
            "[ng-click*='dialogs.linkingNumberDialog']", "Кнопка 'Связывание номеров DEF и ABC'"
        )
        self.UNLINK_BTN = Element("[ng-click*='massActions.unLinkNumbers']", "Кнопка 'Развязать'")
        self.SET_OUT_USE_BTN = Element("[ng-click*='setNumbersAsOutUse']", "Кнопка 'Исключить'")
        self.SET_OUT_OF_ISOLATION_BTN = Element("[ng-click*='outOfIsolation']", "Кнопка 'Вывод из карантина'")
        self.LINK_NUMBER_BTN = Element("[ng-click*='linkingNumberDialog']", "Кнопка 'Связывание номеров DEF и ABC'")
        self.DOWNLOAD_BTN = Element("[ng-click*='massActions.csvExport']", "Кнопка 'Выгрузить в Excel'")
        self.REFRESH_BTN = Element("[ng-click*='search'][icon='refresh']", "Кнопка 'Обновить'")
        self.SEARCH_BTN = Element("a.lis-toolbar-search__link", "Кнопка 'Поиск'")
        self.NUMBERS_COUNTER = Element("div.toolbar-right a.toolbar-quick-filter__item_active", "Счетчик номеров")
        self.ZONE_TYPE = ElementsList("[ng-click*='numZoneSwitch']", "Кнопки 'Код зоны нумерации'")

        # TAB Список MSISDN заголовки столбцов таблицы
        self.DATE_CHANGE_CONDITION_HEADER = Element(
            "//table//tr/th[contains(@class, 'n-grid__title')][9]", "Заголовок/Кнопка 'Дата смены состояния'"
        )
        self.DATE_CHANGE_STATUS_HEADER = Element(
            "//table//tr/th[contains(@class, 'n-grid__title')][7]", "Заголовок/Кнопка 'Дата смены статуса'"
        )
        self.MSISDN_HEADER = Element(
            "//ps-grid[contains(@rows, 'model.phoneNumbers.rows')]//tr/th[contains(@class, 'n-grid__title')][3]",
            "Заголовок/Кнопка 'MSISDN'",
        )

        # TAB Список MSISDN Таблица Общая часть + DEF
        self.CHECK_ALL_BTN = Element("//ps-tabs//tr/th[2]", "Кнопка 'Выбрать все'")
        self.TABLE_LINE = ElementsList("tr.n-grid__row", "Строки таблицы")
        self.PHONE_NUMBERS_COLOUR = ElementsList("tr.n-grid__row td:nth-child(1)", "Цвета статусов номер телефонов")
        self.LINE_CHECKBOXES = ElementsList("tr.n-grid__row span.n-check-checkbox", "Чекбоксы строк таблицы")
        self.PHONE_NUMBERS = ElementsList("tr.n-grid__row td:nth-child(3)", "Номера телефонов")
        self.PHONE_NUMBERS_CLASS = ElementsList("tr.n-grid__row td:nth-child(5)", "Классы номеров телефонов")
        self.PHONE_NUMBERS_STATUS = ElementsList("tr.n-grid__row td:nth-child(6)", "Статусы номеров телефонов")
        self.PHONE_NUMBERS_STATE = ElementsList("tr.n-grid__row td:nth-child(8)", "Состояния номеров телефонов")
        self.PHONE_NUMBERS_BLOCKING = ElementsList("tr.n-grid__row td:nth-child(11)", "Блокировки номеров телефонов")
        self.PHONE_NUMBERS_COMMUTATORS = ElementsList("tr.n-grid__row td:nth-child(12)", "Коммутатор номеров телефонов")
        self.PHONE_NUMBERS_STANDARDS = ElementsList("tr.n-grid__row td:nth-child(13)", "Стандарт номеров телефонов")
        self.PHONE_NUMBERS_OPERATORS = ElementsList("tr.n-grid__row td:nth-child(14)", "Оператор номеров телефонов")
        self.PHONE_NUMBERS_TYPES = ElementsList("tr.n-grid__row td:nth-child(15)", "Тип операции номеров телефонов")
        self.COMMENTS = ElementsList("tr.n-grid__row td:nth-child(20)", "Комментарии номеров телефонов")
        self.NO_MSISDN_OR_LOADER = Element(
            "[ps-link-element='elements.loader.center']",
            "Окно 'Нет данных' или 'Загрузка...' в списке MSISDN",
        )

        # TAB Список MSISDN Таблица ABC
        self.PHONE_NUMBERS_COMMUTATORS_ABC = ElementsList(
            "tr.n-grid__row td:nth-child(13)", "Коммутатор номеров телефонов"
        )
        self.PHONE_NUMBERS_STANDARDS_ABC = ElementsList("tr.n-grid__row td:nth-child(14)", "Стандарт номеров телефонов")
        self.PHONE_NUMBERS_OPERATORS_ABC = ElementsList("tr.n-grid__row td:nth-child(15)", "Оператор номеров телефонов")
        self.PHONE_NUMBERS_TYPES_ABC = ElementsList("tr.n-grid__row td:nth-child(16)", "Тип операции номеров телефонов")
        self.COMMENTS_ABC = ElementsList("tr.n-grid__row td:nth-child(21)", "Комментарии номеров телефонов")

        # Модалка История по номеру
        self.REFRESH_HISTORY_BTN = Element("[ng-click*='refreshGrid()']", "Кнопка 'Обновить данные'")
        self.HISTORY_TYPE_BTN = ElementsList("[ng-click*='historyDialog.setActive']", "Кнопка 'Обновить данные'")

        # Поиск
        self.MSISDN_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][1]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'MSISDN'",
        )
        self.MSISDN_OPTION_INTERVAL = Element(
            "//*[count(ps-list-item) = 7]/ps-list-item[contains(@user-value, 'INTERVAL')]",
            "Опция фильтра 'MSISDN' По диапазону",
        )
        self.MSISDN_OPTION_VALUE = Element(
            "//*[count(ps-list-item) = 7]/ps-list-item[contains(@user-value, 'VALUE')]",
            "Опция фильтра 'MSISDN' Точное значение",
        )
        self.MSISDN_SELECTED_OPTIONS = Element(
            "//div[@class='lis-search-numbers-params__item'][1]//div[contains(@ps-link-element, 'elements.value')]",
            "Выбранное значение 'MSISDN'",
        )
        self.MSISDN_FILTER_INPUT = Element(
            "//div[@class='lis-search-numbers-params__item'][1]//input", "Поле ввода фильтр 'MSISDN'"
        )
        self.MSISDN_FILTER_INPUT_FROM = Element(
            "[ng-model*='searchParameters.MSISDN.startValue']",
            "Поле ввода фильтр 'MSISDN' Начальное значение",
        )
        self.MSISDN_FILTER_INPUT_TO = Element(
            "[ng-model*='searchParameters.MSISDN.endValue']", "Поле ввода фильтр 'MSISDN' Конечное значение"
        )
        self.CATEGORY_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][2]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Категория'",
        )
        self.CLASS_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][3]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Класс'",
        )
        self.CLASS_FILTER_OPTIONS = ElementsList("//*[@user-value='item.numberClassId']", "Опции фильтр 'Класс'")
        self.STATUS_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][4]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Статус'",
        )
        self.STATUS_OPTION_BUSY = Element("//span[contains(text(), 'Занят')]", "Фильтр 'Статус' опция 'Занят'")
        self.STATUS_OPTION_UNAVAILABLE = Element(
            "//span[contains(text(), 'Недоступен')]", "Фильтр 'Статус' опция 'Недоступен'"
        )
        self.STATUS_OPTION_FREE = Element("//span[contains(text(), 'Свободен')]", "Фильтр 'Статус' опция 'Свободен'")
        self.CHANGE_STATUS_DATE_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][5]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Дата смены статуса'",
        )
        self.STATE_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][6]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Состояние'",
        )
        self.STATE_FILTER_OPTIONS = ElementsList(
            "//*[@user-value='item.phoneNumberStateId']", "Опции фильтр 'Состояние'"
        )
        self.OPERATOR_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][7]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Оператор'",
        )
        self.USER_FILTER_FIELD = Element(
            "//div[@class='lis-search-numbers-params__item'][8]//input", "Поле ввода 'Пользователь'"
        )
        self.NUMBER_TYPE_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][9]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Тип нумерации'",
        )
        self.STANDARD_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][10]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Стандарт'",
        )
        self.COMMUTATOR_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][11]//div[contains(@class, 'button')]/ps-button[2]",
            "Кнопка открыть фильтр 'Коммутатор'",
        )
        self.BLOCKING_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][12]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Блокировка'",
        )
        self.BLOCKED_OPTION = Element(
            "//ps-list-item//span[contains(text(), 'Установлена')]",
            "Фильтр 'Блокировка' вариант 'Установлена'",
        )
        self.NOT_BLOCKED_OPTION = Element(
            "//ps-list-item//span[contains(text(), 'Не установлена')]",
            "Фильтр 'Блокировка' вариант 'Не установлена'",
        )
        self.LINK_NUMBER_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][13]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Связанный номер'",
        )
        self.LINK_NUMBER_OPTION_INTERVAL = Element(
            "//*[count(ps-list-item) = 5]/ps-list-item[contains(@user-value, 'INTERVAL')]",
            "Опция фильтра 'Связанный номер' По диапазону",
        )
        self.LINK_NUMBER_SELECTED_OPTIONS = Element(
            "//div[@class='lis-search-numbers-params__item'][13]//div[contains(@ps-link-element, 'elements.value')]",
            "Выбранное значение 'Связанный номер'",
        )
        self.GOAL_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][14]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Цель использования'",
        )
        self.BILLING_CONNECTION_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][15]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Принадлежность к биллингу'",
        )
        self.COMMENT_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][16]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'Комментарий'",
        )
        self.COMMENT_OPTION_NOT_FILLED = Element(
            "//*[count(ps-list-item) = 3]/ps-list-item[contains(@user-value, 'true')]",
            "Опция фильтра 'Комментарий' Не заполнен",
        )
        self.COMMENT_SELECTED_OPTIONS = Element(
            "//div[@class='lis-search-numbers-params__item'][16]//div[contains(@ps-link-element, 'elements.value')]",
            "Выбранное значение 'Комментарий'",
        )

        self.FILTER_SEARCH_BTN = Element(".lis-search-numbers-view [ng-click*='search()']", "Кнопка 'Найти'")
        self.CLEAR_FILTER_BTN = Element(
            ".lis-search-numbers-view [ng-click*='numValueSearchClear()']", "Кнопка 'Очистить фильтры'"
        )

        # Модальное окно Добавление номера
        self.MODAL_ADD_NUMBER = Element("//body/div[contains(@class, 'n-popup')][1]", "Окно 'Добавление номера'")
        self.MODAL_ADD_NUMBER_TITLE = Element(
            "//body/div[contains(@class, 'n-popup')][1]/div[1]/div[1]", "Заголовок окна 'Добавление номера'"
        )
        self.LOAD_NUMBER_BUTTON = Element(
            "//body/div[contains(@class, 'n-popup')][1]//ps-button[@icon='open']", "Кнопка 'Загрузить номера'"
        )
        self.UPLOADED_FILE_NAME = Element(
            "//body/div[contains(@class, 'n-popup')][1]//span[@ng-if='addNumberDialog.file']",
            "Название загруженного файла",
        )
        self.DELETE_FILE_BUTTON = Element(
            "//body/div[contains(@class, 'n-popup')][1]//ps-button[@icon='trash-inverted']",
            "Кнопка 'Удалить файл'",
        )
        self.START_PHONE_NUMBER = Element("[name*='startPhoneNumber']", "Поле ввода 'Начальный MSISDN'")
        self.COUNT_PHONE_NUMBER = Element("[name*='countPhoneNumber']", "Поле ввода 'Количество MSISDN'")
        self.CHOOSE_COMMUTATOR_BTN = Element(
            ".n-popup [ng-model*='equipmentId'] ps-button:last-child", "Кнопка выбора 'Коммутатор'"
        )
        self.CHOOSE_COMMUTATOR_BLOCK = Element(".n-popup [ng-model*='.equipmentId']", "Блок 'Коммутатор'")
        self.CHOSEN_CATEGORY_FIELD = Element("[ng-model*='numberCategoryId'] > div > div", "Поле 'Категория'")
        self.CHOSEN_CATEGORY_BLOCK = Element("[ng-model*='numberCategoryId']", "Блок 'Категория'")
        self.CHOSEN_STATUS_FIELD = Element("[ng-model*='status']", "Поле 'Статус'")
        self.NUMBER_TYPE_FIELD = Element("[ng-model*='phoneNumberTypeId'] > div > div", "Поле 'Тип нумерации'")
        self.NUMBER_TYPE_BLOCK = Element("[ng-model*='phoneNumberTypeId']", "Блок 'Тип нумерации'")
        self.NUMBER_TYPE_OPTIONS = ElementsList(
            "//ps-list-item[contains(@user-value, 'type.phoneNumberTypeId')]",
            "Варианты списка 'Тип нумерации'",
        )
        self.OPERATOR_FIELD_BLOCK = Element("[ng-model*='operatorId']", "Блок 'Оператор'")
        self.OPERATOR_FIELD = Element("[ng-model*='operatorId'] > div > div", "Поле 'Оператор'")
        self.OPERATOR_OPTIONS = ElementsList(
            "//ps-list-item[contains(@user-value, 'operator.operatorId')]", "Варианты списка 'Оператор'"
        )
        self.AVAILABLE_TO_LINK = Element(
            ".n-popup [ng-model*='phoneNumberTypeLinkId'] > div > div", "Поле 'Доступность для связки'"
        )
        self.USE_GOAL_FIELD = Element("[ng-model*='phoneNumberPurposeId'] > div > div", "Поле 'Цель использования'")
        self.COMMENT_FIELD = Element(".n-popup [ng-model*='note']", "Поле 'Комментарий'")
        self.NUMBER_TYPE_LINE = ElementsList(
            "//body/div[contains(@class, 'n-popup')][1] //td/..", "Строки таблицы 'Разметка классов'"
        )
        self.NUMBER_TYPE_CLASSES = ElementsList(
            "//body/div[contains(@class, 'n-popup')][1]//tr/td[2]", "Классы 'Разметка классов'"
        )
        self.NUMBER_TYPE_CHECKBOXES = ElementsList(
            "//body/div[contains(@class, 'n-popup')][1]//tr/td[1]", "Чекбоксы 'Разметка классов'"
        )
        self.NUMBER_TYPE_ALL_CHECKBOX = Element(
            "//body/div[contains(@class, 'n-popup')][1]//tr/th[1]", "Выбрать все чекбоксы 'Разметка классов'"
        )
        self.CANCEL_ADD_NUMBER = Element(
            "//ps-button[contains(@ng-click, 'addNumberDialog.close()')]",
            "Кнопка 'Отменить' добавление номера",
        )

        # Модальное окно Связывание номеров
        self.TEMPLATE_INPUT = Element("[ng-model*='templateSearch']", "Поле ввода 'Шаблон отбора'")
        self.ABC_START_INPUT = Element("[ng-model*='startPhoneNumberABC']", "Поле ввода 'Начальное значение ABC'")
        self.ABC_END_INPUT = Element("[ng-model*='endPhoneNumberABC']", "Поле ввода 'Конечное значение ABC'")
        self.DEF_START_INPUT = Element("[ng-model*='startPhoneNumberDEF']", "Поле ввода 'Начальное значение ABC'")
        self.DEF_END_INPUT = Element("[ng-model*='endPhoneNumberDEF']", "Поле ввода 'Конечное значение ABC'")

        # Модальное окно Изменение класса номера
        self.CHOOSE_CLASS_TITLE = Element(
            "//*[contains(@ng-model, 'editNumber.numberClassId')]/../div[1]", "Заголовок 'Класс номера'"
        )
        self.CHOOSE_CLASS_FIELD = SelectLIS(
            "[ng-model*='editNumber.numberClassId'] [ps-link-element='elements.value']", "Поле выбора класса"
        )
        self.CLASS_OPTIONS = ElementsList("ps-list-item[user-value='item.numberClassId']", "Опции выбора класса")
        self.CONFIRM_CHANGE_CLASS_BTN = Element("[on-submit*='updateNumberClass']", "Кнопка 'Сохранить'")
        self.CANCEL_CHANGE_CLASS_BTN = Element("[ng-click*='massEditNumberClassDialog.close']", "Кнопка 'Отменить'")

        # TAB Шаблоны классов номеров Кнопки для работы с шаблонами
        self.ADD_TEMPLATE_BTN = Element("[ng-click*=addTemplate]", "Кнопка 'Добавить шаблон'")
        self.EDIT_TEMPLATE_BTN = Element("[ng-click*=editTemplate]", "Кнопка 'Редактировать шаблон'")
        self.DELETE_TEMPLATE_BTN = Element("[ng-click*=deleteTamplates]", "Кнопка 'Удалить шаблон'")
        self.UPDATE_TEMPLATE_BTN = Element(
            "[ng-click*='refreshGrid(model.templates)']", "Кнопка 'Обновить список шаблонов'"
        )

        # TAB Шаблоны классов номеров Таблица шаблонов
        self.TEMPLATE_TABLE_COLUMN_NAMES = ElementsList(
            "[rows='model.templates.rows'] tr.n-grid__head-row th>div", "Названия столбцов таблицы шаблонов"
        )
        self.TEMPLATE_TABLE_LINE = ElementsList(
            "[rows='model.templates.rows'] tr.n-grid__row", "Строки таблицы шаблонов"
        )
        self.TEMPLATE_NAME = ElementsList(
            "[rows='model.templates.rows'] tr.n-grid__row td:nth-child(2)", "Наименование шаблона"
        )
        self.TEMPLATE_CLASS = ElementsList(
            "[rows='model.templates.rows'] tr.n-grid__row td:nth-child(3)", "Класс шаблона"
        )
        self.TEMPLATE_PRIORITY = ElementsList(
            "[rows='model.templates.rows'] tr.n-grid__row td:nth-child(4)", "Приоритет шаблона"
        )
        self.TEMPLATE_IS_DEFAULT = ElementsList(
            "[rows='model.templates.rows'] tr.n-grid__row td:nth-child(5)",
            "Используется шаблон 'по умолчанию'",
        )

        # Модальное окно Добавление шаблона класса
        self.TEMPLATE_NAME_INPUT_TITLE = Element(
            "//*[contains(@ng-model, 'addTemplate.values.name')]/../div[1]",
            "Название поля 'Наименование шаблона'",
        )
        self.TEMPLATE_NAME_INPUT = Element(
            "input[ng-model*='addTemplate.values.name']", "Поле ввода 'Наименование шаблона'"
        )
        self.CHOOSE_CLASS_BLOCK_TITLE = Element(
            "//*[contains(@ng-model, 'addTemplate.values.numberClassId')]/../div[1]", "Название поля 'Класс'"
        )
        self.CHOOSE_CLASS_BLOCK = SelectLIS("[ng-model*='addTemplate.values.numberClassId']", "Блок выбора 'Класс'")
        self.TEMPLATE_PRIORITY_INPUT_TITLE = Element(
            "//*[contains(@ng-model, 'addTemplate.values.priority')]/../div[1]", "Название поля 'Приоритет'"
        )
        self.TEMPLATE_PRIORITY_INPUT = Element(
            "input[ng-model*='addTemplate.values.priority']", "Поле ввода 'Приоритет'"
        )
        self.TEMPLATE_IS_DEFAULT_CHECKBOX = Element(
            "[ng-model*='addTemplate.values.isDefault'] span.n-check-checkbox",
            "Чекбокс 'Использовать как Шаблон по умолчанию'",
        )
        self.ADD_TEMPLATE_MODAL_BTN = Element("[on-submit*=addClassTemplate]", "Кнопка 'Добавить'")
        self.CLOSE_ADD_TEMPLATE_BTN = Element("[ng-click*='addTemplate.close']", "Кнопка 'Отменить'")

        # Модальное окно Редактирование шаблона класса
        self.EDIT_TEMPLATE_NAME_INPUT = Element(
            "input[ng-model*='editTemplate.values.name']", "Поле ввода 'Наименование шаблона'"
        )
        self.EDIT_CHOOSE_CLASS_BLOCK = SelectLIS(
            "[ng-model*='editTemplate.values.numberClass.numberClassId']", "Блок выбора 'Класс'"
        )
        self.EDIT_TEMPLATE_PRIORITY_INPUT = Element(
            "input[ng-model*='editTemplate.values.priority']", "Поле ввода 'Приоритет'"
        )
        self.EDIT_TEMPLATE_IS_DEFAULT_CHECKBOX = Element(
            "[ng-model*='editTemplate.values.isDefault'] span.n-check-checkbox",
            "Чекбокс 'Использовать как Шаблон по умолчанию'",
        )
        self.EDIT_TEMPLATE_MODAL_BTN = Element("[on-submit*=editClassTemplate]", "Кнопка 'Добавить'")
        self.CLOSE_EDIT_TEMPLATE_BTN = Element("[ng-click*='editTemplate.close']", "Кнопка 'Отменить'")

        # TAB Шаблоны классов номеров Кнопки для работы с условиями
        self.ADD_RULE_BTN = Element("[ng-click*=addRules]", "Кнопка 'Добавить условие'")
        self.EDIT_RULE_BTN = Element("[ng-click*=editRules]", "Кнопка 'Редактировать условие'")
        self.DELETE_RULE_BTN = Element("[ng-click*=deleteRules]", "Кнопка 'Удалить условие'")

        # TAB Шаблоны классов номеров Таблица условий
        self.RULE_TABLE_COLUMN_NAMES = ElementsList(
            "[rows='model.templatesRules.rows'] tr.n-grid__head-row th>div",
            "Названия столбцов таблицы условий",
        )
        self.RULE_TABLE_LINE = ElementsList(
            "[rows='model.templatesRules.rows'] tr.n-grid__row", "Строки таблицы условий"
        )
        self.RULE_NAME = ElementsList(
            "[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(1)", "Наименование условия"
        )
        self.RULE_CONDITION = ElementsList(
            "[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(2)", "Условие"
        )
        self.RULE_IS_ACTIVE = ElementsList(
            "[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(3)", "Активность условия"
        )
        self.RULE_TEST_NUMBER = ElementsList(
            "[rows='model.templatesRules.rows'] tr.n-grid__row td:nth-child(4)", "Тестовый номер"
        )

        # Модальное окно Добавление условия шаблона
        self.RULE_NAME_INPUT_TITLE = Element(
            "//*[contains(@ng-model, 'addRules.values.name')]/../div[1]",
            "Название поля 'Наименование условия'",
        )
        self.RULE_NAME_INPUT = Element("input[ng-model*='addRules.values.name']", "Поле ввода 'Наименование условия'")
        self.RULE_CONDITION_INPUT_TITLE = Element(
            "//*[contains(@ng-model, 'addRules.values.condition')]/../div[1]", "Название поля 'Условие'"
        )
        self.RULE_CONDITION_INPUT = Element("*[ng-model*='addRules.values.condition']", "Поле ввода 'Условие'")
        self.RULE_TEST_NUMBER_INPUT = Element(
            "input[ng-model*='addRules.values.testMSISDN']", "Поле ввода 'Тестовый номер'"
        )
        self.RULE_IS_ACTIVE_CHECKBOX = Element(
            "[ng-model*='addRules.values.isActive'] span.n-check-checkbox", "Чекбокс 'Активировать условие'"
        )
        self.ADD_RULE_MODAL_BTN = Element("[on-submit*=addRulesTemplate]", "Кнопка 'Добавить'")
        self.CLOSE_ADD_RULE_BTN = Element("[ng-click*='addRules.close']", "Кнопка 'Отменить'")

        # Модальное окно Редактирование условия шаблона
        self.EDIT_RULE_NAME_INPUT = Element(
            "input[ng-model*='editRules.values.name']", "Поле ввода 'Наименование условия'"
        )
        self.EDIT_RULE_CONDITION_INPUT = Element("*[ng-model*='editRules.values.condition']", "Поле ввода 'Условие'")
        self.EDIT_RULE_TEST_NUMBER_INPUT = Element(
            "input[ng-model*='editRules.values.testMSISDN']", "Поле ввода 'Тестовый номер'"
        )
        self.EDIT_RULE_IS_ACTIVE_CHECKBOX = Element(
            "[ng-model*='editRules.values.isActive'] span.n-check-checkbox", "Чекбокс 'Активировать условие'"
        )
        self.EDIT_RULE_MODAL_BTN = Element("[on-submit*=editRulesTemplate]", "Кнопка 'Добавить'")
        self.CLOSE_EDIT_RULE_BTN = Element("[ng-click*='editRules.close']", "Кнопка 'Отменить'")

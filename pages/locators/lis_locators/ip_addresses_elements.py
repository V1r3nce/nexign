from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class IpAdressesElementsLis(BaseElementsLis):
    """Страница 'IP-адреса' LIS"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("h2", "Заголовок страницы")

        self.IP_RESULT_VIEW = Element(".lis-ip-result-view", "Просмотр результатов по ip")

        # FIELDS
        self.IP_FILTER_BTN = Element("#ID71001 .b-combobox__buttons", "Кнопка открыть фильтр 'IP-адрес'")
        self.IP_OPTION_INTERVAL = Element(
            "//ps-list-item[contains(@user-value, 'INTERVAL')]", "Опция фильтра 'IP-адрес' По диапазону"
        )
        self.IP_OPTION_VALUE = Element(
            "//ps-list-item[contains(@user-value,'VALUE')]", "Опция фильтра 'IP-адрес' Точное значение"
        )
        self.IP_SELECTED_OPTION = Element("#ID71001 div span", "Выбранное значение 'IP-адрес'")
        self.IP_START_VALUE = Element(
            "#ID71001 input[ng-model='model.searchParameters.IPAddress.startValue']", "Начальное значение IP"
        )
        self.IP_END_VALUE = Element(
            "#ID71001 input[ng-model='model.searchParameters.IPAddress.endValue']", "Конечное значение IP"
        )

        self.IP_TYPE_FILTER_BTN = Element("#ID71003 .b-combobox__buttons", "Кнопка открыть фильтр 'Тип IP-адреса'")
        self.IP_TYPE_OPTION_EXTERNAL = Element(
            "//ps-list-item[contains(@user-value,'item.IPAddressTypeId')][1]",
            "Опция фильтра 'Тип IP-адреса' Внешний",
        )
        self.IP_TYPE_SELECTED_OPTION = Element(
            "#ID71003 div span .b-multiselect-item__title", "Выбранное значение 'Типа IP-адреса'"
        )

        self.IP_STATUS_BTN = Element("#ID71002 .b-combobox__buttons", "Кнопка открыть фильтр 'Статус'")
        self.IP_STATUS_OPTION_UNAVAILABLE = Element(
            "//ps-list-item[contains(@user-value,'item.logicalStatusId')][2]",
            "Опция фильтра 'Статус' Недоступен",
        )
        self.IP_STATUS_OPTION_AVAILABLE = Element(
            "//ps-list-item[contains(@user-value,'item.logicalStatusId')][3]",
            "Опция фильтра 'Статус' Свободен",
        )
        self.IP_STATUS_SELECTED_OPTION = Element(
            "#ID71002 div span .b-multiselect-item__title", "Выбранное значение 'Типа IP-адреса'"
        )

        # BUTTONS
        self.ADD_ADDRESS_BTN = Element("ps-button[icon = 'plus']", "Кнопка 'Добавить адрес'")
        self.INTO_SERVICE_BTN = Element("ps-button[icon = 'ok']", "Кнопка 'В эксплуатацию'")
        self.OUT_OF_SERVICE_BTN = Element("ps-button[icon = 'archive']", "Кнопка 'Исключить'")
        self.WITHDRAWAL_BTN = Element("ps-toolbar ps-button[icon = 'delete']", "Кнопка 'Изъять'")
        self.HISTORY_BTN = Element("ps-button[icon = 'calendar-inverted']", "Кнопка 'История'")
        self.DOWNLOAD_BTN = Element("ps-button[icon = 'download']", "Кнопка 'История'")
        self.ADDRESS_REFRESH = Element("ps-button[title='Обновить']", "Кнопка 'Обновить'")
        self.SEARCH_BTN = Element("ps-button[icon = 'search']", "Кнопка 'Найти'")
        self.CLEAR_FILTERS_BTN = Element("ps-button[icon = 'cross-inverted']", "Кнопка 'Очистить фильтры'")
        self.CHOOSE_TEMPLATE_BTN = Element("ps-button[icon = 'open']", "Кнопка 'Выбрать шаблон поиска'")
        self.TEMPLATE_NAMES_LIST = ElementsList(
            "[ng-click='selectedTemplate(item)'] span", "Список наименований шаблонов поиска"
        )
        self.SAVE_TEMPLATE_BTN = Element("ps-button[icon = 'save']", "Кнопка 'Сохранить шаблон поиска'")
        self.TEMPLATE_OPTION_NEW = Element(
            "//ps-list-item[contains(@user-value,'new')]", "Опция сохранения шаблона поиска 'Новый шаблон'"
        )
        self.DELETE_TEMPLATE_BTN = Element("#ID50004", "Кнопка 'Удалить текущий шаблон'")

        # TABLE
        self.TOOLBAR_TOTAL_TEXT = Element(".toolbar-right span:nth-child(1)", "Текст тулбара 'Всего'")
        self.TOOLBAR_IP_COUNT = Element(".toolbar-right span:nth-child(2)", "Количество ip адресов")
        self.TABLE_LINE = ElementsList("tr.n-grid__row", "Строки таблицы")
        self.ALL_CHECKBOX = Element("th:nth-child(2) .n-check-checkbox", "Чекбокс 'Выбрать все'")
        self.DATE_STATUS_CHANGED = Element("th:nth-child(8)", "заголовок столбца 'Дата смены статуса'")
        self.CHECKBOX_LIST = ElementsList("tbody tr td:nth-child(2) span", "Список чекбоксов")
        self.IP_LIST = ElementsList("tbody tr td:nth-child(3) div", "Список ip")
        self.IP_TYPE_LIST = ElementsList("tbody tr td:nth-child(6) div", "Список типов ip")
        self.STATUS_LIST = ElementsList("tbody tr td:nth-child(7) div", "Список статусов")
        self.STATE_LIST = ElementsList("tbody tr td:nth-child(9) div", "Список состояние")

        # ADD_ADDRESS_MODAL
        self.IP_MODALS_LIST = ElementsList(".ps-dialog.n-popup", "Список модальных окон")
        self.ADD_ADDRESS_MODAL = Element("form[name='ipUploadForm']", "Модальное окно 'Добавление IP-адресов'")
        self.ACCESS_POINT_MORE_BTN = Element(".ps-dialog.n-popup ps-button[icon='dots']", "Кнопка 'Обзор'")
        self.ACCESS_POINT_FIELD = Element(
            "form[name='ipUploadForm'] [ng-model='apnDialog.accessPointName'] input", "Поле 'Точка доступа'"
        )
        self.IP_INITIAL_VALUE = Element("#ID73025 input", "Поле 'Начальное значение'")
        self.IP_FINAL_VALUE = Element("#ID73028 input", "Поле 'Конечное значение'")
        self.ADD_IP_BTN = Element("form[name='ipUploadForm'] .n-popup-foot ps-button[icon='ok']", "Кнопка 'Добавить'")

        # ACCESS_POINT_SELECTION_MODAL
        self.ACCESS_POINT_MODAL = Element("div[ui-lock='apnDialog.apnLock']", "Модальное окно 'Выбор точки доступа APN'")
        self.ACCESS_POINT_OPTION = Element("div[ui-lock='apnDialog.apnLock'] tbody > tr:first-child", "Точка доступа")
        self.ACCESS_POINT_NAME = Element(
            "[ui-lock='apnDialog.apnLock'] tr:first-child > td:first-child div", "Наименование точки доступа"
        )
        self.CHOOSE_BTN = Element("div[ui-lock='apnDialog.apnLock'] ps-button[icon='ok']", "Кнопка 'Выбрать'")

        # CONFIRMATION_IP_MODAL
        self.CONFIRMATION_IP_MSG = Element(".ps-dialog.n-popup .n-popup-message-align", "Текст подтверждения ip")

        # INFORMATION_IP_MODAL
        self.INFORMATION_OK_BTN = Element("body .ps-dialog[tabindex='-1']:nth-last-of-type(2) ps-button", "Кнопка 'ОК'")

        # HISTORY_MODAL
        self.HISTORY_REFRESH_BTN = Element("ps-button[icon = 'refresh-inverted']", "Кнопка 'Обновить данные'")

        # TEMPLATE_MODAL
        self.TEMPLATE_TITLE = Element(".n-popup-head__title", "Заголовок формы сохранения шаблона")
        self.NEW_TEMPLATE_NAME = Element("#ID50014 INPUT", "Поле ввода названия нового шаблона")
        self.TEMPLATE_SAVE_BTN = Element(
            ".ps-dialog[tabindex='-1']:nth-last-of-type(2) ps-button:nth-child(1)", "Кнопка 'Сохранить'"
        )

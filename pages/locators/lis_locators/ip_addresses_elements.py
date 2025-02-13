from playwright.sync_api import Page

from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class IpAdressesElementsLis(BaseElementsLis):
    """Страница 'IP-адреса' LIS"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("h2", "Заголовок страницы", self.page)

        self.IP_RESULT_VIEW = Element(".lis-ip-result-view", "Просмотр результатов по ip", self.page)

        #FIELDS
        self.IP_FILTER_BTN = Element("#ID71001 .b-combobox__buttons", "Кнопка открыть фильтр 'IP-адрес'", self.page)
        self.IP_OPTION_INTERVAL = Element("//ps-list-item[contains(@user-value, 'INTERVAL')]", "Опция фильтра 'IP-адрес' По диапазону",self.page)
        self.IP_OPTION_VALUE = Element("//ps-list-item[contains(@user-value,'VALUE')]", "Опция фильтра 'IP-адрес' Точное значение", self.page)
        self.IP_SELECTED_OPTION = Element("#ID71001 div span", "Выбранное значение 'IP-адрес'", self.page)
        self.IP_START_VALUE = Element("#ID71001 input[ng-model='model.searchParameters.IPAddress.startValue']", "Начальное значение IP", self.page)
        self.IP_END_VALUE = Element("#ID71001 input[ng-model='model.searchParameters.IPAddress.endValue']", "Конечное значение IP", self.page)
        
        #BUTTONS
        self.ADD_ADDRESS_BTN = Element("ps-button[icon = 'plus']", "Кнопка 'Добавить адрес'", self.page)
        self.HISTORY_BTN = Element("ps-button[icon = 'calendar-inverted']", "Кнопка 'История'", self.page)
        self.ADDRESS_REFRESH = Element("ps-button[title='Обновить']", "Кнопка 'Обновить'", self.page)
        self.SEARCH_BTN = Element("ps-button[icon = 'search']", "Кнопка 'Найти'", self.page)
        self.CLEAR_FILTERS_BTN = Element("ps-button[icon = 'cross-inverted']", "Кнопка 'Очистить фильтры'", self.page)
        self.CHOOSE_TEMPLATE_BTN = Element("ps-button[icon = 'open']", "Кнопка 'Выбрать шаблон поиска'", self.page)
        self.SAVE_TEMPLATE_BTN = Element("ps-button[icon = 'save']", "Кнопка 'Сохранить шаблон поиска'", self.page)

        #TABLE
        self.TOOLBAR_TOTAL_TEXT = Element(".toolbar-right span:nth-child(1)", "Текст тулбара 'Всего'", self.page)
        self.TOOLBAR_IP_COUNT = Element(".toolbar-right span:nth-child(2)", "Количество ip адресов", self.page)
        self.CHECKBOX_LIST = ElementsList("tbody tr td:nth-child(2) span", "Список чекбоксов", self.page)
        self.IP_LIST = ElementsList("tbody tr td:nth-child(3) div", "Список ip", self.page)
        self.STATUS_LIST = ElementsList("tbody tr td:nth-child(7) div", "Список статусов", self.page)
        self.STATE_LIST = ElementsList("tbody tr td:nth-child(9) div", "Список состояние", self.page)

        #ADD_ADDRESS_MODAL
        self.IP_MODALS_LIST = ElementsList(".ps-dialog.n-popup", "Список модальных окон", self.page)
        self.ADD_ADDRESS_MODAL = Element("form[name='ipUploadForm']", "Модальное окно 'Добавление IP-адресов'", self.page)
        self.ACCESS_POINT_MORE_BTN = Element(".ps-dialog.n-popup ps-button[icon='dots']", "Кнопка 'Обзор'", self.page)
        self.ACCESS_POINT_FIELD = Element("form[name='ipUploadForm'] [ng-model='apnDialog.accessPointName'] input", "Поле 'Точка доступа'", self.page)
        self.IP_INITIAL_VALUE = Element("#ID73025 input", "Поле 'Начальное значение'", self.page)
        self.IP_FINAL_VALUE = Element("#ID73028 input", "Поле 'Конечное значение'", self.page)
        self.ADD_IP_BTN = Element("form[name='ipUploadForm'] .n-popup-foot ps-button[icon='ok']", "Кнопка 'Добавить'", self.page)

        #ACCESS_POINT_SELECTION_MODAL
        self.ACCESS_POINT_MODAL = Element("div[ui-lock='apnDialog.apnLock']", "Модальное окно 'Выбор точки доступа APN'", self.page)
        self.ACCESS_POINT_OPTION = Element("div[ui-lock='apnDialog.apnLock'] tbody > tr:first-child", "Точка доступа", self.page)
        self.ACCESS_POINT_NAME= Element("[ui-lock='apnDialog.apnLock'] tr:first-child > td:first-child div", "Наименование точки доступа", self.page)
        self.CHOOSE_BTN = Element("div[ui-lock='apnDialog.apnLock'] ps-button[icon='ok']", "Кнопка 'Выбрать'", self.page)

        #CONFIRMATION_IP_MODAL
        self.CONFIRMATION_IP_MSG = Element(".ps-dialog.n-popup .n-popup-message-align", "Текст подтверждения ip", self.page)
        self.CONFIRMATION_YES_BTN = Element("table + div .n-popup-foot__right ps-button:nth-child(1)", "Кнопка 'Да'", self.page)

        #INFORMATION_IP_MODAL
        self.INFORMATION_OK_BTN = Element("body .ps-dialog[tabindex='-1']:nth-last-of-type(2) ps-button", "Кнопка 'ОК'", self.page)

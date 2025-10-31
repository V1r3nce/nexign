from playwright.sync_api import Page

from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Element, Select, ElementsList


class AgreementForm(DynamicForms):
    """Страница /customer-hierarchy-management/agreements/{agreementId}/agreement
    Форма подписания/редактирования договора"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("[class*=drawer-open] h3", "Заголовок формы", self.page)
        self.SIGNING_DATE = Element("#agreement-card-edit_signingDate", "Дата подписания договора", self.page)
        self.OPERATOR_REPRESENTATIVE_NAME = Select(
            "//div[@id='signingUser' or @aria-labelledby='signingUser']//input[contains"
            "(@class, 'ant-select-selection-search-input')]",
            "ФИО представителя оператора",
            self.page)
        self.CLIENT_REPRESENTATIVE_NAME = Select("#agentSigner", "ФИО представителя клиента", self.page)
        self.NO_LINK_PERSON_ATTENTION = Element(
            "[class*=platform-attention-label]", "Предупреждение 'У клиента нет связанных лиц'", self.page
        )
        self.CREATE_LINK_PERSON_BTN = Element(
            "button[label='Создать связанное лицо']", "Кнопка 'Создать связанное лицо'", self.page
        )
        self.ATTACH_DOCUMENT_FIELD = Element("input:is([multiple])", "Поле 'Перетащить файл'", self.page)
        self.INDEFINITE_CHECKBOX = Element("#agreement-card-edit_isIndefinitely", "Чекбокс 'Бессрочно'", self.page)
        self.EXPIRATION_DATE = DatePicker("#agreement-card-edit_expireDate", "Дата расторжения договора", self.page)
        self.AGREEMENT_TYPE = Select("#agreement-card-edit_agreementType", "Тип договора", self.page)
        self.CLIENT_REPRESENTATIVE_NAME_NOT_FILLED_ERROR = Element(
            "#agentSigner_help", "Ошибка 'Обязательно для заполнения' для ФИО представителя клиента", self.page
        )
        self.ATTACH_DOCUMENT_FIELD_NOT_FILLED_ERROR = Element(
            "#document_help", "Ошибка 'Обязательно для заполнения' для файла", self.page
        )

        self.HISTORY_BTN = Element(
            "//button[.//span[@data-icon='History']]",
            "Кнопка 'История изменений'",
            self.page
        )
        self.HISTORY_SIDEBAR_TITLE = Element(
            "[class*=drawer-open] [class*=drawer-title] h3",
            "Заголовок сайдбара истории",
            self.page,
        )
        self.HISTORY_TABLE_CELLS = ElementsList(
            "//div[contains(@class, 'table')]//tr[contains(@data-row-key, '-') and descendant::td[contains(@class, 'table-cell')]]",
            "Строки таблицы истории изменений",
            self.page,
        )
        self.HISTORY_SIDEBAR_CLOSE_BTN = Element(
            "//div[contains(@class, 'drawer-open')]//span[@data-icon='Close' and contains(@class, 'platform-icon')]",
            "Кнопка закрытия сайдбара истории изменений",
            self.page,
        )

        self.REFRESH_BTN = Element(
            "//button[.//span[@data-icon='Refresh']]",
            "Кнопка обновления истории изменений",
            self.page,
        )
        self.HISTORY_TABLE_ROWS = ElementsList(
            "//div[contains(@class, 'ant-table-tbody-virtual-holder-inner')]//tr[contains(@class, 'ant-table-row')]",
            "Строки таблицы истории изменений",
            self.page
        )

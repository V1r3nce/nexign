from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Element, ElementsList, Select


class AgreementFormElements(DynamicForms):
    """Страница /customer-hierarchy-management/agreements/{agreementId}/agreement
    Форма подписания/редактирования договора"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[class*=drawer-open] h3", "Заголовок формы")
        self.SIGNING_DATE = Element("#agreement-card-edit_signingDate , #signingDate", "Дата подписания договора")
        self.CLIENT_REPRESENTATIVE_NAME = Select(
            "#agreement-card-edit_agreementSigner, #agentSigner", "ФИО представителя клиента"
        )
        self.OPERATOR_REPRESENTATIVE_NAME = Select(
            "#agreement-card-edit_signingUser, #signingUser", "ФИО представителя оператора"
        )
        self.SIGNER_PROXY_INFO = Element(
            "#agreement-card-edit_customerSignerProxyInfo, #customerSignerProxyInfo", "Номер доверенности"
        )
        self.USE_EXISTING_BANK_DATA = Element(
            "#agreement-card-edit_useExistingBankData", "Выбрать существующие реквизиты"
        )
        self.NO_LINK_PERSON_ATTENTION = Element(
            "[class*=platform-attention-label]", "Предупреждение 'У клиента нет связанных лиц'"
        )
        self.CREATE_LINK_PERSON_BTN = Element(
            "button[label='Создать связанное лицо']", "Кнопка 'Создать связанное лицо'"
        )
        self.ATTACH_DOCUMENT_FIELD = Element("input:is([multiple])", "Поле 'Перетащить файл'")
        self.INDEFINITE_CHECKBOX = Element("#agreement-card-edit_isIndefinitely", "Чекбокс 'Бессрочно'")
        self.EXPIRATION_DATE = DatePicker("#agreement-card-edit_expireDate", "Дата расторжения договора")
        self.AGREEMENT_TYPE = Select("#agreement-card-edit_agreementType", "Тип договора")
        self.CLIENT_REPRESENTATIVE_NAME_NOT_FILLED_ERROR = Element(
            "#agentSigner_help", "Ошибка 'Обязательно для заполнения' для ФИО представителя клиента"
        )
        self.ATTACH_DOCUMENT_FIELD_NOT_FILLED_ERROR = Element(
            "#document_help", "Ошибка 'Обязательно для заполнения' для файла"
        )

        self.HISTORY_BTN = Element("//button[.//span[@data-icon='History']]", "Кнопка 'История изменений'")
        self.HISTORY_SIDEBAR_TITLE = Element(
            "[class*=drawer-open] [class*=drawer-title] h3",
            "Заголовок сайдбара истории",
        )
        self.HISTORY_SIDEBAR_CLOSE_BTN = Element(
            "//div[contains(@class, 'drawer-open')]//span[@data-icon='Close' and contains(@class, 'platform-icon')]",
            "Кнопка закрытия сайдбара истории изменений",
        )

        self.REFRESH_BTN = Element(
            "//button[.//span[@data-icon='Refresh']]",
            "Кнопка обновления истории изменений",
        )
        self.TAB_DOCUMENT = Element("[data-node-key='documents'] ", "Таб 'Документы'")
        self.DOCUMENTS_TABLE_CELLS = ElementsList(
            "[id*=panel-documents] tbody[class*=table] > tr[data-row-key]", "Строки таблицы документов"
        )
        self.HISTORY_TABLE_ROWS = ElementsList(
            "[class*=drawer-open] [class*=table-tbody] [class*=table-row][data-row-key]",
            "Строки таблицы истории изменений",
        )

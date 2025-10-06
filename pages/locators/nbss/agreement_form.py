from playwright.sync_api import Page

from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Element, Select


class AgreementForm(DynamicForms):
    """Страница /customer-hierarchy-management/agreements/{agreementId}/agreement
    Форма подписания/редактирования договора"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("[class*=drawer-open] h3", "Заголовок формы", self.page)
        self.SIGNING_DATE = Element("[class*=picker-outlined] > div > input", "Дата подписания", self.page)
        self.OPERATOR_REPRESENTATIVE_NAME = Select("#signingUser", "ФИО представителя оператора", self.page)
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

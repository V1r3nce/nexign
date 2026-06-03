from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Element


class EditProductActivationDateForm(DynamicForms):
    """Страница customers/{customerId}/products 'Продуктовый профиль клиента', форма 'Редактирование даты активации продукта'"""

    def __init__(self) -> None:
        super().__init__()

        self.INFORMATION_MESSAGE = Element(
            "div[class*=drawer-body] p:not([color])[data-name=paragraphInfo]", "Информационное сообщение"
        )
        self.ACTIVATION_DATE = DatePicker("#activationDate", "Поле 'Дата активации'")
        self.REASON = Element("#comment", "Поле 'Обоснование'")

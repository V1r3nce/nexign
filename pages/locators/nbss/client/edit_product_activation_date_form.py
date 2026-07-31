from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import DatePicker, Element, ElementsList


class EditExecutionDateForm(DynamicForms):
    """Сайдбар 'Редактирование даты' (выполнение заказа будущей датой)."""

    def __init__(self) -> None:
        super().__init__()

        self.DRAWER_TITLE = Element(
            "[class*=drawer-open] [class*=drawer-title] h3", "Заголовок сайдбара 'Редактирование даты'"
        )
        self.EXECUTION_DATE = Element(
            "[class*=drawer-open] #futureDate", "Поле 'Планируемая дата' (сайдбар редактирования даты)"
        )
        self.EXECUTION_DATE_ERROR = ElementsList(
            "[class*=drawer-open] #futureDate_help, [class*=drawer-open] [class*=explain-error]",
            "Предупреждение о недопустимой дате ('Дата не может быть позже/раньше ...')",
        )
        self.INFO_MESSAGE: Element = Element(
            "[class*=drawer-open] [class*=attention-label] p[data-name=paragraph]",
            "Уведомление о повторной проверке конфигурации после изменения даты",
        )
        self.CURRENT_TIME_BTN = Element("[class*=picker-now-btn]", "Кнопка календаря 'Текущий момент'")


class EditProductActivationDateForm(DynamicForms):
    """Страница customers/{customerId}/products 'Продуктовый профиль клиента', форма 'Редактирование даты активации продукта'"""

    def __init__(self) -> None:
        super().__init__()

        self.INFORMATION_MESSAGE = Element(
            "div[class*=drawer-body] p:not([color])[data-name=paragraphInfo]", "Информационное сообщение"
        )
        self.ACTIVATION_DATE = DatePicker("#activationDate", "Поле 'Дата активации'")
        self.ACTIVATION_DATE_ERROR = Element("#activationDate_help", "Ошибка рядом с полем 'Дата активации'")
        self.REASON = Element("#comment", "Поле 'Обоснование'")

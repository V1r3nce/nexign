from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import Element, ElementsList, SelectWithId


class DiscountsAndChargesSettingsElements(DynamicForms):
    """Страница настройки шаблонов 'Скидки/доначисления' (Биллинг > Скидки/доначисления)"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_ACTION_BTN = Element("//button[@id='addActionBtn']", "Кнопка 'Добавить действие'")
        self.DISCOUNT_EDIT_BTN = ElementsList("[class*=platform-toolbar] [id=editBtn]", "Кнопка 'Редактировать'")
        self.DISCOUNT_DELETE_BTN = ElementsList("[class*=platform-toolbar] [id=deleteBtn]", "Кнопка 'Удалить'")
        self.ACCEPT_DISCOUNT_DELETE_BTN = Element(
            "[class*=modal-content] [class*=btn-primary]", "Подтверждение удаление шаблона"
        )
        self.NAME_FIND_TABLE = Element(
            "[class*=spin-container] [class*=table-thead] span[class*=input-outlined] input", "Поиск по Имени в таблице"
        )
        self.DISCOUNT_NAME = ElementsList("#add-new-template_name", "Название шаблона")
        self.DISCOUNT_NAME_ROWS = ElementsList(
            "[class*=table-small] [class*=tbody-virtual-holder] [class*=table-row] div",
            "Имена в таблице Скидки/Доначисления",
        )
        self.ROW_DISCOUNT = ElementsList(
            "[class*=table-small] [class*=tbody-virtual-holder] [class*=table-row]",
            "Поле в таблице 'Скидки/Доначисления'",
        )
        self.DATE = ElementsList(
            "//div[@id='validFor_control']//input[@date-range]", "Даты периода когда шаблон может быть назначен"
        )
        self.ACTION = SelectWithId("add-action_actionName", "Действие шаблона")
        self.ACTION_PRIORITY = Element("#add-action_priority", "Приоритет")
        self.DISCOUNT = Element("#add-action_discountValue", "Размер скидки")
        self.THRESHOLD = Element("#add-action_threshold", "Порог суммы, с которой предоставляется скидка")
        self.SIZE_DISCOUNT = Element("input[id*=discountValue]", "Поле 'Размер скидки'")
        self.NAME_ACTION_DISCOUNT = ElementsList(
            "[id*=billingDiscountTemplateActions_control] [class*=table-tbody] [class*=table-row] [class*=table-cell]:nth-child(1)",
            "Поле в таблице редактирования действий шаблона",
        )

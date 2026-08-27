from pages.locators.base_elements import BaseElements
from pages.ui_elements import ElementsList


class InquiryOverviewTab(BaseElements):
    """Форма заявки, вкладка Обзор"""

    def __init__(self) -> None:
        super().__init__()

        self.ADDITIONAL_ATTRIBUTE_LABELS = ElementsList(
            "[data-testid*=AdditionalAttributes] p[data-name=paragraphInfo]", "Лейблы дополнительных атрибутов заявки"
        )
        self.ADDITIONAL_ATTRIBUTE_LINKS = ElementsList(
            "[data-testid*=AdditionalAttributes] a[class*=text-link]", "Ссылки дополнительных атрибутов заявки"
        )
        self.ADDITIONAL_ATTRIBUTE_VALUES = ElementsList(
            "[data-testid*=AdditionalAttributes] p[data-name=paragraph]", "Значения дополнительных атрибутов заявки"
        )
        self.ADDITIONAL_ATTRIBUTE_LABELS_EDIT_FORM = ElementsList(
            "[data-testid*=AdditionalAttributes] label", "Лейблы дополнительных атрибутов заявки на форме редактирования"
        )
        self.ADDITIONAL_ATTRIBUTE_INPUTS_EDIT_FORM = ElementsList(
            "[data-testid*=AdditionalAttributes] input",
            "Поля ввода значений дополнительных атрибутов заявки на форме редактирования",
        )

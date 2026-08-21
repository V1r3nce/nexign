import allure

from common.helpers.checker import assert_that
from pages.base_page import BasePage
from pages.locators.nbss.inquiry.inquiry_sale_card_tab import InquirySaleCardTab


class InquirySaleCardPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.inquiry_sale_card = InquirySaleCardTab()

    @allure.step("Проверка состава групп атрибутов на активной вкладке заявки")
    def check_attribute_groups(
        self, displayed: list[str | list[str]] | None = None, hidden: list[str | list[str]] | None = None
    ) -> None:
        """
        Проверяет, какие группы доп. атрибутов и коллапсы отображаются на активной вкладке заявки.
        Элементом списка может быть как заголовок группы, так и список заголовков.

        :param displayed: заголовки групп, которые должны отображаться
        :param hidden: заголовки групп, которых быть не должно
        """

        def flatten(groups: list[str | list[str]] | None) -> list[str]:
            return [name for group in groups or [] for name in ([group] if isinstance(group, str) else group)]

        self.inquiry_sale_card.ATTRIBUTE_GROUP_TITLES.wait_to_be_visible()
        for group in flatten(displayed):
            self.inquiry_sale_card.ATTRIBUTE_GROUP_TITLES.wait_for_text_in_all([group])
        for group in flatten(hidden):
            assert_that(
                lambda name=group: name not in self.inquiry_sale_card.ATTRIBUTE_GROUP_TITLES.text_list,
                lambda name=group: (
                    f"Группа '{name}' отображается, хотя должна быть скрыта. "
                    f"Отображаются: {self.inquiry_sale_card.ATTRIBUTE_GROUP_TITLES.text_list}"
                ),
            )

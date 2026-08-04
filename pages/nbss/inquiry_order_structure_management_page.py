from typing import Literal

import allure

from common.helpers.checker import assert_that
from common.helpers.string_helper import extract_volume_in_inquiry
from pages.base_page import BasePage
from pages.locators.nbss.client.edit_product_activation_date_form import EditExecutionDateForm
from pages.locators.nbss.inquiries_elements import InquiriesElements, MassDiscountEditForm, ProductEditForm


class InquiryOrderStructureManagement(BasePage):
    """Шаг заявки 'Управление составом заказа': работа с датой выполнения заказа (отложенная активация)."""

    def __init__(self) -> None:
        super().__init__()
        self.locators = InquiriesElements()
        self.edit_form = EditExecutionDateForm()
        self.product_edit_form = ProductEditForm()
        self.mass_discount_form = MassDiscountEditForm()

    @allure.step("Проверить всплывающую подсказку с налогом у итоговой платы")
    def check_total_payment_tax_tooltip(self, fee_type: Literal["subscription", "one_time"] = "one_time") -> str:
        """Навести курсор на 'i' возле итоговой платы и вернуть текст всплывающей подсказки.

        :param fee_type: тип начисления - ["subscription", "one_time"]
        :return: текст всплывающей подсказки
        """
        if fee_type == "subscription":
            info_icon = self.locators.TOTAL_SUBSCRIPTION_FEE_INFO_ICON
        else:
            info_icon = self.locators.TOTAL_ONE_TIME_PAYMENT_INFO_ICON

        info_icon.wait_to_be_visible(timeout=10000)
        info_icon.hover()
        self.locators.TOOLTIP.wait_to_be_visible(timeout=10000)
        tooltip_text = self.locators.TOOLTIP.text or ""
        assert_that(
            lambda: any(char.isdigit() for char in tooltip_text),
            f"Во всплывающей подсказке у итоговой платы нет сумм: '{tooltip_text}'",
        )
        return tooltip_text

    @allure.step("Заполнить скидки на разовую плату на форме массового назначения скидок")
    def fill_one_time_discounts_on_mass_discount_assignment_form(self, discount_percent: list) -> None:
        """Заполнить скидки на разовую плату для продуктов, у которых она есть.

        Дополняет fill_discounts_on_mass_discount_assignment_form, который заполняет только
        скидки на абонентскую плату.

        :param discount_percent: список процентов скидки по продуктам
        """
        self.mass_discount_form.ONE_TIME_DISCOUNT_INPUTS.wait_to_have_count_or_greater(len(discount_percent))
        for i in range(len(discount_percent)):
            self.mass_discount_form.ONE_TIME_DISCOUNT_INPUTS[i].wait_to_be_visible()
            self.mass_discount_form.ONE_TIME_DISCOUNT_INPUTS[i].fill(str(discount_percent[i]))

    @allure.step("Проверить, что заявка на шаге 'Управление составом заказа'")
    def check_order_management_step(self) -> None:
        self.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
        self.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
        self.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

    @allure.step("Установить дату выполнения заказа на форме выбора ПП")
    def set_execution_date_on_product_form(self, date: str | None = None, current_time: bool = False) -> None:
        form = self.locators.product_offer_form
        form.SCHEDULE_EXECUTION_CHECKBOX.wait_to_be_visible(timeout=10000)
        if not form.SCHEDULE_EXECUTION_CHECKBOX.has_attribute_value("checked", ""):
            form.SCHEDULE_EXECUTION_CHECKBOX.click()
        form.PLANNED_DATE.wait_to_be_visible(timeout=10000)
        if current_time:
            form.PLANNED_DATE.click()
            self.edit_form.CURRENT_TIME_BTN.wait_to_be_visible(timeout=10000)
            self.edit_form.CURRENT_TIME_BTN.click()
        else:
            form.PLANNED_DATE.fill(date)
            self.press_keyboard_button("Enter")

    @allure.step("Проверить наличие даты выполнения заказа на вкладке 'Активный шаг'")
    def check_execution_date_on_active_step(self, expected_date: str | None = None) -> None:
        self.locators.EXECUTION_DATE_EDIT_BTN.wait_to_be_visible(timeout=60000)
        if expected_date:
            self.locators.EXECUTION_DATE_PLAN_BLOCK.to_contain_text(expected_date, timeout_sec=10)

    @allure.step("Редактировать дату выполнения заказа через вкладку 'Активный шаг'")
    def edit_execution_date_active_step(
        self, date: str | None = None, current_time: bool = False, expect_warning: bool = True, save: bool = True
    ) -> None:
        """Открыть сайдбар 'Редактирование даты' и задать дату выполнения заказа.

        :param date: новая дата "ДД.ММ.ГГГГ чч:мм" (если current_time=False)
        :param current_time: выбрать в календаре 'Текущий момент' вместо ввода даты
        :param expect_warning: ожидать уведомление о повторной проверке конфигурации
        :param save: нажимать ли 'Сохранить' (False — оставить сайдбар открытым, например для проверки ошибки)
        """
        self.locators.EXECUTION_DATE_EDIT_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.EXECUTION_DATE_EDIT_BTN.click()
        self.edit_form.EXECUTION_DATE.wait_to_be_visible(timeout=10000)
        if current_time:
            self.edit_form.EXECUTION_DATE.click()
            self.edit_form.CURRENT_TIME_BTN.wait_to_be_visible(timeout=10000)
            self.edit_form.CURRENT_TIME_BTN.click()
        else:
            self.edit_form.EXECUTION_DATE.fill(date)
            self.press_keyboard_button("Enter")
        if expect_warning:
            self.edit_form.INFO_MESSAGE.to_contain_text("повторная проверка конфигурации", timeout_sec=10)
        if save:
            self.edit_form.ACCEPT_BTN.wait_to_be_enabled(timeout=10000)
            self.edit_form.ACCEPT_BTN.click()
            self.edit_form.EXECUTION_DATE.not_to_be_visible(timeout=60000)
            self.locators.LOAD_SPINS.not_to_be_visible(timeout=30000)

    @allure.step("Проверить предупреждение о недопустимой дате выполнения заказа")
    def check_execution_date_error(self) -> None:
        self.edit_form.EXECUTION_DATE_ERROR.wait_to_be_visible()

    @allure.step("Редактировать дату выполнения заказа через вкладку 'Элементы заказа'")
    def edit_execution_date_order_elements(
        self, date: str | None = None, current_time: bool = False, expect_warning: bool = True, save: bool = True
    ) -> None:
        self.edit_execution_date_active_step(
            date=date, current_time=current_time, expect_warning=expect_warning, save=save
        )

    @allure.step("Проверить что объемы соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_on_product_card(self, expected_product_volumes: list[int]) -> None:
        self.locators.product_offer_form.PRODUCT_CARD_VOLUMES.wait_to_have_count(len(expected_product_volumes))

        minutes_volume = self.locators.product_offer_form.PRODUCT_CARD_VOLUMES[0].text
        internet_volume = self.locators.product_offer_form.PRODUCT_CARD_VOLUMES[1].text
        sms_volume = self.locators.product_offer_form.PRODUCT_CARD_VOLUMES[2].text

        product_volumes = [minutes_volume, internet_volume, sms_volume]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Проверить что объемы в сайдбаре соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_in_sidebar(self, expected_product_volumes: list[int]) -> None:
        self.locators.product_offer_form.PRODUCT_CARD_VOLUMES.wait_to_have_count(len(expected_product_volumes))

        minutes_volume_product_info_sidebar = self.locators.product_offer_form.product_info_form.PRODUCT_VOLUMES[0].text
        internet_volume_product_info_sidebar = self.locators.product_offer_form.product_info_form.PRODUCT_VOLUMES[1].text
        sms_volume_product_info_sidebar = self.locators.product_offer_form.product_info_form.PRODUCT_VOLUMES[2].text

        product_volumes = [
            minutes_volume_product_info_sidebar,
            internet_volume_product_info_sidebar,
            sms_volume_product_info_sidebar,
        ]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Проверить что объемы в тултипе соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_in_tooltip(self, expected_product_volumes: list[int]) -> None:
        self.locators.TOOLTIP_VOLUMES.wait_to_have_count(len(expected_product_volumes) + 1)

        internet_volume_subtitle = self.locators.TOOLTIP_VOLUMES[1].text
        minutes_volume_subtitle = self.locators.TOOLTIP_VOLUMES[2].text
        sms_volume_subtitle = self.locators.TOOLTIP_VOLUMES[3].text

        product_volumes = [internet_volume_subtitle, minutes_volume_subtitle, sms_volume_subtitle]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Проверить что объемы а вкладке Объемы соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_on_volumes_tab(self, expected_product_volumes: list[int]) -> None:
        self.product_edit_form.PRODUCT_VOLUMES.wait_to_have_count(len(expected_product_volumes))

        internet_volume_edit_form = self.product_edit_form.PRODUCT_VOLUMES[0].text
        minutes_volume_edit_form = self.product_edit_form.PRODUCT_VOLUMES[1].text
        sms_volume_edit_form = self.product_edit_form.PRODUCT_VOLUMES[2].text

        product_volumes = [internet_volume_edit_form, minutes_volume_edit_form, sms_volume_edit_form]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Сравнение объемов")
    def check_volumes(self, volumes: list[str], expected_volumes: list[int]) -> None:
        for i in range(len(expected_volumes)):
            volume = extract_volume_in_inquiry(volumes[i])
            assert_that(
                lambda: volume == expected_volumes[i],
                f"Объем отличется от ожидаемого: Фактический объем - {volume}, Ожидаемый объем - {expected_volumes[i]}",
            )

    @allure.step("Показать объемы продукта в тултипе")
    def show_volumes_tooltip(self, product_index: int = 0) -> None:
        self.locators.BOX_BUTTON[product_index].wait_to_be_visible(timeout=10000)
        self.locators.BOX_BUTTON[product_index].hover()
        self.locators.TOOLTIP_VOLUMES.wait_to_be_visible()

import allure

from pages.base_page import BasePage
from pages.locators.nbss.client.edit_product_activation_date_form import EditExecutionDateForm
from pages.locators.nbss.inquiries_elements import InquiriesElements


class InquiryOrderStructureManagement(BasePage):
    """Шаг заявки 'Управление составом заказа': работа с датой выполнения заказа (отложенная активация)."""

    def __init__(self) -> None:
        super().__init__()
        self.locators = InquiriesElements()

    @allure.step("Установить дату выполнения заказа на форме выбора ПП")
    def set_execution_date_on_product_form(self, date: str | None = None, current_time: bool = False) -> None:
        form = self.locators.product_offer_form
        edit_form = EditExecutionDateForm()
        form.SCHEDULE_EXECUTION_CHECKBOX.wait_to_be_visible(timeout=10000)
        if not form.SCHEDULE_EXECUTION_CHECKBOX.has_attribute_value("checked", ""):
            form.SCHEDULE_EXECUTION_CHECKBOX.click()
        form.PLANNED_DATE.wait_to_be_visible(timeout=10000)
        if current_time:
            form.PLANNED_DATE.click()
            edit_form.CURRENT_TIME_BTN.wait_to_be_visible(timeout=10000)
            edit_form.CURRENT_TIME_BTN.click()
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
        edit_form = EditExecutionDateForm()
        self.locators.EXECUTION_DATE_EDIT_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.EXECUTION_DATE_EDIT_BTN.click()
        edit_form.EXECUTION_DATE.wait_to_be_visible(timeout=10000)
        if current_time:
            edit_form.EXECUTION_DATE.click()
            edit_form.CURRENT_TIME_BTN.wait_to_be_visible(timeout=10000)
            edit_form.CURRENT_TIME_BTN.click()
        else:
            edit_form.EXECUTION_DATE.fill(date)
            self.press_keyboard_button("Enter")
        if expect_warning:
            edit_form.INFO_MESSAGE.to_contain_text("повторная проверка конфигурации", timeout_sec=10)
        if save:
            edit_form.EXECUTION_DATE_SAVE_BTN.wait_to_be_enabled(timeout=10000)
            edit_form.EXECUTION_DATE_SAVE_BTN.click()
            edit_form.EXECUTION_DATE.not_to_be_visible(timeout=60000)

    @allure.step("Проверить предупреждение о недопустимой дате выполнения заказа")
    def check_execution_date_error(self) -> None:
        EditExecutionDateForm().EXECUTION_DATE_ERROR.wait_to_be_visible()

    @allure.step("Редактировать дату выполнения заказа через вкладку 'Элементы заказа'")
    def edit_execution_date_order_elements(
        self, date: str | None = None, current_time: bool = False, expect_warning: bool = True, save: bool = True
    ) -> None:
        self.edit_execution_date_active_step(
            date=date, current_time=current_time, expect_warning=expect_warning, save=save
        )

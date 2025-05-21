import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.adjustment_requests import AdjustmentRequests
from api.requests.client_requests import ClientInfo
from api.requests.payments_requests import PaymentInfo
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_datetime_from_full_time_string,
)
from pages.adjustments_page import AdjustmentsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.adjustments import CreateAdjustmentForm


@allure.suite("E2E_77 Управление корректировками начислений и платежей")
@allure.sub_suite("Корректировки платежей")
class TestPaymentAdjustment:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_account_with_payment: tuple[ClientInfo, PaymentInfo],
    ) -> None:
        self.adjustment_api = AdjustmentRequests(api_request_auth_context)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.adjustments_page = AdjustmentsPage(nexign_ui_stand_login)
        self.create_adjustment_form = CreateAdjustmentForm(nexign_ui_stand_login)
        self.client, self.payment = create_account_with_payment

    @allure.title("Создание отрицательной корректировки платежа")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(586521)
    @pytest.mark.regress
    def test_create_negative_adjustment(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(2)
        payment_date = get_datetime_from_full_time_string(self.payment.payment_date)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment.payment_date,
            document_number=self.payment.document_number,
            amount=self.payment.amount,
        )

        with allure.step("Заполнить остальные обязательные поля"):
            tax = self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_type="Отрицательная корректировка",
                adjustment_sum=adjustment_sum,
                reason="Корректировка платежа",
            )
            adjustment_date = get_current_datetime_string(is_full_format=False)
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.payment.amount:.2f}")
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка платежа",
                date=adjustment_date,
                sum_with_tax=-adjustment_sum,
                tax=-tax,
                status="Создание",
                reason="Корректировка платежа",
                target=f"Платёж: {self.payment.document_number} от {payment_date.strftime('%d.%m.%Y')}",
            )

        with allure.step("Дождаться выполнения запроса"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(
                f"{(self.payment.amount - adjustment_sum):.2f}", timeout=15000
            )

    @allure.title("Создание положительной корректировки платежа")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(587093)
    @pytest.mark.regress
    def test_create_positive_adjustment(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(2)
        payment_date = get_datetime_from_full_time_string(self.payment.payment_date)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment.payment_date,
            document_number=self.payment.document_number,
            amount=self.payment.amount,
        )

        with allure.step("Заполнить остальные обязательные поля"):
            tax = self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_type="Положительная корректировка",
                adjustment_sum=adjustment_sum,
                reason="Положительная корректировка платежа",
            )
            adjustment_date = get_current_datetime_string(is_full_format=False)
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.payment.amount:.2f}")
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Положительная корректировка платежа",
                date=adjustment_date,
                sum_with_tax=adjustment_sum,
                tax=tax,
                status="Создание",
                reason="Положительная корректировка платежа",
                target=f"Платёж: {self.payment.document_number} от {payment_date.strftime('%d.%m.%Y')}",
            )

        with allure.step("Дождаться выполнения запроса"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(
                f"{(self.payment.amount + adjustment_sum):.2f}", timeout=15000
            )

    @allure.title("Создание отрицательной корректировки платежа (Списание КЗ)")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(587106)
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_create_negative_adjustment_payables_cancellation(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(2)
        payment_date = get_datetime_from_full_time_string(self.payment.payment_date)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment.payment_date,
            document_number=self.payment.document_number,
            amount=self.payment.amount,
        )

        with allure.step("Заполнить остальные обязательные поля"):
            tax = self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_type="Отрицательная корректировка",
                adjustment_sum=adjustment_sum,
                reason="Списание КЗ",
            )
            adjustment_date = get_current_datetime_string(is_full_format=False)
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.locators.BALANCE.wait_to_have_text(f"{self.payment.amount:.2f}")
            self.adjustments_page.check_adjustment(
                idx=0,
                adjustment_type="Отрицательная корректировка платежа",
                date=adjustment_date,
                sum_with_tax=-adjustment_sum,
                tax=-tax,
                status="Создание",
                reason="Списание КЗ",
                target=f"Платёж: {self.payment.document_number} от {payment_date.strftime('%d.%m.%Y')}",
            )

        with allure.step("Дождаться выполнения запроса"):
            self.adjustment_api.wait_adjustment_status(self.client.account_id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(
                f"{(self.payment.amount - adjustment_sum):.2f}", timeout=15000
            )

    @allure.title("Создание отрицательной корректировки платежа (Сумма корректировки превышает сумму платежа)")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(592823)
    @pytest.mark.regress
    def test_create_negative_adjustment_with_summ_more_then_payment(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(4)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Фин карточка' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment.payment_date,
            document_number=self.payment.document_number,
            amount=self.payment.amount,
        )

        with allure.step("Заполнить остальные обязательные поля"):
            self.adjustments_page.fill_other_required_input_create_adjustment_form(
                adjustment_type="Отрицательная корректировка",
                adjustment_sum=adjustment_sum,
                reason="Корректировка платежа",
            )
            self.create_adjustment_form.TITLE.not_to_be_visible()
            self.adjustments_page.base_elements.MODAL_TITLE[0].to_contain_text("Ошибка")
            self.adjustments_page.base_elements.MODAL_BODY_TEXT[0].to_contain_text(
                "Сумма больше чем доступная для исправления для платежа с идентификатором"
            )

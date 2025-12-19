import allure
import pytest

from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.payments_requests import PaymentInfo, PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_current_datetime_string,
    get_datetime_from_full_time_string,
)
from models.client import IndividualClient
from models.context import test_context
from pages.locators.nbss.finances.adjustments import CreateAdjustmentForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage


@allure.suite("E2E_77 Управление корректировками начислений и платежей")
@allure.sub_suite("Корректировки платежей")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestPaymentAdjustment:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_user_with_agreement_and_account: IndividualClient) -> None:
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.adjustment_api = AdjustmentRequests()
        self.client_profile = ClientProfilePage()
        self.adjustments_page = AdjustmentsPage()
        self.create_adjustment_form = CreateAdjustmentForm()

        self.client = create_user_with_agreement_and_account
        amount = generate_random_number(3)
        self.payment = PaymentInfo(account_id=test_context.client.agreements[0].accounts[0].id, amount=amount)
        self.payment_api.wait_check_create_payment(self.payment)
        self.payment_api.create_payment(self.payment)
        self.payment_api.wait_last_payment_done(test_context.client.agreements[0].accounts[0].id)
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, amount
        )
        self.payment_date = self.payment_api.get_payments(test_context.client.agreements[0].accounts[0].id).json()[
            "items"
        ][0]["paymentDate"][:19]
        self.payment_date_string = get_datetime_from_full_time_string(self.payment_date).strftime("%d.%m.%Y %H:%M:%S")

    @allure.title("Создание отрицательной корректировки платежа")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(586521)
    def test_create_negative_adjustment(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(2)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Финансы' > 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment_date,
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
                target=f"Платёж: {self.payment.document_number} от {self.payment_date_string}",
            )

        with allure.step("Дождаться выполнения запроса"):
            self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(
                f"{(self.payment.amount - adjustment_sum):.2f}", timeout=15000
            )

    @allure.title("Создание положительной корректировки платежа")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(587093)
    def test_create_positive_adjustment(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(2)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Финансы' > 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment_date,
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
                target=f"Платёж: {self.payment.document_number} от {self.payment_date_string}",
            )

        with allure.step("Дождаться выполнения запроса"):
            self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(
                f"{(self.payment.amount + adjustment_sum):.2f}", timeout=15000
            )

    @allure.title("Создание отрицательной корректировки платежа (Списание КЗ)")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(587106)
    @pytest.mark.smoke
    def test_create_negative_adjustment_payables_cancellation(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(2)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Финансы' > 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment_date,
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
                target=f"Платёж: {self.payment.document_number} от {self.payment_date_string}",
            )

        with allure.step("Дождаться выполнения запроса"):
            self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)
            self.adjustments_page.locators.UPDATE_TABLE_BTN.click()
            self.adjustments_page.check_adjustment(idx=0, status="Одобрено")
            self.adjustments_page.locators.BALANCE.wait_to_have_text(
                f"{(self.payment.amount - adjustment_sum):.2f}", timeout=15000
            )

    @allure.title("Создание отрицательной корректировки платежа (Сумма корректировки превышает сумму платежа)")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(592823)
    def test_create_negative_adjustment_with_summ_more_then_payment(self, base_url: str) -> None:
        adjustment_sum = generate_random_number(4)

        with allure.step("Переход в контекст ЛС"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Финансы' > 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.check_create_payment_adjustment_form()

        self.adjustments_page.fill_payment_input_create_adjustment_form(
            payment_date=self.payment_date,
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
                "Сумма больше чем доступная для исправления платежа"
            )

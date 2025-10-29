import allure
import pytest

from common.helpers.data_generator import get_current_datetime_string
from common.helpers.time_helpers import delay
from tests.nbss.debt_restructuring.debt_restructuring_base import DebtRestructuringBase


@allure.suite("E2E_68 Поддержка реструктуризации задолженности")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestDebtRestructuringPart2(DebtRestructuringBase):
    @allure.title("02.2 Создание рассрочки (Сумма рассрочки не задана)")
    @allure.id(616335)
    def test_installment_creation_not_specified_amount(self) -> None:
        self.set_installment_type("error")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([0], expected_date_number=0)
        self.base_elements.MODAL.wait_to_be_visible()
        self.base_elements.MODAL_BODY_TEXT.to_contain_text_in_all(
            "Сумма для отобранной детали счета должна быть положительной"
        )

    @allure.title("03 Редактирование рассрочки")
    @allure.id(617596)
    def test_installment_edit(self) -> None:
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client)

        new_payment_number = 3
        new_inquiry_id = self.debt_restructuring_page.inquiry_create(self.client, seq_number=2)
        with allure.step("Выбор рассрочки"):
            self.debt_restructuring.REFRESH_INSTALLMENTS_BTN.wait_to_be_visible()
            self.debt_restructuring.REFRESH_INSTALLMENTS_BTN.click()
            self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1)
            self.debt_restructuring.INSTALLMENTS[0].click()
        with allure.step("Редактирование параметров выбранной рассрочки"):
            delay(1, "Не успевает подгрузиться кнопка")
            self.debt_restructuring.EDIT_BTN.click()
            self.debt_restructuring.FIRST_PAYMENT_DATE.fill(get_current_datetime_string(is_full_format=False))
            self.debt_restructuring.PAYMENT_NUMBER.fill(str(new_payment_number))
            self.debt_restructuring.CALCULATE_BTN.click()
            self.debt_restructuring.PAYMENTS.wait_to_have_count(new_payment_number)
            self.debt_restructuring.REGISTER_BTN.click()
        self.debt_restructuring_page.inquiry_forward(new_inquiry_id, self.client)
        with allure.step("Проверка отображения изменений"):
            self.debt_restructuring_page.check_payment_number(new_payment_number)

    @allure.title("06 Создание рассрочки (С первоначальным платежом)")
    @allure.id(618090)
    def test_installment_creation_init_payment(self) -> None:
        self.set_installment_type("init_payment")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)
        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring.REFRESH_INSTALLMENTS_BTN.click()
        self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1)
        self.debt_restructuring.INSTALLMENTS[0].click()
        self.debt_restructuring.PAYMENT_HEADER.wait_to_have_count(2)
        self.debt_restructuring.PAYMENT_HEADER.to_contain_text_in_any(str(self.init_payment))
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client)

    @allure.title("09 Создание рассрочки (Активация Черновика)")
    @allure.id(618088)
    def test_installment_draft_activation(self) -> None:
        self.set_installment_type("draft")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.draft_check(self.client)
        self.debt_restructuring.EDIT_BTN.click()
        self.debt_restructuring.REGISTER_BTN.click()
        self.set_installment_type("default")
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client)

    @allure.title("17 Просмотр Рассрочки (Первый платеж по графику частично оплачен)")
    @allure.id(619407)
    def test_installment_creation_first_payment_partially_paid(self) -> None:
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client)

        paid_sum = self.debt / 4 - 10
        self.payment_api.create_default_payment(self.client.get_agreement().accounts[0].id, paid_sum)
        self.set_installment_type("partially_paid")
        self.installment_api.check_installment_done_status(status_timeout=45)
        with allure.step("Проверка оплаты первого платежа"):
            self.base_page.refresh_page(wait="load")
            self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1, timeout=15000)
            self.debt_restructuring.INSTALLMENTS[0].click()
            self.debt_restructuring.PAYMENTS_PAID_SUM[0].wait_to_have_text(f"{paid_sum:.2f}")

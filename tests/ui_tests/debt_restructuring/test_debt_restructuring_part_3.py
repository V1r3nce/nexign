import allure
import pytest

from common.helpers.time_helpers import delay
from tests.ui_tests.debt_restructuring.debt_restructuring_base import DebtRestructuringBase


@allure.suite("E2E_68 Поддержка реструктуризации задолженности")
@pytest.mark.regress
class TestDebtRestructuringPart3(DebtRestructuringBase):
    @allure.title("02.3 Создание рассрочки (Удален платеж из графика)")
    @allure.id(617527)
    def test_installment_creation_payment_deleted(self) -> None:
        self.set_installment_type("delete")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        self.base_elements.MODAL.wait_to_be_visible()
        self.base_elements.MODAL_BODY_TEXT.to_contain_text_in_all(
            "Общая сумма отобранных деталей не соответствует суммам графика"
        )

    @allure.title("04 Аннулирование рассрочки")
    @allure.id(618124)
    def test_installment_cancel(self) -> None:
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client)

        self.set_installment_type("cancel")
        self.debt_restructuring_page.inquiry_create(self.client, seq_number=2)
        self.debt_restructuring_page.installment_cancel(self.client)

    @allure.title("07 Создание рассрочки (Черновик)")
    @allure.id(617939)
    def test_installment_draft_creation(self) -> None:
        self.set_installment_type("draft")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.draft_check(self.client)

    @allure.title("12 Просмотр Рассрочки (Первоначальный платеж оплачен)")
    @allure.id(618201)
    def test_installment_creation_init_payment_paid(self) -> None:
        self.set_installment_type("init_payment")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        with allure.step("Проверка появления информации о первоначальном платеже"):
            self.debt_restructuring.REFRESH_INSTALLMENTS_BTN.click()
            self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1)
            self.debt_restructuring.INSTALLMENTS[0].click()
            self.debt_restructuring.PAYMENT_HEADER.wait_to_have_count(2)
            self.debt_restructuring.PAYMENT_HEADER.to_contain_text_in_any(str(self.init_payment))
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client)

        self.payment_api.create_default_payment(self.client.get_agreement().accounts[0].id, self.init_payment)
        self.installment_api.check_initial_payment_done_status(self.client)
        with allure.step("Проверка оплаты первоначального платежа"):
            self.base_page.refresh_page(wait="load")
            self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1, timeout=15000)
            self.debt_restructuring.INSTALLMENTS[0].click()
            self.debt_restructuring.INIT_PAYMENT_DONE.wait_to_be_visible()

    @allure.title("18 Просмотр Рассрочки (Рассрочка оплачена)")
    @allure.id(619412)
    def test_installment_creation_fully_paid(self) -> None:
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt], payment_number=1, expected_date_number=1)
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client, payment_number=1)

        self.payment_api.create_default_payment(self.client.get_agreement().accounts[0].id, self.debt + 50)
        self.set_installment_type("paid")
        self.installment_api.check_installment_done_status(self.client)
        with allure.step("Проверка оплаты первого платежа"):
            self.base_page.refresh_page(wait="load")
            self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1, timeout=15000)
            self.debt_restructuring.INSTALLMENTS[0].click()
            self.debt_restructuring.STATUS.wait_to_have_text(self.installment_type_status_map[self.installment_type])
            self.debt_restructuring.PAYMENTS_STATUSES[0].wait_to_have_text("Оплачен")

import allure
import pytest

from common.helpers.time_helpers import delay
from tests.nbss.debt_restructuring.debt_restructuring_base import DebtRestructuringBase


@allure.suite("E2E_68 Поддержка реструктуризации задолженности")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestDebtRestructuringPart1(DebtRestructuringBase):
    @allure.title("02.1 Создание рассрочки (Рассрочка превышает сумму долга)")
    @allure.id(617433)
    def test_installment_creation_installment_exceeds_debt(self) -> None:
        self.set_installment_type("error")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt + 100], expected_date_number=0)
        self.base_elements.MODAL.wait_to_be_visible()
        self.base_elements.MODAL_BODY_TEXT.to_contain_text_in_all("Требуются выбранные детали с суммами")

    @allure.title("02 Создание рассрочки (Без первоначального платежа)")
    @allure.id(616268)
    def test_installment_creation(self) -> None:
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id)

    @allure.title("05 Создание рассрочки (Без первоначального платежа, несколько счетов)")
    @allure.id(617535)
    def test_installment_creation_few_accounts(self) -> None:
        self.debt = 50
        self.client, self.product = self.client_prepare(category="internet")
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.product.subscription_fee, self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id, self.client, payment_number=5)

    @allure.title("08 Создание рассрочки (Аннулирование Черновика)")
    @allure.id(617945)
    def test_installment_draft_cancel(self) -> None:
        self.set_installment_type("draft")
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.draft_check()
        self.debt_restructuring_page.installment_cancel()

    @allure.title("13 Просмотр Рассрочки (Первый платеж по графику оплачен)")
    @allure.id(619352)
    def test_installment_creation_first_payment_paid(self) -> None:
        self.client, self.product = self.client_prepare()
        self.billing_conduction(self.client)
        inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)

        self.installment_create([self.debt])
        delay(2, "Не успевает появиться в списке")
        self.debt_restructuring_page.inquiry_forward(inquiry_id)

        installment_payment_amount = self.debt / 4
        self.payment_api.create_default_payment(
            self.client.get_agreement().accounts[0].id, installment_payment_amount + 10
        )
        self.set_installment_type("partially_paid")
        self.installment_api.check_installment_done_status(status_timeout=45)
        with allure.step("Проверка оплаты первого платежа"):
            self.base_page.refresh_page(wait="load")
            self.debt_restructuring.INSTALLMENTS.wait_to_have_count(1, timeout=15000)
            self.debt_restructuring.INSTALLMENTS[0].click()
            self.debt_restructuring.STATUS.wait_to_have_text(self.installment_type_status_map[self.installment_type])
            self.debt_restructuring.PAYMENTS_STATUSES[0].wait_to_have_text("Оплачен")

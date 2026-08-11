import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.time_helpers import delay
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_profile_page import ClientProfilePage
from tests.nbss.debt_restructuring.debt_restructuring_base import DebtRestructuringBase


@allure.suite("E2E_68 Поддержка реструктуризации задолженности")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestDebtRestructuringExtension(DebtRestructuringBase):
    @pytest.fixture(autouse=True)
    def extension_setup(self, setup) -> None:
        """Зависит от setup, иначе объекты создадутся до авторизации и API контекст не будет найден."""
        self.client_inquiry_api = ClientInquiriesRequests()
        self.client_profile_page = ClientProfilePage()

    @allure.title("Extension. Отображение наличия рассрочки в списке биллинговых счетов")
    @allure.id(955738)
    def test_installment_sign_in_bills_list(self, base_url: str) -> None:
        with allure.step("Создание клиента, продажа ПП на постоплатный ЛС, проведение внеочередного биллинга"):
            self.client = self.client_api.create_organization_client_with_postpaid_account(self.type)
            inquiry = self.client_inquiry_api.product_sale(self.client, prepare_inquiries("internet"))
            bill_debts = [inquiry.product.subscription_fee, inquiry.product.one_time_payment]
            account_id = self.client.agreement.account.id
            self.personal_account_api.wait_check_current_main_balance(account_id, -sum(bill_debts))
            self.billing_api.execute_unscheduled_billing_and_wait_completion(
                billing_profile_id=self.billing_api.get_billing_profile_id(account_id)
            )

        with allure.step("Создание заявки на реструктуризацию долга и добавление рассрочки"):
            inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)
            self.installment_create(bill_debts)
            delay(2, "Не успевает появиться в списке")
            self.debt_restructuring_page.inquiry_forward(inquiry_id, payment_number=None)

        with allure.step("Переход в контекст лицевого счета"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/accounts/{account_id}/account")
            self.client_profile_page.locators.PERSONAL_ACCOUNT_BALANCE.wait_to_be_enabled(timeout=25000)

        with allure.step("Нажать на Бургер меню. Перейти в Финансы -> Биллинговые счета"):
            self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts_page.check_installment_sign()

        with allure.step("Проверка признака рассрочки в ответе API"):
            self.billing_api.wait_bill_installment_sign(self.billing_api.get_billing_profile_id(account_id))

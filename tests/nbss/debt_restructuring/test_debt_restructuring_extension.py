import allure
import pytest

from common.helpers.time_helpers import delay
from tests.nbss.debt_restructuring.debt_restructuring_base import DebtRestructuringBase


@allure.suite("E2E_68 Поддержка реструктуризации задолженности")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestDebtRestructuringExtension(DebtRestructuringBase):
    @allure.title("Extension. Отображение наличия рассрочки в списке биллинговых счетов")
    @allure.id(955738)
    def test_installment_sign_in_bills_list(self, base_url: str) -> None:
        with allure.step("Создание клиента, продажа ПП на постоплатный ЛС, проведение внеочередного биллинга"):
            self.client = self.client_prepare_with_sale()

        with allure.step("Создание заявки на реструктуризацию долга и добавление рассрочки"):
            inquiry_id = self.debt_restructuring_page.inquiry_create(self.client)
            self.installment_create(self.bill_debts)
            delay(2, "Не успевает появиться в списке")
            self.debt_restructuring_page.inquiry_forward(inquiry_id)

        account_id = self.client.get_agreement().accounts[0].id
        with allure.step("Переход в контекст лицевого счета"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/accounts/{account_id}/account")
            self.client_profile_page.locators.PERSONAL_ACCOUNT_BALANCE.wait_to_be_enabled(timeout=25000)

        with allure.step("Нажать на Бургер меню. Перейти в Финансы -> Биллинговые счета"):
            self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts_page.check_installment_sign()

        with allure.step("Проверка признака рассрочки в ответе POST bss-box/v2/finance/bills/search"):
            self.billing_api.wait_bill_installment_sign(self.billing_api.get_billing_profile_id(account_id))

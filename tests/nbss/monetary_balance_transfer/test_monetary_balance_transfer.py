import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.string_helper import convert_amount_to_balance_string
from models.context import test_context
from models.user import (
    EntrepreneurClient,
    IndividualClient,
    OrganizationClient,
    generate_individual_client,
)
from pages.base_page import BasePage
from pages.locators.nbss.finances.adjustments import Adjustments
from pages.locators.nbss.finances.payments_elements import PaymentElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage
from pages.nbss.finances.payments_page import PaymentsPage


@allure.suite("E2E_71 Перенос монетарного баланса")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestMonetaryBalanceTransfer:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, base_url) -> None:
        self.base_page = BasePage()
        self.payments_elements = PaymentElements()
        self.adjustments = Adjustments()
        self.client_profile = ClientProfilePage()
        self.payments_page = PaymentsPage()
        self.adjustments_page = AdjustmentsPage()
        self.client_api = ClientRequests()
        self.base_url = base_url
        self.balance_first_user = 1190
        self.balance_second_user = 200
        self.transfer_amount = 150

    @allure.step("Проведение переноса")
    def process_transfer(self, account_from_id: int, account_to_num: int) -> None:
        with allure.step("Переход в контекст ЛС"):
            self.base_page.open(self.base_url + f"customer-hierarchy-management/accounts/{account_from_id}/account")
        self.client_profile.locators.BURGER_MENU.wait_to_be_visible()
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Платежи")
        self.payments_elements.CREATE_PAYMENT_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.transfer_monetary_balance(account_to_num, self.transfer_amount)
        with allure.step("Проверка изменения баланса"):
            self.payments_elements.USER_BALANCE.wait_to_have_text(
                convert_amount_to_balance_string(self.balance_first_user - self.transfer_amount), timeout=15000
            )

    @allure.step("Проверка выполнения переноса и его корректности")
    def check_personal_account_adjustment(self, account_id, transfer_type: str):
        with allure.step("Переход в контекст ЛС"):
            self.base_page.open(self.base_url + f"customer-hierarchy-management/accounts/{account_id}/account")
        self.client_profile.locators.BURGER_MENU.wait_to_be_visible()
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        with allure.step("Проверка корректности отображения корректировки"):
            self.adjustments_page.check_monetary_balance_transfer_adjustment(
                account_id, transfer_type, self.transfer_amount
            )

    @allure.title("Перенос денежных средств между ЛС разных клиентов ФЛ")
    @allure.id(586948)
    def test_transfer_individual_entities(self) -> None:
        with allure.step("Подготовка первого клиента"):
            self.user_first = self.client_api.create_client_with_payment(
                generate_individual_client(), self.balance_first_user
            )
        with allure.step("Подготовка второго клиента"):
            self.user_second = self.client_api.create_client_with_payment(
                generate_individual_client(), self.balance_second_user
            )

        self.process_transfer(
            self.user_first.agreements[0].accounts[0].id, self.user_second.agreements[0].accounts[0].number
        )
        self.check_personal_account_adjustment(self.user_first.agreements[0].accounts[0].id, "donor")
        self.check_personal_account_adjustment(self.user_second.agreements[0].accounts[0].id, "recipient")

    @allure.title("Перенос денежных средств между ЛС одного клиента ЮЛ")
    @allure.id(587095)
    def test_transfer_organization_entity(self, create_organization: OrganizationClient) -> None:
        with allure.step("Подготовка первого ЛС"):
            self.client_api.create_agreement_and_account_with_payment(test_context.client, self.balance_first_user)
        with allure.step("Подготовка второго ЛС"):
            self.client_api.create_agreement_and_account_with_payment(test_context.client, self.balance_second_user)

        self.process_transfer(
            test_context.client.agreements[0].accounts[0].id, test_context.client.agreements[1].accounts[0].number
        )
        self.check_personal_account_adjustment(test_context.client.agreements[0].accounts[0].id, "donor")
        self.check_personal_account_adjustment(test_context.client.agreements[1].accounts[0].id, "recipient")

    @allure.title("Перенос денежных средств между ЛС одного клиента ФЛ")
    @allure.id(586773)
    def test_transfer_individual_entity(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Подготовка первого ЛС"):
            self.client_api.create_agreement_and_account_with_payment(test_context.client, self.balance_first_user)
        with allure.step("Подготовка второго ЛС"):
            self.client_api.create_agreement_and_account_with_payment(test_context.client, self.balance_second_user)

        self.process_transfer(
            test_context.client.agreements[0].accounts[0].id, test_context.client.agreements[1].accounts[0].number
        )
        self.check_personal_account_adjustment(test_context.client.agreements[0].accounts[0].id, "donor")
        self.check_personal_account_adjustment(test_context.client.agreements[1].accounts[0].id, "recipient")

    @allure.title("Вывод денежных средств частями")
    @allure.id(588840)
    def test_transfer_money_by_parts(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Подготовка клиента"):
            payment = self.client_api.create_agreement_and_account_with_payment(
                test_context.client, self.balance_first_user
            )
        with allure.step("Переход в контекст клиента"):
            self.base_page.open(
                self.base_url
                + f"customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.fill_payment_input_create_adjustment_form(
                None, payment.document_number, self.balance_first_user
            )
            self.adjustments_page.fill_other_required_input_create_adjustment_form(
                self.transfer_amount, "Вывод денежных средств по заявлению клиента", "Отрицательная корректировка"
            )
        self.adjustments_page.check_monetary_balance_transfer_adjustment(
            test_context.client.agreements[0].accounts[0].id,
            "donor",
            self.transfer_amount,
            alter_reason="Вывод денежных средств по заявлению клиента",
        )
        self.base_page.refresh_page(wait="load")
        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.fill_payment_input_create_adjustment_form(
                None, payment.document_number, self.balance_first_user
            )
            self.adjustments_page.fill_other_required_input_create_adjustment_form(
                self.transfer_amount, "Вывод денежных средств по заявлению клиента", "Отрицательная корректировка"
            )
        self.adjustments_page.check_monetary_balance_transfer_adjustment(
            test_context.client.agreements[0].accounts[0].id,
            "donor",
            self.transfer_amount,
            alter_reason="Вывод денежных средств по заявлению клиента",
            seq_number=2,
        )
        self.payments_elements.USER_BALANCE.wait_to_have_text(
            convert_amount_to_balance_string(self.balance_first_user - 2 * self.transfer_amount), timeout=15000
        )

    @allure.title("Вывод денежных средств")
    @allure.id(588382)
    def test_transfer_money(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Подготовка клиента"):
            payment = self.client_api.create_agreement_and_account_with_payment(
                test_context.client, self.balance_first_user
            )
        with allure.step("Переход в контекст клиента"):
            self.base_page.open(
                self.base_url
                + f"customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.fill_payment_input_create_adjustment_form(
                None, payment.document_number, self.balance_first_user
            )
        self.adjustments_page.fill_other_required_input_create_adjustment_form(
            self.balance_first_user, "Вывод денежных средств по заявлению клиента", "Отрицательная корректировка"
        )
        self.adjustments_page.check_monetary_balance_transfer_adjustment(
            test_context.client.agreements[0].accounts[0].id,
            "donor",
            self.balance_first_user,
            alter_reason="Вывод денежных средств по заявлению клиента",
        )

    @allure.title("Вывод денежных средств (недостаточно средств)")
    @allure.id(588838)
    def test_transfer_money_exceed_debt(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Подготовка клиента"):
            payment = self.client_api.create_agreement_and_account_with_payment(
                test_context.client, self.balance_first_user
            )
        with allure.step("Переход в контекст клиента"):
            self.base_page.open(
                self.base_url
                + f"customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.fill_payment_input_create_adjustment_form(
                None, payment.document_number, self.balance_first_user
            )
        self.adjustments_page.fill_other_required_input_create_adjustment_form(
            self.balance_first_user, "Вывод денежных средств по заявлению клиента", "Отрицательная корректировка"
        )
        self.adjustments_page.check_monetary_balance_transfer_adjustment(
            test_context.client.agreements[0].accounts[0].id,
            "donor",
            self.balance_first_user,
            alter_reason="Вывод денежных средств по заявлению клиента",
        )
        with allure.step("Переход в контекст клиента"):
            self.base_page.open(
                self.base_url
                + f"customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
        self.client_profile.locators.BURGER_MENU.wait_to_be_visible()
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
        with allure.step("Нажать кнопку 'Добавить корректировку' - 'Ввод корректировки платежа'"):
            self.adjustments_page.locators.ADD_ADJUSTMENT_BTN.select_by_value("Ввод корректировки платежа")
            self.adjustments_page.fill_payment_input_create_adjustment_form(
                None, payment.document_number, self.balance_first_user
            )
            self.adjustments_page.fill_other_required_input_create_adjustment_form(
                self.transfer_amount, "Вывод денежных средств по заявлению клиента", "Отрицательная корректировка"
            )
            self.payments_elements.MODAL.wait_to_be_visible()

    @allure.title("Перенос с постоплатного ЛС")
    @allure.id(588478)
    def test_transfer_postpaid_individual_entities(self) -> None:
        self.balance_first_user = 0
        with allure.step("Подготовка первого клиента"):
            self.user_first = self.client_api.create_individual_client_with_postpaid_account(
                generate_individual_client()
            )
        with allure.step("Подготовка второго клиента"):
            self.user_second = self.client_api.create_client_with_payment(
                generate_individual_client(), self.balance_second_user
            )
        self.process_transfer(
            self.user_first.agreements[0].accounts[0].id, self.user_second.agreements[0].accounts[0].number
        )
        self.check_personal_account_adjustment(self.user_first.agreements[0].accounts[0].id, "donor_postpaid")
        self.check_personal_account_adjustment(self.user_second.agreements[0].accounts[0].id, "recipient")

    @allure.title("Перенос с персонального ЛС")
    @allure.id(588477)
    def test_transfer_entrepreneur(self, create_entrepreneur: EntrepreneurClient) -> None:
        with allure.step("Подготовка первого ЛС"):
            self.client_api.create_agreement_and_account_with_payment(test_context.client, self.balance_first_user)
        with allure.step("Подготовка второго ЛС"):
            self.client_api.create_agreement_and_account_with_payment(test_context.client, self.balance_second_user)

        self.process_transfer(
            test_context.client.agreements[0].accounts[0].id, test_context.client.agreements[1].accounts[0].number
        )
        self.check_personal_account_adjustment(test_context.client.agreements[0].accounts[0].id, "donor")
        self.check_personal_account_adjustment(test_context.client.agreements[1].accounts[0].id, "recipient")

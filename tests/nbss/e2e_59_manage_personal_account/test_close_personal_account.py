import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from common.enums.ats import AtsAttributes, PersonalAccountStatusNames
from common.enums.user import User
from models.client import OrganizationClient, PaymentInfo
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.personal_account_page import PersonalAccountPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_59 Управление лицевым счетом")
@allure.suite("E2E_59 Управление лицевым счетом")
class TestClosePersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.personal_account_page = PersonalAccountPage()
        self.client_profile_page = ClientProfilePage()

        self.payments_requests = PaymentsRequests()
        self.personal_account_requests = PersonalAccountRequests()
        self.client_inquiries = ClientInquiriesRequests()

        self.b2b_client = create_organization_with_agreement_and_account
        self.account_id = self.b2b_client.agreements[0].accounts[0].id

    @allure.title("01. Ручное закрытие лицевого счета")
    @allure.id(836129)
    def test_close_personal_account(self) -> None:
        with allure.step("Precondition: открыть форму просмотра ЛС"):
            self.personal_account_page.open_personal_account_page(self.account_id)

        with allure.step("Нажать «Закрыть лицевой счёт» и подтвердить в диалоге"):
            self.personal_account_page.close_personal_account()

    @allure.title("02. Ручное закрытие лицевого счета без роли")
    @allure.id(836132)
    @pytest.mark.user(User.CUSTOMER_CARE_TEST)
    def test_close_personal_account_without_role(self) -> None:
        with allure.step("Precondition: открыть форму просмотра ЛС под CUSTOMER_CARE"):
            self.personal_account_page.open_personal_account_page(self.account_id)

        with allure.step("Проверить, что кнопка «Закрыть лицевой счёт» не отображается"):
            self.personal_account_page.locators.CLOSE_PERSONAL_ACCOUNT_BTN.not_to_be_visible()

    @allure.title("03. Ручное закрытие лицевого счета: ЛС персональный")
    @allure.id(836133)
    def test_close_personal_account_individual(self) -> None:
        with allure.step("Precondition: создать персональный ЛС"):
            account_data = PersonalAccountData(agreement_id=self.b2b_client.agreements[0].id, account_type_id=3)
            account_id = self.personal_account_requests.create_personal_account(account_data, self.b2b_client.user_id)[0]

        with allure.step("Precondition: открыть форму просмотра ЛС"):
            self.personal_account_page.open_personal_account_page(account_id)

        with allure.step("Проверить, что кнопка неактивна с подсказкой"):
            self.personal_account_page.check_close_button_disabled_with_tooltip(
                "Закрытие персонального лицевого счета невозможно"
            )

    @allure.title("04. Ручное закрытие лицевого счета: ЛС в статусе Закрыт")
    @allure.id(836134)
    def test_close_already_closed_account(self) -> None:
        with allure.step("Precondition: закрыть ЛС"):
            self.personal_account_page.open_personal_account_page(self.account_id)
            self.personal_account_page.close_personal_account()

        with allure.step("Проверить, что кнопка неактивна с подсказкой"):
            self.personal_account_page.check_close_button_disabled_with_tooltip(
                "Закрытие лицевого счета в статусе «Закрыт» невозможно"
            )

    @allure.title("05. Ручное закрытие лицевого счета: ненулевой баланс")
    @allure.id(836135)
    def test_close_account_with_nonzero_balance(self) -> None:
        with allure.step("Precondition: совершить платёж для ненулевого баланса"):
            payment = PaymentInfo(amount=100, account_id=self.account_id)
            self.payments_requests.wait_check_create_payment(payment)
            self.payments_requests.create_payment(payment)
            self.personal_account_requests.wait_check_current_main_balance(self.account_id, 100)

        with allure.step("Precondition: открыть форму просмотра ЛС"):
            self.personal_account_page.open_personal_account_page(self.account_id)

        with allure.step("Проверить, что кнопка неактивна с подсказкой"):
            self.personal_account_page.check_close_button_disabled_with_tooltip(
                "Закрытие лицевого счета невозможно, так как его баланс не равен нулю"
            )

    @allure.title("06. Ручное закрытие лицевого счета: есть активный продукт")
    @allure.id(836138)
    def test_close_account_with_active_product(self) -> None:
        with allure.step("Precondition: продать продукт «Интернет в офис»"):
            self.client_inquiries.product_sale(self.b2b_client, inquiry=prepare_inquiries(category="internet"))

        with allure.step("Precondition: открыть форму просмотра ЛС"):
            self.personal_account_page.open_personal_account_page(self.account_id)

        with allure.step("Проверить, что кнопка неактивна с подсказкой"):
            self.personal_account_page.check_close_button_disabled_with_tooltip(
                "Закрытие лицевого счета невозможно, так как на нем числятся активные продукты"
            )

    @allure.title("07. Ручное закрытие лицевого счета: есть отключенный продукт")
    @allure.id(836208)
    def test_close_account_with_disconnected_product(self) -> None:
        with allure.step("Precondition: продать и отключить продукт «Интернет в офис»"):
            self.client_inquiries.product_sale(self.b2b_client, inquiry=prepare_inquiries(category="internet"))
            self.client_inquiries.product_disconnect()

        with allure.step("Precondition: открыть форму просмотра ЛС"):
            self.personal_account_page.open_personal_account_page(self.account_id)

        with allure.step("Нажать «Закрыть лицевой счёт» и подтвердить в диалоге"):
            self.personal_account_page.close_personal_account()

    @allure.title("08. Просмотр истории закрытого лицевого счета")
    @allure.id(836140)
    def test_view_closed_account_history(self) -> None:
        with allure.step("Precondition: закрыть ЛС"):
            self.personal_account_page.open_personal_account_page(self.account_id)
            self.personal_account_page.close_personal_account()

        with allure.step("Проверить наличие записи о переводе в статус «Закрыт»"):
            self.client_profile_page.check_attributes_history(
                attributes=[AtsAttributes.personal_account_status_name],
                old_values=[PersonalAccountStatusNames.active],
                new_values=[PersonalAccountStatusNames.closed],
            )

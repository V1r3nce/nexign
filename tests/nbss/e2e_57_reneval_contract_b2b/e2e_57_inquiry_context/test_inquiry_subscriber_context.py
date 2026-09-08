import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.dynamic_forms.panel_toolbar.create_sales_form_page import CreateSalesFormPage


@allure.epic("E2E_57 Переоформление договора B2B")
@allure.suite("Уточнение контекста договора/ЛС в форме создания заявки")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestInquirySubscriberContext:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()
        self.client_product_profile_page = ClientProductProfilePage()
        self.create_sales_form_page = CreateSalesFormPage()
        self.personal_account_requests = PersonalAccountRequests()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.payment_requests = PaymentsRequests()

    @allure.title("33. Передача значений атрибутов абонента в заявку")
    @allure.id(859585)
    def test_subscriber_attributes_in_inquiry(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        with allure.step("Продать продукт на договор Y и создать второй договор X с ЛС"):
            self.personal_account_requests.create_agreement_and_account(test_context.client, status_id=1)
            self.client_inquiries_requests.product_sale(test_context.client, inquiry=prepare_inquiries("internet"))
            self.payment_requests.create_default_payment(
                test_context.client.agreement.account.id, test_context.client.inquiry.product.total_amount
            )
            self.personal_account_requests.wait_check_current_main_balance(test_context.client.agreement.account.id, 0)
            self.client_inquiries_requests.wait_products_active_by_agreement(
                test_context.client.user_id, test_context.client.agreement.id
            )

        agreement_y = test_context.client.agreements[0]
        agreement_x = test_context.client.agreements[1]

        self.client_profile_page.open_account_page(agreement_x.account.id)
        self.client_profile_page.locators.LINK_IN_CONTEXT.wait_to_be_visible()
        self.client_profile_page.locators.LINK_IN_CONTEXT.wait_to_have_count_or_greater(1)
        self.client_profile_page.locators.LINK_IN_CONTEXT[0].click()
        self.client_profile_page.click_tab("Продукты")

        with allure.step("Изменение опций через абонента"):
            self.client_product_profile_page.add_adoption_product("Безлимит")
            self.create_sales_form_page.check_context(agreement_y.number, agreement_y.account.number)
            self.create_sales_form_page.close_without_saving()

        with allure.step("Редактирование продукта через абонента"):
            self.client_product_profile_page.open_products_all_subscriber()
            self.client_product_profile_page.open_edit_product_form()
            self.create_sales_form_page.check_context(agreement_y.number, agreement_y.account.number)
            self.create_sales_form_page.close_without_saving()

        with allure.step("Отключение продукта через абонента"):
            self.client_product_profile_page.open_products_all_subscriber()
            self.client_product_profile_page.open_disconnect_product_form()
            self.create_sales_form_page.check_context(agreement_y.number, agreement_y.account.number)
            self.create_sales_form_page.close_without_saving()

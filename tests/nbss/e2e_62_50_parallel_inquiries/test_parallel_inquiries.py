import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.inquiry import InquiryAddAgreementAdd, InquiryStep
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.feature(
    "E2E_62_50 Продажа клиенту B2B. (Запрет параллельных заказов на стадии подключения/активации по абоненту)"
)
class TestParallelInquiries:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_postpaid_account):
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()

        self.client_inquiries_api = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()

    @allure.title("Продажа клиенту B2B: два параллельных заказа")
    @allure.id(839833)
    def test_two_parallel_inquiries(self):
        with allure.step("Продажа продукта для клиента"):
            self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("satellite_rent"))
            self.personal_account_api.wait_check_current_main_balance(
                account_id=test_context.client.agreements[0].accounts[0].id,
                desired_balance=-test_context.client.inquiry.product.total_amount,
            )
            self.client_inquiries_api.wait_products_active_by_agreement(
                user_id=test_context.client.user_id, agreement_id=test_context.client.agreements[0].id
            )

        with allure.step("Подготовка заявок на продажу доп ПП"):
            self.client_inquiries_api.additional_product_for_main_create_inquiry(
                main_product=test_context.client.inquiry.product, additional_product_name="Доступ в интернет"
            )
            self.client_inquiries_api.additional_product_for_main_create_inquiry(
                main_product=test_context.client.inquiry.product, additional_product_name="Белый IP"
            )
            first_inquiry = test_context.client.inquiry_list[1]
            second_inquiry = test_context.client.inquiry_list[2]
            test_context.client.inquiry = second_inquiry
            self.client_inquiries_api.resources_reserve(product=second_inquiry.product.additional_product)
            self.client_inquiries_api.forward_step_with_check(second_inquiry.commercial_order_number)

        with allure.step("Открытие первой заявки, нажатие кнопки Далее"):
            self.inquiries_page.open_inquiry_commercial_order_step(first_inquiry.id)
            self.inquiries_page.click_next("Проверка возможности заключения договора")
        with allure.step("Открытие второй заявки, нажатие кнопки Далее"):
            self.inquiries_page.open_inquiry_commercial_order_step(second_inquiry.id)
            self.inquiries_page.click_next("Проверка возможности заключения договора")
            self.inquiries_page.check_and_wait_parallel_inquiry(first_inquiry.id)
        with allure.step("Открытие первой заявки, ожидание завершения"):
            self.inquiries_page.open_inquiry_page(first_inquiry.id)
            self.inquiries_page.wait_sale_completion()
        with allure.step("Открытие второй заявки, ожидание завершения"):
            self.inquiries_page.open_inquiry_page(second_inquiry.id)
            self.inquiries_page.wait_sale_completion()

    @allure.title("Продажа клиенту B2B: три параллельных заказа")
    @allure.id(839816)
    def test_three_parallel_inquiries(self):
        with allure.step("Продажа продукта для клиента"):
            self.client_inquiries_api.product_sale(
                inquiry=prepare_inquiries(category=["satellite_rent", "satellite_rent"], as_list=False)
            )
            self.personal_account_api.wait_check_current_main_balance(
                account_id=test_context.client.agreements[0].accounts[0].id,
                desired_balance=-2 * test_context.client.inquiry.product.total_amount,
            )
            self.client_inquiries_api.wait_products_active_by_agreement(
                user_id=test_context.client.user_id, agreement_id=test_context.client.agreements[0].id
            )

        with allure.step("Подготовка заявок на продажу доп ПП"):
            self.client_inquiries_api.additional_product_for_main_create_inquiry(
                main_product=test_context.client.inquiry.product_list[0],
                additional_product_name="Доступ в интернет",
                agreement_add=InquiryAddAgreementAdd.manual,
            )
            self.client_inquiries_api.additional_product_for_main_create_inquiry(
                main_product=test_context.client.inquiry.product_list[1],
                additional_product_name="Белый IP",
                agreement_add=InquiryAddAgreementAdd.manual,
            )
            self.client_inquiries_api.additional_product_for_main_create_inquiry(
                main_product=test_context.client.inquiry.product_list[1],
                additional_product_name="Доступ в интернет",
                agreement_add=InquiryAddAgreementAdd.manual,
            )
            first_inquiry = test_context.client.inquiry_list[1]
            second_inquiry = test_context.client.inquiry_list[2]
            third_inquiry = test_context.client.inquiry_list[3]
            test_context.client.inquiry = second_inquiry
            self.client_inquiries_api.resources_reserve(product=second_inquiry.product.additional_product)
            self.client_inquiries_api.forward_step_with_check(second_inquiry.commercial_order_number)
            self.client_inquiries_api.pass_manual_agreement_and_account_steps(first_inquiry, False, False, False)
            self.client_inquiries_api.pass_manual_agreement_and_account_steps(second_inquiry, False, False, False)
            self.client_inquiries_api.pass_manual_agreement_and_account_steps(third_inquiry, False, False, False)

        with allure.step("Открытие первой заявки, нажатие кнопки Далее"):
            self.inquiries_page.open_inquiry_page(first_inquiry.id)
            self.inquiries_page.click_next(InquiryStep.ControlCommercialOrderCheck)
        with allure.step("Открытие второй заявки, нажатие кнопки Далее"):
            self.inquiries_page.open_inquiry_page(second_inquiry.id)
            self.inquiries_page.click_next(InquiryStep.ControlCommercialOrderCheck)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.ManageProducts, timeout=40000)
        with allure.step("Открытие третьей заявки, нажатие кнопки Далее"):
            self.inquiries_page.open_inquiry_page(third_inquiry.id)
            self.inquiries_page.click_next(InquiryStep.ControlCommercialOrderCheck)
            self.inquiries_page.check_and_wait_parallel_inquiry([second_inquiry.id])
        with allure.step("Открытие первой заявки, ожидание завершения"):
            self.inquiries_page.open_inquiry_page(first_inquiry.id)
            self.inquiries_page.wait_sale_completion()
        with allure.step("Открытие второй заявки, ожидание завершения"):
            self.inquiries_page.open_inquiry_page(second_inquiry.id)
            self.inquiries_page.wait_sale_completion()
        with allure.step("Открытие третьей заявки, ожидание завершения"):
            self.inquiries_page.open_inquiry_page(third_inquiry.id)
            self.inquiries_page.wait_sale_completion()

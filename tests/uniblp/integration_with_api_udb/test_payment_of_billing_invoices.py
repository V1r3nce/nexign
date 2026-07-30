import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.billing_requests import BillingRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts
from pages.uniblp_pages.files_page import FilesUniblpPage
from pages.uniblp_pages.home_uniblp_page import HomeUniblpPage
from pages.uniblp_pages.statements_page import StatementsUniblpPage


@allure.suite("Реализация интеграции UNIBLP с API UDB, возвращающим список неоплаченных счетов по ЛС")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.uniblp
class TestBillingInvoicesPayment:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        stand_login_uniblp,
        app_parameter_post_pays,
        organization_user_data: OrganizationClient,
    ) -> None:
        self.billing_api = BillingRequests()
        self.client_request_api = ClientInquiriesRequests()
        self.app_parameter = "BLP_TARGET_POST_PAYS_ENABLE"
        self.product_1 = B2BProducts.mobile_mini
        self.product_2 = B2BProducts.mobile
        self.uniblp_page = HomeUniblpPage()
        self.files_page = FilesUniblpPage()
        self.statements_page = StatementsUniblpPage()
        self.client_api = ClientRequests()
        self.client = self.client_api.create_organization_client_with_postpaid_account(organization_user_data)

    @allure.title("Частичная оплата биллинговых счетов")
    @allure.id(870158)
    def test_partial_payment_of_billing_invoices(self, remove_file_from_download_folder: list) -> None:
        with allure.step("Продажа клиенту монопродукта"):
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(category="mobile", product_offering_id=self.product_1)
            )

        with allure.step("Проведение внеочередного биллинга"):
            self.billing_api.execute_unscheduled_billing_and_wait_completion()

        with allure.step("Продажа клиенту монопродукта"):
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(category="mobile", product_offering_id=self.product_2)
            )

        with allure.step("Повторное проведение внеочередного биллинга"):
            self.billing_api.execute_unscheduled_billing_and_wait_completion()

        with allure.step("Загрузка выписки в UNIBLP UI"):
            self.uniblp_page.open_files_tab()

            redemption_amount = 150.00
            self.files_page.upload_statement(
                file_name="1c_1docs_870158.txt", amount=redemption_amount, remove_file=remove_file_from_download_folder
            )

        with allure.step("Переход в форму 'Документы выписки'"):
            self.files_page.open_file()

        with allure.step("Переход в форму 'Платежи'"):
            self.statements_page.open_statement()

        with allure.step("Переход в форму 'Поиск плательщика'"):
            self.statements_page.search_and_select_payer(test_context.client.agreements[0].accounts[0].number)

        with allure.step("Проверка параметров после выбора клиента"):
            self.statements_page.verify_client_info_after_selection()

        with allure.step("Сохранение платежа"):
            self.statements_page.save_payment_and_verify_fields()

        with allure.step("Поиск непогашенных счетов клиента"):
            self.statements_page.locators.TARGET_POST_PAYS_BTN.wait_to_be_enabled(timeout=15000)
            self.statements_page.locators.TARGET_POST_PAYS_BTN.click()

        with allure.step("Ручное разнесение первого счета"):
            remainder_amount = self.statements_page.manual_post_payment(
                row_index=0, amount=1.00, remainder_amount=redemption_amount
            )

        with allure.step("Ручное разнесение второго счета"):
            self.statements_page.manual_post_payment(row_index=1, amount=149.00, remainder_amount=remainder_amount)

        with allure.step("Сохранение целеуказаний"):
            self.statements_page.save_target_pays()

        with allure.step("Сохранение документа в биллинг"):
            self.statements_page.save_document_to_billing()

        with allure.step("Проверка биллинговых счетов"):
            self.billing_api.wait_for_billing_accounts_status(expected_status="Частично оплачен")

    @allure.title("Полная оплата биллинговых счетов")
    @allure.id(870031)
    def test_full_payment_of_billing_invoices(self, remove_file_from_download_folder: list) -> None:
        with allure.step("Продажа клиенту монопродукта"):
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(category="mobile", product_offering_id=self.product_1)
            )

        with allure.step("Проведение внеочередного биллинга"):
            self.billing_api.execute_unscheduled_billing_and_wait_completion()

        with allure.step("Продажа клиенту монопродукта"):
            self.client_request_api.product_sale(
                inquiry=prepare_inquiries(category="mobile", product_offering_id=self.product_2)
            )

        with allure.step("Повторное проведение внеочередного биллинга"):
            self.billing_api.execute_unscheduled_billing_and_wait_completion()

        with allure.step("Загрузка выписки в UNIBLP UI"):
            self.uniblp_page.open_files_tab()

            redemption_amount = 700.00
            self.files_page.upload_statement(
                file_name="1c_1docs_870031.txt", amount=redemption_amount, remove_file=remove_file_from_download_folder
            )

        with allure.step("Переход в форму 'Документы выписки'"):
            self.files_page.open_file()

        with allure.step("Переход в форму 'Платежи'"):
            self.statements_page.open_statement()

        with allure.step("Переход в форму 'Поиск плательщика'"):
            self.statements_page.search_and_select_payer(test_context.client.agreements[0].accounts[0].number)

        with allure.step("Проверка параметров после выбора клиента"):
            self.statements_page.verify_client_info_after_selection()

        with allure.step("Сохранение платежа"):
            self.statements_page.save_payment_and_verify_fields()

        with allure.step("Поиск непогашенных счетов клиента"):
            self.statements_page.locators.TARGET_POST_PAYS_BTN.wait_to_be_enabled(timeout=15000)
            self.statements_page.locators.TARGET_POST_PAYS_BTN.click()

        with allure.step("Ручное разнесение первого счета"):
            remainder_amount = self.statements_page.manual_post_payment(
                row_index=0, amount=250.00, remainder_amount=redemption_amount
            )

        with allure.step("Ручное разнесение второго счета"):
            self.statements_page.manual_post_payment(row_index=1, amount=450.00, remainder_amount=remainder_amount)

        with allure.step("Сохранение целеуказаний"):
            self.statements_page.save_target_pays()

        with allure.step("Сохранение документа в биллинг"):
            self.statements_page.save_document_to_billing()

        with allure.step("Проверка биллинговых счетов"):
            self.billing_api.wait_for_billing_accounts_status()

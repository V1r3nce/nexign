import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.user import OrganizationClient
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_48 Смена Продуктового Предложения")
@allure.suite("E2E_48_3 Смена основного ПП_1этап")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestChangeProductOfferContract:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, organization_user_data: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.user_data = organization_user_data
        self.client_profile = ClientProfilePage()
        self.client_api = ClientRequests()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.inquiries_page = InquiriesPage()

    @allure.title("Смена продуктового предложения (Договор и ДС. Один продукт изменен)")
    @allure.id(681064)
    @pytest.mark.skip(reason="https://jira.nexign.com/browse/TUDS-5439")
    def test_change_product_offer_contract(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 5000)
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("mobile"))
        self.base_page.open(BASE_URL + f"customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
        self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
        self.client_profile.change_product_offer_with_contract(False)

        self.inquiries_page.locators.ADD_SALE_BTN.wait_to_be_enabled(timeout=40000)  # Идет оформление, загрузка
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.AGREEMENT.wait_to_have_count(1, timeout=45000)
        self.inquiries_page.locators.AGREEMENT[0].click()
        self.inquiries_page.locators.DOWNLOAD_DOCUMENT.wait_to_be_enabled(timeout=20000)

        with allure.step("Скачать документ и дождаться загрузки файла"):
            with self.inquiries_page.page.expect_download() as download_info:
                self.inquiries_page.locators.DOWNLOAD_DOCUMENT.click()
            download = download_info.value
        pdf_file = CheckFile(download.suggested_filename)
        pdf_file.process_downloaded_pdf(download)

    @allure.title("Смена продуктового предложения (Договор и ДС. Один продукт изменен. Один продукт не изменен)")
    @allure.id(678947)
    @pytest.mark.skip(reason="https://jira.nexign.com/browse/TUDS-5439")
    def test_change_one_product_offer_from_several_contract(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 5000)
        products = prepare_inquiries(["mobile", "mobile"], as_list=False)
        self.client_inquiries_api.product_sale(inquiry=products)
        self.base_page.open(BASE_URL + f"customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
        self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
        self.client_profile.change_product_offer_with_contract(False)

        self.inquiries_page.locators.ADD_SALE_BTN.wait_to_be_enabled(timeout=40000)  # Идет оформление, загрузка
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.AGREEMENT.wait_to_have_count(1, timeout=45000)
        self.inquiries_page.locators.AGREEMENT[0].click()
        self.inquiries_page.locators.DOWNLOAD_DOCUMENT.wait_to_be_enabled(timeout=20000)

        with allure.step("Скачать документ и дождаться загрузки файла"):
            with self.inquiries_page.page.expect_download() as download_info:
                self.inquiries_page.locators.DOWNLOAD_DOCUMENT.click()
            download = download_info.value
        pdf_file = CheckFile(download.suggested_filename)
        pdf_file.process_downloaded_pdf(download)

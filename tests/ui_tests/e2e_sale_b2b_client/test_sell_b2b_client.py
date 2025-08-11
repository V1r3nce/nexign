import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientRequests
from common.helpers.checker import assert_that
from models.user import OrganizationClient
from pages.inquiries_page import InquiriesPage
from pages.locators.select_product_offers_form import SelectProductOffersForm


@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
@pytest.mark.regress
class TestSellB2BClient:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_organization: OrganizationClient,
    ) -> None:
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.product_offer = SelectProductOffersForm(nexign_ui_stand_login)
        self.client_request_api = ClientRequests(api_request_auth_context)
        self.client = create_organization
        self.client_request_api.create_linked_person(self.client.user_id, "Тест связанное лицо")

    @allure.title('Продажа "бандл" продукта B2B клиенту с ручным созданием договора и ЛС')
    @allure.id(533492)
    def test_selling_bundle_b2b_product_client_manual_creation_agreement(self, base_url: str) -> None:
        self.inquiries_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.inquiries_page.sale_initialization(create_add_agreement="manual")

        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer.PRODUCT_TYPE.select_by_value("Бандл")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
        self.product_offer.SEARCH_BTN.click()
        self.inquiries_page.choose_product_offer_with_name("Все для бизнеса")
        self.product_offer.ADD_BTN.click()
        # TODO дописать тест после актуализации тест-кейса в аллюре https://jira.nexign.com/browse/TUDS-3795
        assert_that(lambda: False, "Необходимо дописать тест, задача https://jira.nexign.com/browse/TUDS-3795")

    @allure.title('Продажа "моно" продукта B2B клиенту с ручным созданием договора и ЛС')
    @allure.id(539223)
    @pytest.mark.smoke
    def test_selling_mono_b2b_product_client_manual_creation_agreement(self, base_url: str) -> None:
        self.inquiries_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.inquiries_page.sale_initialization(create_add_agreement="manual", priority="Низкий")

        self.inquiries_page.locators.ADD_SALE_BTN.click()

        self.product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
        self.product_offer.PRODUCT_CATEGORY.select_by_value("Интернет")
        self.product_offer.SEARCH_BTN.click()
        self.inquiries_page.choose_product_offer_with_name("Интернет в офис")
        self.product_offer.ADD_BTN.click()
        # TODO дописать тест после актуализации тест-кейса в аллюре https://jira.nexign.com/browse/TUDS-3795
        assert_that(lambda: False, "Необходимо дописать тест, задача https://jira.nexign.com/browse/TUDS-3795")

import allure
import pytest
from playwright.sync_api import Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.user import User
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ChangeMainProductForm
from pages.locators.nbss.finances.payments_elements import ConsumptionElements
from pages.nbss.agreement_page import AgreementPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.payments_page import PaymentsPage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_48 Смена Продуктового Предложения")
@allure.suite("E2E_48 Смена продуктового предложения")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestChangeProductOfferContract:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login: Page,
        organization_user_data: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.client_api = ClientRequests()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.inquiries_page = InquiriesPage()
        self.payments_page = PaymentsPage()
        self.payments_elements = ConsumptionElements()
        self.agreements_page = AgreementPage()
        self.change_product_form = ChangeMainProductForm()

    @allure.title("01. Смена основного продукта (ДС авто, без опций, с изменением цены на новом ПП)")
    @allure.id(743164)
    def test_change_product_offer_with_price_auto(self, create_organization_with_postpaid_account) -> None:
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("satellite_rent"))
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        name_product = self.client_profile.change_product_offer_with_contract(auto_contract=True)

        self.inquiries_page.proceed_to_auto_contract_closure()
        self.inquiries_page.wait_closed_and_check_agreement()
        # self.inquiries_page.download_and_check_agreement_pdf()
        # ToDo Разкомментить строчку, после починки скачивания файлов https://jira.nexign.com/browse/TUDS-5439
        self.base_page.open(
            f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
        )
        self.client_profile.open_personal_agreement()
        self.agreements_page.open_documents_tab_and_check_count(expected_count=2)
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.check_main_product_changed(name_product)
        self.client_profile.open_payments_for_current_account()

        self.payments_page.payment_elements.REFRESH_PAYMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.payment_elements.TAB[1].click()
        self.payments_page.payment_elements.REFRESH_PAYMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.payment_elements.TAB[16].click()
        self.payments_elements.PROFIT_ACTIONS.wait_to_have_count(4, timeout=10000)

    @allure.title("02. Смена основного продукта (ДС вручную, с проверкой тех.возможности)")
    @allure.id(743160)
    def test_change_product_offer_with_price_manual(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 5000)
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("internet"))
        self.base_page.open(BASE_URL + f"customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        name_product = self.client_profile.change_product_offer_with_contract(auto_contract=False)
        self.inquiries_page.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.wait_to_be_enabled(timeout=60000)
        self.inquiries_page.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
        self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible(timeout=60000)
        self.inquiries_page.locators.REFRESH_BTN_INQUIRY.wait_to_be_enabled(timeout=15000)
        self.inquiries_page.locators.REFRESH_BTN_INQUIRY.click()
        self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN.wait_to_be_enabled(timeout=150000)
        self.inquiries_page.go_to_agreement_step()
        self.inquiries_page.locators.AGREEMENT[0].click()  # Эту строчку убрать, когда починят скачивание
        # self.inquiries_page.download_and_check_agreement_pdf()
        # ToDo Разкомментить строчку, после починки скачивания файлов https://jira.nexign.com/browse/TUDS-5439
        self.inquiries_page.approve_agreement()
        self.inquiries_page.wait_closed_and_check_agreement()
        self.base_page.open(
            f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
        )
        self.client_profile.open_personal_agreement()
        self.agreements_page.open_documents_tab_and_check_count(expected_count=2)
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.check_main_product_changed(name_product)
        self.client_profile.open_payments_for_current_account()

        self.payments_page.payment_elements.REFRESH_PAYMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.payment_elements.TAB[1].click()
        self.payments_page.payment_elements.REFRESH_PAYMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.payment_elements.TAB[16].click()
        self.payments_elements.PROFIT_ACTIONS.wait_to_have_count(4, timeout=10000)

    @allure.title("03. Смена основного продукта (есть несовместимые опции, активная заявка на смену)")
    @allure.id(743162)
    @pytest.mark.skip("Будет реализовано после добавления таких ПП в коробку")
    def test_change_offer_with_incompatible_options(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 5000)
        self.client_inquiries_api.product_sale(
            inquiry=prepare_inquiries("internet", additional_product=[["Статический IP", "Безлимит ВК Видео"]])
        )
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        # ToDo Будет дописано после появление таких ПП в коробке https://jira.nexign.com/browse/TUDS-5854

    @allure.title("04. Смена основного продукта (ПП с номенклатурой)")
    @allure.id(743166)
    def test_change_offer_with_nomenclature(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 99999999)
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("satellite_rent"))
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        name_product = self.client_profile.change_product_offer_with_contract(auto_contract=True, product_number=3)

        self.inquiries_page.proceed_to_auto_contract_closure()
        self.inquiries_page.wait_closed_and_check_agreement()
        # self.inquiries_page.download_and_check_agreement_pdf()
        # ToDo Разкомментить строчку, после починки скачивания файлов https://jira.nexign.com/browse/TUDS-5439
        self.base_page.open(
            BASE_URL + f"customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
        )
        self.client_profile.open_personal_agreement()
        self.agreements_page.open_documents_tab_and_check_count(expected_count=3)
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.check_main_product_changed(name_product)
        self.client_profile.open_payments_for_current_account()

        self.payments_page.payment_elements.REFRESH_PAYMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.payment_elements.TAB[1].click()
        self.payments_page.payment_elements.REFRESH_PAYMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.payments_page.payment_elements.TAB[16].click()
        self.payments_elements.PROFIT_ACTIONS.wait_to_have_count(2, timeout=15000)

    @allure.title("05. Смена основного продукта (нет роли)")
    @allure.id(743161)
    @pytest.mark.user(User.FINANCE_TEST)
    def test_change_offer_without_permission(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 5000)
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("mobile"))
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].wait_to_be_enabled()
        self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.client_profile.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
        self.client_profile.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.not_to_be_enabled()

    @allure.title("06. Смена основного продукта (есть активная заявка)")
    @allure.id(743163)
    def test_change_offer_already_application(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 5000)
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("mobile"))
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.change_product_offer_with_contract(auto_contract=False)
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
        self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()

        self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].wait_to_be_enabled()
        self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
        self.client_profile.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
        self.client_profile.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.not_to_be_visible()

    @allure.title("07. Смена основного продукта (нет ПП на замену)")
    @allure.id(743165)
    def test_change_offer_without_other_products(self, organization_user_data) -> None:
        self.client_api.create_client_with_payment(organization_user_data, 99999999)
        self.client_inquiries_api.product_sale(inquiry=prepare_inquiries("fixed_phone"))
        self.base_page.open(BASE_URL + f"customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
        self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
        with allure.step("Инициировать смену продукта"):
            self.client_profile.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")
            self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].wait_to_be_enabled(timeout=20000)
            self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.client_profile.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            self.client_profile.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.click()

        with allure.step("Убедиться, что выбор продуктов для замены пуст"):
            self.change_product_form.SEARCH_BTN.wait_to_be_enabled()
            self.change_product_form.LOTTIE_TEXT.wait_to_have_text("Монопродуктов по заданным фильтрам не найдено")

    @allure.title("08. Смена основного продукта (ПП с отложенной активацией)")
    @allure.id(743159)
    @pytest.mark.skip("Будет реализовано после добавления такого ПП в коробку")
    def test_change_offer_without_activations(self, organization_user_data) -> None:
        pass

    # TODO Дописать кейс после возможности продавать с отложенной активацией https://jira.nexign.com/browse/TUDS-5854

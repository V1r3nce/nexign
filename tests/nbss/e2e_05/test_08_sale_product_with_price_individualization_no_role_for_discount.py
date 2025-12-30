import allure
import pytest
from playwright.sync_api import Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.enums.user import User
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestSaleProductWithPriceIndividualizationNoRoleForDiscount:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        page: Page,
        nexign_stand_login,
    ) -> None:
        self.base_page = BasePage()
        self.page = page
        self.inquiries_page = InquiriesPage()
        self.product_edit_form = ProductEditForm()
        self.client_profile = ClientProfilePage()
        self.inquiry_api = ClientInquiriesRequests()

    @pytest.mark.user(User.SELLER_JR_TEST)
    @allure.title(
        "08. Продажа продуктового предложения с индивидуализацией стоимости абонентской платы (Нет роли для задания скидки)"
    )
    @allure.id(703125)
    @allure.description(
        """
        Проверить, что пользователь с ролью SELLER_JR_TEST не может редактировать скидку на продукт.
        """
    )
    def test_sale_product_no_role_for_discount(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        client = create_organization_with_agreement_and_account

        with allure.step("Подготовка: Создание заявки и добавление продукта через API под Admin"):
            test_context.client = client

            test_context.client.inquiry_list = prepare_inquiries(category="satellite_rent")

            test_context.switch_api_context_to_user(User.ADMIN)

            self.inquiry_api._sale_prepare_and_add_product(need_spd=False, need_create_link_person=True)

            product = test_context.client.inquiry.product
            product.switch_name = "Коммутатор_Спутниковая_связь"
            self.inquiry_api._resources_reserve(product)

            self.inquiry_api._order_check(test_context.client.inquiry.commercial_order_number)
            self.inquiry_api._check_commercial_status()

        with allure.step("Шаг 1: Открытие заявки и переход к форме редактирования продукта"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{client.user_id}/overview")
            self.client_profile.locators.REQUESTS_TAB.wait_to_be_visible(timeout=10000)
            self.client_profile.locators.REQUESTS_TAB.click()
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_be_visible(timeout=10000)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_be_visible(timeout=10000)

            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.TITLE.wait_to_be_visible(timeout=10000)

        with allure.step("Шаг 2: Переход на вкладку 'Цены' и проверка недоступности поля скидки"):
            self.product_edit_form.PRICE_TAB.click()
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.not_to_be_enabled(timeout=5000)

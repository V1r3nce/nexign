import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
@allure.suite("E2E_05 Управление атрибутами продукта/сервиса/ресурса абонента (Индивидуализация цены)")
class TestViewAndSelectProductWithPriceIndividualization:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.client = create_organization_with_agreement_and_account
        self.inquiries_page = InquiriesPage()
        self.client_profile = ClientProfilePage()
        self.inquiry_api = ClientInquiriesRequests()

    @allure.title("01. Просмотр и выбор продуктового предложения с индивидуализацией стоимости")
    @allure.id(660537)
    @allure.description(
        """
        Проверить возможность просмотра и выбора продуктового предложения
        с индивидуализацией стоимости. Продукт с возможностью персонализации
        должен отображаться в заявке на продажу с синей ценой.
        """
    )
    def test_view_and_select_product_with_price_individualization(self) -> None:
        with allure.step("Подготовка: Создание заявки и добавление продукта через API"):
            test_context.client = self.client
            test_context.client.inquiry_list = prepare_inquiries(category="satellite_rent")

            self.inquiry_api._sale_prepare_and_add_product(need_spd=False, need_create_link_person=True)

            product = test_context.client.inquiry.product
            product.switch_name = "Коммутатор_Спутниковая_связь"

            self.inquiry_api._resources_reserve(product)
            self.inquiry_api._order_check(test_context.client.inquiry.commercial_order_number)
            self.inquiry_api._check_commercial_status()

        with allure.step("Шаг 1: Открытие заявки и ожидание загрузки продукта"):
            self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/inquiries")
            self.inquiries_page.locators.LOAD_SPIN_SECOND.not_to_be_visible(timeout=30000)
            self.client_profile.locators.REQUEST_NUMBER.wait_to_have_count(1, timeout=30000)
            self.client_profile.locators.REQUEST_NUMBER[0].click()

            self.inquiries_page.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_be_visible(timeout=10000)

        with allure.step("Шаг 2: Проверка отображения продукта с индивидуализацией и доступности для редактирования"):
            self.inquiries_page.locators.ADDED_PRODUCT_NAMES[0].wait_to_be_visible(timeout=5000)
            self.inquiries_page.locators.ADDED_PRODUCT_NAMES[0].to_contain_text(product.product_name)

            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_NEW_PRICE[0].wait_to_be_visible(timeout=5000)
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_NEW_PRICE[0].element_have_css_color(
                "color", "deep_blue"
            )

            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON.wait_to_have_count(1, timeout=10000)

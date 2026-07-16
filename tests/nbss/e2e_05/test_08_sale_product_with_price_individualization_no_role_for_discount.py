import allure
import pytest

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
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.product_edit_form = ProductEditForm()
        self.client_profile = ClientProfilePage()
        self.inquiry_api = ClientInquiriesRequests()
        self.client = create_organization_with_agreement_and_account

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
    def test_sale_product_no_role_for_discount(self) -> None:
        with allure.step("Подготовка: Создание заявки и добавление продукта через API под Admin"):
            test_context.client.inquiry = prepare_inquiries(category="satellite_rent", as_list=False)
            test_context.switch_api_context_to_user(User.ADMIN)
            self.inquiry_api.sale_prepare_and_add_product(need_spd=False, need_create_link_person=True)

            product = test_context.client.inquiry.product
            product.switch_name = "Коммутатор_Спутниковая_связь"

            self.inquiry_api.resources_reserve(product)
            self.inquiry_api.forward_step_with_check(test_context.client.inquiry.commercial_order_number)
            self.inquiry_api.check_commercial_status()

        with allure.step("Шаг 1: Открытие заявки и переход к форме редактирования продукта"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile.open_requests_tab()
            self.client_profile.open_request()
            self.inquiries_page.open_edit_product_form()

        with allure.step("Шаг 2: Переход на вкладку 'Цены' и проверка недоступности поля скидки"):
            self.inquiries_page.open_price_tab()
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.type("Поле недоступно для заполнения")
            self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_have_text("")

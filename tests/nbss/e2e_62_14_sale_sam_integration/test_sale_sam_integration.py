import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ProductInfoForm, ReplaceResource
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.crab
@allure.suite("E2E_62_14 Продажа B2B (Интеграция с SAM)")
@allure.link(
    "confluence.nexign.com/pages/viewpage.action?pageId=759702532", name="CONF.QF.26 Управление ролевой моделью (группы)"
)
@allure.link(
    "confluence.nexign.com/pages/viewpage.action?pageId=768010781",
    name="E2E_62_14 Продажа клиенту B2B (Интеграция с SAM) (RMBSS-1068)",
)
@allure.link("confluence.nexign.com/pages/viewpage.action?pageId=711544937", name="[NBSS.DS.RM] Ролевая модель")
@allure.link("confluence.nexign.com/pages/viewpage.action?pageId=762889099", name="КР [NBSS] Интеграция с SAM")
class TestSaleSamIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization, create_oms_db_connection):
        self.client_inquiry_api = ClientInquiriesRequests()
        self.oms_db = create_oms_db_connection
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.product_info_form = ProductInfoForm()
        self.replace_resource_form = ReplaceResource()
        self.inquiries_page = InquiriesPage()

    @allure.id(696190)
    @allure.title("Сценарий провиженинга в центральном узле (ServiceActivator) Продажа ПП")
    @allure.link(
        "confluence.nexign.com/pages/viewpage.action?pageId=694456499",
        name="NBSS.DS.CRAB УПК. Подключение сервисов абонента (nbssServiceConnect)",
    )
    def test_sale_sam_integration(self):
        self.client_inquiry_api.product_sale(inquiry=prepare_inquiries("satellite_rent"))
        service_activator_order_id = self.oms_db.get_sam_service_order_id(test_context.client.inquiry.id, "connect")
        assert_that(lambda: service_activator_order_id is not None, "Заказ на активацию продукта не был создан")
        self.oms_db.check_order_success_status(service_activator_order_id)

    @allure.id(696188)
    @allure.title("Сценарий провиженинга в центральном узле (ServiceActivator) Отключение ПП")
    @allure.link(
        "confluence.nexign.com/pages/viewpage.action?pageId=699798607",
        name="NBSS.DS.CRAB УПК. Отключение сервисов абонента (nbssServiceDisconnect)",
    )
    def test_disconnect_sam_integration(self):
        self.client_inquiry_api.product_sale(inquiry=prepare_inquiries("satellite_rent"))
        self.client_inquiry_api.product_disconnect()
        service_activator_order_id = self.oms_db.get_sam_service_order_id(test_context.client.inquiry.id, "disconnect")
        assert_that(lambda: service_activator_order_id is not None, "Заказ на активацию продукта не был создан")
        self.oms_db.check_order_success_status(service_activator_order_id)

    @allure.id(696123)
    @allure.title("Сценарий провиженинга в центральном узле (ServiceActivator) Редактирование ПП")
    @allure.link(
        "confluence.nexign.com/pages/viewpage.action?pageId=694456499",
        name="NBSS.DS.CRAB УПК. Подключение сервисов абонента (nbssServiceConnect)",
    )
    def test_product_edit_sam_integration(self):
        self.client_inquiry_api.product_sale()
        old_number = test_context.client.inquiry.product.phone_number
        replace_number_price = 5000.00
        self.payment_api.create_default_payment(
            test_context.client.agreements[0].accounts[0].id,
            test_context.client.inquiry.product.total_amount + replace_number_price,
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, replace_number_price
        )

        new_number, replace_inquiry_id = self.client_inquiry_api.replace_number(test_context.client.inquiry.product)

        assert_that(lambda: new_number != old_number, "Номер не был изменен")
        service_activator_order_id = self.oms_db.get_sam_service_order_id(replace_inquiry_id, "change")
        assert_that(lambda: service_activator_order_id is not None, "Заказ на замену номера не был создан")
        self.oms_db.check_order_success_status(service_activator_order_id)

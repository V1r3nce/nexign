import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.checker import assert_that
from models.context import test_context
from models.inquiry import prepare_inquiries


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
    def setup(self, nexign_ui_stand_login, create_organization, create_oms_db_connection):
        self.client_inquiry_api = ClientInquiriesRequests()
        self.oms_db = create_oms_db_connection

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

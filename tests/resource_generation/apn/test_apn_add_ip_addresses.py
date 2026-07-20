import allure
import pytest
from allure_commons.types import AttachmentType

from api.lis_requests.apn import APNRequests
from api.lis_requests.ip_addresses import IpAddressRequests
from models.stand_context import stand_context


class TestAPNAddIpAddresses:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login):
        self.ip_api = IpAddressRequests()
        self.apn_api = APNRequests()

    @allure.step("Генерация IP адресов на APN")
    def test_apn_add_ip_addresses(self):
        if stand_context.stand_equipment.default_apn is not None:
            self.ip_api.generate_ip_addresses_for_apn(
                stand_context.stand_equipment.default_apn, stand_context.generate_ips_count
            )
        else:
            allure.attach(
                "Пропуск генерации IP адресов для дефолтной APN в связи с ее отсутствием",
                name="Skip default APN IP generation",
                attachment_type=AttachmentType.TEXT,
            )

    @allure.step("Создание APN и генерация IP адресов")
    def test_create_apn_add_ip_addresses(self):
        for i in range(stand_context.generate_apns_count):
            apn = self.apn_api.add_apn()
            self.ip_api.generate_ip_addresses_for_apn(apn, stand_context.generate_ips_count)

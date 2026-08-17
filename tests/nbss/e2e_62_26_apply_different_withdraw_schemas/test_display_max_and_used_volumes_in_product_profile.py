import random

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from api.nwm_requests.nwm_requests import NwmRequests, TrafficType
from api.psc_requests.offerings_requests import ProductOfferingRequests
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
class TestDisplayMaxAndUsedVolumesInProductProfile:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization: OrganizationClient,
    ) -> None:
        self.inquiries_page = InquiriesPage()
        self.client_profile = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()

        self.client_inquiries_requests = ClientInquiriesRequests()
        self.nwm_requests = NwmRequests()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.psc_requests = ProductOfferingRequests()

        self.client = create_organization
        self.product_category = "mobile"

        self.internet_volume = self.psc_requests.get_product_offering_volume(B2BProducts.mobile_business, "Интернет")
        self.minutes_volume = self.psc_requests.get_product_offering_volume(B2BProducts.mobile_business, "Минуты")
        self.sms_volume = self.psc_requests.get_product_offering_volume(B2BProducts.mobile_business, "SMS")
        self.used_volume = random.randint(1, self.internet_volume - 1)

    @allure.title("01. Отображение максимального и потребленного объема в продуктовом профиле")
    @allure.id(844910)
    def test_display_max_and_used_volumes_in_product_profile(self) -> None:
        inquiry = prepare_inquiries(
            category=self.product_category, product_offering_id=B2BProducts.mobile_business, as_list=False
        )

        with allure.step("Подготовка: продажа продукта и оплата"):
            self.client_inquiries_requests.product_sale(inquiry=inquiry)
            payment_amount = inquiry.product.one_time_payment + inquiry.product.subscription_fee
            self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, payment_amount)
            self.personal_account_api.wait_accruals(test_context.client.user_id)

        with allure.step("Проверка объемов на странице продуктов до тарификации"):
            self.client_product_profile.open_products_page_and_check(
                user_id=self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=False
            )
            self.client_product_profile.check_product_volumes(
                [self.minutes_volume, self.internet_volume, self.sms_volume],
                [self.minutes_volume, self.internet_volume, self.sms_volume],
            )

        with allure.step("Проверка объемов в сайдбаре продукта до тарификации"):
            self.client_product_profile.click_first_product(
                test_context.client.inquiry.product.phone_number, test_context.client.inquiry.product.product_name
            )
            self.client_product_profile.check_product_volumes(
                [self.minutes_volume, self.internet_volume, self.sms_volume],
                [self.minutes_volume, self.internet_volume, self.sms_volume],
            )

        with allure.step("Генерация тарификации и ожидание начислений"):
            self.nwm_requests.generate_charge(inquiry.product.subs_id, self.used_volume, TrafficType.MOBILE_INTERNET)

        with allure.step("Проверка объемов на странице продуктов после тарификации"):
            self.client_product_profile.open_products_page_and_check(
                user_id=self.client.user_id, product_list=test_context.client.inquiry.product_list, is_activated=False
            )
            self.client_product_profile.check_product_volumes(
                [self.minutes_volume, self.internet_volume - self.used_volume, self.sms_volume],
                [self.minutes_volume, self.internet_volume, self.sms_volume],
            )

        with allure.step("Проверка объемов в сайдбаре продукта после тарификации"):
            self.client_product_profile.click_first_product(
                test_context.client.inquiry.product.phone_number, test_context.client.inquiry.product.product_name
            )
            self.client_product_profile.check_product_volumes(
                expected_volumes=[self.minutes_volume, self.internet_volume - self.used_volume, self.sms_volume],
                expected_max_volumes=[self.minutes_volume, self.internet_volume, self.sms_volume],
            )

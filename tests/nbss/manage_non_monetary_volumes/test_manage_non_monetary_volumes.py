import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.inquiry_requests import AppealRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from models.client import IndividualClient
from models.context import test_context
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.consumption_page import ConsumptionPage


@allure.suite("E2E_28 Управление немонетарными объемами (витрина объемов)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestManageNonMonetaryVolumes:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_individual_user: IndividualClient) -> None:
        self.client_requests = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.inquiry_api = AppealRequests()
        self.client_profile = ClientProfilePage()
        self.consumption_page = ConsumptionPage()

        self.inquiry = self.client_requests.product_sale()
        balance = 100.00
        self.payment_api.create_default_payment(
            test_context.client.agreements[0].accounts[0].id,
            self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee + balance,
        )
        self.personal_account_api.wait_check_current_main_balance(
            test_context.client.agreements[0].accounts[0].id, balance
        )
        self.personal_account_api.wait_accruals(test_context.client.user_id)
        subscription_id = self.personal_account_api.get_client_subscriptions(test_context.client.user_id).json()[
            "items"
        ][0]["subscriptionId"]
        self.internet_volume, self.call_volume, self.sms_volume = 10240, 100, 100
        self.used_internet, self.used_call, self.used_sms = 15, 5, 2
        self.inquiry_api.generate_traffic(
            test_context.client.user_id,
            test_context.client.agreements[0].accounts[0].id,
            subscription_id,
            "internet",
            self.used_internet,
        )
        self.inquiry_api.generate_traffic(
            test_context.client.user_id,
            test_context.client.agreements[0].accounts[0].id,
            subscription_id,
            "calls",
            self.used_call * 60,
        )
        self.inquiry_api.generate_traffic(
            test_context.client.user_id,
            test_context.client.agreements[0].accounts[0].id,
            subscription_id,
            "SMS",
            self.used_sms,
        )
        self.personal_account_api.wait_subscription_calls(
            test_context.client.agreements[0].accounts[0].id, subscription_id, 4
        )

    @allure.title("1. Просмотр объемов на витрине")
    @allure.id(647182)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=767218609",
        name="CLM-477550 - Витрины потребления: отображение объемов на CSM (целевое решение)",
    )
    def test_view_volumes_on_the_showcase(self, base_url: str):
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
        )

        with allure.step("Перейти в 'Продукты'"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_have_count(1)

        with allure.step("Перейти к деталям потребления"):
            self.client_profile.locators.PRODUCT_LIMIT.wait_to_be_visible(timeout=10000)
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.click(force=True)
            self.client_profile.locators.PRODUCTS_DETAILS_BTN.click()
            self.consumption_page.locators.PAGE_TITLE.wait_to_have_text("Потребление")
            self.consumption_page.locators.SUBSCRIBER_NUM.wait_to_have_count(1)
            self.consumption_page.locators.SUBSCRIBER_NUM[0].wait_to_have_text(self.inquiry.product.phone_number)

        with allure.step("Перейти на вкладку 'Объемы'"):
            self.consumption_page.click_tab("Объемы")
            self.consumption_page.locators.VOLUME.wait_to_have_count(3)
            self.consumption_page.check_volume(
                name="Интернет",
                volume_remaining=self.internet_volume - self.used_internet,
                volume_issued=self.internet_volume,
                product=self.inquiry.product.product_name,
                check_more_info=True,
                volume_used=self.used_internet,
            )
            self.consumption_page.check_volume(
                volume_index=1,
                name="Минуты",
                volume_remaining=self.call_volume - self.used_call,
                volume_issued=self.call_volume,
                product=self.inquiry.product.product_name,
                check_more_info=True,
                volume_used=self.used_call,
            )
            self.consumption_page.check_volume(
                volume_index=2,
                name="SMS",
                volume_remaining=self.sms_volume - self.used_sms,
                volume_issued=self.sms_volume,
                product=self.inquiry.product.product_name,
                check_more_info=True,
                volume_used=self.used_sms,
            )

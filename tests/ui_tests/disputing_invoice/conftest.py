import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.exceptions import CreatePaymentException, GetBillingException
from api.requests.billing_requests import BillingRequests
from api.requests.inquiry_requests import InquiryRequests, InquiryInfo, CustomProperty, ForwardInfo
from api.requests.payments_requests import PaymentsRequests, PaymentInfo
from common.helpers.checker import wait_that
from tests.ui_tests.conftest import ClientInfo


@pytest.fixture(scope="function")
def create_client_with_billing_and_claim(create_user_with_agreement_and_account: ClientInfo,
                                         api_request_auth_context: APIRequestContext):
    payment_api = PaymentsRequests(api_request_auth_context)
    inquiry_api = InquiryRequests(api_request_auth_context)
    billing_api = BillingRequests(api_request_auth_context)
    client = create_user_with_agreement_and_account

    with allure.step(f"Добавление платежа для ЛС: {client.account_id}"):
        payment_data = PaymentInfo(item_type="CUSTOMER_ACCOUNT", amount=100, currency_code="RUB",
                                   account_id=client.account_id, payment_method_type="CASH")
        wait_that(
            lambda: len(payment_api.check_create_payment(payment_data).json()["conflicts"]) == 0,
            timeout=10, sleep_seconds=0.5, message="При создании платежа возникнет ошибка",
            exception=CreatePaymentException
        )
        payment_api.create_payment(payment_data)
        wait_that(lambda: payment_api.get_payments(client.account_id, "-paymentDate").json()["items"][0][
                              "status"]["code"] == "SUCCEEDED", exception=CreatePaymentException,
                  timeout=25, sleep_seconds=0.5, message="Платеж не появился в указанное время")

    with allure.step(f"Проведение биллинга для ЛС: {client.account_id}"):
        billing_profile_id = billing_api.get_billing_profile_id(client.account_id)
        billing_api.run_unscheduled_billing(billing_profile_id)
        end_period_start = "2000-01-01T00:00:00.000"
        end_period_end = "3000-01-01T00:00:00.000"
        wait_that(
            lambda: len(billing_api.get_billing_profile_runs(
                billing_profile_id, end_period_datetime_range_start=end_period_start,
                end_period_datetime_range_end=end_period_end)) > 0, exception=GetBillingException,
            timeout=10, sleep_seconds=0.5, message="Биллинг не появился в указанное время")
        wait_that(
            lambda: billing_api.get_billing_profile_runs(
                billing_profile_id, end_period_datetime_range_start=end_period_start,
                end_period_datetime_range_end=end_period_end)[0]["billingTask"]["status"]["billingTaskStatusId"] == 3,
            timeout=40, sleep_seconds=0.5, exception=GetBillingException,
            message="Биллинг не завершился в указанное время")

    with allure.step(f"Создание заявки для клиента: {client.user_id}"):
        inquiry_id = inquiry_api.create_inquiry(InquiryInfo(
            customer_id=client.user_id,
            custom_property=[CustomProperty(
                custom_property_declaration_code="inqrLinkedPerson",
                custom_property_declaration_id=426,
                custom_property_type="DICTIONARY",
                custom_property_values=[]
            )],
            topic_id=36
        ))
        inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=140, queue_id=21))
    return client.account_id, inquiry_id

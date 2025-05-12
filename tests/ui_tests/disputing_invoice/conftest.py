import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.requests.billing_requests import BillingRequests
from api.requests.client_requests import ClientInfo
from api.requests.inquiry_requests import CustomProperty, ForwardInfo, InquiryInfo, InquiryRequests
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from common.helpers.data_generator import generate_random_number


@pytest.fixture(scope="function")
def create_client_with_billing_and_claim(
    create_user_with_agreement_and_account: ClientInfo, api_request_auth_context: APIRequestContext
) -> tuple:
    payment_api = PaymentsRequests(api_request_auth_context)
    inquiry_api = InquiryRequests(api_request_auth_context)
    billing_api = BillingRequests(api_request_auth_context)
    client = create_user_with_agreement_and_account

    with allure.step(f"Добавление платежа для ЛС: {client.account_id}"):
        payment_data = PaymentInfo(
            item_type="CUSTOMER_ACCOUNT",
            amount=100,
            currency_code="RUB",
            account_id=client.account_id,
            document_number=generate_random_number(4),
            payment_method_type="CASH",
        )
        payment_api.wait_check_create_payment(payment_data)
        payment_api.create_payment(payment_data)
        payment_api.wait_last_payment_successful(client.account_id)

    with allure.step(f"Проведение биллинга для ЛС: {client.account_id}"):
        billing_profile_id = billing_api.get_billing_profile_id(client.account_id)
        billing_api.run_unscheduled_billing(billing_profile_id)
        billing_api.wait_billing(billing_profile_id)
        billing_api.wait_finish_billing(billing_profile_id, 3)

    with allure.step(f"Создание заявки для клиента: {client.user_id}"):
        inquiry_id = inquiry_api.create_inquiry(
            InquiryInfo(
                customer_id=client.user_id,
                custom_property=[
                    CustomProperty(
                        custom_property_declaration_code="inqrLinkedPerson",
                        custom_property_declaration_id=426,
                        custom_property_type="DICTIONARY",
                        custom_property_values=[],
                    )
                ],
                topic_id=36,
            )
        )
        inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=277, queue_id=21))
    return client.account_id, inquiry_id, billing_profile_id

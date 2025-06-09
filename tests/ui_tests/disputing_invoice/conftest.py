import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.requests.billing_requests import BillingRequests
from api.requests.inquiry_requests import CustomProperty, ForwardInfo, InquiryInfo, InquiryRequests
from api.requests.payments_requests import PaymentsRequests
from models.user import IndividualClient


@pytest.fixture(scope="function")
def create_client_with_billing_and_claim(
    create_user_with_agreement_and_account: IndividualClient, api_request_auth_context: APIRequestContext
) -> tuple:
    payment_api = PaymentsRequests(api_request_auth_context)
    inquiry_api = InquiryRequests(api_request_auth_context)
    billing_api = BillingRequests(api_request_auth_context)
    client = create_user_with_agreement_and_account

    payment_api.create_default_payment(client.account_id, 100)

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

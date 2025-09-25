import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.inquiry_requests import InquiryRequests
from models.user import IndividualClient


@pytest.fixture(scope="function")
def create_client_with_billing_and_claim(
    create_user_with_agreement_and_account: IndividualClient, api_request_auth_context: APIRequestContext
) -> tuple:
    payment_api = PaymentsRequests(api_request_auth_context)
    inquiry_api = InquiryRequests(api_request_auth_context)
    billing_api = BillingRequests(api_request_auth_context)
    client = create_user_with_agreement_and_account

    payment_api.create_default_payment(client.agreements[0].accounts[0].id, 100)

    with allure.step(f"Проведение биллинга для ЛС: {client.agreements[0].accounts[0].id}"):
        billing_profile_id = billing_api.get_billing_profile_id(client.agreements[0].accounts[0].id)
        billing_api.run_unscheduled_billing(billing_profile_id)
        billing_api.wait_billing(billing_profile_id)
        billing_api.wait_finish_billing(billing_profile_id, 3)

    inquiry_id = inquiry_api.claim_not_agree_with_calculation(client.user_id)
    return client.agreements[0].accounts[0].id, inquiry_id, billing_profile_id

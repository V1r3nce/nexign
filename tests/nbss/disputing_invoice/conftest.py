import allure
import pytest

from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.inquiry_requests.inquiry_requests import InquiriesRequests
from models.client import IndividualClient
from models.context import test_context


@pytest.fixture(scope="function")
def create_client_with_billing_and_claim(create_user_with_agreement_and_account: IndividualClient) -> tuple:
    payment_api = PaymentsRequests()
    inquiry_api = InquiriesRequests()
    billing_api = BillingRequests()
    client = create_user_with_agreement_and_account

    payment_api.create_default_payment(client.agreements[0].accounts[0].id, 100)

    with allure.step(f"Проведение биллинга для ЛС: {test_context.client.agreement.account.id}"):
        bill = billing_api.execute_unscheduled_billing_and_wait_completion(client.agreement.account.id)

    inquiry_id = inquiry_api.claim_not_agree_with_calculation(client.user_id)
    return client.agreements[0].accounts[0].id, inquiry_id, bill

import allure
import pytest


@pytest.mark.regress
@pytest.mark.nbss_portal
class TestBillingObjectsSelection:
    @pytest.fixture(autouse=True)
    def setup(self, create_organization_with_agreement_and_account) -> None:
        self.page = None

    @allure.title("01. Проверка учета платежей в пределах текущего биллингового периода")
    @allure.id(946234)
    def test_billing_payment_selection(self):
        pass

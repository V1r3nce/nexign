import random
import re

import allure
import pytest

from common.helpers.string_helper import check_price
from models.client import IndividualClient
from models.context import test_context
from pages.locators.nbss.dynamic_form_elements import PersonalAccountForm
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_53 Управление кредитным порогом клиента (Экстра)")
@allure.suite("E2E_53 Управление кредитным порогом клиента (Экстра)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestEditPersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_user_with_postpaid_account: IndividualClient) -> None:
        self.personal_account_page = PersonalAccountPage()
        self.personal_account_form = PersonalAccountForm()
        self.client = create_user_with_postpaid_account
        self.deactivation_threshold = "2000"

    @allure.title("Редактирование ЛС с постоплатным способом оплаты")
    @allure.id(540288)
    def test_edit_personal_account_with_postpaid_payment_method(self, base_url: str) -> None:
        new_deactivation_threshold = str(random.randint(0, 100000))
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_have_text("Редактирование лицевого счёта")
        self.personal_account_form.PAYMENT_METHOD.wait_to_have_text("Постоплатный")
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.to_have_class(
            re.compile(r"ant\d*-checkbox-wrapper-checked")
        )
        check_price(self.personal_account_form.THRESHOLD_CONTROL_FLD, float(self.deactivation_threshold), False)

        self.personal_account_form.THRESHOLD_CONTROL_FLD.fill(new_deactivation_threshold)
        self.personal_account_form.SAVE_BTN.click()

        self.personal_account_page.locators.INFO_MESSAGE.wait_to_have_text("Данные лицевого счёта обновлены")
        self.personal_account_page.check_personal_account_data(
            payment_method="Постоплатный",
            threshold_control="Да",
            threshold_break=new_deactivation_threshold,
        )

    @allure.title("Отмена редактирования ЛС с постоплатным способом оплаты")
    @allure.id(539963)
    def test_cancel_edit_personal_account_with_postpaid_payment_method(self, base_url: str) -> None:
        new_deactivation_threshold = str(random.randint(0, 100000))
        self.personal_account_page.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
        self.personal_account_form.TITLE.wait_to_have_text("Редактирование лицевого счёта")
        self.personal_account_form.PAYMENT_METHOD.wait_to_have_text("Постоплатный")
        self.personal_account_form.THRESHOLD_CONTROL_CHECKBOX.to_have_class(
            re.compile(r"ant\d*-checkbox-wrapper-checked")
        )
        check_price(self.personal_account_form.THRESHOLD_CONTROL_FLD, float(self.deactivation_threshold), False)

        self.personal_account_form.THRESHOLD_CONTROL_FLD.fill(new_deactivation_threshold)
        self.personal_account_form.CANCEL_BTN.click()

        self.personal_account_form.TITLE.not_to_be_visible()
        self.personal_account_page.check_personal_account_data(
            payment_method="Постоплатный",
            threshold_control="Да",
            threshold_break=self.deactivation_threshold,
        )

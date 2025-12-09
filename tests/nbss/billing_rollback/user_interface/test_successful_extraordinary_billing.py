import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.inquiry_requests import AppealRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import get_datetime_from_full_time_string
from models.context import test_context
from models.user import IndividualClient
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.billing_accounts_page import BillingAccountsPage
from pages.nbss.finances.consumption_page import ConsumptionPage
from tests.conftest import CreatedImsis


@allure.suite("E2E_85 Откат биллинга")
@allure.link(url="jira.nexign.com/browse/TUDS-2569", name="TUDS-2569")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=555189386", name="Откат биллинга по клиенту")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.bia
class TestSuccessfulExtraordinaryBilling:
    @pytest.fixture(autouse=True)
    def setup(
        self, nexign_stand_login, create_individual_user: IndividualClient, add_two_imsi_free_shipped: CreatedImsis
    ):
        self.client_profile = ClientProfilePage()
        self.consumption_page = ConsumptionPage()
        self.billing_accounts_page = BillingAccountsPage()
        self.client_api = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()
        self.inquiry_api = AppealRequests()

        self.client = create_individual_user
        self.inquiry = self.client_api.product_sale(self.client)
        balance = 100.00
        self.payment_api.create_default_payment(
            test_context.client.agreements[0].accounts[0].id,
            self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee + balance,
        )
        self.personal_account_api.wait_accruals(test_context.client.user_id)

        subscription_id = self.personal_account_api.get_client_subscriptions(test_context.client.user_id).json()[
            "items"
        ][0]["subscriptionId"]
        self.inquiry_api.generate_traffic(
            test_context.client.user_id, test_context.client.agreements[0].accounts[0].id, subscription_id, "calls", 300
        )
        self.inquiry_api.generate_traffic(
            test_context.client.user_id, test_context.client.agreements[0].accounts[0].id, subscription_id, "SMS", 5
        )
        self.inquiry_api.generate_traffic(
            test_context.client.user_id,
            test_context.client.agreements[0].accounts[0].id,
            subscription_id,
            "internet",
            15,
        )
        self.personal_account_api.wait_subscription_calls(
            test_context.client.agreements[0].accounts[0].id, subscription_id, 7
        )

        self.billing_profile_id = self.billing_api.get_billing_profile_id(
            test_context.client.agreements[0].accounts[0].id
        )
        self.billing_api.run_unscheduled_billing(self.billing_profile_id)
        self.billing_api.wait_billing(self.billing_profile_id)
        self.billing_api.wait_finish_billing(self.billing_profile_id, 3)
        bill_data = self.billing_api.get_list_of_bills([self.billing_profile_id])[0]
        self.bill_number = bill_data["billNumber"]
        self.bill_date = get_datetime_from_full_time_string(bill_data["currentDebitInfo"]["paidDate"], True).strftime(
            "%d.%m.%Y %H:%M:%S"
        )

    @allure.title("Успешный откат внеочередного биллинга")
    @allure.id(576807)
    @allure.description("Сценарий успешного отката биллинга из пользовательского интерфейса")
    def test_successful_extraordinary_billing(self, create_individual_user: IndividualClient, base_url: str):
        with allure.step('Перейти на форму "Потребление" и выбрать абонента'):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.locators.SUBSCRIBER_NUM[0].to_contain_text(self.inquiry.product.phone_number)
            self.consumption_page.click_tab("Объемы")
            self.consumption_page.check_volume(0, volume_remaining=10225, volume_issued=10240)
            self.consumption_page.check_volume(1, volume_remaining=95, volume_issued=100)
            self.consumption_page.check_volume(2, volume_remaining=95, volume_issued=100)
            self.consumption_page.locators.TAB.wait_for_text_in_all(["Объемы"])
            self.consumption_page.locators.TAB.wait_for_text_in_all(["Трафик"])
            self.consumption_page.locators.TAB.wait_for_text_in_all(["Начисления"])

        with allure.step('Перейти на вкладку "Начисления" и включить отображение данных о биллинге'):
            self.consumption_page.click_tab("Начисления")
            self.consumption_page.locators.MORE_ACTIONS_BTN.click()
            self.consumption_page.locators.SWITCH_SHOW_BILLING.click()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST.wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[18].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[19].wait_to_have_text("Дата выставления счета")
            self.consumption_page.locators.ACCRUAL_LOADER.not_to_be_visible()
            self.consumption_page.locators.CHARGES_BILLING_NUM_LIST.to_contain_text_in_all(self.bill_number)
            self.consumption_page.locators.CHARGES_INVOICE_DATE_LIST.to_contain_text_in_all(self.bill_date)

        with allure.step('Перейти на вкладку "Трафик" и включить отображение данных о биллинге'):
            self.consumption_page.click_tab("Трафик")
            self.consumption_page.locators.SWITCH_BTN_LIST.click(0)
            self.consumption_page.locators.SWITCH_BTN_LIST.click(1)
            self.consumption_page.locators.TRAFFIC_TITLE_LIST.wait_to_be_visible()
            self.consumption_page.locators.TRAFFIC_TITLE_LIST[27].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.TRAFFIC_TITLE_LIST[28].wait_to_have_text("Дата выставления счета абоненту")
            self.consumption_page.locators.TRAFFIC_LOADER.not_to_be_visible()
            self.consumption_page.locators.TRAFFIC_BILLING_NUM_LIST.to_contain_text_in_all(self.bill_number)
            self.consumption_page.locators.TRAFFIC_INVOICE_DATE_LIST.to_contain_text_in_all(self.bill_date)

        with allure.step('Перейти на форму "Биллинговые счета" и открыть последний биллинговый счёт'):
            self.consumption_page.click_tab("Биллинговые счета")
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Выполнить"'):
            self.billing_accounts_page.locators.BILLING_BTNS.click(0)
            self.billing_accounts_page.locators.MODAL.wait_to_be_visible()
            rollback_modal_text = re.compile(
                r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}."
                r"Количество счетов: 1"
            )
            self.billing_accounts_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(rollback_modal_text)
            self.billing_accounts_page.locators.MODAL_SECOND_BTN.click()
            self.billing_accounts_page.locators.MODAL.wait_not_to_be_visible()
            rollback_popup_text = re.compile(
                rf"Запущен откат внеочередного биллинга от \d{{2}}\.\d{{2}}\.\d{{4}} \d{{2}}:\d{{2}}:\d{{2}} по лицевому счету: {self.client.agreements[0].accounts[0].number} Задание: \d{{4}}-\d{{12}}-\d{{2}}"
            )
            self.billing_accounts_page.locators.INFO_MESSAGE[0].wait_to_have_text("Формируется заявка на откат")
            self.billing_accounts_page.locators.INFO_MESSAGE.wait_elements_visible(1)
            self.billing_accounts_page.locators.INFO_MESSAGE[-1].wait_to_have_text(rollback_popup_text)
            self.billing_api.wait_billing(self.billing_profile_id, 2)
            self.billing_api.wait_finish_billing(self.billing_profile_id, 3)

        with allure.step(
            'Нажать кнопку "Список заданий биллинга" и после проверки закрыть список заданий биллинга и нажать кнопку "Обновить"'
        ):
            self.billing_accounts_page.locators.BILLING_TASKS_BTN.click()
            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_to_have_count(2)
            self.billing_accounts_page.check_billing_task(task_type="Биллинг", status="Завершено или откачено")
            self.billing_accounts_page.check_billing_task(task_index=1, task_type="Откат биллинга", status="Завершено")
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()
            self.billing_accounts_page.locators.REFRESH_BTN.click()
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(0)

        with allure.step('Перейти на форму "Потребление" и выбрать абонента'):
            self.billing_accounts_page.click_tab("Потребление")
            self.consumption_page.locators.SUBSCRIBER_NUM.click(0)

        with allure.step('Перейти на вкладку "Начисления" и включить отображение данных о биллинге'):
            self.consumption_page.click_tab("Начисления")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST.wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[18].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[19].wait_to_have_text("Дата выставления счета")
            self.consumption_page.locators.ACCRUAL_LOADER.not_to_be_visible()
            self.consumption_page.locators.CHARGES_BILLING_NUM_LIST.to_contain_text_in_all("—")
            self.consumption_page.locators.CHARGES_INVOICE_DATE_LIST.to_contain_text_in_all("—")

        with allure.step('Перейти на вкладку "Трафик" и включить отображение данных о биллинге'):
            self.consumption_page.click_tab("Трафик")
            self.consumption_page.locators.TRAFFIC_TITLE_LIST.wait_to_be_visible()
            self.consumption_page.locators.TRAFFIC_TITLE_LIST[27].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.TRAFFIC_TITLE_LIST[28].wait_to_have_text("Дата выставления счета абоненту")
            self.consumption_page.locators.TRAFFIC_LOADER.not_to_be_visible()
            self.consumption_page.locators.TRAFFIC_BILLING_NUM_LIST.to_contain_text_in_all("—")
            self.consumption_page.locators.TRAFFIC_INVOICE_DATE_LIST.to_contain_text_in_all("—")

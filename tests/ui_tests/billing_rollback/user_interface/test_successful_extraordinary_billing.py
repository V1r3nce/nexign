import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.billing_requests import BillingRequests
from api.requests.inquiry_requests import CustomProperty, ForwardInfo, InquiryInfo, InquiryRequests
from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.time_helpers import delay
from models.user import IndividualClient
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.consumption_page import ConsumptionPage
from pages.inquiries_page import InquiriesPage


@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestSuccessfulExtraordinaryBilling:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext):
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)

        self.inquiry_api = InquiryRequests(api_request_auth_context)
        self.consumption_page = ConsumptionPage(page)
        self.billing_accounts_page = BillingAccountsPage(page)

    @allure.suite("E2E_85 Откат биллинга")
    @allure.title("Успешный откат внеочередного биллинга")
    @allure.id(576807)
    @allure.description("Сценарий успешного отката биллинга из пользовательского интерфейса")
    @allure.link(url="jira.nexign.com/browse/TUDS-2569", name="TUDS-2569")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=555189386", name="Откат биллинга по клиенту")
    @pytest.mark.regress
    def test_successful_extraordinary_billing(self, page: Page, create_individual_user: IndividualClient, base_url: str):
        with allure.step("Проведение продажи и начисление платежа клиенту"):
            user_id = create_individual_user.user_id
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
            delay(2, "Подрузка контекста для дальнейшей продажи")
            product = self.inquiries_page.sale_phone_number()
            account_id = self.personal_account_api.get_personal_accounts("customer", user_id).json()["items"][0][
                "accountId"
            ]
            subscription_id = self.personal_account_api.get_client_subscriptions(user_id).json()["items"][0][
                "subscriptionId"
            ]
            replace_number_price = 100.00
            payment_data = PaymentInfo(
                item_type="CUSTOMER_ACCOUNT",
                amount=product.one_time_payment + product.subscription_fee + replace_number_price,
                currency_code="RUB",
                account_id=account_id,
                payment_method_type="CASH",
            )
            self.payment_api.create_payment(payment_data)

        with allure.step("Генерация трафика"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/products")
            self.client_profile.locators.SUBSCRIBER.wait_to_be_visible()
            phone_num = self.client_profile.locators.SUBSCRIBER.text
            account_num = self.client_profile.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM.text

        with allure.step(f"Генерация траффика 'Звонки' для клиента: {user_id}"):
            inquiry_id = self.inquiry_api.create_inquiry(
                InquiryInfo(
                    customer_id=user_id,
                    custom_property=[
                        CustomProperty(
                            custom_property_declaration_code="spdAccount",
                            custom_property_declaration_id=415,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": account_id}],
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedAmountMin",
                            custom_property_declaration_id="418",
                            custom_property_type="STRING",
                            custom_property_values="300",
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedSubscriber",
                            custom_property_declaration_id=419,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": subscription_id}],
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedServiceType",
                            custom_property_declaration_id=420,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": "1"}],
                        ),
                    ],
                    topic_id=39,
                )
            )
            self.inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=113, queue_id=1))
        with allure.step(f"Генерация траффика 'SMS' для клиента: {user_id}"):
            inquiry_id = self.inquiry_api.create_inquiry(
                InquiryInfo(
                    customer_id=user_id,
                    custom_property=[
                        CustomProperty(
                            custom_property_declaration_code="spdAccount",
                            custom_property_declaration_id=415,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": account_id}],
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedAmountSms",
                            custom_property_declaration_id="416",
                            custom_property_type="STRING",
                            custom_property_values="5",
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedSubscriber",
                            custom_property_declaration_id=419,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": subscription_id}],
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedServiceType",
                            custom_property_declaration_id=420,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": "2"}],
                        ),
                    ],
                    topic_id=39,
                )
            )
            self.inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=113, queue_id=1))
        with allure.step(f"Генерация траффика 'Интернет' для клиента: {user_id}"):
            inquiry_id = self.inquiry_api.create_inquiry(
                InquiryInfo(
                    customer_id=user_id,
                    custom_property=[
                        CustomProperty(
                            custom_property_declaration_code="spdAccount",
                            custom_property_declaration_id=415,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": account_id}],
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedAmountMb",
                            custom_property_declaration_id="417",
                            custom_property_type="STRING",
                            custom_property_values="15",
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedSubscriber",
                            custom_property_declaration_id=419,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": subscription_id}],
                        ),
                        CustomProperty(
                            custom_property_declaration_code="tedServiceType",
                            custom_property_declaration_id=420,
                            custom_property_type="DICTIONARY",
                            custom_property_values=[{"itemCode": "3"}],
                        ),
                    ],
                    topic_id=39,
                )
            )
            self.inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=113, queue_id=1))

        with allure.step(f"Проведение биллинга для ЛС: {account_id}"):
            self.personal_account_api.wait_accruals(subscription_id)
            billing_profile_id = self.billing_api.get_billing_profile_id(account_id)
            self.billing_api.run_unscheduled_billing(billing_profile_id)
            self.billing_api.wait_billing(billing_profile_id)
            self.billing_api.wait_finish_billing(billing_profile_id, 3)

        with allure.step('Перейти на форму "Потребление" и выбрать абонента'):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/products")
            self.client_profile.locators.SUBSCRIBER.wait_to_be_visible()
            account_num = self.client_profile.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM.text

            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{account_id}/account")
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.locators.SUBSCRIBER_NUM[0].to_contain_text(phone_num)
            self.consumption_page.locators.TABS_LIST[0].click()
            self.consumption_page.locators.TABS_LIST[0].to_have_class(class_name=re.compile(r"ant-tabs-tab-active"))
            self.consumption_page.locators.REMAINING_VOLUMES_LIST[0].wait_to_have_text(
                re.compile(r"10\s225\sиз\s10\s240")
            )
            self.consumption_page.locators.REMAINING_VOLUMES_LIST[1].wait_to_have_text(re.compile(r"90\sиз\s100"))
            self.consumption_page.locators.REMAINING_VOLUMES_LIST[2].wait_to_have_text(re.compile(r"95\sиз\s100"))
            self.consumption_page.locators.TABS_LIST[1].wait_to_be_visible()
            self.consumption_page.locators.TABS_LIST[2].wait_to_be_visible()

        with allure.step('Перейти на вкладку "Начисления" и включить отображение данных о биллинге'):
            self.consumption_page.locators.TABS_LIST[2].click()
            self.consumption_page.locators.TABS_LIST[2].to_have_class(class_name=re.compile(r"ant-tabs-tab-active"))

            self.consumption_page.locators.ACCRUALS_TABPANEL_BTNS[6].wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TABPANEL_BTNS[6].click()
            self.consumption_page.locators.SWITCH_LIST[1].wait_to_be_visible()
            self.consumption_page.locators.SWITCH_LIST[1].click()
            self.consumption_page.locators.ACCRUALS_TABPANEL_BTNS[6].click()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].not_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[15].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[16].wait_to_have_text("Дата выставления счета")

        with allure.step('Перейти на вкладку "Трафик" и включить отображение данных о биллинге'):
            self.consumption_page.locators.TABS_LIST[1].wait_to_be_visible()
            self.consumption_page.locators.TABS_LIST[1].click()
            self.consumption_page.locators.SWITCH_BTN_LIST[0].wait_to_be_visible()
            self.consumption_page.locators.SWITCH_BTN_LIST[0].click()
            self.consumption_page.locators.SWITCH_BTN_LIST[1].wait_to_be_enabled()
            self.consumption_page.locators.SWITCH_BTN_LIST[1].click()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].not_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[23].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[24].wait_to_have_text("Дата выставления счета абоненту")

        with allure.step('Перейти на форму "Биллинговые счета" и открыть последний биллинговый счёт'):
            self.consumption_page.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")

            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.wait_elements_visible(0)
            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST[0].click()

            self.billing_accounts_page.check_billing_properties()

        with allure.step('Нажать кнопку "Откатить биллинг" и нажать кнопку "Выполнить"'):
            self.billing_accounts_page.locators.BILLING_BTNS[0].click()

            self.billing_accounts_page.locators.MODAL.wait_to_be_visible()
            rollback_modal_text = re.compile(
                r"Будет выполнен откат внеочередного биллинга от \d{2}\.\d{2}\.\d{4} \d{2}\:\d{2}\:\d{2}."
                r"Количество счетов: 1"
            )
            self.billing_accounts_page.locators.MODAL_BODY_TEXT[0].wait_to_have_text(rollback_modal_text)
            self.billing_accounts_page.locators.SECOND_BTN.click()
            self.billing_accounts_page.locators.MODAL.wait_not_to_be_visible()
            self.billing_accounts_page.locators.INFO_MESSAGE_CLOSE_BTN.wait_to_be_visible()
            rollback_popup_text = re.compile(
                rf"Запущен откат внеочередного биллинга от \d{{2}}\.\d{{2}}\.\d{{4}} \d{{2}}\:\d{{2}}\:\d{{2}} по лицевому счету: {account_num} Задание: \d{{4}}-\d{{12}}-\d{{2}}"
            )
            self.billing_accounts_page.locators.INFO_MESSAGE.wait_to_have_text(rollback_popup_text)
            self.billing_api.wait_finish_billing(billing_profile_id, 3)

        with allure.step(
            'Нажать кнопку "Список заданий биллинга" и после проверки закрыть список заданий биллинга и нажать кнопку "Обновить"'
        ):
            self.billing_accounts_page.locators.MORE_BTN.select_by_value("Список заданий биллинга")

            self.billing_accounts_page.locators.TASK_TYPE_LIST.wait_elements_visible(1)
            self.billing_accounts_page.locators.TASK_TYPE_LIST[0].to_contain_text("Биллинг")
            self.billing_accounts_page.locators.TASK_TYPE_LIST[1].to_contain_text("Откат биллинга")
            self.billing_accounts_page.locators.TASK_STATUS_LIST[0].to_contain_text("Завершено или откачено")
            self.billing_accounts_page.locators.TASK_STATUS_LIST[1].to_contain_text("Завершено")
            self.billing_accounts_page.locators.TASKS_CLOSE_BTN.click()

            self.billing_accounts_page.locators.REFRESH_BTN.wait_to_be_visible()
            self.billing_accounts_page.locators.REFRESH_BTN.click()

            self.billing_accounts_page.locators.ACCOUNT_NUMS_LIST.not_to_contain_text_in_any(r"\d{4}-\d{2}-\d{12}")

        with allure.step('Перейти на форму "Потребление" и выбрать абонента'):
            self.billing_accounts_page.locators.BURGER_MENU.select_by_value("Финансы > Потребление")

            self.consumption_page.locators.SUBSCRIBER_NUM[0].wait_to_be_visible()
            self.consumption_page.locators.SUBSCRIBER_NUM[0].click()

        with allure.step('Перейти на вкладку "Начисления" и включить отображение данных о биллинге'):
            self.consumption_page.locators.TABS_LIST[2].click()
            self.consumption_page.locators.TABS_LIST[2].to_have_class(class_name=re.compile(r"ant-tabs-tab-active"))

            self.consumption_page.locators.ACCRUALS_TABPANEL_BTNS[4].wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].not_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[0].wait_to_be_enabled()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[15].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[16].wait_to_have_text("Дата выставления счета")
            self.consumption_page.locators.CHARGES_BILLING_NUM_LIST.to_contain_text_in_all("—")
            self.consumption_page.locators.CHARGES_INVOICE_DATE_LIST.to_contain_text_in_all("—")

        with allure.step('Перейти на вкладку "Трафик" и включить отображение данных о биллинге'):
            self.consumption_page.locators.TABS_LIST[1].wait_to_be_visible()
            self.consumption_page.locators.TABS_LIST[1].click()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].wait_to_be_visible()
            self.consumption_page.locators.ACCRUALS_SPINNING[0].not_to_be_visible()
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[23].wait_to_have_text("Номер биллингового счета")
            self.consumption_page.locators.ACCRUALS_TITLE_LIST[24].wait_to_have_text("Дата выставления счета абоненту")
            self.consumption_page.locators.TRAFFIC_BILLING_NUM_LIST.to_contain_text_in_all("—")
            self.consumption_page.locators.TRAFFIC_INVOICE_DATE_LIST.to_contain_text_in_all("—")

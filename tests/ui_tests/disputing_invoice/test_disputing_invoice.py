import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.billing_requests import BillingRequests
from api.requests.client_requests import ClientRequests
from api.requests.inquiry_requests import CustomProperty, ForwardInfo, InquiryInfo, InquiryRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from models.user import IndividualClient
from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.consumption_page import ConsumptionPage
from pages.locators.dynamic_form_elements import (
    ChooseRequestTopic,
    ForwardInquiryForm,
    LinkedInquiriesForm,
    LinkingToInquiresForm,
    RequestCreate,
)
from tests.conftest import CreatedImsis


@allure.suite("Оспаривание счетов")
class TestDisputingInvoice:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.inquiry_api = InquiryRequests(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)
        self.client_request_api = ClientRequests(api_request_auth_context)

        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.billing_accounts = BillingAccountsPage(nexign_ui_stand_login)
        self.consumption_page = ConsumptionPage(nexign_ui_stand_login)

        self.request_create = RequestCreate(nexign_ui_stand_login)
        self.choose_request_topic = ChooseRequestTopic(nexign_ui_stand_login)
        self.forward_inquiry_form = ForwardInquiryForm(nexign_ui_stand_login)
        self.linking_to_inquires_form = LinkingToInquiresForm(nexign_ui_stand_login)
        self.linked_inquires_form = LinkedInquiriesForm(nexign_ui_stand_login)

    @allure.title("01. Создание заявки-претензии")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
        name="КР [RM.2] Оспаривание счетов (Упрощенное)",
    )
    @allure.id(602765)
    @pytest.mark.regress
    def test_create_claim_form(self, create_individual_user: IndividualClient, base_url: str) -> None:
        with allure.step("Клиент предварительно найден"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/customers/{create_individual_user.user_id}/overview"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("В правом сайдбаре выбрать пункт 'Создание заявки'"):
            self.client_profile.locators.RIGHT_SIDE_BTN.wait_to_have_count(4)
            self.client_profile.locators.RIGHT_SIDE_BTN.click(0)
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step('Выбрать тему (Обязательно): Нажать на "..."'):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.wait_to_be_visible()
            self.choose_request_topic.TITLE.to_contain_text("Выбор темы заявки")

        with allure.step("Выбрать тему: 'Претензия' - 'Не согласен с расчетами'"):
            self.choose_request_topic.REQUEST_TOPIC_NAME.wait_for_text_in_all(["Претензия"])
            topic_index = self.choose_request_topic.REQUEST_TOPIC_NAME.text_list.index("(3) 03 Претензия")
            self.choose_request_topic.EXPAND_BTN.click(topic_index)
            self.choose_request_topic.REQUEST_TOPIC_NAME.wait_for_text_in_all(["Не согласен с расчетами"])
            topic_index = self.choose_request_topic.REQUEST_TOPIC_NAME.text_list.index("(301) Не согласен с расчетами")
            self.choose_request_topic.REQUEST_TOPIC_NAME.click(topic_index)

        with allure.step("Нажать 'Применить'"):
            self.choose_request_topic.ACCEPT_BTN.wait_to_be_enabled()
            self.choose_request_topic.ACCEPT_BTN.click()
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.EMAIL.check_attribute_not_contain_value("aria-required", "true")
            self.request_create.PHONE.check_attribute_not_contain_value("aria-required", "true")
            self.request_create.DESCRIPTION.check_attribute_not_contain_value("aria-required", "true")
            self.request_create.PRIORITY.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.to_contain_text("Не согласен с расчетами")
            self.request_create.CODE.to_contain_text("301")
            self.request_create.PRIORITY.to_contain_text("Низкий")

        with allure.step("Нажать 'Передать' на форме 'Создание заявки'"):
            self.request_create.FORWARD_BTN.wait_to_be_enabled()
            self.request_create.FORWARD_BTN.click()
            self.forward_inquiry_form.FORWARD_FORM.wait_to_be_visible()
            self.forward_inquiry_form.check_form_fields()
            self.forward_inquiry_form.TITLE.wait_to_have_text("Передача на обработку")
            self.forward_inquiry_form.PROCESS_FIELD.to_contain_text("Обработка претензий")
            self.forward_inquiry_form.QUEUE_FIELD.to_contain_text("Обработка претензий B2C")

        with allure.step("Нажать 'Передать' на форме 'Передача на обработку'"):
            self.forward_inquiry_form.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry_form.FORWARD_BTN.click()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_be_visible()
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_have_text(re.compile(r"Заявка \d+ создана и передана\."))
            inquiry_id = self.forward_inquiry_form.INFO_MESSAGE.text.split()[1]

        with allure.step("Заявка отображена в списке заявок"):
            self.client_profile.locators.REQUESTS_TAB.click()
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_TYPE[0].wait_to_have_text("Не согласен с расчетами")

    @allure.title("02. Связывание Претензии с Объектом Обслуживания (счет)")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
        name="КР [RM.2] Оспаривание счетов (Упрощенное)",
    )
    @allure.id(603457)
    @pytest.mark.regress
    def test_link_claim_to_invoice(
        self, create_client_with_billing_and_claim: tuple[int, int, int], base_url: str
    ) -> None:
        account_id, inquiry_id, billing_profile_id = create_client_with_billing_and_claim

        with allure.step("На главной странице выбранного клиента выбрать лицевой счет"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{account_id}/account")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Открыть боковое меню, выбрать пункт меню 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.base_elements.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        with allure.step("Выбрать биллинговый счет и нажать кнопку 'Связать с заявкой'"):
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts.locators.BILLING_BTNS[1].wait_to_have_text("Связать с заявкой")
            self.billing_accounts.locators.BILLING_BTNS[1].click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.wait_to_be_visible()
            self.linking_to_inquires_form.TITLE.to_contain_text("Связывание с заявкой")

        with allure.step("Выбрать заявку, нажать 'Связать'"):
            self.linking_to_inquires_form.choice_inquiry(inquiry_id)
            self.linking_to_inquires_form.IMPROVE_BALANCE_CHECKBOX.to_have_class(re.compile(r"checkbox-checked"))
            self.linking_to_inquires_form.LINKED_BTN.wait_to_be_enabled()
            self.linking_to_inquires_form.LINKED_BTN.click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.not_to_be_visible()
            self.linking_to_inquires_form.INFO_MESSAGE.wait_to_be_visible()
            self.linking_to_inquires_form.INFO_MESSAGE.wait_to_have_text("Запрос на связывание с заявкой успешно создан")
            self.billing_api.wait_link_bill_and_inquiry(billing_profile_id)

        with allure.step("Заявка отображается в графе 'Связанные заявки' на вкладке 'Свойства'"):
            self.billing_accounts.locators.REFRESH_BTN.click()
            self.billing_accounts.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Связанные заявки"])
            property_index = self.billing_accounts.locators.BILLING_PROPERTIES.text_list.index("Связанные заявки")
            self.billing_accounts.locators.BILLING_PROPERTY_VALUES[property_index].to_contain_text("1 заявка")
            self.billing_accounts.locators.LINKED_CLAIM_LIST_BTN.click()
            self.linked_inquires_form.check_inquires(inquiry_id=inquiry_id, topic="Не согласен с расчетами", count=1)

    @allure.title("03. Связывание Претензии с Объектом Обслуживания (начисление)")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
        name="КР [RM.2] Оспаривание счетов (Упрощенное)",
    )
    @allure.id(603463)
    @pytest.mark.regress
    def test_link_claim_to_accrual(
        self, add_two_imsi_free_shipped: CreatedImsis, create_individual_user: IndividualClient, base_url: str
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client, product = self.client_request_api.product_sale(create_individual_user.user_id)
            subscription_id = self.personal_account_api.get_client_subscriptions(client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {client.account_id}"):
                self.payment_api.create_default_payment(
                    client.account_id, product.one_time_payment + product.subscription_fee + 100
                )
                self.personal_account_api.wait_check_current_main_balance(client.account_id, 100)
                self.personal_account_api.wait_accruals(subscription_id)

            with allure.step(f"Создание заявки для клиента: {client.user_id}"):
                inquiry_id = self.inquiry_api.create_inquiry(
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
                self.inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=277, queue_id=21))

            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.BALANCE.wait_to_be_visible()
            self.client_profile.locators.BALANCE[0].to_contain_text("100.00")

        with allure.step("На главной странице выбранного клиента перейти в Продукты"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_have_count(1)
            self.client_profile.locators.SUBSCRIBER.wait_to_have_text(product.phone_number)
            self.client_profile.locators.PRODUCT_NAME[0].wait_to_have_text(product.product_name)

        with allure.step("Напротив продукта нажать на 3 точки, Выбрать 'Перейти к деталям потребления'"):
            self.client_profile.locators.PRODUCTS_DETAILS_OPEN_BTN.hover()
            self.client_profile.locators.PRODUCTS_DETAILS_BTN.click()
            self.consumption_page.locators.PAGE_TITLE.wait_to_have_text("Потребление")
            self.consumption_page.locators.SUBSCRIBER_NUM.wait_to_have_count(1)
            self.consumption_page.locators.SUBSCRIBER_NUM[0].wait_to_have_text(product.phone_number)

        with allure.step("Перейти в 'Начисления'"):
            self.consumption_page.locators.TABS_LIST.wait_to_have_count(3)
            self.consumption_page.locators.TABS_LIST[2].wait_to_have_text("Начисления")
            self.consumption_page.locators.TABS_LIST.click(2)
            self.consumption_page.locators.CLEAR_FILTER_BTN.click()
            self.consumption_page.locators.ACCRUAL_LIST.wait_to_be_visible()

        with allure.step("Выбрать начисление, нажать кнопку 'Связать с заявкой'"):
            self.consumption_page.locators.ACCRUAL_CHECKBOXES.click(0)
            self.consumption_page.locators.LINKED_INQUIRES_BTN.click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.wait_to_be_visible()
            self.linking_to_inquires_form.TITLE.to_contain_text("Связывание с заявкой")

        with allure.step("Выбрать заявку, нажать 'Связать'"):
            self.linking_to_inquires_form.CLEAR_FILTER_BTN.click()
            self.linking_to_inquires_form.choice_inquiry(inquiry_id)
            self.linking_to_inquires_form.IMPROVE_BALANCE_CHECKBOX.to_have_class(re.compile(r"checkbox-checked"))
            self.linking_to_inquires_form.LINKED_BTN.wait_to_be_enabled()
            self.linking_to_inquires_form.LINKED_BTN.click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.not_to_be_visible()
            self.linking_to_inquires_form.INFO_MESSAGE.wait_to_be_visible()
            self.linking_to_inquires_form.INFO_MESSAGE.wait_to_have_text("Запрос на связывание с заявкой успешно создан")

        with allure.step("Заявка связана с начислением и отображена в связанных заявках"):
            self.personal_account_api.wait_link_last_accrual_with_inquiry(subscription_id, inquiry_id)
            self.consumption_page.locators.UPDATE_ACCRUAL_LIST_BTN.click()
            self.consumption_page.locators.DETAIL_LINKED_INQUIRES[0].wait_to_have_text("1 заявка")
            self.consumption_page.locators.LINKED_INQUIRES_LIST_BTN[0].click()
            self.linked_inquires_form.check_inquires(inquiry_id=inquiry_id, topic="Не согласен с расчетами", count=1)

    @allure.title("04. Связывание Претензии с Объектом Обслуживания (деталь счета)")
    @allure.tag("can_aurh", "success")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
        name="КР [RM.2] Оспаривание счетов (Упрощенное)",
    )
    @allure.id(603002)
    @pytest.mark.regress
    def test_link_claim_to_invoice_detail(
        self, add_two_imsi_free_shipped: CreatedImsis, create_individual_user: IndividualClient, base_url: str
    ) -> None:
        with allure.step("Выполнение предусловий"):
            client, product = self.client_request_api.product_sale(create_individual_user.user_id)
            subscription_id = self.personal_account_api.get_client_subscriptions(client.user_id).json()["items"][0][
                "subscriptionId"
            ]

            with allure.step(f"Добавление платежа для ЛС {client.account_id}"):
                self.payment_api.create_default_payment(
                    client.account_id, product.one_time_payment + product.subscription_fee + 100
                )
                self.personal_account_api.wait_check_current_main_balance(client.account_id, 100)

            with allure.step(f"Создание заявки для клиента: {client.user_id}"):
                inquiry_id = self.inquiry_api.create_inquiry(
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
                self.inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=inquiry_id, activity_id=277, queue_id=21))

            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.BALANCE.wait_to_be_visible()
            self.client_profile.locators.BALANCE[0].to_contain_text("100.00")

            with allure.step(f"Проведение биллинга для ЛС: {client.account_id}"):
                self.personal_account_api.wait_accruals(subscription_id)
                billing_profile_id = self.billing_api.get_billing_profile_id(client.account_id)
                self.billing_api.run_unscheduled_billing(billing_profile_id)
                self.billing_api.wait_billing(billing_profile_id)
                self.billing_api.wait_finish_billing(billing_profile_id, 3)

        with allure.step("На главной странице выбранного клиента выбрать лицевой счет"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{client.account_id}/account")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Открыть боковое меню, перейти на форму 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Биллинговые счета")
            self.billing_accounts.base_elements.SELECTED_TAB_TITLE.wait_to_have_text("Биллинговые счета")
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_be_visible()
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)

        with allure.step("Перейти на вкладку 'Детали'"):
            self.billing_accounts.locators.DETAILS_TAB.click()
            self.billing_accounts.locators.DETAIL.wait_to_be_visible()

        with allure.step("Выбрать деталь, нажать кнопку 'Связать с заявкой'"):
            self.billing_accounts.locators.DETAIL_CHECKBOX.click(0)
            self.billing_accounts.locators.LINKED_INQUIRES_BTN.click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.wait_to_be_visible()
            self.linking_to_inquires_form.TITLE.to_contain_text("Связывание с заявкой")

        with allure.step("Выбрать заявку, нажать 'Связать'"):
            self.linking_to_inquires_form.choice_inquiry(inquiry_id)
            self.linking_to_inquires_form.IMPROVE_BALANCE_CHECKBOX.to_have_class(re.compile(r"checkbox-checked"))
            self.linking_to_inquires_form.LINKED_BTN.wait_to_be_enabled()
            self.linking_to_inquires_form.LINKED_BTN.click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.not_to_be_visible()
            self.linking_to_inquires_form.INFO_MESSAGE.wait_to_be_visible()
            self.linking_to_inquires_form.INFO_MESSAGE.wait_to_have_text("Запрос на связывание с заявкой успешно создан")

        with allure.step("Заявка связана с деталью и отображена в связанных заявках"):
            bill_id = self.billing_api.get_list_of_bills([billing_profile_id])[0]["billId"]
            self.billing_api.wait_link_bill_detail_and_inquiry(bill_id)
            self.billing_accounts.locators.UPDATE_DETAILS_LIST_BTN.click()
            self.billing_accounts.locators.DETAIL_LINKED_INQUIRES[0].wait_to_have_text("1 заявка")
            self.billing_accounts.locators.LINKED_INQUIRES_LIST_BTN[0].click()
            self.linked_inquires_form.check_inquires(inquiry_id=inquiry_id, topic="Не согласен с расчетами", count=1)

        with allure.step("Заявка отображается в графе 'Связанные заявки' на вкладке 'Свойства'"):
            self.billing_accounts.locators.PROPERTIES_TAB.click()
            self.billing_accounts.locators.REFRESH_BTN.click()
            self.billing_accounts.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Связанные заявки"])
            property_index = self.billing_accounts.locators.BILLING_PROPERTIES.text_list.index("Связанные заявки")
            self.billing_accounts.locators.BILLING_PROPERTY_VALUES[property_index].to_contain_text("1 заявка")
            self.billing_accounts.locators.LINKED_CLAIM_LIST_BTN.click()
            self.linked_inquires_form.check_inquires(inquiry_id=inquiry_id, topic="Не согласен с расчетами", count=1)

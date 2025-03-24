import re

import allure
import pytest
from playwright.sync_api import Page, APIRequestContext

from pages.billing_accounts_page import BillingAccountsPage
from pages.client_profile_page import ClientProfilePage
from pages.locators.dynamic_form_elements import RequestCreate, ChooseRequestTopic, ForwardInquiryForm, \
    CreateInquiryNotification, LinkedInquiriesForm, LinkingToInquiresForm, Notifications


@allure.suite("Оспаривание счетов")
class TestDisputingInvoice:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext):
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.billing_accounts = BillingAccountsPage(nexign_ui_stand_login)

        self.request_create = RequestCreate(nexign_ui_stand_login)
        self.choose_request_topic = ChooseRequestTopic(nexign_ui_stand_login)
        self.forward_inquiry_form = ForwardInquiryForm(nexign_ui_stand_login)
        self.create_inquery_notification = CreateInquiryNotification(nexign_ui_stand_login)
        self.linking_to_inquires_form = LinkingToInquiresForm(nexign_ui_stand_login)
        self.notifications = Notifications(nexign_ui_stand_login)
        self.linked_inquires_form = LinkedInquiriesForm(nexign_ui_stand_login)

    @allure.title("01. Создание заявки-претензии")
    @allure.tag("can_aurh", "success")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
                 name="КР [RM.2] Оспаривание счетов (Упрощенное)")
    @allure.id(602765)
    def test_create_claim_form(self, create_user: int, base_url: str):

        with allure.step("Клиент предварительно найден"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("В правом сайдбаре выбрать пункт 'Создание заявки'"):
            self.client_profile.locators.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.client_profile.locators.RIGHT_SIDE_BTN.click(0)
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему (Обязательно): Нажать на \"...\""):
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
            self.create_inquery_notification.INQUIRY_NOTIFICATION.wait_to_be_visible()
            self.create_inquery_notification.INQUIRY_TEXT.wait_to_have_text(
                re.compile(r"Заявка \d{4} создана и передана\."))
            inquiry_id = self.create_inquery_notification.INQUIRY_TEXT.text.split()[1]

        with allure.step("Заявка отображена в списке заявок"):
            self.client_profile.locators.REQUESTS_TAB.click()
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_TYPE[0].wait_to_have_text("Не согласен с расчетами")

    @allure.title("02. Связывание Претензии с Объектом Обслуживания (счет)")
    @allure.tag("can_aurh", "success")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
                 name="КР [RM.2] Оспаривание счетов (Упрощенное)")
    @allure.id(603457)
    def test_link_claim_to_invoice(self, create_client_with_billing_and_claim: (int, int), base_url: str):
        account_id, inquiry_id = create_client_with_billing_and_claim

        with allure.step("На главной странице выбранного клиента выбрать лицевой счет"):
            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{account_id}/account")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Открыть боковое меню, выбрать пункт меню 'Биллинговые счета'"):
            self.client_profile.locators.BURGER_MENU_BTN.click()
            self.client_profile.locators.BURGER_MENU_EL_BTN[8].wait_to_have_text("Биллинговые счета")
            self.client_profile.locators.BURGER_MENU_EL_BTN[8].click()
            self.billing_accounts.base_elements.PAGE_TITLE.wait_to_have_text("Биллинговые счета")

        with allure.step("Выбрать биллинговый счет и нажать кнопку 'Связать с заявкой'"):
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.wait_to_have_count(1)
            self.billing_accounts.locators.ACCOUNT_NUMS_LIST.click(0)
            self.billing_accounts.locators.BILLING_BTNS[1].wait_to_have_text("Связать с заявкой")
            self.billing_accounts.locators.BILLING_BTNS[1].click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.wait_to_be_visible()
            self.linking_to_inquires_form.TITLE.to_contain_text("Связывание с заявкой")

        with allure.step("Выбрать заявку, нажать 'Связать'"):
            self.linking_to_inquires_form.choice_inquiry(inquiry_id)
            self.linking_to_inquires_form.IMPROVE_BALANCE_CHECKBOX.to_have_class(re.compile(r"ant-checkbox-checked"))
            self.linking_to_inquires_form.LINKED_BTN.wait_to_be_enabled()
            self.linking_to_inquires_form.LINKED_BTN.click()
            self.linking_to_inquires_form.LINKING_TO_INQUIRIES_FORM.not_to_be_visible()
            self.notifications.NOTIFICATION.wait_to_be_visible()
            self.notifications.NOTIFICATION.wait_to_have_text("Запрос на связывание с заявкой успешно создан")

        with allure.step("Заявка отображается в графе 'Связанные заявки' на вкладке 'Свойства'"):
            self.billing_accounts.locators.REFRESH_BTN.click()
            self.billing_accounts.locators.BILLING_PROPERTIES.wait_for_text_in_all(["Связанные заявки"])
            property_index = self.billing_accounts.locators.BILLING_PROPERTIES.text_list.index("Связанные заявки")
            self.billing_accounts.locators.BILLING_PROPERTY_VALUES[property_index].to_contain_text("1 заявка")
            self.billing_accounts.locators.LINKED_CLAIM_LIST_BTN.click()
            self.linked_inquires_form.check_inquires(inquiry_id=inquiry_id, topic="Не согласен с расчетами", count=1)

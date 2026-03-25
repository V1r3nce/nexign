import re

import allure
import pytest

from models.client import IndividualClient
from pages.locators.nbss.dynamic_form_elements import (
    ChooseRequestTopic,
    ForwardInquiryForm,
    RequestCreate,
)
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.suite("Оспаривание счетов")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=518623236",
    name="КР [RM.2] Оспаривание счетов (Упрощенное)",
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestDisputingInvoice:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile = ClientProfilePage()
        self.request_create = RequestCreate()
        self.choose_request_topic = ChooseRequestTopic()
        self.forward_inquiry_form = ForwardInquiryForm()

    @allure.title("01. Создание заявки-претензии")
    @allure.id(602765)
    def test_create_claim_form(self, create_individual_user: IndividualClient, base_url: str) -> None:
        with allure.step("Клиент предварительно найден"):
            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/customers/{create_individual_user.user_id}/overview"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("В правом сайдбаре выбрать пункт 'Создание заявки'"):
            self.client_profile.locators.CREATE_REQUEST.click()
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
            self.forward_inquiry_form.INFO_MESSAGE.wait_to_have_text(re.compile(r"Заявка \d+ создана\."))
            inquiry_id = self.forward_inquiry_form.INFO_MESSAGE.text.split()[1]

        with allure.step("Заявка отображена в списке заявок"):
            self.client_profile.locators.REQUESTS_TAB.click()
            self.client_profile.locators.REQUESTS.wait_to_be_visible()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].wait_to_have_text(inquiry_id)
            self.client_profile.locators.REQUEST_TYPE[0].wait_to_have_text("Не согласен с расчетами")

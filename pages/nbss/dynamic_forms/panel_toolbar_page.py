import allure

from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import ChooseRequestTopic, RequestCreate
from pages.locators.nbss.inquiries_elements import InquiriesElements
from pages.locators.nbss.inquiry.inquiry_sale_card_tab import InquirySaleCardTab


class PanelToolbarPage(BasePage):
    """Правая боковая панель с действиями над клиентом."""

    def __init__(self) -> None:
        super().__init__()

        self.locators = BaseElements()
        self.request_create = RequestCreate()
        self.choose_request_topic = ChooseRequestTopic()
        self.inquiries_form = InquiriesElements()
        self.inquiry_sale_card = InquirySaleCardTab()

    @allure.step("Создание заявки с темой {topics} по договору и ЛС с индексом {agreement_index}")
    def create_inquiry_with_agreement_and_account(self, topics: list[str], agreement_index: int = 0) -> None:
        """Создать заявку из боковой панели: выбрать тему, договор и ЛС, сохранить заявку.

        :param topics: путь до темы заявки в дереве тем
        :param agreement_index: индекс договора и ЛС в выпадающих списках
        """
        self.locators.CREATE_REQUEST.wait_to_be_visible(timeout=15000)
        self.locators.CREATE_REQUEST.click()
        self.request_create.CREATE_FORM.wait_to_be_visible(timeout=15000)
        self.request_create.TOPIC.click()
        self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.wait_to_be_visible(timeout=15000)
        self.choose_request_topic.choose_topic(topics)
        self.request_create.CREATE_FORM.wait_to_be_visible(timeout=15000)
        self.inquiries_form.BTN_OPEN_DROPDOWN_AGREEMENT_AND_ACCOUNT.wait_to_be_visible(timeout=15000)
        self.inquiries_form.BTN_OPEN_DROPDOWN_AGREEMENT_AND_ACCOUNT[0].click()
        self.inquiry_sale_card.ATTRIBUTES_AGREEMENT.select_by_index(agreement_index)
        self.inquiry_sale_card.ATTRIBUTES_ACCOUNT.select_by_index(agreement_index)
        self.request_create.SAVE_BTN.wait_to_be_enabled(timeout=15000)
        self.request_create.SAVE_BTN.click()
        self.request_create.CREATE_FORM.not_to_be_visible(timeout=30000)

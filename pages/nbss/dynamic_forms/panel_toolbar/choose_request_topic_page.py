import allure

from common.enums.topic import ActionTopic, BaseTopic, SettlementServiceTopic
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import (
    ChooseRequestTopic,
    CreateSalesAndServiceManagement,
    ForwardInquiryForm,
    RequestCreate,
)


class ChooseRequestTopicPage(BasePage):
    """Форма выбора темы заявки"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = ChooseRequestTopic()
        self.request_create = RequestCreate()
        self.forward_inquiry_form = ForwardInquiryForm()
        self.create_sales_form = CreateSalesAndServiceManagement()

    @allure.step("Выбрать тему заявки {topic_name} и применить")
    def select_request_topic(self, topic_name: BaseTopic) -> None:
        self.request_create.TOPIC.wait_to_be_visible()
        self.request_create.TOPIC.click()
        self.locators.CHOOSE_REQUEST_TOPIC_FORM.wait_to_be_visible(timeout=10000)
        self.locators.TOPIC_SEARCH_INPUT.wait_to_be_visible()
        self.locators.TOPIC_SEARCH_INPUT.click()
        self.locators.TOPIC_SEARCH_INPUT.fill(topic_name)
        self.locators.REQUEST_TOPIC_NAME.wait_for_text_in_all([topic_name], timeout=10000)
        self.locators.REQUEST_TOPIC_NAME.click_by_text(topic_name)

        self.locators.ACCEPT_BTN.wait_to_be_enabled(timeout=10000)
        self.locators.ACCEPT_BTN.click()
        self.locators.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
        self.request_create.CREATE_FORM.wait_to_be_visible()

    @allure.step("Проверить значение поля 'Договор' для заявки с темой {topic}: {expected}")
    def check_agreement_field(self, topic: BaseTopic, expected: str) -> None:
        match topic:
            case ActionTopic.TransferProducts:
                locator = self.locators.AGREEMENT_SELECT
            case ActionTopic.AgreementTermination:
                locator = self.forward_inquiry_form.TERMINATE_CONTRACT_FIELD
            case ActionTopic.SaleTopic:
                locator = self.create_sales_form.SELECTED_AGREEMENT
            case SettlementServiceTopic.DebtRestructuring:
                locator = self.request_create.AGREEMENT
            case _:
                raise AssertionError(f"Нет проверки поля 'Договор' для темы {topic}")

        locator.wait_to_be_visible(timeout=20000)
        if expected:
            locator.to_contain_text(expected, timeout_sec=15)
        else:
            locator.to_have_value("")

    @allure.step("Проверить значение поля 'Лицевой счёт' для заявки с темой {topic}: {expected}")
    def check_account_field(self, topic: BaseTopic, expected: str) -> None:
        match topic:
            case ActionTopic.SaleTopic:
                locator = self.create_sales_form.SALE_ACCOUNT
            case SettlementServiceTopic.DebtRestructuring:
                locator = self.request_create.ACCOUNT
            case SettlementServiceTopic.ProvisionOfSettlementDocuments:
                locator = self.request_create.SPD_ACCOUNT
            case SettlementServiceTopic.RefundOfFunds:
                locator = self.request_create.ACCOUNT_FIELD
            case _:
                raise AssertionError(f"Нет проверки поля 'Лицевой счёт' для темы {topic}")

        locator.wait_to_be_visible(timeout=20000)
        if expected:
            locator.to_contain_text(expected, timeout_sec=15)
        else:
            locator.to_have_value("")

    @allure.step("Проверить, что поле 'Лицевой счёт' отсутствует для заявки с темой {topic}")
    def check_account_field_not_visible(self, topic: BaseTopic) -> None:
        match topic:
            case ActionTopic.SaleTopic:
                locator = self.create_sales_form.SALE_ACCOUNT
            case SettlementServiceTopic.DebtRestructuring:
                locator = self.request_create.ACCOUNT
            case SettlementServiceTopic.ProvisionOfSettlementDocuments:
                locator = self.request_create.SPD_ACCOUNT
            case SettlementServiceTopic.RefundOfFunds:
                locator = self.request_create.ACCOUNT_FIELD
            case _:
                raise AssertionError(f"Нет проверки поля 'Лицевой счёт' для темы {topic}")

        locator.not_to_be_visible()

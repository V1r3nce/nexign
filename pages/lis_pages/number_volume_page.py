import allure
from playwright.sync_api import Page
from pages.base_page import BasePage

from pages.locators.lis_locators.number_volume_elements import NumberVolumeElementsLis


class NumberVolumePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = NumberVolumeElementsLis(page)

    @allure.step("Проверить элементы Поиск")
    def check_search_elements(self):
        self.locators.MSISDN_FILTER_BTN.wait_to_be_visible()
        self.locators.CATEGORY_FILTER_BTN.wait_to_be_visible()
        self.locators.CLASS_FILTER_BTN.wait_to_be_visible()
        self.locators.STATUS_FILTER_BTN.wait_to_be_visible()
        self.locators.CHANGE_STATUS_DATE_BTN.wait_to_be_visible()
        self.locators.STATE_FILTER_BTN.wait_to_be_visible()
        self.locators.OPERATOR_FILTER_BTN.wait_to_be_visible()
        self.locators.USER_FILTER_FIELD.wait_to_be_visible()
        self.locators.NUMBER_TYPE_FILTER_BTN.wait_to_be_visible()
        self.locators.STANDARD_FILTER_BTN.wait_to_be_visible()
        self.locators.COMMUTATOR_FILTER_BTN.wait_to_be_visible()
        self.locators.BLOCKING_FILTER_BTN.wait_to_be_visible()
        self.locators.LINK_NUMBER_FILTER_BTN.wait_to_be_visible()
        self.locators.GOAL_FILTER_BTN.wait_to_be_visible()
        self.locators.BILLING_CONNECTION_FILTER_BTN.wait_to_be_visible()
        self.locators.COMMENT_FILTER_BTN.wait_to_be_visible()

        self.locators.FILTER_SEARCH_BTN.wait_to_be_visible()
        self.locators.CLEAR_FILTER_BTN.wait_to_be_visible()
        self.locators.CHOOSE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()
        self.locators.SAVE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()
        self.locators.HIDE_FILTER_BTN.wait_to_be_visible()

    @allure.step("Проверить элементы Добавление номера")
    def check_add_new_number_elements(self):
        self.locators.START_PHONE_NUMBER.wait_to_be_visible()
        self.locators.COUNT_PHONE_NUMBER.wait_to_be_visible()
        self.locators.CHOOSE_COMMUTATOR_BTN.wait_to_be_visible()
        self.locators.CHOSEN_CATEGORY_FIELD.to_contain_text("Телефония")
        self.locators.CHOSEN_STATUS_FIELD.check_attribute_by_value("disabled", "disabled")
        self.locators.NUMBER_TYPE_FIELD.to_contain_text("Федеральная")
        self.locators.OPERATOR_FIELD.wait_to_be_visible()
        self.locators.USE_GOAL_FIELD.wait_to_be_visible()
        self.locators.COMMENT_FIELD.wait_to_be_visible()
        self.locators.NUMBER_TYPE_CHECKBOXES.wait_to_have_count(5)

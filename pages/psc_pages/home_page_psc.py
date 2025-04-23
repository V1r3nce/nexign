import allure
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.psc_locators.home_element_psc import (
    CreateProductSpecificationForm,
    CreateProjectForm,
    HomeElementsPsc,
)


class HomePagePsc(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = HomeElementsPsc(page)
        self.create_product_specification_form = CreateProductSpecificationForm(page)
        self.create_project_form = CreateProjectForm(page)

    @allure.step("Добавить опцию CFSS")
    def add_cfss_option(self, option: str) -> None:
        self.create_product_specification_form.ADD_CFSS_BTN.click(force=True)
        self.create_product_specification_form.CFSS_INPUT.fill(option)
        delay(0.7)
        self.create_product_specification_form.CFSS_OPTIONS[0].wait_to_be_visible(timeout=10000)
        for item in self.create_product_specification_form.CFSS_OPTIONS:
            if item.text == option:
                item.click()
                break
        self.create_product_specification_form.CHOSEN_CFSS_OPTIONS[-1].wait_to_have_text(option)

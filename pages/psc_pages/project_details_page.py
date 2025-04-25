import allure
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.psc_locators.project_details_elements import CreateProductProposalForm, ProjectDetailsElements


class ProjectPagePsc(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ProjectDetailsElements(page)
        self.create_pp_form = CreateProductProposalForm(page)

    @allure.step("Добавить опцию Спецификация")
    def add_ps_option(self, option: str) -> None:
        self.create_pp_form.PS_FIELD.click()
        self.create_pp_form.PS_INPUT.fill(option)
        self.create_pp_form.PS_OPTIONS.wait_to_be_visible()
        delay(0.7)
        self.create_pp_form.PS_OPTIONS[0].click()
        self.create_pp_form.PS_FIELD.to_contain_text(option)

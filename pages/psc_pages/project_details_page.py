import allure
from playwright.sync_api import APIRequestContext, Page

from api.requests.psc_requests.projects_requests import ProjectRequests
from common.helpers.data_generator import generate_random_number, get_current_datetime_string
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.psc_locators.project_details_elements import CreateProductProposalForm, ProjectDetailsElements
from pages.psc_pages.home_page_psc import HomePagePsc
from pages.psc_pages.product_proposal_page import ProductProposalPagePsc


class ProjectPagePsc(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ProjectDetailsElements(page)
        self.create_pp_form = CreateProductProposalForm(page)
        self.project_proposal_page = ProductProposalPagePsc(page)
        self.home_page_psc = HomePagePsc(page)

    @allure.step("Добавить опцию Спецификация")
    def add_ps_option(self, option: str) -> None:
        self.create_pp_form.PS_FIELD.click()
        self.create_pp_form.PS_INPUT.fill(option)
        self.create_pp_form.PS_OPTIONS.wait_to_be_visible()
        delay(0.7)
        self.create_pp_form.PS_OPTIONS[0].click()
        self.create_pp_form.PS_FIELD.to_contain_text(option)

    @allure.step("Создание нового проекта и продуктового предложения")
    def create_new_project_and_pp(self, api_request_auth_context: APIRequestContext) -> None:
        """Создание нового проекта и продуктового предложения"""
        project_requests_api = ProjectRequests(api_request_auth_context)
        ps_name = [
            item["name"]
            for item in project_requests_api.get_ps_specifications().json()["content"]
            if "E2E_41" in item["name"]
        ][0]
        new_name = "E2E_41_" + str(generate_random_number(4))
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        self.home_page_psc.locators.PROJECTS_BTN.click()
        self.home_page_psc.locators.CREATE_PROJECT_BTN.click()

        self.home_page_psc.create_project_form.TITLE.wait_to_have_text("Создание нового проекта")
        self.home_page_psc.create_project_form.TYPE_BTNS[0].to_contain_text("Проект")
        self.home_page_psc.create_project_form.TYPE_BTNS[0].element_have_css_color("color", "deep_blue")
        self.home_page_psc.create_project_form.PROJECT_NAME.fill(new_name)
        self.home_page_psc.create_project_form.START_DATE_INPUT.type(today_user_friendly_view)
        self.home_page_psc.create_project_form.DESCRIPTION_INPUT.fill(
            "E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов"
        )
        self.home_page_psc.create_project_form.SECOND_BTN_FORM.to_contain_text("Создать")
        self.home_page_psc.create_project_form.SECOND_BTN_FORM.click()

        self.locators.PROJECT_STATUS.wait_to_be_visible(timeout=10000)
        self.locators.PROJECT_STATUS.wait_to_have_text("В разработке")
        self.locators.PROJECT_NAME.wait_to_have_text(new_name)

        self.locators.PP_TAB.click()
        self.locators.ADD_PP_BUTTON.click()
        self.locators.ADD_NEW_PP_BUTTON.click()

        self.create_pp_form.TITLE.wait_to_have_text(" Создание продуктового предложения ")
        self.create_pp_form.PP_NAME.fill(ps_name)
        self.create_pp_form.PP_FORMAT[0].element_have_css_color("color", "deep_blue")
        self.create_pp_form.PP_TYPE_DROPDOWN_BTN.click()
        self.create_pp_form.TYPE_OPTIONS[2].to_contain_text("Основной")
        self.create_pp_form.TYPE_OPTIONS[2].click()
        self.add_ps_option(ps_name)
        self.create_pp_form.SUPPLIER_DROPDOWN_BTN.click()
        self.create_pp_form.TYPE_OPTIONS[0].click()
        self.create_pp_form.DESCRIPTION_INPUT.fill(
            "E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов"
        )
        self.locators.SECOND_BTN_FORM.to_contain_text("Создать")
        self.locators.SECOND_BTN_FORM.click()

        self.locators.TABLE_PP_NAME[0].wait_to_have_text(ps_name)
        self.locators.TABLE_PP_NAME[0].click()
        self.project_proposal_page.locators.PP_STATUS.wait_to_have_text("Не опубликовано")
        self.project_proposal_page.locators.PP_NAME.wait_to_have_text(ps_name)

        self.project_proposal_page.locators.CHARACTERISTICS_TAB.element_have_css_color("color", "deep_blue")
        self.project_proposal_page.locators.EDIT_BUTTON.click()
        self.project_proposal_page.locators.CONNECTION_STANDARD_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("нет")
        self.project_proposal_page.locators.MULTIPLE_OCCURRENCE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("да")

        self.project_proposal_page.locators.CHARACTERISTICS_GROUPS[1].click()

        self.project_proposal_page.add_characteristic("Тип подписки")
        self.project_proposal_page.locators.SUBSCRIPTION_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("REGULAR")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-1].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.to_contain_text("Сохранить изменения")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Тип владельца")
        self.project_proposal_page.locators.OWNER_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("SUBSCRIPTION")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-2].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Технические метки")
        self.project_proposal_page.locators.PRODUCT_TECHNICAL_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("IS_SELLABLE_STANDALONE")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-3].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Не предоставлять услуги при неоплате продукта")
        self.project_proposal_page.locators.CONTROL_PRODUCT_CHARGE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("да")

        self.project_proposal_page.add_characteristic("Цвет номера")
        self.project_proposal_page.locators.NUM_COLOR_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Простой")
        self.project_proposal_page.locators.NUM_COLOR_SETTING_BTN.click()
        self.project_proposal_page.locators.NUM_COLOR_CHECKBOXES[0].click()
        self.project_proposal_page.locators.APPLY_BTN.click()
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-5].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic_and_value("fillStage", "Наполнение Заказа")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Адрес")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-6].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic_and_value("fillStage", "Наполнение Заказа")
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Категория ПП")
        self.project_proposal_page.locators.PRODUCT_PP_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("MOBILE_PHONE")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-7].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic_and_value("needIncludeIntoTechOrder", "да")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Сегмент")
        self.project_proposal_page.locators.SEGMENT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("B2B")
        self.project_proposal_page.choose_option("B2C")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-8].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic_and_value("needIncludeIntoTechOrder", "да")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Использование лимитов на основном счете")
        self.project_proposal_page.locators.APPLY_LIMITS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("да")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-9].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.add_meta_characteristic_and_value("Видимость", "нет")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()
        self.project_proposal_page.locators.SAVE_BUTTON.click()
        self.project_proposal_page.locators.SAVE_BUTTON.not_to_be_visible()
        self.project_proposal_page.locators.CHARACTERISTIC_MENU.wait_to_have_count(17)

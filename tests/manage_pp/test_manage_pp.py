import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number, get_current_datetime_string
from pages.locators.psc_locators.project_details_elements import ProjectDetailsElements
from pages.psc_pages.home_page_psc import HomePagePsc


@allure.epic("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@allure.suite("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
class TestManageProductProposal:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_pcs: Page) -> None:
        self.home_page_psc = HomePagePsc(stand_login_pcs)
        self.project_details = ProjectDetailsElements(stand_login_pcs)

    @allure.title("01.00 Создание PS 'Е2Е_41'")
    @allure.id(594439)
    @allure.description("01.00 Создание PS 'Е2Е_41'")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=746621151",
        name="NBSS.INFO.PRODUCT.PSC Создание продуктовых предложений",
    )
    @allure.tag("can_auth", "success")
    def test_create_ps(self) -> None:
        today_user_friendly_view = get_current_datetime_string(is_full_format=False)
        new_name = "E2E_41_" + str(generate_random_number(4))
        self.home_page_psc.locators.SPECIFICATIONS_BTN.click()
        self.home_page_psc.locators.FUNCTION_TECH_LAYER_BTN.click()
        self.home_page_psc.locators.PS_BTN.element_have_css_color("color", "deep_blue")
        self.home_page_psc.locators.CREATE_PS_BTN.click()

        self.home_page_psc.create_product_specification_form.TITLE.wait_to_have_text("Создание продуктовой спецификации")
        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text("Шаг 1: Основные параметры")
        self.home_page_psc.create_product_specification_form.NAME_INPUT.fill(new_name)
        self.home_page_psc.create_product_specification_form.TYPE_DROPDOWN_BTN.click()
        self.home_page_psc.create_product_specification_form.TYPE_OPTIONS[3].wait_to_have_text("Сетевой продукт")
        self.home_page_psc.create_product_specification_form.TYPE_OPTIONS[3].click()
        self.home_page_psc.create_product_specification_form.IS_ONE_TIME_INPUT.to_have_value("Нет")
        self.home_page_psc.create_product_specification_form.START_DATE_INPUT.type(today_user_friendly_view)
        self.home_page_psc.create_product_specification_form.DESCRIPTION_INPUT.fill(
            "E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов"
        )
        self.home_page_psc.create_product_specification_form.NEXT_BTN.click()

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text("Шаг 2: Состав CFSS")
        self.home_page_psc.add_cfss_option("Доступ к сети GSM")
        self.home_page_psc.add_cfss_option("Входящая связь")
        self.home_page_psc.add_cfss_option("Исходящая связь")
        self.home_page_psc.add_cfss_option("Интернет")
        self.home_page_psc.add_cfss_option("Конференц-связь")
        self.home_page_psc.add_cfss_option("Определитель номера (АОН)")
        self.home_page_psc.add_cfss_option("MMS")
        self.home_page_psc.add_cfss_option("SMS")
        self.home_page_psc.add_cfss_option("Переадресация вызова")
        self.home_page_psc.add_cfss_option("Удержание вызова")
        self.home_page_psc.create_product_specification_form.CHOSEN_CFSS_OPTIONS.wait_to_have_count(10)
        self.home_page_psc.create_product_specification_form.NEXT_BTN.click()

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text(
            re.compile("Шаг 2: Состав RS")
        )
        self.home_page_psc.create_product_specification_form.NEXT_BTN.click()

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text(
            re.compile("Шаг 2: Характеристики")
        )
        self.home_page_psc.create_product_specification_form.ADD_BTN.click()
        self.home_page_psc.create_product_specification_form.SEARCH_INPUT.fill("Тип активации")
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_OPTIONS[0].wait_to_have_text(
            "Тип активации"
        )
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_OPTIONS[0].click()
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_STATUS_BTN[1].click()
        self.home_page_psc.create_product_specification_form.CHARACTERISTIC_DROPDOWN_BTN.click()
        self.home_page_psc.create_product_specification_form.CHARACTERISTIC_OPTIONS[2].click()

        self.home_page_psc.create_product_specification_form.CHARACTERISTIC_MENU.click()
        self.home_page_psc.create_product_specification_form.META_CHARACTERISTIC_BTN.click()
        self.home_page_psc.create_product_specification_form.META_ADD_BTN.click()
        self.home_page_psc.create_product_specification_form.SEARCH_INPUT.fill("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_OPTIONS[0].wait_to_have_text(
            "needIncludeIntoTechOrder"
        )
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_OPTIONS[0].click()
        self.home_page_psc.create_product_specification_form.META_CHARACTERISTIC_DROPDOWN_BTN.click()
        self.home_page_psc.create_product_specification_form.CHARACTERISTIC_OPTIONS[0].click()
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.to_contain_text("Сохранить изменения")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()
        self.home_page_psc.create_product_specification_form.NEXT_BTN.click()

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text(re.compile("Шаг 3: Статус"))
        self.home_page_psc.create_product_specification_form.RADIO_OPTIONS_FOR_ATTRIBUTES[1].click()
        self.home_page_psc.create_product_specification_form.CREATE_BTN.click()

        self.home_page_psc.locators.PS_NAMES.to_contain_text(0, new_name)
        self.home_page_psc.locators.PS_STATUSES[0].wait_to_have_text("Действует")

    @allure.title("02 Создание проекта 'Проект Е2Е_41'")
    @allure.id(594440)
    @allure.description("02 Создание проекта 'Проект Е2Е_41'")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=746621151",
        name="NBSS.INFO.PRODUCT.PSC Создание продуктовых предложений",
    )
    @allure.tag("can_auth", "success")
    def test_create_project(self) -> None:
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

        self.project_details.PROJECT_STATUS.wait_to_be_visible(timeout=10000)
        self.project_details.PROJECT_STATUS.wait_to_have_text("В разработке")
        self.project_details.PROJECT_NAME.wait_to_have_text(new_name)

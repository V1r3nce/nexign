import re

import allure
import pytest

from api.psc_requests.projects_requests import ProjectRequests
from common.helpers.data_generator import generate_random_number, get_current_datetime_string
from common.helpers.env_helper import BASE_URL_PSC
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.psc_pages.home_page_psc import HomePscPage
from pages.psc_pages.product_proposal_page import ProductProposalPscPage
from pages.psc_pages.project_details_page import ProjectPscPage


@allure.epic("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@allure.suite("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@pytest.mark.extended_regress
@pytest.mark.psc
@pytest.mark.nbss_portal
class TestManageProductProposal:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_pcs) -> None:
        self.base_page = BasePage()
        self.home_page_psc = HomePscPage()
        self.project_page_psc = ProjectPscPage()
        self.project_proposal_page = ProductProposalPscPage()
        self.project_requests_api = ProjectRequests()

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

        (
            self.home_page_psc.create_product_specification_form.TITLE.wait_to_have_text(
                "Создание продуктовой спецификации"
            )
        )
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
            re.compile("Шаг 3: Состав RS")
        )
        self.home_page_psc.create_product_specification_form.NEXT_BTN.click()

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text(
            re.compile("Шаг 4: Характеристики")
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
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.home_page_psc.create_product_specification_form.META_ADD_BTN.click()
        self.home_page_psc.create_product_specification_form.SEARCH_INPUT.fill("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_OPTIONS[0].wait_to_have_text(
            "needIncludeIntoTechOrder"
        )
        self.home_page_psc.create_product_specification_form.CHARACTERISTICS_OPTIONS[0].click()
        self.home_page_psc.create_product_specification_form.META_CHARACTERISTIC_DROPDOWN_BTN[0].click()
        self.home_page_psc.create_product_specification_form.CHARACTERISTIC_OPTIONS[0].click()
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.to_contain_text("Сохранить изменения")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()
        self.home_page_psc.create_product_specification_form.NEXT_BTN.click()

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text(re.compile("Шаг 5: Статус"))
        self.home_page_psc.create_product_specification_form.RADIO_OPTIONS_FOR_ATTRIBUTES[1].click()
        self.home_page_psc.create_product_specification_form.CREATE_BTN.click()

        self.home_page_psc.locators.PS_NAMES.to_contain_text(0, new_name, timeout=10000)
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

        self.project_page_psc.locators.PROJECT_STATUS.wait_to_be_visible(timeout=10000)
        self.project_page_psc.locators.PROJECT_STATUS.wait_to_have_text("В разработке")
        self.project_page_psc.locators.PROJECT_NAME.wait_to_have_text(new_name)

    @allure.title("03.00 Создание продуктового предложения 'ПП Е2Е_41' в проекте 'Проект Е2Е_41'")
    @allure.id(594461)
    @allure.description("NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=746621151",
        name="NBSS.INFO.PRODUCT.PSC Создание продуктовых предложений",
    )
    @allure.tag("can_auth", "success")
    def test_add_pp(self) -> None:
        project_id = self.project_requests_api.get_project_id_by_params({"productOfferingsNumber": 0})["id"]
        ps_name = self.project_requests_api.get_ps_specification_by_name("E2E_41")["name"]
        self.base_page.open(f"{BASE_URL_PSC}/ProductCatalog/ui/projects/{project_id}/main-parameters")
        self.project_page_psc.locators.PP_TAB.click()
        self.project_page_psc.locators.ADD_PP_BUTTON.click()
        self.project_page_psc.locators.ADD_NEW_PP_BUTTON.click()

        self.project_page_psc.create_pp_form.TITLE.wait_to_have_text(" Создание продуктового предложения ")
        self.project_page_psc.create_pp_form.PP_NAME.fill(ps_name)
        self.project_page_psc.create_pp_form.PP_FORMAT[0].element_have_css_color("color", "deep_blue")
        self.project_page_psc.create_pp_form.PP_TYPE_DROPDOWN_BTN.click()
        self.project_page_psc.create_pp_form.TYPE_OPTIONS[2].to_contain_text("Основной")
        self.project_page_psc.create_pp_form.TYPE_OPTIONS[2].click()
        self.project_page_psc.add_ps_option(ps_name)
        self.project_page_psc.create_pp_form.SUPPLIER_DROPDOWN_BTN.click()
        self.project_page_psc.create_pp_form.TYPE_OPTIONS[0].click()
        self.project_page_psc.create_pp_form.DESCRIPTION_INPUT.fill(
            "E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов"
        )
        self.project_page_psc.locators.SECOND_BTN_FORM.to_contain_text("Создать")
        self.project_page_psc.locators.SECOND_BTN_FORM.click()

        self.project_page_psc.locators.TABLE_PP_NAME[0].wait_to_have_text(ps_name)
        self.project_page_psc.locators.TABLE_PP_NAME[0].click()
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
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.to_contain_text("Сохранить изменения")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Тип владельца")
        self.project_proposal_page.locators.OWNER_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("SUBSCRIPTION")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-2].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Технические метки")
        self.project_proposal_page.locators.PRODUCT_TECHNICAL_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("IS_SELLABLE_STANDALONE")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-3].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
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
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic_and_value("fillStage", "Наполнение Заказа")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Адрес")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-6].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic_and_value("fillStage", "Наполнение Заказа")
        self.project_proposal_page.add_meta_characteristic("Видимость")
        self.project_proposal_page.add_meta_characteristic("needIncludeIntoTechOrder")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Категория ПП")
        self.project_proposal_page.locators.PRODUCT_PP_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("MOBILE_PHONE")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-7].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic_and_value("needIncludeIntoTechOrder", "да")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Сегмент")
        self.project_proposal_page.locators.SEGMENT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("B2B")
        self.project_proposal_page.choose_option("B2C")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-8].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic_and_value("needIncludeIntoTechOrder", "да")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()

        self.project_proposal_page.add_characteristic("Использование лимитов на основном счете")
        self.project_proposal_page.locators.APPLY_LIMITS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("да")
        self.project_proposal_page.locators.CHARACTERISTIC_MENU[-9].click()
        self.project_proposal_page.locators.META_CHARACTERISTIC_BTN[-1].click()
        self.project_proposal_page.locators.META_ATTRIBUTE_TAB.click()
        self.project_proposal_page.add_meta_characteristic_and_value("Видимость", "нет")
        self.home_page_psc.create_product_specification_form.SECOND_BTN_FORM.click()
        self.project_proposal_page.locators.SAVE_BUTTON.click()
        self.project_proposal_page.locators.SAVE_BUTTON.not_to_be_visible()
        self.project_proposal_page.locators.CHARACTERISTIC_MENU.wait_to_have_count(17)

    @allure.title("03.01 Создание периодической цены в 'ПП Е2Е_41'")
    @allure.id(594466)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_price_subscription_fee(self) -> None:
        project_id = self.project_requests_api.get_project_id_by_params(
            {"productOfferingsNumber": 1, "lifecycleStatus": "EDITING"}
        )["id"]
        self.base_page.open(f"{BASE_URL_PSC}/ProductCatalog/ui/projects/{project_id}/main-parameters")
        self.project_page_psc.locators.PP_TAB.click()
        self.project_page_psc.locators.TABLE_PP_NAME[0].click()
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Абонентская плата")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Периодическая АП NORCA")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 3: События"))
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile(r"Шаг 4: Алгоритм применения цены \(PLA\)")
        )
        self.project_proposal_page.create_price_form.ALLOW_PARTIAL_PAYMENT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("нет")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 5: Характеристики цены")
        )
        (
            self.project_proposal_page.create_price_form.PRICE_ROLE_VALUES[0].wait_to_have_text(
                re.compile("BaseProdOfferPrice")
            )
        )
        self.project_proposal_page.create_price_form.MAKE_DEBIT_CHARGE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option(
            "Не выполнять списание АП в дебет, если баланс абонента неотрицателен, но недостаточен для списания начисления"
        )
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option_contains(
            "Абон. плата за мобильный интернет с объемами с цветом номера - обычный"
        )
        self.project_proposal_page.create_price_form.IS_INSTANTIATION_PRICE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("да")
        self.project_proposal_page.add_form_characteristic("Выравнивание интервала")
        self.project_proposal_page.add_form_characteristic("Период оплаты при выходе из финансовой блокировки")

        self.project_proposal_page.create_price_form.INTERVAL_ALIGNMENT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Без выравнивания")
        self.project_proposal_page.create_price_form.PAY_FIN_BLOCK_PERIOD_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Период оплаты включает в себя период финансовой блокировки")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Правила"))
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 7: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Периодическая АП")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_NAME_INPUT.fill("Период оплаты")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Месяц")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("PeriodUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Месяц")
        self.project_proposal_page.create_price_form.PRICE_QUANTITY_INPUT.fill("100")
        self.project_proposal_page.create_price_form.PRICE_TAX_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VAT")
        self.project_proposal_page.create_price_form.CURRENCY_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("RUB")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 8: Связи"))
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(0, "Периодическая АП", timeout=10000)

    @allure.title("03.02 Создание цены за объемы интернета в 'ПП Е2Е_41'")
    @allure.id(594486)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_price_for_internet_volume(self) -> None:
        project_id = self.project_requests_api.get_project_id_by_params(
            {"productOfferingsNumber": 1, "lifecycleStatus": "EDITING"}
        )["id"]
        self.base_page.open(f"{BASE_URL_PSC}/ProductCatalog/ui/projects/{project_id}/main-parameters")
        self.project_page_psc.locators.PP_TAB.click()
        self.project_page_psc.locators.TABLE_PP_NAME[0].click()
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Объемы")
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Шаблон объема интернета моб.")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Шаблон объема интернета моб.")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 3: Конфигурация события потребления")
        )
        self.project_proposal_page.locators.RADIO_OPTIONS[3].click()
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile(r"Шаг 4: Алгоритм применения цены \(PLA\)")
        )

        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 5: Характеристики цены")
        )
        self.project_proposal_page.add_form_characteristic("Роль цены")
        self.project_proposal_page.add_form_characteristic("Платежная деталь")
        self.project_proposal_page.add_form_characteristic("Вес характеристики")
        self.project_proposal_page.create_price_form.PRICE_ROLE_VALUES[0].wait_to_have_text(
            re.compile("BaseProdOfferPrice")
        )
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option_contains("Объем интернет трафика")
        self.project_proposal_page.create_price_form.CHARACTERISTIC_WEIGHT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("1")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Правила"))

        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 7: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Объем интернета моб.")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_NAME_INPUT.fill("Период оплаты")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Месяц")
        self.project_proposal_page.create_price_form.PRIORITY_INPUT.fill("1000")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("10240")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VolumeUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Мегабайт")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 8: Связи"))
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(
            0, "Объем интернета моб.", timeout=10000
        )

    @allure.title("03.03 Создание цены за объемы минут в 'ПП Е2Е_41'")
    @allure.id(594561)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_price_for_minutes_volume(self) -> None:
        project_id = self.project_requests_api.get_project_id_by_params(
            {"productOfferingsNumber": 1, "lifecycleStatus": "EDITING"}
        )["id"]
        self.base_page.open(f"{BASE_URL_PSC}/ProductCatalog/ui/projects/{project_id}/main-parameters")
        self.project_page_psc.locators.PP_TAB.click()
        self.project_page_psc.locators.TABLE_PP_NAME[0].click()
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Объемы")
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Шаблон объема исх. связи моб.")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Шаблон объема исх. связи моб.")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 3: Конфигурация события потребления")
        )
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Исходящяя связь моб. объем")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile(r"Шаг 4: Алгоритм применения цены \(PLA\)")
        )

        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 5: Характеристики цены")
        )
        self.project_proposal_page.add_form_characteristic("Роль цены")
        self.project_proposal_page.add_form_characteristic("Платежная деталь")
        self.project_proposal_page.add_form_characteristic("Вес характеристики")
        self.project_proposal_page.create_price_form.PRICE_ROLE_VALUES[0].wait_to_have_text(
            re.compile("BaseProdOfferPrice")
        )
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option_contains("Объем голосовых минут")
        self.project_proposal_page.create_price_form.CHARACTERISTIC_WEIGHT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("2")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Правила"))
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 7: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Объем исх. связи моб.")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_NAME_INPUT.fill("Период оплаты")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Месяц")
        self.project_proposal_page.create_price_form.PRIORITY_INPUT.fill("1000")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("100")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VolumeUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Мин.")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 8: Связи"))
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(
            0, "Объем исх. связи моб.", timeout=10000
        )

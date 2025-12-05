import re

import allure
import pytest

from common.helpers.data_generator import generate_random_number, get_current_datetime_string
from common.helpers.time_helpers import delay
from pages.psc_pages.home_page_psc import HomePagePsc
from pages.psc_pages.product_proposal_page import ProductProposalPagePsc
from pages.psc_pages.project_details_page import ProjectPagePsc


@allure.epic("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@allure.suite("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
class TestManageProductProposalPublishing:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_pcs) -> None:
        self.project_page_psc = ProjectPagePsc()
        self.project_proposal_page = ProductProposalPagePsc()
        self.home_page_psc = HomePagePsc()

    @allure.title("04.00 Публикация проекта 'ПП Е2Е_41' в тестовую зону")
    @allure.id(594670)
    @allure.description(
        "ФС: CLM-403222. Публикация PSC-RSC-OCSDB https://confluence.nexign.com/pages/viewpage.action?pageId=310913182"
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.extended_regress
    @pytest.mark.psc
    @pytest.mark.nbss_portal
    def test_publish_pp(self) -> None:
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

        self.home_page_psc.create_product_specification_form.STEP_NAME[0].wait_to_have_text(re.compile("Шаг 3: Статус"))
        self.home_page_psc.create_product_specification_form.RADIO_OPTIONS_FOR_ATTRIBUTES[1].click()
        self.home_page_psc.create_product_specification_form.CREATE_BTN.click()

        self.home_page_psc.locators.PS_NAMES.to_contain_text(0, new_name, timeout=10000)
        self.home_page_psc.locators.PS_STATUSES[0].wait_to_have_text("Действует")
        self.home_page_psc.locators.APP_LOGO.click()

        self.project_page_psc.create_new_project_and_pp(add_color=False)
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
        self.project_proposal_page.create_price_form.PRICE_ROLE_VALUES[0].wait_to_have_text(
            re.compile("BaseProdOfferPrice")
        )
        self.project_proposal_page.create_price_form.MAKE_DEBIT_CHARGE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option(
            "Не выполнять списание АП в дебет, если баланс абонента неотрицателен, но недостаточен для списания начисления"
        )
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option(
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
        self.project_proposal_page.refresh_page(wait="domcontentloaded")
        self.project_proposal_page.locators.PROJECT_LINK.click()
        self.project_page_psc.locators.ACTION_INPUT.click()
        self.project_page_psc.locators.ACTION_OPTIONS[0].wait_to_have_text("Перевести в тестирование")
        self.project_page_psc.locators.ACTION_OPTIONS[0].click()
        self.project_page_psc.publish_confirmation_form.TITLE.wait_to_have_text(" Перевести проект в тестирование? ")
        self.project_page_psc.publish_confirmation_form.PUBLISH_PARAMS[0].click()
        self.project_page_psc.publish_confirmation_form.PUBLISH_PARAMS[1].to_have_class(re.compile("is-checked"))
        self.project_page_psc.publish_confirmation_form.MOVE_BTN.click()
        self.project_page_psc.publish_confirmation_form.NOTIFICATION_CONTENT.wait_to_have_text(
            re.compile("Идет публикация проекта"), timeout=10000
        )
        self.project_page_psc.locators.PROJECT_STATUS.wait_to_have_text(re.compile("Тестирование"), timeout=80000)

        self.project_page_psc.locators.ACTION_INPUT.click()
        self.project_page_psc.locators.ACTION_OPTIONS[1].wait_to_have_text("Опубликовать")
        self.project_page_psc.locators.ACTION_OPTIONS[1].click()
        self.project_page_psc.publish_confirmation_form.TITLE.wait_to_have_text(
            " Опубликовать проект в промышленную среду? "
        )
        self.project_page_psc.publish_confirmation_form.MOVE_BTN.click()
        self.project_page_psc.locators.PROJECT_NOTIFICATIONS.wait_to_have_count(2, timeout=80000)
        self.project_page_psc.locators.PROJECT_STATUS.wait_to_have_text(" Введён в действие ")
        self.project_page_psc.locators.PROJECT_NOTIFICATIONS[0].wait_to_have_text(
            "Проект опубликован в промышленную среду, но дата вступления в силу еще не наступила"
        )

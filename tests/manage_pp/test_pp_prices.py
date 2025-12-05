import re

import allure
import pytest

from common.helpers.time_helpers import delay
from pages.locators.psc_locators.pp_elements_psc import CreateRuleFormElements
from pages.psc_pages.product_proposal_page import ProductProposalPagePsc
from pages.psc_pages.project_details_page import ProjectPagePsc


@allure.epic("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@allure.suite("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@pytest.mark.extended_regress
@pytest.mark.psc
@pytest.mark.nbss_portal
class TestManageProductProposalPrices:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_pcs) -> None:
        self.project_page_psc = ProjectPagePsc()
        self.project_proposal_page = ProductProposalPagePsc()
        self.create_rule_form = CreateRuleFormElements()

    @allure.title("03.04 Создание цены за минуты сверх объема в 'ПП Е2Е_41'")
    @allure.id(594569)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_price_for_minutes_under_volume(self) -> None:
        self.project_page_psc.create_new_project_and_pp
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Трафик")
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Шаблон трафика исх. связи моб.")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Шаблон трафика исх. связи моб.")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 3: Конфигурация события потребления")
        )
        (
            self.project_proposal_page.locators.STATIC_CHECKBOX_VALUE[0].wait_to_have_text(
                re.compile("Исходящая связь мобильная")
            )
        )
        self.project_proposal_page.locators.STATIC_CHECKBOX_OPTIONS[0].to_have_class(re.compile("is-checked"))
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
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option_contains("Потребление голосового трафика")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Правила"))
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 7: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Трафик исх. связи моб.")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VolumeUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Мин.")
        self.project_proposal_page.create_price_form.PRICE_QUANTITY_INPUT.fill("1.5")
        self.project_proposal_page.create_price_form.PRICE_TAX_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VAT")
        self.project_proposal_page.create_price_form.CURRENCY_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("RUB")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 8: Связи"))
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(
            0, "Трафик исх. связи моб.", timeout=10000
        )

    @allure.title("03.05 Создание цены за интернет трафик сверх объема в 'ПП Е2Е_41'")
    @allure.id(594636)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_price_for_internet_under_volume(self) -> None:
        self.project_page_psc.create_new_project_and_pp
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Трафик")
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Шаблон трафика интернета моб.")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Шаблон трафика интернета моб.")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 3: Конфигурация события потребления")
        )
        self.project_proposal_page.locators.STATIC_CHECKBOX_VALUE[0].wait_to_have_text(re.compile("Интернет моб."))
        self.project_proposal_page.locators.STATIC_CHECKBOX_OPTIONS[0].to_have_class(re.compile("is-checked"))
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
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option_contains("Потребление интернет трафика (Мобильный интернет с объемами)")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Правила"))
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 7: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Трафик интернета моб.")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VolumeUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Мегабайт")
        self.project_proposal_page.create_price_form.PRICE_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.PRICE_TAX_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VAT")
        self.project_proposal_page.create_price_form.CURRENCY_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("RUB")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 8: Связи"))
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(
            0, "Трафик интернета моб.", timeout=10000
        )

    @allure.title("03.06 Создание цены за СМС в 'ПП Е2Е_41'")
    @allure.id(594646)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_price_for_sms(self) -> None:
        self.project_page_psc.create_new_project_and_pp
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Трафик")
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Шаблон трафика SMS моб.")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Шаблон трафика SMS моб.")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 3: Конфигурация события потребления")
        )
        self.project_proposal_page.locators.STATIC_CHECKBOX_VALUE[0].wait_to_have_text(re.compile("SMS моб."))
        self.project_proposal_page.locators.STATIC_CHECKBOX_OPTIONS[0].to_have_class(re.compile("is-checked"))
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
        self.project_proposal_page.create_price_form.BILL_DETAILS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option_contains("Отправка SMS")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Правила"))
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 7: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Стоимость СМС")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VolumeUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("SMS")
        self.project_proposal_page.create_price_form.PRICE_QUANTITY_INPUT.fill("4")
        self.project_proposal_page.create_price_form.PRICE_TAX_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VAT")
        self.project_proposal_page.create_price_form.CURRENCY_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("RUB")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 8: Связи"))
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(0, "Стоимость СМС", timeout=10000)

    @allure.title("03.07 Создание шаблона лимита интернета моб.")
    @allure.id(608821)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_template_mobile_internet(self) -> None:
        self.project_page_psc.create_new_project_and_pp
        self.project_proposal_page.locators.PRICE_TAB.click()
        self.project_proposal_page.locators.PRICE_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_BTN.to_contain_text("Добавить цену")
        self.project_proposal_page.locators.ADD_BTN.click()
        self.project_proposal_page.create_price_form.CREATE_PRICE_LARGE_BTN.click()
        self.project_proposal_page.create_price_form.PRICE_TYPE_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Лимит потребления объёма")
        self.project_proposal_page.locators.FORM_DIALOG_SEARCH_INPUT.fill("Шаблон лимита интернета моб.")
        self.project_proposal_page.locators.RADIO_OPTIONS[0].click()
        self.project_proposal_page.locators.LOADING_SPINNER.not_to_be_visible()
        delay(1, reason="Не успевает загрузиться следующая форма")
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 2: Параметры шаблона цены")
        )
        self.project_proposal_page.create_price_form.FORM_VALUES[0].wait_to_have_text("Шаблон лимита интернета моб.")
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 3: Конфигурация события потребления")
        )
        self.project_proposal_page.locators.STATIC_CHECKBOX_VALUE[0].wait_to_have_text(re.compile("Интернет моб."))
        self.project_proposal_page.locators.STATIC_CHECKBOX_OPTIONS[0].to_have_class(re.compile("is-checked"))
        self.project_proposal_page.locators.NEXT_BTN.click()
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(
            re.compile("Шаг 4: Характеристики цены")
        )
        self.project_proposal_page.create_price_form.PRICE_ROLE_VALUES[0].wait_to_have_text(
            re.compile("BaseProdOfferPrice")
        )
        self.project_proposal_page.create_price_form.COUNTER_REPORT_THRESHOLD_VALUES[0].wait_to_have_text(
            re.compile("90")
        )
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 5: Правила"))
        self.project_proposal_page.locators.NEXT_BTN.click()

        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_count(1)
        self.project_proposal_page.create_price_form.STEP_NAME.wait_to_have_text(re.compile("Шаг 6: Атрибуты"))
        self.project_proposal_page.create_price_form.PRICE_NAME_INPUT.fill("Лимит на мобильный интернет 10 GB")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.RECURRING_CHARGE_PERIOD_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Месяц")
        self.project_proposal_page.create_price_form.MAX_VOLUME_QUANTITY_INPUT.fill("10240")
        self.project_proposal_page.create_price_form.MAX_VOLUME_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Мегабайт")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_QUANTITY_INPUT.fill("1")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_CLASS_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("VolumeUnitOfMeasure")
        self.project_proposal_page.create_price_form.UNIT_OF_MEASURE_UNIT_DROPDOWN_BTN.click()
        self.project_proposal_page.choose_option("Мегабайт")
        self.project_proposal_page.create_price_form.DONE_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(
            0, "Лимит на мобильный интернет 10 GB", timeout=10000
        )

    @allure.title("03.08 Создание правил в 'ПП Е2Е_41'")
    @allure.id(609073)
    @allure.description(
        "NBSS.CP.PO Конструктор PO https://confluence.nexign.com/pages/viewpage.action?pageId=725108815#NBSS.CP."
        "PO%D0%9A%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80PO-%D0%A6%D0%B5%D0%BD%D1%8B"
    )
    @allure.tag("can_auth", "success")
    def test_add_rule_to_pp(self) -> None:
        self.project_page_psc.create_new_project_and_pp
        self.project_proposal_page.locators.RULES_TAB.click()
        self.project_proposal_page.locators.RULES_TAB.element_have_css_color("color", "deep_blue")

        self.project_proposal_page.locators.ADD_RULE_BTN.click()
        self.create_rule_form.CHOOSE_RULE_LARGE_BTN.click()
        self.create_rule_form.SEARCH_NAME_INPUT.fill("Схема N-M-30")
        self.create_rule_form.STATIC_CHECKBOX_VALUE[0].wait_to_have_text(re.compile("Схема N-M-30"))
        self.create_rule_form.STATIC_CHECKBOX_OPTIONS[0].click()
        self.create_rule_form.ADD_BTN.click()

        self.project_proposal_page.locators.TABLE_NAME_LINK_FIELDS.to_contain_text(0, "Схема N-M-30", timeout=10000)

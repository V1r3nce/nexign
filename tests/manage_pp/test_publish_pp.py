import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from common.helpers.time_helpers import delay
from pages.psc_pages.product_proposal_page import ProductProposalPagePsc
from pages.psc_pages.project_details_page import ProjectPagePsc


@allure.epic("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
@allure.suite("E2E_41 Управление продуктовыми предложениями (оферами) и тарифной линейкой/оферов")
class TestManageProductProposalPublishing:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_pcs: Page) -> None:
        self.project_page_psc = ProjectPagePsc(stand_login_pcs)
        self.project_proposal_page = ProductProposalPagePsc(stand_login_pcs)

    @allure.title("04.00 Публикация проекта 'ПП Е2Е_41' в тестовую зону")
    @allure.id(594670)
    @allure.description(
        "ФС: CLM-403222. Публикация PSC-RSC-OCSDB https://confluence.nexign.com/pages/viewpage.action?pageId=310913182"
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.extended_regress
    def test_publish_pp(self, api_request_auth_context: APIRequestContext) -> None:
        self.project_page_psc.create_new_project_and_pp(api_request_auth_context)
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
        self.project_page_psc.locators.PROJECT_STATUS.wait_to_have_text(re.compile("Тестирование"))

        self.project_page_psc.locators.ACTION_INPUT.click()
        self.project_page_psc.locators.ACTION_OPTIONS[1].wait_to_have_text("Опубликовать")
        self.project_page_psc.locators.ACTION_OPTIONS[1].click()
        self.project_page_psc.publish_confirmation_form.TITLE.wait_to_have_text(
            " Опубликовать проект в промышленную среду? "
        )
        self.project_page_psc.publish_confirmation_form.MOVE_BTN.click()
        self.project_page_psc.locators.PROJECT_STATUS.wait_to_have_text(re.compile("Введён в действие"))
        self.project_page_psc.locators.PROJECT_NOTIFICATIONS[0].wait_to_have_text(
            "Проект опубликован в промышленную среду, но дата вступления в силу еще не наступила"
        )

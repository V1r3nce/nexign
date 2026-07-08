from datetime import timedelta

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.enums.billing import DiscountTemplateAction
from common.helpers.checker import assert_that
from common.helpers.data_generator import (
    generate_english_string,
    generate_russian_string,
)
from common.helpers.time_helpers import get_current_moscow_datetime
from db.requests.db_requests import UDBRequests
from pages.locators.nbss.finances.discount_and_charges import (
    AddBillingDiscountFormStep4,
    AddBillingDiscountOrChargeFormStep3,
    AddProductOfferForm,
    FilterForm,
)
from pages.nbss.finances.discount_charges_setting import DiscountChargesSettingPage


@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=659783906", name="8.6. Управление биллинговыми скидками"
)
@allure.epic("E2E_67 Управление биллинговыми скидками")
@allure.suite("E2E_67 Управление биллинговыми скидками")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestEditBillingDiscount:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        create_organization,
        create_udb_connection: UDBRequests,
    ) -> None:
        self.client_request_api = ClientInquiriesRequests()
        self.discount_page = DiscountChargesSettingPage()
        self.discount_requests_api = BillingDiscountsRequests()
        self.add_discount_form_step_2 = AddProductOfferForm()
        self.filter_form = FilterForm()
        self.start_dt = get_current_moscow_datetime()
        self.start_date = self.start_dt.strftime("%d.%m.%Y")
        self.end_date = (self.start_dt + timedelta(days=30)).strftime("%d.%m.%Y")
        self.discount_amount = "50"
        self.priority = "1"
        self.add_discount_form_step_4 = AddBillingDiscountFormStep4()
        self.add_discount_form_step_3 = AddBillingDiscountOrChargeFormStep3()
        self.udb: UDBRequests = create_udb_connection

    @allure.title("19. Сохранение истории создания шаблона биллинговых скидок")
    @allure.id(936943)
    def test_delete_billing_discount(self) -> None:
        discount_scheme_name_ru = f"Тестовая_биллинговая_скидка_{generate_russian_string(6)}"
        discount_scheme_name_en = f"Test_billing_discount_{generate_english_string(6)}"

        with allure.step("Запрос в UDB — список шаблонов биллинговых скидок до создания"):
            template_ids_before = {int(row[1]) for row in self.udb.get_discount_templates_history()}

        self.discount_page.open_discount_charges_setting_page()
        self.discount_page.create_discount_template(
            discount_scheme_name_ru=discount_scheme_name_ru,
            discount_scheme_name_en=discount_scheme_name_en,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        with allure.step("Повторный запрос в UDB — шаблон создан под новым id, number_history=1, CREATE"):
            dbdt_id = self.udb.get_template_id_by_name(discount_scheme_name_ru)
            assert_that(
                lambda: dbdt_id not in template_ids_before,
                f"DB: шаблон с id {dbdt_id} существовал в истории до создания",
            )
            self.udb.check_template_history(dbdt_id, action_type=DiscountTemplateAction.CREATE, number_history=1)
            self.udb.discount_template_compare(dbdt_id)

    @allure.title("20. Сохранение истории изменения шаблона биллинговых скидок")
    @allure.id(937068)
    def test_save_billing_discount(self) -> None:
        discount_scheme_name_ru = f"Тестовая_биллинговая_скидка_{generate_russian_string(6)}"
        discount_scheme_name_en = f"Test_billing_discount_{generate_english_string(6)}"

        with allure.step("Запрос в UDB — список шаблонов биллинговых скидок"):
            self.udb.get_discount_templates_history()

        self.discount_page.open_discount_charges_setting_page()
        self.discount_page.create_discount_template(
            discount_scheme_name_ru=discount_scheme_name_ru,
            discount_scheme_name_en=discount_scheme_name_en,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        with allure.step("Проверка предусловия: в UDB есть запись о созданном шаблоне (CREATE)"):
            dbdt_id = self.udb.get_template_id_by_name(discount_scheme_name_ru)
            entry_before = self.udb.check_template_history(
                dbdt_id, action_type=DiscountTemplateAction.CREATE, number_history=1
            )

        self.discount_page.find_and_select_template(discount_scheme_name_ru)
        self.discount_page.edit_discount_action_size(discount_size="15")

        with allure.step("Повторный запрос в UDB — number_history увеличен на 1, action_type=UPDATE"):
            self.udb.check_template_history(
                dbdt_id, action_type=DiscountTemplateAction.UPDATE, number_history=entry_before["number_history"] + 1
            )
            self.udb.discount_template_compare(dbdt_id)

    @allure.title("21. Сохранение истории удаления шаблона биллинговых скидок")
    @allure.id(937144)
    def test_save_billing_discount_remove(self) -> None:
        discount_scheme_name_ru = f"Тестовая_биллинговая_скидка_{generate_russian_string(6)}"
        discount_scheme_name_en = f"Test_billing_discount_{generate_english_string(6)}"

        with allure.step("Запрос в UDB — список шаблонов биллинговых скидок"):
            self.udb.get_discount_templates_history()

        self.discount_page.open_discount_charges_setting_page()
        self.discount_page.create_discount_template(
            discount_scheme_name_ru=discount_scheme_name_ru,
            discount_scheme_name_en=discount_scheme_name_en,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        with allure.step("Проверка предусловия: в UDB есть запись о созданном шаблоне (CREATE)"):
            dbdt_id = self.udb.get_template_id_by_name(discount_scheme_name_ru)
            entry_before = self.udb.check_template_history(
                dbdt_id, action_type=DiscountTemplateAction.CREATE, number_history=1
            )

        self.discount_page.find_and_select_template(discount_scheme_name_ru)
        self.discount_page.delete_selected_template()

        with allure.step("Повторный запрос в UDB — number_history увеличен на 1, action_type=DELETE"):
            self.udb.check_template_history(
                dbdt_id, action_type=DiscountTemplateAction.DELETE, number_history=entry_before["number_history"] + 1
            )
            self.udb.discount_template_compare(dbdt_id)

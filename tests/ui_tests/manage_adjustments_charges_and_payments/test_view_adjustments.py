import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.download_helper import CheckFile
from models.user import IndividualClient
from pages.client_profile_page import ClientProfilePage
from pages.nbss.finances.adjustments_page import AdjustmentsPage


@allure.suite("E2E_77 Управление корректировками начислений и платежей")
@allure.sub_suite("Просмотр корректировок")
@pytest.mark.regress
class TestViewAdjustment:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.payment_api = PaymentsRequests(api_request_context)
        self.billing_api = BillingRequests(api_request_context)
        self.adjustment_api = AdjustmentRequests(api_request_context)

        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.adjustments_page = AdjustmentsPage(nexign_ui_stand_login)
        self.client = create_user_with_agreement_and_account
        self.balance = 100.00
        self.adjustment_sum = generate_random_number(2)

    @allure.title("Просмотр списка корректировок")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588495)
    def test_view_adjustment_list(self, base_url: str) -> None:
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{self.client.agreements[0].accounts[0].id}/account"
        )
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Финансы' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()

    @allure.title("Просмотр списка корректировок (Выгрузка в файл)")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=367529056",
        name="ПМИ Создание корректировки к ранее выставленным счетам и СФ",
    )
    @allure.id(588497)
    def test_view_adjustment_list_export_in_file(self, base_url: str, remove_file_from_download_folder: list) -> None:
        adjustment_count = 1

        with allure.step("Выполнение предусловий"):
            with allure.step(f"Добавление платежа для ЛС {self.client.agreements[0].accounts[0].id}"):
                self.payment_api.create_default_payment(self.client.agreements[0].accounts[0].id, self.balance)
                self.personal_account_api.wait_check_current_main_balance(
                    self.client.agreements[0].accounts[0].id, self.balance
                )
                payment_data = self.payment_api.get_payments(self.client.agreements[0].accounts[0].id).json()["items"][0]
                payment_id = int(payment_data["paymentId"])
                billing_payment_id = int(payment_data["paymentItem"]["paymentItemId"])

            with allure.step("Создание отрицательной корректировки платежа"):
                self.payment_api.wait_check_add_adjustment_for_payment(payment_id)
                self.adjustment_api.create_adjustment(
                    adjustment_type_id=3,
                    adjustment_reason_id=3,
                    billing_payment_id=billing_payment_id,
                    billing_profile_id=self.billing_api.get_billing_profile_id(self.client.agreements[0].accounts[0].id),
                    amount=self.adjustment_sum,
                )
                self.adjustment_api.wait_adjustment_status(self.client.agreements[0].accounts[0].id)

            self.client_profile.open(
                f"{base_url}customer-hierarchy-management/accounts/{self.client.agreements[0].accounts[0].id}/account"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Перейти на форму 'Финансы' - 'Корректировки'"):
            self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Корректировки")
            self.adjustments_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Корректировки")
            self.adjustments_page.check_buttons()
            self.adjustments_page.locators.ADJUSTMENTS.wait_to_have_count(adjustment_count)

        with allure.step("Нажать кнопку 'Экспортировать в XLS файл'"):
            headers, adjustment_list = self.adjustments_page.get_info_about_adjustment_table()
            with self.adjustments_page.page.expect_download(timeout=20000) as download_info:
                self.adjustments_page.locators.EXPORT_TO_XLS_BTN.click()
            download = download_info.value
            file_name = download.suggested_filename
            self.file_check = CheckFile(file_name)
            download.save_as(self.file_check.path)
            remove_file_from_download_folder.append(file_name)
            self.file_check.check_excel_file_table(headers, adjustment_list)

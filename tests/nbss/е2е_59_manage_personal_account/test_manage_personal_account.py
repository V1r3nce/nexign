import datetime

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from common.helpers.checker import wait_that
from models.context import test_context
from models.user import IndividualClient
from pages.locators.nbss.dynamic_form_elements import PersonalAccountForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.payments_page import PaymentsPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_59 Управление лицевым счетом")
@allure.suite("E2E_59 Управление лицевым счетом")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=694466095",
    name="RMBSS-1195 Управление лицевым счетом",
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestManagePersonalAccount:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        create_individual_user_with_agreement: IndividualClient,
        api_request_context: APIRequestContext,
        base_url,
    ) -> None:
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.personal_account_form = PersonalAccountForm(nexign_ui_stand_login)
        self.payment_page = PaymentsPage(nexign_ui_stand_login)

    @allure.title("[01] Создание ЛС с предоплатной схемой оплаты")
    @allure.description("[01] Создание ЛС с предоплатной схемой оплаты")
    @allure.id(706945)
    def test_create_prepaid_personal_account(self, base_url: str) -> None:
        with allure.step("Создать предоплатный лицевой счет"):
            self.personal_account_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
            self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
            self.personal_account_page.add_personal_account()
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00", timeout=7000)

        with allure.step("Доступность приема платежей"):
            self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")
            self.payment_page.payment_elements.CREATE_PAYMENT_BTN.wait_to_be_enabled()

    @allure.title("[02] Создание ЛС с постоплатной схемой оплаты")
    @allure.description("[02] Создание ЛС с постоплатной схемой оплаты")
    @allure.id(706946)
    def test_create_postpaid_personal_account(self, base_url: str) -> None:
        with allure.step("Создать постоплатный лицевой счет"):
            self.personal_account_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
            self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
            self.personal_account_page.add_personal_account("Постоплатный")
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00", timeout=7000)

        with allure.step("Доступен прием платежей"):
            self.client_profile_page.locators.BURGER_MENU.select_by_value("Финансы > Платежи")
            self.payment_page.payment_elements.CREATE_PAYMENT_BTN.wait_to_be_enabled()

    @allure.title("[03] Редактирование атрибутов лицевого счета с предоплатной схемой оплаты")
    @allure.description("[03] Редактирование атрибутов лицевого счета с предоплатной схемой оплаты")
    @allure.id(706947)
    def test_update_prepaid_personal_account(self, base_url: str) -> None:
        with allure.step("Создать предоплатный лицевой счет"):
            self.personal_account_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
            self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
            self.personal_account_page.add_personal_account()
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00", timeout=7000)

        with allure.step("Изменить лицевой счет"):
            self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
            self.personal_account_form.TITLE.wait_to_be_visible()
            self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
            self.personal_account_form.SAVE_BTN.click()
            self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00")

    @allure.title("[04] Редактирование атрибутов лицевого счета с постоплатной схемой оплаты")
    @allure.description("[04] Редактирование атрибутов лицевого счета с постоплатной схемой оплаты")
    @allure.id(706948)
    def test_update_postpaid_personal_account(self, base_url: str) -> None:
        with allure.step("Создать постоплатный лицевой счет"):
            self.personal_account_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
            self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
            self.personal_account_page.add_personal_account("Постоплатный")
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00", timeout=7000)

        with allure.step("Изменить лицевой счет"):
            self.personal_account_page.locators.EDIT_DETAILS_ACCOUNT_BTN.click()
            self.personal_account_form.TITLE.wait_to_be_visible()
            self.personal_account_form.PAYMENT_METHOD.select_by_value("Предоплатный")
            self.personal_account_form.SAVE_BTN.click()
            self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible()
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00")

    @allure.title("[05] Обновление баланса на карточке ЛС")
    @allure.description("[05] Обновление баланса на карточке ЛС")
    @allure.id(707230)
    def test_automatic_updates_balance(self, base_url: str) -> None:
        with allure.step("Создать предоплатный лицевой счет"):
            self.personal_account_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
            self.personal_account_page.locators.PERSONAL_ACCOUNTS_TAB.click()
            self.personal_account_page.add_personal_account()
            self.payment_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00", timeout=7000)

        with allure.step("Дождаться обновления баланса"):
            self.payment_page.payment_elements.USER_BALANCE_UPDATE_TIME.wait_to_be_visible()
            update_value_text = self.payment_page.payment_elements.USER_BALANCE_UPDATE_TIME.text.split()[2]
            update_time = datetime.datetime.strptime(update_value_text, "%H:%M:%S")
            wait_that(
                lambda: update_time
                < datetime.datetime.strptime(
                    self.payment_page.payment_elements.USER_BALANCE_UPDATE_TIME.text.split()[2], "%H:%M:%S"
                ),
                timeout=10,
                sleep_seconds=2,
                exception=AssertionError,
                message="Время обновления баланса не изменилось за 10 секунд",
            )

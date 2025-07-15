import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL
from models.user import OrganizationClient
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.inquiries_elements import CloseInquiryForm, ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm


@allure.suite("E2E_62_34 Отмена продажи (заявки)")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=736548885", name='Сценарий "Отмена продажи (УПК)"')
@pytest.mark.regress
class TestSaleCancellation:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_organization_with_agreement_and_account: OrganizationClient,
    ) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.create_request_form = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(nexign_ui_stand_login)
        self.close_inquiry_form = CloseInquiryForm(nexign_ui_stand_login)
        self.client = create_organization_with_agreement_and_account
        self.agreement_date = get_current_datetime_string(False)

    def create_sale_add_product_and_check_configuration(self):
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{self.client.user_id}/overview")

        with allure.step("Нажать на кнопку 'Создание продажи и управление услугами'"):
            self.inquiries_page.locators.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"], timeout=10000)
            self.inquiries_page.locators.CREATE_APPLICATION.click()
            self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=10000)

        with allure.step("Заполнить поля, нажать 'Сохранить'"):
            self.create_request_form.CHOOSE_AGREEMENT_BTN.select_by_value(value="Вручную")
            self.create_request_form.SAVE_BTN.click()
            self.inquiries_page.check_open_sale_inquiry()
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")

        with allure.step("Добавить продукт, нажать 'Проверить конфигурацию'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.locators.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.inquiries_page.locators.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.inquiries_page.locators.product_offer_form.SEARCH_BTN.click()
            product = self.inquiries_page.choose_product_offer_with_name("Гибкий бизнес")
            self.product_offer_form.ADD_BTN.click()

            with allure.step("Бронирование ресурсов"):
                self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
                self.product_edit_form.RESOURCES_TAB.click()
                product.phone_number = self.inquiries_page.auto_reserve_phone_number_resources()[1]
                self.product_edit_form.INNER_CANCEL_BTN.click()

            self.inquiries_page.check_configuration()

    def close_inquiry_and_check(self, reason: str, step: str) -> None:
        with allure.step("Нажать 'Закрыть заявку'"):
            self.inquiries_page.locators.CLOSE_INQUIRY_BTN.wait_to_have_text("Закрыть заявку")
            self.inquiries_page.locators.CLOSE_INQUIRY_BTN.click()
            self.close_inquiry_form.TITLE.wait_to_have_text("Закрытие заявки")

        with allure.step("Выбрать причину, нажать на кнопку 'Закрыть'"):
            self.close_inquiry_form.CLOSE_REASON.select_by_value(reason)
            self.close_inquiry_form.INNER_ACCEPT_BTN.click()
            self.close_inquiry_form.FORM.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто")
            self.inquiries_page.locators.CLIENT.click()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.NO_SUBSCRIBERS_BLOCK.wait_to_be_visible()

        with allure.step("Перейти в Заявки"):
            self.inquiries_page.locators.CLIENT.click()
            self.client_profile.locators.REQUESTS_TAB.click()
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.check_request(request_type="Продажа и управление услугами", status="Закрыто", step=step)
            self.client_profile.locators.REQUESTS.click(0)

        with allure.step("Нажать на закрытую заявку, перейти в 'Карточка продажи'"):
            self.client_profile.locators.REQUEST_NUMBER.click(0)
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами"), timeout=10000
            )
            self.inquiries_page.click_tab("Карточка продажи")
            self.inquiries_page.locators.CLOSE_REASON.wait_to_have_text(reason)

    @allure.title('01. Отмена продажи на этапе "Управление составом заказа"')
    @allure.id(620097)
    def test_cancel_on_step_management_order(self, base_url: str) -> None:
        reason = "Отказ клиента"
        step = "Управление составом заказа"
        self.create_sale_add_product_and_check_configuration()
        self.close_inquiry_and_check(reason, step)

    @allure.title('02. Отмена продажи на этапе "Формирование и согласование документа КП"')
    @allure.id(620791)
    def test_cancel_on_step_commercial_offer(self, base_url: str) -> None:
        reason = "Отказ клиента"
        step = "Формирование и согласование документа КП"
        self.create_sale_add_product_and_check_configuration()
        self.inquiries_page.click_next_and_step(step)
        self.close_inquiry_and_check(reason, step)

    @allure.title('03. Отмена продажи на этапе "Регистрация/Выбор договора"')
    @allure.id(621593)
    def test_cancel_on_step_create_use_agreement(self, base_url: str) -> None:
        reason = "Ошибочная"
        step = "Регистрация/Выбор договора"
        self.create_sale_add_product_and_check_configuration()
        self.inquiries_page.click_next_and_step(step)
        self.close_inquiry_and_check(reason, step)

    @allure.title('04. Отмена продажи на этапе "Распределение продуктов заказа по ЛС"')
    @allure.id(621612)
    def test_cancel_on_step_distribution_products_by_account(self, base_url: str) -> None:
        reason = "Ошибочная"
        step = "Распределение продуктов заказа по ЛС"
        self.create_sale_add_product_and_check_configuration()
        self.inquiries_page.click_next_and_step("Регистрация/Выбор договора")
        self.inquiries_page.choose_agreement(self.client.agreements[0].number, self.agreement_date)
        self.inquiries_page.click_next(step)
        self.close_inquiry_and_check(reason, step)

    @allure.title('05. Отмена продажи на этапе "Формирование заказа на комплекты документов"')
    @allure.id(621675)
    def test_cancel_on_step_formation_order_for_kits_documents(self, base_url: str) -> None:
        reason = "Отсутствует тех.возможность"
        step = "Формирование заказа на комплекты документов"
        self.create_sale_add_product_and_check_configuration()
        self.inquiries_page.click_next_and_step("Регистрация/Выбор договора")
        self.inquiries_page.choose_agreement(self.client.agreements[0].number, self.agreement_date)
        self.inquiries_page.click_next("Распределение продуктов заказа по ЛС")
        self.inquiries_page.choose_account(self.client.agreements[0].accounts[0].number)
        self.inquiries_page.click_next_and_step(step)
        self.close_inquiry_and_check(reason, step)

    @allure.title('06. Отмена продажи на этапе "Формирование и подписание документа Договор/ДС"')
    @allure.id(621703)
    def test_cancel_on_step_generating_and_signing_agreement(self, base_url: str) -> None:
        reason = "Отсутствует тех.возможность"
        step = "Формирование и подписание документа Договор/ДС"
        self.create_sale_add_product_and_check_configuration()
        self.inquiries_page.click_next_and_step("Регистрация/Выбор договора")
        self.inquiries_page.choose_agreement(self.client.agreements[0].number, self.agreement_date)
        self.inquiries_page.click_next("Распределение продуктов заказа по ЛС")
        self.inquiries_page.choose_account(self.client.agreements[0].accounts[0].number)
        self.inquiries_page.click_next_and_step("Формирование документов", step)
        self.close_inquiry_and_check(reason, step)

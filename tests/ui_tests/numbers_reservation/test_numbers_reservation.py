import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import get_current_datetime_string
from pages.client_profile_page import ClientProfilePage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberVolumePage, NumberInfo
from pages.locators.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.inquiries_page import InquiriesPage, ProductEditForm, ChangeResourcesForm
from pages.locators.select_product_offers_form import SelectProductOffersForm
from tests.ui_tests.numbers_reservation.conftest import ClientInfo


class TestNumbersReservation:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, lis_stand_login_new_page: Page, create_account: ClientInfo):
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.create_sale = CreateSalesAndServiceManagement(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.product_edit_form = ProductEditForm(nexign_ui_stand_login)
        self.change_resources_form = ChangeResourcesForm(nexign_ui_stand_login)
        self.home_page_lis = HomeLisPage(lis_stand_login_new_page)
        self.number_volume_page = NumberVolumePage(lis_stand_login_new_page)
        self.client = create_account
        self.agreement_date = get_current_datetime_string(is_full_format=False)

    @allure.suite("E2E_15 Бронирование номеров")
    @allure.title("02. Бронирование ресурсов на шаге продажи")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=689024215",
                 name="NBSS.TPM.15 [2.0.3] Бронирование номеров")
    @allure.description('Бронирование номера на шаге продажи')
    @allure.id(581192)
    def test_reserve_resource_at_sale(self, base_url: str):

        with allure.step("Перейти на форму подготовленного Лицевого счета"):
            self.client_profile.bring_to_front(self.client_profile.page.title())
            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Нажать на кнопку 'Создание продажи и управления услугами'"):
            self.client_profile.locators.CREATE_APPLICATION.click()
            self.create_sale.CREATE_FORM.wait_to_be_visible()
            self.create_sale.TITLE.to_contain_text("Создание продажи и управление услугами")

        with allure.step(
                "Заполнить поля: Номер договора, Лицевой счет, Обязательное поле: 'Создание дополнительного соглашения'"):
            self.create_sale.SELECTED_SALE.select_by_value(
                value=f'{self.client.agreement_number} от {self.agreement_date}')
            self.create_sale.SALE_ACCOUNT.select_by_value(value=f'{self.client.account_number}')
            self.create_sale.CREATE_ADD_AGREEMENT.to_be_enabled()
            self.create_sale.TITLE_CREATE_ADD_AGREEMENT.to_have_class(re.compile(r".*ant-form-item-required.*"))
            self.create_sale.CREATE_ADD_AGREEMENT.select_by_value(value='Сформировать автоматически')
            self.create_sale.CREATE_ADD_AGREEMENT.to_be_enabled()

        with allure.step("Нажать 'Сохранить'"):
            self.create_sale.SAVE_BTN.click()
            self.create_sale.CREATE_FORM.not_to_be_visible()
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"),
                                                               timeout=10000)
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.STEP_TITLE.to_contain_text("Наполнение и уточнение коммерческого заказа")

        with allure.step("Добавить продукт"):
            self.inquiries_page.ADD_SALE_BTN.click()
            self.product_offer_form.TITLE.to_contain_text("Выбор продуктовых предложений")
            with allure.step("Выбрать: Монопродукт, Мобильная связь"):
                self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()
            with allure.step("В появившемся списке монопродуктов нажать кнопку 'Выбрать' у подходящего продукта"):
                self.product_offer_form.PRODUCT_CARD.wait_elements_visible(0)
                product_name = self.product_offer_form.PRODUCT_CARD_NAME[0].text
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.TITLE.not_to_be_visible()

        with allure.step("Выбранный монопродукт добавлен в коммерческий заказ"):
            self.inquiries_page.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.ADDED_PRODUCT_NAMES[0].to_contain_text(product_name)

        with allure.step("Открыть форму редактирования продукта"):
            self.inquiries_page.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.TITLE.to_contain_text(product_name)

        with allure.step("Автоматически подобрать ресурсы"):
            self.product_edit_form.RESOURCES_TAB.click()
            phone_number = self.product_edit_form.auto_reserve_phone_number_resources()

        with allure.step("Перейти в систему 'Единое ресурсное окно' (LIS)"):
            self.home_page_lis.bring_to_front(self.home_page_lis.page.title())
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step(f"Найти и проверить номер {phone_number}"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
            self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.check_number_params(number=phone_number,
                                                        params=NumberInfo(color="dark_red", is_block=True))

    @allure.suite("E2E_15 Бронирование номеров")
    @allure.title("03. Снятие бронирования с номера с последующим бронированием другого номера")
    @allure.tag("can_auth", "success")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=689024215",
                 name="NBSS.TPM.15 [2.0.3] Бронирование номеров")
    @allure.description('Бронирование номера на шаге продажи')
    @allure.id(581790)
    def test_cansel_reserve_and_reserve_new_number(self, base_url: str):

        with allure.step("Перейти на форму подготовленного Лицевого счета"):
            self.client_profile.bring_to_front(self.client_profile.page.title())
            self.client_profile.open(f"{base_url}customer-hierarchy-management/accounts/{self.client.account_id}/account")
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Нажать на кнопку 'Создание продажи и управления услугами'"):
            self.client_profile.locators.CREATE_APPLICATION.click()
            self.create_sale.CREATE_FORM.wait_to_be_visible()
            self.create_sale.TITLE.to_contain_text("Создание продажи и управление услугами")

        with allure.step(
                "Заполнить поля: Номер договора, Лицевой счет, Обязательное поле: 'Создание дополнительного соглашения'"):
            self.create_sale.SELECTED_SALE.select_by_value(
                value=f'{self.client.agreement_number} от {self.agreement_date}')
            self.create_sale.SALE_ACCOUNT.select_by_value(value=f'{self.client.account_number}')
            self.create_sale.CREATE_ADD_AGREEMENT.to_be_enabled()
            self.create_sale.TITLE_CREATE_ADD_AGREEMENT.to_have_class(re.compile(r".*ant-form-item-required.*"))
            self.create_sale.CREATE_ADD_AGREEMENT.select_by_value(value='Сформировать автоматически')
            self.create_sale.CREATE_ADD_AGREEMENT.to_be_enabled()

        with allure.step("Нажать 'Сохранить'"):
            self.create_sale.SAVE_BTN.click()
            self.create_sale.CREATE_FORM.not_to_be_visible()
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"),
                                                               timeout=10000)
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.STEP_TITLE.to_contain_text("Наполнение и уточнение коммерческого заказа")

        with allure.step("Добавить продукт"):
            self.inquiries_page.ADD_SALE_BTN.click()
            self.product_offer_form.TITLE.to_contain_text("Выбор продуктовых предложений")
            with allure.step("Выбрать: Монопродукт, Мобильная связь"):
                self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()
            with allure.step("В появившемся списке монопродуктов нажать кнопку 'Выбрать' у подходящего продукта"):
                self.product_offer_form.PRODUCT_CARD.wait_elements_visible(0)
                product_name = self.product_offer_form.PRODUCT_CARD_NAME[0].text
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.TITLE.not_to_be_visible()

        with allure.step("Выбранный монопродукт добавлен в коммерческий заказ"):
            self.inquiries_page.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.ADDED_PRODUCT_NAMES[0].to_contain_text(product_name)

        with allure.step("Открыть форму редактирования продукта"):
            self.inquiries_page.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.TITLE.to_contain_text(product_name)

        with allure.step("Автоматически подобрать ресурсы"):
            self.product_edit_form.RESOURCES_TAB.click()
            phone_number = self.product_edit_form.auto_reserve_phone_number_resources()

        with allure.step("Перейти в систему 'Единое ресурсное окно' (LIS)"):
            self.home_page_lis.bring_to_front(self.home_page_lis.page.title())
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            self.home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            self.number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step(f"Найти и проверить номер {phone_number}"):
            self.number_volume_page.locators.SEARCH_BTN.click()
            self.number_volume_page.locators.MSISDN_FILTER_BTN.click()
            self.number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.check_number_params(number=phone_number,
                                                        params=NumberInfo(color="dark_red", is_block=True))

        with allure.step("Нажать на кнопку 'Замена ресурса' для ручного выбора номера"):
            self.client_profile.bring_to_front(self.client_profile.page.title())
            self.product_edit_form.CHANGE_RESOURCES_BTN.click()
            self.change_resources_form.FORM.wait_to_be_visible()
            self.change_resources_form.TITLE.to_contain_text("Замена ресурса")
            self.change_resources_form.SUBTITLE.to_contain_text(f"Заменяемый ресурс: {phone_number}")
            self.change_resources_form.INNER_ACCEPT_BTN.not_to_be_enabled()

        with allure.step("Выбрать новый номер для бронирования"):
            self.change_resources_form.NUMBERS.wait_elements_visible(0)
            new_phone_number = self.change_resources_form.NUMBERS[0].text
            self.change_resources_form.NUMBERS[0].click()
            self.change_resources_form.INNER_ACCEPT_BTN.to_be_enabled()
            self.change_resources_form.INNER_ACCEPT_BTN.click()
            self.change_resources_form.FORM.not_to_be_visible()
            self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
            self.product_edit_form.PHONE_NUMBER.not_to_contain_text(phone_number)
            self.product_edit_form.PHONE_NUMBER.wait_to_have_text(new_phone_number)

        with (allure.step("Проверить выбранный ранее номера в системе 'Единое ресурсное окно' (LIS)")):
            self.number_volume_page.bring_to_front(self.number_volume_page.page.title())
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.check_number_params(number=phone_number,
                                                        params=NumberInfo(color="dark_green", is_block=False))

        with allure.step("Проверить текущий номер в системе 'Единое ресурсное окно' (LIS)"):
            self.number_volume_page.locators.MSISDN_FILTER_INPUT.fill(new_phone_number)
            self.number_volume_page.locators.FILTER_SEARCH_BTN.click()
            self.number_volume_page.check_number_params(number=new_phone_number,
                                                        params=NumberInfo(color="dark_red", is_block=True))

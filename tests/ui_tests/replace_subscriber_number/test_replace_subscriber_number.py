import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL_LIS
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberInfo, NumberVolumePage
from pages.locators.dynamic_form_elements import ProductInfo, ReplaceResource
from pages.locators.inquiries_page import InquiriesPage


@allure.suite("E2E_45 Замена номера абонента")
class TestReplaceSubscriberNumber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login: Page, api_request_auth_context: APIRequestContext) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.product_info_form = ProductInfo(nexign_ui_stand_login)
        self.replace_resource_form = ReplaceResource(nexign_ui_stand_login)

    @allure.title("01. Успешная замена номера")
    @allure.tag("can_auth", "success")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=697149245", name="E2E_45 Замена номера")
    @allure.description("Бронирование номера на шаге продажи")
    @allure.id(591144)
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_success_replace_number(self, create_user: int, base_url: str) -> None:
        with allure.step("Проведение продажи и начисление платежа клиенту"):
            user_id = create_user
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{user_id}/overview")
            product = self.inquiries_page.sale_phone_number()
            account_id = self.personal_account_api.get_personal_accounts("customer", user_id).json()["items"][0][
                "accountId"
            ]
            replace_number_price = 100.00
            payment_data = PaymentInfo(
                item_type="CUSTOMER_ACCOUNT",
                amount=product.one_time_payment + product.subscription_fee + replace_number_price,
                currency_code="RUB",
                account_id=account_id,
                payment_method_type="CASH",
            )
            self.payment_api.create_payment(payment_data)

        with allure.step("Перейти с карточки клиента во вкладку 'Продукты'"):
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.check_balance(0, 100.00)
            self.client_profile.locators.PRODUCTS_TAB.click()

        self.client_profile.click_first_product(subscriber=product.phone_number, product_name=product.product_name)

        with allure.step("Перейти на вкладку 'Ресурсы'"):
            self.product_info_form.PRODUCT_NAME.wait_to_have_text(product.product_name)
            self.product_info_form.RESOURCES_TAB.click()

        with allure.step("Напротив Телефонного номера нажать на три точки, выбрать 'Замена'"):
            self.product_info_form.PHONE_NUMBER_BLOCK.wait_to_be_visible()
            self.product_info_form.PHONE_NUMBER.wait_to_have_text(product.phone_number)
            self.product_info_form.MENU_PHONE_NUMBER_BTN.hover()
            self.product_info_form.REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.wait_to_be_visible()
            self.replace_resource_form.check_required_fields()

        with allure.step("В ресурсе на замену напротив 'Номер телефона' нажать на кнопку '...'"):
            self.replace_resource_form.CHOICE_PHONE_NUMBER_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.wait_to_be_visible()

        with allure.step("Выбрать номер телефона"):
            self.replace_resource_form.ALLOWED_NUMBERS.wait_elements_visible(0)
            new_phone_number = self.replace_resource_form.ALLOWED_NUMBERS[0].text
            self.replace_resource_form.ALLOWED_NUMBERS[0].click()

        with allure.step("Нажать кнопку 'Выбрать'"):
            self.replace_resource_form.INNER_ACCEPT_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.not_to_be_visible()
            self.replace_resource_form.INFORMATION_MESSAGE.wait_to_be_visible()
            self.replace_resource_form.INFORMATION_MESSAGE.wait_to_have_text(
                "Тип замены - новый номер. Стоимость: 100.00 RUB"
            )

        with allure.step("Нажать 'Выполнить замену'"):
            self.replace_resource_form.DO_REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.not_to_be_visible()
            self.product_info_form.CROSS_BTN.click()

        with allure.step("Проверить, что автоматически создана заявка на замену номера"):
            self.client_profile.locators.REQUESTS_TAB.click()
            self.client_profile.locators.REQUESTS.wait_to_have_count(2)
            self.client_profile.locators.REQUEST_TYPE[1].wait_to_have_text("Замена ресурса")
            self.client_profile.wait_request_status(index=1, status="Закрыто")

        with allure.step(
            f"Проверить, что списана комиссия за смену номера, баланс уменьшился на {replace_number_price} руб"
        ):
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.check_balance(0, 0.00)

        with allure.step("Нажать кнопку 'Обновить'"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_elements_visible(0)
            self.client_profile.locators.SUBSCRIBER[0].wait_to_have_text(new_phone_number)

        with allure.step("Перейти в систему LIS"):
            lis_page = self.base_page.open_new_tab()
            home_lis_page = HomeLisPage(lis_page)
            home_lis_page.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
            home_lis_page.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            home_lis_page.locators.NUMBER_VOLUME_BTN.click()
            number_volume_page = NumberVolumePage(lis_page)
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step(f"Найти предыдущий номер телефона {product.phone_number}"):
            number_volume_page.locators.SEARCH_BTN.click()
            number_volume_page.locators.MSISDN_FILTER_BTN.click()
            number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(product.phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=product.phone_number, params=NumberInfo(status="Свободен", state="Освобождён")
            )

        with allure.step(f"Найти новый номер телефона {new_phone_number}"):
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(new_phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=new_phone_number, params=NumberInfo(status="Занят", state="Распределён")
            )

    @allure.title("02. Замена номера (недостаточно средств)")
    @allure.tag("can_auth", "success")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=697149245", name="E2E_45 Замена номера")
    @allure.id(591145)
    @pytest.mark.regress
    def test_replace_number_with_zero_balance(self, create_user: int, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        product = self.inquiries_page.sale_phone_number()

        with allure.step("Перейти с карточки клиента во вкладку 'Продукты'"):
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()

        self.client_profile.click_first_product(subscriber=product.phone_number, product_name=product.product_name)

        with allure.step("Перейти на вкладку 'Ресурсы'"):
            self.product_info_form.PRODUCT_NAME.wait_to_have_text(product.product_name)
            self.product_info_form.RESOURCES_TAB.click()

        with allure.step("Напротив Телефонного номера нажать на три точки, выбрать 'Замена'"):
            self.product_info_form.PHONE_NUMBER_BLOCK.wait_to_be_visible()
            self.product_info_form.PHONE_NUMBER.wait_to_have_text(product.phone_number)
            self.product_info_form.MENU_PHONE_NUMBER_BTN.hover()
            self.product_info_form.REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.wait_to_be_visible()
            self.replace_resource_form.check_required_fields()

        with allure.step("В ресурсе на замену напротив 'Номер телефона' нажать на кнопку '...'"):
            self.replace_resource_form.CHOICE_PHONE_NUMBER_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.wait_to_be_visible()

        with allure.step("Выбрать номер телефона"):
            self.replace_resource_form.ALLOWED_NUMBERS.wait_elements_visible(0)
            self.replace_resource_form.ALLOWED_NUMBERS[0].click()

        with allure.step("Нажать кнопку 'Выбрать'"):
            self.replace_resource_form.INNER_ACCEPT_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.not_to_be_visible()
            self.replace_resource_form.PHONE_NUMBER_HELP.wait_to_have_text("На счету недостаточно средств.")
            self.replace_resource_form.DO_REPLACE_BTN.not_to_be_enabled()

    @allure.title("03. Замена номера на занятый")
    @allure.tag("can_auth", "success")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=697149245", name="E2E_45 Замена номера")
    @allure.id(593160)
    @pytest.mark.regress
    def test_replace_for_busy_number(self, create_user: int, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{create_user}/overview")
        product = self.inquiries_page.sale_phone_number()

        with allure.step("Перейти в систему LIS"):
            lis_page = self.base_page.open_new_tab()
            home_lis_page = HomeLisPage(lis_page)
            home_lis_page.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
            home_lis_page.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            home_lis_page.locators.NUMBER_VOLUME_BTN.click()
            number_volume_page = NumberVolumePage(lis_page)
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Найти номер со статусом 'Занят'"):
            number_volume_page.locators.SEARCH_BTN.click()
            number_volume_page.locators.STATUS_FILTER_BTN.click()
            number_volume_page.locators.STATUS_OPTION_BUSY.click()
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            busy_number = number_volume_page.locators.PHONE_NUMBERS[0].text.strip()

        with allure.step("Перейти с карточки клиента во вкладку 'Продукты'"):
            self.base_page.bring_to_front(self.base_page.page.title())
            number_volume_page.close_page_by_index(-1)
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()

        self.client_profile.click_first_product(subscriber=product.phone_number, product_name=product.product_name)

        with allure.step("Перейти на вкладку 'Ресурсы'"):
            self.product_info_form.PRODUCT_NAME.wait_to_have_text(product.product_name)
            self.product_info_form.RESOURCES_TAB.click()

        with allure.step("Напротив Телефонного номера нажать на три точки, выбрать 'Замена'"):
            self.product_info_form.PHONE_NUMBER_BLOCK.wait_to_be_visible()
            self.product_info_form.PHONE_NUMBER.wait_to_have_text(product.phone_number)
            self.product_info_form.MENU_PHONE_NUMBER_BTN.hover()
            self.product_info_form.REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.wait_to_be_visible()

        with allure.step("В ресурсе на замену напротив 'Номер телефона' нажать на кнопку '...'"):
            self.replace_resource_form.CHOICE_PHONE_NUMBER_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.wait_to_be_visible()
            self.replace_resource_form.FIND_NUMBER_INPUT.fill(f"substr(:0, {len(busy_number)}) = '{busy_number}'")
            self.replace_resource_form.ALLOWED_NUMBERS.wait_elements_visible(0)
            self.replace_resource_form.EMPTY_ALLOWED_NUMBERS_LIST.wait_to_be_visible()

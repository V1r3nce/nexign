import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.env_helper import BASE_URL_LIS
from models.context import test_context
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberInfo, NumberVolumePage
from pages.locators.nbss.dynamic_form_elements import ProductInfoForm, ReplaceResource
from pages.locators.nbss.inquiries_elements import ReserveResourcesForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.suite("E2E_45 Замена номера абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=697149245", name="E2E_45 Замена номера")
@pytest.mark.regress
@pytest.mark.lis
@pytest.mark.nbss_portal
class TestReplaceSubscriberNumber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login, create_individual_user: IndividualClient) -> None:
        self.client_request_api = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.payment_api = PaymentsRequests()
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.product_info_form = ProductInfoForm()
        self.replace_resource_form = ReplaceResource()
        self.inquiries_page = InquiriesPage()
        self.reserve_form = ReserveResourcesForm()
        self.client = create_individual_user
        self.inquiry = self.client_request_api.product_sale()

    @allure.title("01. Успешная замена номера")
    @allure.description("Бронирование номера на шаге продажи")
    @allure.id(591144)
    @pytest.mark.smoke
    def test_success_replace_number(self, base_url: str) -> None:
        with allure.step("Начисление платежа клиенту"):
            replace_number_price = 100.00
            self.payment_api.create_default_payment(
                test_context.client.agreements[0].accounts[0].id,
                self.inquiry.product.one_time_payment + self.inquiry.product.subscription_fee + replace_number_price,
            )
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, replace_number_price
            )

        with allure.step("Перейти с карточки клиента во вкладку 'Продукты'"):
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_TAB.click()

        self.client_profile.click_first_product(
            subscriber=self.inquiry.product.phone_number, product_name=self.inquiry.product.product_name
        )

        with allure.step("Перейти на вкладку 'Ресурсы'"):
            self.product_info_form.PRODUCT_NAME.wait_to_have_text(self.inquiry.product.product_name)
            self.product_info_form.RESOURCES_TAB.click()

        with allure.step("Напротив Телефонного номера нажать на три точки, выбрать 'Замена'"):
            self.product_info_form.PHONE_NUMBER_BLOCK.wait_to_be_visible()
            self.product_info_form.PHONE_NUMBER.wait_to_have_text(self.inquiry.product.phone_number)
            self.product_info_form.MENU_PHONE_NUMBER_BTN.click()
            self.product_info_form.REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.wait_to_be_visible()
            self.replace_resource_form.check_required_fields()

        with allure.step("В ресурсе на замену напротив 'Номер телефона' нажать на кнопку '...'"):
            self.replace_resource_form.CHOICE_PHONE_NUMBER_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.wait_to_be_visible()

        with allure.step("Выбрать номер телефона"):
            new_phone_number = self.inquiries_page.reserve_number()
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
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.check_balance(0, 0.00)

        with allure.step("Нажать кнопку 'Обновить'"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_UPDATE_BTN.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_elements_visible(0)
            self.client_profile.locators.SUBSCRIBER[0].wait_to_have_text(new_phone_number)

        with allure.step("Перейти в систему LIS"):
            self.base_page.open_new_tab()
            home_lis_page = HomeLisPage()
            home_lis_page.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
            home_lis_page.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            home_lis_page.locators.NUMBER_VOLUME_BTN.click()
            number_volume_page = NumberVolumePage()
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step(f"Найти предыдущий номер телефона {self.inquiry.product.phone_number}"):
            number_volume_page.locators.SEARCH_BTN.click()
            number_volume_page.locators.MSISDN_FILTER_BTN.click()
            number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(self.inquiry.product.phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=self.inquiry.product.phone_number, params=NumberInfo(status="Свободен", state="Освобождён")
            )

        with allure.step(f"Найти новый номер телефона {new_phone_number}"):
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(new_phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=new_phone_number, params=NumberInfo(status="Занят", state="Распределён")
            )

    @allure.title("02. Замена номера (недостаточно средств)")
    @allure.id(591145)
    def test_replace_number_with_zero_balance(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        with allure.step("Перейти с карточки клиента во вкладку 'Продукты'"):
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()

        self.client_profile.click_first_product(
            subscriber=self.inquiry.product.phone_number, product_name=self.inquiry.product.product_name
        )

        with allure.step("Перейти на вкладку 'Ресурсы'"):
            self.product_info_form.PRODUCT_NAME.wait_to_have_text(self.inquiry.product.product_name)
            self.product_info_form.RESOURCES_TAB.click()

        with allure.step("Напротив Телефонного номера нажать на три точки, выбрать 'Замена'"):
            self.product_info_form.PHONE_NUMBER_BLOCK.wait_to_be_visible()
            self.product_info_form.PHONE_NUMBER.wait_to_have_text(self.inquiry.product.phone_number)
            self.product_info_form.MENU_PHONE_NUMBER_BTN.click()
            self.product_info_form.REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.wait_to_be_visible()
            self.replace_resource_form.check_required_fields()

        with allure.step("В ресурсе на замену напротив 'Номер телефона' нажать на кнопку '...'"):
            self.replace_resource_form.CHOICE_PHONE_NUMBER_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.wait_to_be_visible()

        with allure.step("Выбрать номер телефона"):
            self.inquiries_page.reserve_number()
            self.replace_resource_form.PHONE_NUMBER_HELP.wait_to_have_text("На счету недостаточно средств.")
            self.replace_resource_form.DO_REPLACE_BTN.not_to_be_enabled()

    @allure.title("03. Замена номера на занятый")
    @allure.id(593160)
    def test_replace_for_busy_number(self, base_url: str) -> None:
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        with allure.step("Перейти в систему LIS"):
            self.base_page.open_new_tab()
            home_lis_page = HomeLisPage()
            home_lis_page.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
            home_lis_page.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            home_lis_page.locators.NUMBER_VOLUME_BTN.click()
            number_volume_page = NumberVolumePage()
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step("Найти номер со статусом 'Занят'"):
            number_volume_page.locators.SEARCH_BTN.click()
            number_volume_page.locators.STATUS_FILTER_BTN.click()
            number_volume_page.locators.STATUS_OPTION_BUSY.click()
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.locators.PHONE_NUMBERS.wait_elements_visible(0)
            busy_number = number_volume_page.locators.PHONE_NUMBERS[0].text.strip()

        with allure.step("Перейти с карточки клиента во вкладку 'Продукты'"):
            self.base_page.bring_to_front(self.base_page.title)
            number_volume_page.close_page_by_index(-1)
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()

        self.client_profile.click_first_product(
            subscriber=self.inquiry.product.phone_number, product_name=self.inquiry.product.product_name
        )

        with allure.step("Перейти на вкладку 'Ресурсы'"):
            self.product_info_form.PRODUCT_NAME.wait_to_have_text(self.inquiry.product.product_name)
            self.product_info_form.RESOURCES_TAB.click()

        with allure.step("Напротив Телефонного номера нажать на три точки, выбрать 'Замена'"):
            self.product_info_form.PHONE_NUMBER_BLOCK.wait_to_be_visible()
            self.product_info_form.PHONE_NUMBER.wait_to_have_text(self.inquiry.product.phone_number)
            self.product_info_form.MENU_PHONE_NUMBER_BTN.click()
            self.product_info_form.REPLACE_BTN.click()
            self.replace_resource_form.REPLACE_RESOURCE_FORM.wait_to_be_visible()

        with allure.step("В ресурсе на замену напротив 'Номер телефона' нажать на кнопку '...'"):
            self.replace_resource_form.CHOICE_PHONE_NUMBER_BTN.click()
            self.replace_resource_form.REPLACE_PHONE_NUMBER_FORM.wait_to_be_visible()
            self.reserve_form.MASK_INPUT.fill(busy_number)
            self.reserve_form.SEARCH_BUTTON.click()
            self.reserve_form.NO_RECORDS_FOUND.to_contain_text("Записи не найдены", timeout=5000)

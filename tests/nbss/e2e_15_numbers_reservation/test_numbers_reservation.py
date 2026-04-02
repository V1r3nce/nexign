import allure
import pytest

from common.helpers.env_helper import BASE_URL_LIS
from models.client import IndividualClient
from models.context import test_context
from pages.base_page import BasePage
from pages.lis_pages.home_lis_page import HomeLisPage
from pages.lis_pages.number_volume_page import NumberInfo, NumberVolumePage
from pages.locators.nbss.inquiries_elements import ProductEditForm, ReserveResourcesForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.inquiries_page import InquiriesPage


@allure.suite("E2E_15 Бронирование номеров")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=689024215",
    name="NBSS.TPM.15 [2.0.3] Бронирование номеров",
)
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=749571323",
    name="Актуальная: Форма бронирования ресурсов во внешней системе",
)
@pytest.mark.regress
@pytest.mark.lis
@pytest.mark.nbss_portal
class TestNumbersReservation:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_individual_user: IndividualClient) -> None:
        self.base_page = BasePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.reserve_form = ReserveResourcesForm()
        self.client = create_individual_user

    @allure.title("02. Бронирование ресурсов на шаге продажи")
    @allure.description("Бронирование номера на шаге продажи")
    @allure.id(581192)
    def test_reserve_resource_at_sale(self, base_url: str) -> None:
        with allure.step(
            "Перейти на форму подготовленного ЛС, нажать 'Создание продажи и управления услугами, заполнить форму"
        ):
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.inquiries_page.sale_initialization()
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")

        with allure.step("Добавить продукт"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.TITLE.to_contain_text("Выбор продуктов")
            with allure.step("Выбрать: Монопродукт, Мобильная связь"):
                self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
                self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
                self.product_offer_form.SEARCH_BTN.click()
            with allure.step("В появившемся списке монопродуктов нажать кнопку 'Выбрать' у подходящего продукта"):
                self.product_offer_form.PRODUCT_CARD.wait_elements_visible(0)
                product_name = self.product_offer_form.PRODUCT_CARD_NAME[0].text
                self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.TITLE.not_to_be_visible(timeout=10000)

        with allure.step("Выбранный монопродукт добавлен в коммерческий заказ"):
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.locators.ADDED_PRODUCT_NAMES[0].to_contain_text(product_name)

        with allure.step("Открыть форму редактирования продукта"):
            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.TITLE.to_contain_text(product_name)

        with allure.step("Подобрать ресурсы"):
            self.product_edit_form.RESOURCES_TAB.click()
            phone_number = self.inquiries_page.auto_reserve_phone_number_resources()[1]

        with allure.step("Перейти в систему 'Единое ресурсное окно' (LIS)"):
            self.base_page.open_new_tab()
            home_page_lis = HomeLisPage()
            home_page_lis.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
            home_page_lis.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            number_volume_page = NumberVolumePage()
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step(f"Найти и проверить номер {phone_number}"):
            number_volume_page.locators.SEARCH_BTN.click()
            number_volume_page.locators.MSISDN_FILTER_BTN.click()
            number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=phone_number, params=NumberInfo(color="dark_red", is_block=True)
            )

    @allure.title("03. Снятие бронирования с номера с последующим бронированием другого номера")
    @allure.description("Бронирование номера на шаге продажи")
    @allure.id(581790)
    def test_cansel_reserve_and_reserve_new_number(self, base_url: str) -> None:
        with allure.step(
            "Перейти на форму подготовленного ЛС, нажать 'Создание продажи и управления услугами, заполнить форму"
        ):
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.inquiries_page.sale_initialization()
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")

        with allure.step("Добавить продукт"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.TITLE.to_contain_text("Выбор продуктов")
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
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.locators.ADDED_PRODUCT_NAMES[0].to_contain_text(product_name)

        with allure.step("Открыть форму редактирования продукта"):
            self.inquiries_page.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.TITLE.to_contain_text(product_name)

        with allure.step("Подобрать ресурсы"):
            self.product_edit_form.RESOURCES_TAB.click()
            phone_number = self.inquiries_page.auto_reserve_phone_number_resources()[1]

        with allure.step("Перейти в систему 'Единое ресурсное окно' (LIS)"):
            self.base_page.open_new_tab()
            home_page_lis = HomeLisPage()
            home_page_lis.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html")
            home_page_lis.locators.NUMBER_VOLUME_BTN.wait_to_be_visible()
            home_page_lis.locators.NUMBER_VOLUME_BTN.click()
            number_volume_page = NumberVolumePage()
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")

        with allure.step(f"Найти и проверить номер {phone_number}"):
            number_volume_page.locators.SEARCH_BTN.click()
            number_volume_page.locators.MSISDN_FILTER_BTN.click()
            number_volume_page.locators.MSISDN_OPTION_VALUE.click()
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=phone_number, params=NumberInfo(color="dark_red", is_block=True)
            )

        with allure.step("Нажать на кнопку 'Замена ресурса' для ручного выбора номера"):
            self.base_page.bring_to_front(self.base_page.title)
            number_volume_page.close_page_by_index(-1)
            self.product_edit_form.CHANGE_NUMBER_BTN.click()
            self.reserve_form.TITLE.to_contain_text("Бронирование номера")

        with allure.step("Выбрать новый номер для бронирования"):
            new_phone_number = self.inquiries_page.reserve_number()
            self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
            self.product_edit_form.PHONE_NUMBER.not_to_contain_text(phone_number)
            self.product_edit_form.PHONE_NUMBER.wait_to_have_text(new_phone_number)

        with allure.step("Проверить выбранный ранее номера в системе 'Единое ресурсное окно' (LIS)"):
            self.base_page.open_new_tab()
            number_volume_page = NumberVolumePage()
            number_volume_page.open(f"{BASE_URL_LIS}/ps/ng-urw/index.html#/numValue")
            number_volume_page.locators.TITLE.to_contain_text("Номерная ёмкость")
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=phone_number, params=NumberInfo(color="dark_green", is_block=False)
            )

        with allure.step("Проверить текущий номер в системе 'Единое ресурсное окно' (LIS)"):
            number_volume_page.locators.MSISDN_FILTER_INPUT.fill(new_phone_number)
            number_volume_page.locators.FILTER_SEARCH_BTN.click()
            number_volume_page.check_number_params(
                number=new_phone_number, params=NumberInfo(color="dark_red", is_block=True)
            )

import allure
import pytest

from common.enums.user import User
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL
from models.address_info import AlternativeAddress, BasicSystemAddress, RegionWithoutAddress
from models.client import OrganizationClient
from models.context import test_context
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import (
    ProductInfoForm,
)
from pages.locators.nbss.inquiries_elements import ProductEditForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_62_9 Продажа клиенту B2B")
@allure.suite("E2E_62_9 Продажа клиенту B2B (Подбор ресурсов с учетом совместимости)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestSaleWithRegionCheck:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.client_product_profile = ClientProductProfilePage()
        self.inquiries_page = InquiriesPage()
        self.product_offer_form = SelectProductOffersFormElements()
        self.product_edit_form = ProductEditForm()
        self.product_info_form = ProductInfoForm()
        self.basic_address = BasicSystemAddress.address
        self.basic_region = BasicSystemAddress.region
        self.product_name_x = product_names_map[B2BProducts.internet]
        self.product_name_y = product_names_map[B2BProducts.mobile]
        self.alternative_address = AlternativeAddress.address
        self.alternative_region = AlternativeAddress.region

    @allure.title("01 Выбор ПП если адреса подключения нет, но задается вручную (есть спец роль)")
    @pytest.mark.skip(reason="Адрес, как отдельная характеристика у ПП, пока не внедрена")
    @allure.id(841531)
    def test_sale_with_custom_address(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=False, priority="Высокий", add_kp="no"
        )
        with allure.step("Открытие формы добавления ПП в КЗ"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.basic_region)

        with allure.step("Ввод адреса вручную"):
            self.product_offer_form.enter_new_address_in_form(self.alternative_address)

            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.alternative_region)

        with allure.step("Выбор нужных ПП"):
            self.inquiries_page.search_and_select_product(
                product_offer_name=self.product_name_x, product_category_name="Интернет"
            )
            self.inquiries_page.search_and_select_product(
                product_offer_name=self.product_name_y, product_category_name="Мобильная связь"
            )

        with allure.step("Проверка, что элементы readonly"):
            self.product_offer_form.REGION.to_be_disabled()
            self.product_offer_form.ADDRESS.to_be_disabled()

            self.product_offer_form.ADD_BTN.click()

        with allure.step("Добавление Доп. Опции ПП X"):
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(2, timeout=15000)
            self.inquiries_page.add_additional_option_with_address_check(
                product_name=self.product_name_x, address=self.alternative_address, region=self.alternative_region
            )

        with allure.step("Проверка адресов в форме заявки"):
            self.inquiries_page.check_product_addresses(
                address=self.alternative_address, region=self.alternative_region, has_additional_option=True
            )

        with allure.step("Завершение продажи"):
            self.inquiries_page.auto_reserve_all_resources()
            self.inquiries_page.check_configuration()
            self.inquiries_page.check_technical_feasibility()
            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=15000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        with allure.step("Проверка адреса в форме 'Продукты'"):
            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.wait_to_be_enabled(timeout=15000)
            self.client_product_profile.locators.PRODUCTS_TAB.click()
            self.client_product_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_product_profile.expand_all_products()
            product_index_in_profile_x = self.client_product_profile.locators.PRODUCT_NAME.text_list.index(
                self.product_name_x
            )
            assert_that(
                lambda: product_index_in_profile_x is not None, f"Продукт {self.product_name_x} не найден в списке"
            )
            self.client_product_profile.locators.PRODUCT_NAME[product_index_in_profile_x].click()
            self.product_info_form.verify_product_addresses(self.alternative_region, self.alternative_address)

    @allure.title(
        "02 Выбор ПП если адрес подключения не задается (два ПП у одного обязательный адрес, у другого нет, проверка конфликта )"
    )
    @pytest.mark.skip(reason="Адрес, как отдельная характеристика у ПП, пока не внедрена")
    @allure.id(841533)
    def test_sale_without_address(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=True, priority="Высокий", add_kp="no"
        )
        with allure.step("Открытие формы добавления ПП в КЗ"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.REGION.select_by_value(RegionWithoutAddress.region)
            self.product_offer_form.ADDRESS_TEXT.not_to_be_visible()

        with allure.step("Выбор ПП"):
            self.inquiries_page.search_and_select_product(
                product_offer_name=self.product_name_x, product_category_name="Интернет"
            )
            self.product_offer_form.REGION.to_be_disabled()
            self.product_offer_form.ADDRESS.to_be_disabled()
            self.product_offer_form.ADD_BTN.click()

        self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
            f'Не задано обязательное поле "Адрес подключения" для ПП {self.product_name_x}'
        )

    @pytest.mark.user(User.SELLER_TEST)
    @allure.title("03 Выбор ПП если регион подключения не совпадает с регионом точки продаж")
    @allure.id(841528)
    def test_sale_with_conflict_address(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=True, priority="Высокий", add_kp="no"
        )
        with allure.step("Открытие формы добавления ПП в КЗ"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.ADDRESS_TEXT.to_contain_text(self.basic_address)
            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.basic_region)

        with allure.step("Ввод адреса, который не входит в регион точки продаж"):
            self.product_offer_form.enter_new_address_in_form(self.alternative_address)

            self.product_offer_form.MODAL.wait_to_have_count(1)
            self.product_offer_form.MODAL_TITLE[0].to_contain_text("Ошибка")
            self.product_offer_form.MODAL_BODY_TEXT.to_contain_text_in_any(
                "Регион подключения не соответствует региону продажи"
            )
            self.product_offer_form.MODAL_X_BTN.click()

            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.basic_region, timeout=20000)

    @allure.title("04 Выбор ПП с заданным адресом клиента")
    @pytest.mark.skip(reason="Адрес, как отдельная характеристика у ПП, пока не внедрена")
    @allure.id(841526)
    def test_sale_with_default_address(self) -> None:
        client_address = test_context.client.registration_address
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")

        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=True, priority="Высокий", add_kp="no"
        )
        with allure.step("Открытие формы добавления ПП в КЗ"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.ADDRESS_TEXT.to_contain_text(client_address)

        with allure.step("Выбор ПП"):
            self.inquiries_page.search_and_select_product(
                product_offer_name=self.product_name_x, product_category_name="Интернет"
            )
            self.product_offer_form.REGION.to_be_disabled()
            self.product_offer_form.ADDRESS.to_be_disabled()
            self.product_offer_form.ADD_BTN.click()

        with allure.step("Добавление Доп. Опции"):
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=15000)
            self.inquiries_page.add_additional_option_with_address_check(
                product_name=self.product_name_x, address=client_address, region=self.basic_region
            )

        with allure.step("Проверка добавления адреса у продукта"):
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(2, timeout=15000)
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].wait_to_be_visible(timeout=15000)
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].click(force=True)

            self.product_edit_form.REGION.to_contain_text(self.basic_region, timeout_sec=2)
            self.product_edit_form.ADDRESS.to_contain_text(client_address, timeout_sec=2)
            self.product_edit_form.INNER_CANCEL_BTN.click()

    @allure.title("05 Доступность изменения адреса и региона при удалении выбранных продуктов")
    @allure.id(841532)
    def test_sale_with_delete_product(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(
            test_context.client, need_contact_data=True, priority="Высокий", add_kp="no"
        )

        with allure.step("Открытие формы добавления ПП в КЗ"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.ADDRESS_TEXT.to_contain_text(self.basic_address)
            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.basic_region, timeout=15000)

        with allure.step("Ввод адреса, который не входит в регион точки продаж"):
            self.product_offer_form.enter_new_address_in_form(self.alternative_address)
            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.alternative_region)

        with allure.step("Выбор ПП"):
            self.inquiries_page.search_and_select_product(
                product_offer_name=self.product_name_x, product_category_name="Интернет"
            )
            self.product_offer_form.REGION.to_be_disabled(timeout=15000)
            self.product_offer_form.ADDRESS.to_be_disabled()

        with allure.step("Удаление ПП"):
            self.product_offer_form.PRODUCT_DELETE_BTN[0].click()
            self.product_offer_form.REGION.element_not_contain_disabled_attribute(timeout=2)
            self.product_offer_form.REGION_TEXT.wait_to_have_text(self.alternative_region)
            self.product_offer_form.ADDRESS.element_not_contain_disabled_attribute()
            self.product_offer_form.ADDRESS_TEXT.to_contain_text(self.alternative_address)

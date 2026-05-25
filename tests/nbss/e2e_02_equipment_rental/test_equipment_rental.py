import allure
import pytest

from api.lis_requests.equipment import EquipmentRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement, ProductInfoForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_02 Аренда оборудования")
@allure.suite("E2E_02 Аренда оборудования")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestEquipmentRental:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.client_profile_page = ClientProfilePage()
        self.select_offers_form = SelectProductOffersFormElements()
        self.product = "Терминал L"
        self.category_product = "Товары и оборудование"
        self.inquiries_page = InquiriesPage()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.product_info_form = ProductInfoForm()
        self.lis_api = EquipmentRequests()

    @allure.step("Парсинг значений оборудования и проверка статуса в LIS")
    def parsing_equipment_attribute_and_check_status(self):
        with allure.step("Проверка значений 'Серийным номер', 'Код номенклатуры'"):
            self.client_profile_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries"
            )
            self.client_profile_page.locators.REQUESTS.wait_to_be_visible(timeout=20000)
            self.client_profile_page.open_request_by_type_name()
            self.inquiries_page.locators.TABS.wait_to_be_visible()
            self.inquiries_page.click_tab("Элементы заказа")
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].wait_to_be_visible(timeout=15000)
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].hover()
            self.inquiries_page.locators.ADDED_PRODUCT_VISIBLE_BTN[0].click(force=True)
            self.product_info_form.RESOURCES_TAB.wait_to_be_visible(timeout=20000)
            self.product_info_form.RESOURCES_TAB.click()
            self.product_info_form.NUMBER_EQUIPMENT.wait_to_be_visible()
            number_equipment = self.product_info_form.NUMBER_EQUIPMENT.text
            nomenclature = self.product_info_form.CODE_NOMENCLATURE.text
        with allure.step("Проверка в LIS, что серийным номер находится в статусе SOLD"):
            all_number_equipment = self.lis_api.search_serial_number(
                nomenclature=nomenclature, partner_point_id=100001, limit=int(number_equipment) + 1, inventory_status=3
            )
            assert number_equipment in all_number_equipment, (
                f"Ожидалось, что {number_equipment} будет в списке {all_number_equipment}"
            )

    @allure.title(
        "01 Аренда оборудования как независимого продукта существующему клиенту, формирование и согласование документов автоматически"
    )
    @allure.id(838822)
    def test_add_equipment_rent_to_existing_client_as_additional_product_with_auto_documents(self):
        with allure.step("Инициация продажи через 'Продажа товаров/оборудования'"):
            self.client_profile_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
            self.client_profile_page.locators.CREATE_SELL_EQUIPMENT.wait_to_be_enabled(timeout=15000)
            self.client_profile_page.locators.CREATE_SELL_EQUIPMENT.click()
            self.select_offers_form.SEARCH_BTN.wait_to_be_enabled(timeout=15000)
        with allure.step("Выбор оборудования, назначение ему типа 'Аренда'"):
            self.inquiries_page.find_product_in_form(
                product_offer_name=self.product, type_transfer_rent=True, product_category_name=self.category_product
            )
        with allure.step("Заполнение формы на создание договора, КП, РПД"):
            self.inquiries_page.sale_initialization(add_kp="no", need_initialization=False)
        with allure.step("Процесс продажи"):
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text(
                "Наполнение и уточнение коммерческого заказа", timeout=55000
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
            self.inquiries_page.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
            self.inquiries_page.auto_reserve_all_resources(category="equipment_sale")
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()
            with allure.step("Проверка конфигурации"):
                self.inquiries_page.check_configuration()
                self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_close_inquiry()
        self.parsing_equipment_attribute_and_check_status()

    @allure.title('02 Продажа основного продукта, в состав которого входит ресурс "оборудование" передаваемый в Аренду')
    @allure.id(838823)
    def test_sell_main_product_with_rented_equipment_resource(self):
        with allure.step("Создание продажи через быстрый доступ"):
            self.client_profile_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.inquiries_page.sale_initialization(add_kp="no")
        with allure.step("Выбор оборудования, назначение ему типа 'Аренда'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.find_product_in_form(
                product_offer_name=self.product, type_transfer_rent=True, product_category_name=self.category_product
            )
        self.inquiries_page.locators.STEP_TITLE.wait_to_have_text(
            "Наполнение и уточнение коммерческого заказа", timeout=55000
        )
        with allure.step("Процесс продажи"):
            self.inquiries_page.auto_reserve_all_resources(category="equipment_sale")
            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()
            with allure.step("Проверка конфигурации"):
                self.inquiries_page.check_configuration()
                self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_close_inquiry()
        self.parsing_equipment_attribute_and_check_status()

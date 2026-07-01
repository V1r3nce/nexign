import re

import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import get_shifted_datetime_string
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.product import B2BProducts, product_names_map
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage

INVALID_DATE_WARNING = re.compile(r"Дата не может быть (позже|раньше)")


@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62_29 продажа клиенту B2B (Подключение/Изменение/Отключение продуктов будущей датой)")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestSellB2BClientFutureDate:
    PRODUCT_CURRENT = product_names_map[B2BProducts.mobile]
    PRODUCT_FUTURE = product_names_map[B2BProducts.mobile_on_date]

    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.product_offer_form = SelectProductOffersFormElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.future_date = get_shifted_datetime_string("+1d", template="%d.%m.%Y %H:%M")
        self.future_date_d = self.future_date.split(" ")[0]
        self.future_date_y = get_shifted_datetime_string("+30d", template="%d.%m.%Y %H:%M")
        self.future_date_y_d = self.future_date_y.split(" ")[0]
        self.invalid_past_date = get_shifted_datetime_string("-1d", template="%d.%m.%Y %H:%M")
        self.invalid_far_date = get_shifted_datetime_string("+100d", template="%d.%m.%Y %H:%M")

    @pytest.fixture
    def future_date_order_step(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto", future_date=self.future_date, verify_open=False)
        self.client_profile.open_created_inquiry(test_context.client.user_id)
        test_context.client.inquiry.product.product_name = self.PRODUCT_FUTURE
        self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
        self.inquiries_page.check_order_management_step()
        self.inquiries_page.auto_reserve_all_resources("mobile")

    @pytest.fixture
    def active_mobile_product(self) -> None:
        self.personal_account_api.create_agreement_and_account(test_context.client)
        self.client_inquiries_requests.product_sale(
            inquiry=prepare_inquiries(category=["mobile"], product_offering_id=[B2BProducts.mobile], as_list=False)
        )

    @allure.id(890120)
    @allure.title("01. Создание заявки на подключение продукта текущей датой")
    def test_create_inquiry_current_date(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto", verify_open=False)
        self.client_profile.open_created_inquiry(test_context.client.user_id)
        test_context.client.inquiry.product.product_name = self.PRODUCT_CURRENT
        self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
        self.inquiries_page.check_order_management_step()
        with allure.step("Завершить продажу текущей датой"):
            self.inquiries_page.auto_reserve_all_resources("mobile")
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=300000)

    @allure.id(883523)
    @allure.title("02. Создание заявки на подключение продукта будущей датой")
    def test_create_inquiry_future_date(self, future_date_order_step) -> None:
        self.inquiries_page.check_execution_date_on_active_step(self.future_date_d)
        with allure.step("Запустить проверку конфигурации и перейти на шаг 'Ожидание даты выполнения заказа'"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.check_execution_date_on_active_step(self.future_date_d)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)

    @allure.id(895015)
    @allure.title("05. Выбор ПП до регистрации заявки через кнопку быстрой продажи товаров/оборудования (текущая дата)")
    def test_quick_equipment_sale_current_date(self) -> None:
        equipment_product = "Терминал L"
        equipment_category = "Товары и оборудование"
        with allure.step("Инициировать продажу через кнопку 'Продажа товаров/оборудования'"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
            self.client_profile.locators.CREATE_SELL_EQUIPMENT.wait_to_be_enabled(timeout=15000)
            self.client_profile.locators.CREATE_SELL_EQUIPMENT.click()
            self.product_offer_form.SEARCH_BTN.wait_to_be_enabled(timeout=15000)
        with allure.step("Выбрать оборудование и добавить"):
            self.inquiries_page.find_product_in_form(
                product_offer_name=equipment_product, product_category_name=equipment_category
            )
        with allure.step("Заполнить сайдбар регистрации и сохранить (текущая дата)"):
            self.inquiries_page.sale_initialization(add_kp="no", need_initialization=False)
        with allure.step("Завершить продажу текущей датой"):
            self.inquiries_page.locators.STEP_TITLE.wait_to_have_text(
                "Наполнение и уточнение коммерческого заказа", timeout=55000
            )
            self.inquiries_page.auto_reserve_all_resources(category="equipment_sale")
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_close_inquiry()

    @allure.id(895016)
    @allure.title("06. Выбор ПП до регистрации заявки через смену ПП с подключением текущей датой")
    def test_change_product_current_date(self, active_mobile_product) -> None:
        with allure.step("Сменить основной продукт текущей датой (авто-договор)"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            name_product = self.client_profile.change_product_offer_with_contract(auto_contract=True)
        with allure.step("Завершить продажу текущей датой и проверить смену основного продукта"):
            self.inquiries_page.proceed_to_auto_contract_closure()
            self.inquiries_page.wait_closed_and_check_agreement()
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.check_main_product_changed(name_product)

    @allure.id(895017)
    @allure.title("07. Подключение текущей датой опции до регистрации заявки к существующему продукту клиента")
    def test_add_option_current_date(self, active_mobile_product) -> None:
        option_name = "+2 ГБ"
        with allure.step("Добавить опцию к продукту через '...' -> 'Добавить опцию'"):
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile.add_adoption_product(option_name)
        with allure.step("Сайдбар регистрации: чекбокс будущей даты присутствует и не заполнен (текущая дата)"):
            self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.wait_to_be_visible(timeout=10000)
            assert_that(
                lambda: not self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.has_attribute_value("checked", ""),
                "Чекбокс отложенного выполнения не должен быть отмечен при текущей дате",
            )
            self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=15000)
            self.create_request_form.SAVE_BTN.click()
        with allure.step("Завершить продажу опции текущей датой"):
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается", timeout=30000)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(generate_documents=False)

    @allure.id(890682)
    @allure.title("12. Создание заявки на отключение продукта клиента текущей датой")
    def test_disconnect_product_current_date(self, active_mobile_product) -> None:
        with allure.step("Открыть продукты клиента и инициировать отключение текущей датой"):
            self.client_profile.open_products_page(
                user_id=test_context.client.user_id, product_list=test_context.client.inquiry.product_list
            )
            self.client_profile.create_product_disconnect_inquiry(test_context.client.inquiry.product)
        with allure.step("Перейти в заявку через уведомление и дождаться завершения отключения"):
            inquiry_id = self.client_profile.get_inquiry_id_from_info_message()
            self.base_page.open(f"{BASE_URL}inquiries/{inquiry_id}")
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=300000)

    @allure.id(890684)
    @allure.title("13. Создание заявки на отключение продукта клиента будущей датой")
    def test_disconnect_product_future_date(self, active_mobile_product) -> None:
        with allure.step("Инициировать отключение будущей датой"):
            self.client_profile.open_products_page(
                user_id=test_context.client.user_id, product_list=test_context.client.inquiry.product_list
            )
            self.client_profile.create_product_disconnect_inquiry(
                test_context.client.inquiry.product, future_date=self.future_date
            )
        with allure.step("Перейти в заявку: шаг 'Ожидание даты выполнения заказа'"):
            inquiry_id = self.client_profile.get_inquiry_id_from_info_message()
            self.base_page.open(f"{BASE_URL}inquiries/{inquiry_id}")
            self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)

    @allure.id(913350)
    @allure.title('14. Редактирование будущей даты через вкладку "Активный шаг" на шаге "Управление составом заказа"')
    def test_edit_future_date_active_step(self, future_date_order_step) -> None:
        self.inquiries_page.check_execution_date_on_active_step(self.future_date_d)
        with allure.step("Изменить дату на дату Y по кнопке 'Редактировать дату'"):
            self.inquiries_page.edit_execution_date_active_step(date=self.future_date_y)
        with allure.step("Проверка конфигурации завершена успешно, дата изменена на Y"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.check_execution_date_on_active_step(self.future_date_y_d)

    @allure.id(755160)
    @allure.title(
        '15. Изменение будущей даты на текущую через вкладку "Активный шаг" на шаге "Управление составом заказа"'
    )
    def test_change_future_to_current_active_step(self, future_date_order_step) -> None:
        with allure.step("Изменить дату на 'Текущее время' по кнопке 'Редактировать дату'"):
            self.inquiries_page.edit_execution_date_active_step(current_time=True)
        with allure.step("Проверка конфигурации успешна, заявка закрывается текущей датой"):
            self.inquiries_page.check_configuration()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=300000)

    @allure.id(754973)
    @allure.title('16. Установка недопустимой даты через вкладку "Активный шаг" на шаге "Управление составом заказа"')
    def test_set_invalid_date_active_step(self, future_date_order_step) -> None:
        with allure.step("Ввести недопустимую дату (раньше текущей) по кнопке 'Редактировать дату'"):
            self.inquiries_page.edit_execution_date_active_step(
                date=self.invalid_past_date, expect_warning=False, save=False
            )
            self.inquiries_page.check_execution_date_error(INVALID_DATE_WARNING)
        with allure.step("Ввести недопустимую дату (позже разрешённой)"):
            self.inquiries_page.edit_execution_date_active_step(
                date=self.invalid_far_date, expect_warning=False, save=False
            )
            self.inquiries_page.check_execution_date_error(INVALID_DATE_WARNING)

    @allure.id(907676)
    @allure.title("03. Создание заявки на подключение неактивного продукта будущей датой")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_create_inquiry_inactive_product_future_date(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto", future_date=self.future_date, verify_open=False)
        self.client_profile.open_created_inquiry(test_context.client.user_id)
        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.inquiries_page.set_execution_date_on_product_form(self.future_date)
        self.inquiries_page.find_product_in_form(
            product_offer_name=self.PRODUCT_FUTURE, product_category_name="Мобильная связь"
        )
        self.inquiries_page.check_order_management_step()
        self.inquiries_page.check_execution_date_on_active_step(self.future_date_d)

    @allure.id(895014)
    @allure.title("04. Выбор ПП до регистрации заявки через Экспресс ПТВ с подключением текущей датой")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_express_ptv_current_date(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto", verify_open=False)
        self.client_profile.open_created_inquiry(test_context.client.user_id)
        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer_form.EXPRESS_PTV.click()

    @allure.id(895018)
    @allure.title("08. Выбор ПП до регистрации заявки через Экспресс ПТВ с подключением будущей датой")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_express_ptv_future_date(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.inquiries_page.sale_initialization(add_kp="auto", future_date=self.future_date, verify_open=False)
        self.client_profile.open_created_inquiry(test_context.client.user_id)
        self.inquiries_page.locators.ADD_SALE_BTN.click()
        self.product_offer_form.EXPRESS_PTV.click()
        self.inquiries_page.set_execution_date_on_product_form(self.future_date)

    @allure.id(895019)
    @allure.title("09. Выбор ПП до регистрации заявки через кнопку быстрой продажи товаров/оборудования (будущая дата)")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_quick_equipment_sale_future_date(self) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)
        self.client_profile.locators.CREATE_SELL_EQUIPMENT.wait_to_be_enabled(timeout=15000)
        self.client_profile.locators.CREATE_SELL_EQUIPMENT.click()
        self.product_offer_form.SEARCH_BTN.wait_to_be_enabled(timeout=15000)
        self.inquiries_page.set_execution_date_on_product_form(self.future_date)
        self.inquiries_page.find_product_in_form(
            product_offer_name="Терминал L", product_category_name="Товары и оборудование"
        )
        self.inquiries_page.sale_initialization(add_kp="no", need_initialization=False)

    @allure.id(895020)
    @allure.title("10. Выбор ПП до регистрации заявки через смену ПП с подключением будущей датой")
    @pytest.mark.skip("Нужен ПП с отложенной активацией в коробке (TUDS-5854)")
    def test_change_product_future_date(self, active_mobile_product) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.change_product_offer_with_contract(auto_contract=True, future_date=self.future_date)
        self.inquiries_page.check_execution_date_on_active_step(self.future_date_d)

    @allure.id(895021)
    @allure.title("11. Подключение будущей датой опции до регистрации заявки к существующему продукту клиента")
    @pytest.mark.skip("Нужен ПП с отложенной активацией в коробке (TUDS-5854)")
    def test_add_option_future_date(self, active_mobile_product) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.add_adoption_product("+2 ГБ")
        self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.wait_to_be_visible(timeout=10000)
        self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.click()
        self.create_request_form.EXECUTION_DATE.wait_to_be_visible(timeout=10000)
        self.create_request_form.EXECUTION_DATE.fill(self.future_date)
        self.base_page.press_keyboard_button("Enter")
        self.create_request_form.NEED_SPD.wait_to_be_visible(timeout=15000)
        self.create_request_form.SAVE_BTN.click()

    @allure.id(753739)
    @allure.title('17. Изменение даты на шаге "Ожидание даты выполнения заказа" через активный шаг')
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_edit_date_on_waiting_step(self, future_date_order_step) -> None:
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)
        self.inquiries_page.edit_execution_date_active_step(date=self.future_date_y)
        self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=60)

    @allure.id(907675)
    @allure.title('18. Изменение будущей даты на сегодняшнюю на шаге "Ожидание даты выполнения заказа"')
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_change_to_today_on_waiting_step(self, future_date_order_step) -> None:
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)
        self.inquiries_page.edit_execution_date_active_step(current_time=True)
        self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=300000)

    @allure.id(883528)
    @allure.title('19. Обработка конфликтов при изменении даты на шаге "Ожидание даты выполнения заказа"')
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_conflicts_on_waiting_step(self, future_date_order_step) -> None:
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)
        self.inquiries_page.edit_execution_date_active_step(current_time=True)

    @allure.id(883532)
    @allure.title("20. Установка корректной будущей даты через элементы заказа")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_valid_future_date_order_elements(self, future_date_order_step) -> None:
        self.inquiries_page.open_tab("Элементы заказа")

    @allure.id(754974)
    @allure.title("21. Установка некорректной будущей даты через элементы заказа")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_invalid_date_order_elements(self, future_date_order_step) -> None:
        self.inquiries_page.open_tab("Элементы заказа")

    @allure.id(755117)
    @allure.title('22. Установка "текущего времени" через элементы заказа')
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_current_time_order_elements(self, future_date_order_step) -> None:
        self.inquiries_page.open_tab("Элементы заказа")

    @allure.id(890693)
    @allure.title("23. Редактирование характеристик продукта текущей датой")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_edit_characteristics_current_date(self, active_mobile_product) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.edit_product()

    @allure.id(890695)
    @allure.title("24. Редактирование характеристик продукта будущей датой")
    @pytest.mark.skip("Залью во 2 коммите сегодня к вечеру")
    def test_edit_characteristics_future_date(self, active_mobile_product) -> None:
        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products")
        self.client_profile.edit_product()

    @allure.id(890715)
    @allure.title("25. Исполнение заявки при наступлении даты выполнения заказа")
    @pytest.mark.skip("Нужен механизм сдвига времени стенда для срабатывания таймера выполнения заказа")
    def test_order_execution_on_timer(self, future_date_order_step) -> None:
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)

    @allure.id(890713)
    @allure.title("26. Недоступность ПП при наступлении даты выполнения заказа")
    @pytest.mark.skip("Нужен механизм сдвига времени и недоступность ПП к дате выполнения заказа")
    def test_product_unavailable_on_timer(self, future_date_order_step) -> None:
        self.inquiries_page.check_configuration()
        self.inquiries_page.locators.NEXT_STEP_BTN.click()
        self.inquiries_page.locators.INQUIRY_STEP.to_contain_text("Ожидание даты выполнения заказа", timeout_sec=180)

import copy
import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
from models.user import OrganizationClient
from pages.locators.nbss.inquiries_elements import CloseInquiryForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage
from tests.conftest import CreatedImsis


@allure.suite("Процесс продажи")
@allure.sub_suite("E2E_43 Подключение пакетных предложений")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestConnectPackageOffers:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        add_two_imsi_free_shipped: CreatedImsis,
        create_organization: OrganizationClient,
    ) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_context)
        self.payment_api = PaymentsRequests(api_request_context)

        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)

        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.close_inquiry_form = CloseInquiryForm(nexign_ui_stand_login)
        self.user_data = create_organization
        self.bundle_name = "Все для бизнеса"
        self.product_names = ["Интернет в офис", "Гибкий бизнес", "Телефонная связь"]

    @allure.title("Фильтрация пакетных предложений")
    @allure.description(
        "Выполняется проверка фильтрации пакетных предложений на этапе выбора продуктовых предложений для продажи"
    )
    @allure.id(583451)
    def test_filter_package_offers(self, base_url: str) -> None:
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_first_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()

        with allure.step("Выбрать тип 'Монопродукт' и нажать кнопку 'Найти'"):
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([self.bundle_name])

        with allure.step(
            "Выбрать тип 'Бандл' и категории 'Интернет', 'Мобильная связь', 'Технические услуги', нажать кнопку 'Найти'"
        ):
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Интернет")
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Мобильная связь")
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Технические услуги")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([self.bundle_name])

        with allure.step("Убрать из фильтра по категории 'Интернет' и нажать кнопку 'Найти'"):
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Интернет", False)
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([self.bundle_name])

        with allure.step("Убрать из фильтра по категории 'Мобильная связь' и нажать кнопку 'Найти'"):
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Мобильная связь", False)
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_not_contain_text_in_all([self.bundle_name])

        with allure.step("Сбросить фильтр, нажав кнопку 'Сбросить'"):
            self.product_offer_form.CLEAR_FILTER_BTN.click()
            checked_value = self.product_offer_form.PRODUCT_TYPE.checked_value
            assert_that(
                lambda: checked_value == "Бандл",
                f"Не выбран тип 'Бандл'. Текущий тип - {checked_value}",
            )
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([self.bundle_name])

        with allure.step("В фильтре по технологии выбрать 'GSM', 'xDSL', нажать кнопку 'Найти'"):
            self.product_offer_form.TECHNOLOGY.select_by_value("GSM")
            self.product_offer_form.TECHNOLOGY.select_by_value("xDSL")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_not_contain_text_in_all([self.bundle_name])

        with allure.step("В фильтр по технологии добавить 'xPON', нажать кнопку 'Найти'"):
            self.product_offer_form.TECHNOLOGY.select_by_value("xPON")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([self.bundle_name])

    @allure.title("Подключение пакетных предложений")
    @allure.description("Выполняется проверка подключения нескольких пакетных предложений")
    @allure.id(643160)
    def test_connect_package_offers(self, base_url: str) -> None:
        balance = 10
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_first_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.SEARCH_BTN.click()

        with allure.step("Выбрать два пакетных предложения из списка"):
            first_bundle = self.inquiries_page.choose_product_offer_with_name(self.bundle_name)
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (1)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.locators.ADD_SALE_BTN.click(timeout=20000)
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.SEARCH_BTN.click()
            second_bundle = self.inquiries_page.choose_product_offer_with_name(self.bundle_name)
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (1)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.check_view_bundle_products(
                [first_bundle, second_bundle], [*self.product_names, *self.product_names]
            )

        self.inquiries_page.auto_reserve_all_resources()
        self.inquiries_page.check_configuration()
        self.inquiries_page.check_technical_feasibility()

        with allure.step(
            "Нажать кнопку 'Далее', в выпадающем меню выбрать 'Автоматическое управление Договором/ДС и ЛС'"
        ):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.AUTO_AGREEMENT_BTN.click()

        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()
        self.inquiries_page.set_products_subscriber([first_bundle, second_bundle])

        with allure.step("Перейти на карточку клиента на вкладку 'Продукты'"):
            account_id = self.personal_account_api.get_personal_accounts("customer", self.user_data.user_id).json()[
                "items"
            ][0]["accountId"]
            self.payment_api.create_default_payment(
                account_id,
                first_bundle.one_time_payment
                + first_bundle.subscription_fee
                + second_bundle.one_time_payment
                + second_bundle.subscription_fee
                + balance,
            )
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_profile.check_all_products([*first_bundle.products, *second_bundle.products])

        with allure.step("Проверить баланс пользователя на вкладке 'Обзор'"):
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.locators.BALANCE[0].wait_to_have_text(f"{balance:.2f} RUB")

    @allure.title("Подключение пакетных предложений с дополнительными опциями")
    @allure.description("Выполняется проверка подключения пакетного предложения с дополнительными опциями")
    @allure.id(643161)
    @pytest.mark.smoke
    def test_connect_package_offers_with_additional_options(self, base_url: str) -> None:
        balance = 10
        first_option_name = "+2 ГБ"
        second_option_name = "+50 SMS"
        option_count = 2
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_first_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.SEARCH_BTN.click()

        with allure.step("Выбрать Бандл из списка"):
            bundle = self.inquiries_page.choose_product_offer_with_name(self.bundle_name)
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (1)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.check_view_bundle_products([bundle], self.product_names)

        self.inquiries_page.auto_reserve_all_resources()

        with allure.step("У одного из монопродуктов нажать кнопку 'Добавить опцию'"):
            product_index = self.inquiries_page.locators.ADDED_PRODUCT_NAMES.text_list.index("Гибкий бизнес")
            self.inquiries_page.locators.ADDED_PRODUCT_ADD_OPTION_BTN[product_index].click(force=True)
            self.product_offer_form.TITLE.wait_to_have_text("Добавление опций")

        with allure.step("Выбрать две опции из списка"):
            first_option = self.inquiries_page.choose_product_offer_with_name(first_option_name)
            second_option = self.inquiries_page.choose_product_offer_with_name(second_option_name)
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (2)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.TITLE.not_to_be_visible()
            total_one_time_payment = (
                bundle.one_time_payment + first_option.one_time_payment + second_option.one_time_payment
            )
            total_subscription_fee = (
                bundle.subscription_fee + first_option.subscription_fee + second_option.subscription_fee
            )
            self.inquiries_page.check_total_fields(total_one_time_payment, total_subscription_fee)

        self.inquiries_page.check_configuration()
        self.inquiries_page.check_technical_feasibility()

        with allure.step(
            "Нажать кнопку 'Далее', в выпадающем меню выбрать 'Автоматическое управление Договором/ДС и ЛС'"
        ):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.AUTO_AGREEMENT_BTN.click()

        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()
        self.inquiries_page.set_products_subscriber([bundle])

        with allure.step("Перейти на карточку клиента на вкладку 'Продукты'"):
            account_id = self.personal_account_api.get_personal_accounts("customer", self.user_data.user_id).json()[
                "items"
            ][0]["accountId"]
            self.payment_api.create_default_payment(
                account_id, total_one_time_payment + total_subscription_fee + balance
            )
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_profile.check_all_products(bundle.products)
            self.client_profile.locators.PRODUCT_NAME.wait_for_text_in_all(["Гибкий бизнес"])
            product_index = self.client_profile.locators.PRODUCT_NAME.text_list.index("Гибкий бизнес")
            assert_that(
                lambda: self.client_profile.get_option_limit_count(product_index) == option_count,
                f"Количество отображаемых лимитов опций продукта должно быть равно {option_count}",
            )

        with allure.step("Развернуть информацию о продукте и проверить отображение опций"):
            self.client_profile.locators.OPEN_OPTIONS_BTN[0].click()
            self.client_profile.locators.CURRENT_OPTION_PRODUCT.wait_to_have_count(option_count)
            self.client_profile.locators.OPTION_NAME.wait_for_text_in_all([first_option.product_name])
            self.client_profile.locators.OPTION_NAME.wait_for_text_in_all([second_option.product_name])
            self.client_profile.locators.OPTION_STATUS_COLOR.element_have_css_color("background-color", "green")

        with allure.step("Проверить баланс пользователя на вкладке 'Обзор'"):
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.locators.BALANCE[0].wait_to_have_text(f"{balance:.2f} RUB")

    @allure.title("Копирование монопродуктов при подключении пакетных предложений")
    @allure.description("Выполняется проверка подключения пакетного предложения со скопированным монопродуктом")
    @allure.id(585279)
    def test_connect_package_offer_with_copy_monoproduct(self, base_url: str) -> None:
        balance = 10
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_first_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.SEARCH_BTN.click()

        with allure.step("Выбрать Бандл из списка"):
            bundle = self.inquiries_page.choose_product_offer_with_name(self.bundle_name)
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (1)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.check_view_bundle_products([bundle], self.product_names)

        with allure.step("У одного из монопродуктов навести курсор на три точки и нажать 'Копировать'"):
            self.inquiries_page.locators.ADDED_PRODUCT_MENU_BTN[-1].click(force=True)
            self.inquiries_page.locators.COPY_BTN.click()
            bundle.add_product(copy.deepcopy(bundle.products[-1]))
            self.inquiries_page.locators.ADDED_MONOPRODUCT.wait_to_have_count(len(bundle.products))
            self.inquiries_page.check_total_fields(bundle.one_time_payment, bundle.subscription_fee)

        self.inquiries_page.auto_reserve_all_resources()
        self.inquiries_page.check_configuration()
        self.inquiries_page.check_technical_feasibility()

        with allure.step(
            "Нажать кнопку 'Далее', в выпадающем меню выбрать 'Автоматическое управление Договором/ДС и ЛС'"
        ):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.AUTO_AGREEMENT_BTN.click()

        self.inquiries_page.wait_connect_package_offers_and_close_inquiry()
        self.inquiries_page.set_products_subscriber([bundle])

        with allure.step("Перейти на карточку клиента на вкладку 'Продукты'"):
            account_id = self.personal_account_api.get_personal_accounts("customer", self.user_data.user_id).json()[
                "items"
            ][0]["accountId"]
            self.payment_api.create_default_payment(
                account_id, bundle.subscription_fee + bundle.one_time_payment + balance
            )
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_profile.check_all_products(bundle.products)

        with allure.step("Проверить баланс пользователя на вкладке 'Обзор'"):
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.locators.BALANCE[0].wait_to_have_text(f"{balance:.2f} RUB")

    @allure.title("Невозможность перехода на следующий этап заявки на продажу до выполнения проверок")
    @allure.description(
        "Выполняется проверка невозможности перехода на следующий этап заявки на продажу до выполнения обязательных проверок"
    )
    @allure.id(585786)
    def test_block_transition_until_complete_checks(self, base_url: str) -> None:
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_first_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.SEARCH_BTN.click()

        with allure.step("Выбрать Бандл и нажать кнопку 'Добавить'"):
            bundle = self.inquiries_page.choose_product_offer_with_name(self.bundle_name)
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.check_view_bundle_products([bundle], self.product_names)

        self.inquiries_page.auto_reserve_all_resources()

        with allure.step("Нажать кнопку 'Далее'"):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.NO_TRANSITION_FOUND.wait_to_be_visible()

        self.inquiries_page.check_configuration()

        with allure.step("Нажать кнопку 'Далее'"):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.NO_TRANSITION_FOUND.wait_to_be_visible()

        self.inquiries_page.check_technical_feasibility()

        with allure.step("Нажать кнопку 'Далее'"):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.AUTO_AGREEMENT_BTN.wait_to_be_visible()

    @allure.title("Подключение нескольких дополнительных опций к пакетному предложению в продуктовом профиле клиента")
    @allure.description("Выполняется проверка подключения дополнительных опций к подключенному пакетному предложению")
    @allure.id(643164)
    def test_connect_additional_options_in_client_profile(self, base_url: str) -> None:
        balance = 10
        first_option_name = "+2 ГБ"
        second_option_name = "+50 SMS"
        option_count = 2
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")
        bundle = self.inquiries_page.sale_bundle()

        with allure.step("Проверить баланс пользователя на вкладке 'Обзор'"):
            account_id = self.personal_account_api.get_personal_accounts("customer", self.user_data.user_id).json()[
                "items"
            ][0]["accountId"]
            self.payment_api.create_default_payment(
                account_id, bundle.subscription_fee + bundle.one_time_payment + balance
            )
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.locators.BALANCE[0].wait_to_have_text(f"{balance:.2f} RUB")

        with allure.step("Перейти на карточку клиента на вкладку 'Продукты'"):
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_profile.check_all_products(bundle.products)

        with allure.step("Выбрать продукт из списка и нажать 'Добавить опции'"):
            self.client_profile.locators.PRODUCT_NAME.wait_for_text_in_all(["Гибкий бизнес"])
            product_index = self.client_profile.locators.PRODUCT_NAME.text_list.index("Гибкий бизнес")
            self.client_profile.locators.PRODUCTS_OPTIONS_OPEN_BTN[product_index].click()
            self.client_profile.locators.PRODUCTS_OPTIONS_ADD_BTN.click()
            self.product_offer_form.TITLE.wait_to_have_text("Добавление опций")

        with allure.step(
            "Выбрать две опции из списка путём нажатия на соответствующие кнопки 'Выбрать', запомнить их стоимость"
        ):
            first_option = self.inquiries_page.choose_product_offer_with_name(first_option_name)
            second_option = self.inquiries_page.choose_product_offer_with_name(second_option_name)
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (2)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()

        with allure.step("Нажать 'Создать заявку'"):
            self.product_offer_form.ADD_BTN.click()
            self.product_offer_form.INFO_MESSAGE.wait_to_be_visible()
            self.product_offer_form.INFO_MESSAGE.wait_to_have_text(
                re.compile(r"Заявка \d+ создана\. Обновите форму и учтите установленные фильтры")
            )

        with allure.step("Перейти на страницу заявки и дождаться её выполнения"):
            self.product_offer_form.INFO_MESSAGE_ACTION_BUTTON.click()
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами")
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry()

        with allure.step("Перейти на карточку клиента на вкладку 'Продукты'"):
            amount = (
                first_option.one_time_payment
                + first_option.subscription_fee
                + second_option.one_time_payment
                + second_option.subscription_fee
            )
            self.payment_api.create_default_payment(account_id, amount)
            self.personal_account_api.wait_check_current_main_balance(account_id, balance + amount)
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_profile.expand_all_products()
            self.client_profile.locators.PRODUCT_NAME.wait_for_text_in_all(["Гибкий бизнес"])
            product_index = self.client_profile.locators.PRODUCT_NAME.text_list.index("Гибкий бизнес")
            assert_that(
                lambda: self.client_profile.get_option_limit_count(product_index) == option_count,
                f"Количество отображаемых лимитов опций продукта должно быть равно {option_count}",
            )

        with allure.step("Развернуть информацию о продукте и проверить отображение опций"):
            self.client_profile.locators.OPEN_OPTIONS_BTN[0].click()
            self.client_profile.locators.CURRENT_OPTION_PRODUCT.wait_to_have_count(option_count)
            self.client_profile.locators.OPTION_NAME.wait_for_text_in_all([first_option.product_name])
            self.client_profile.locators.OPTION_NAME.wait_for_text_in_all([second_option.product_name])
            self.client_profile.locators.OPTION_STATUS_COLOR.to_have_css_color("background-color", "green")

        with allure.step("Проверить баланс пользователя на вкладке 'Обзор'"):
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.locators.BALANCE[0].wait_to_have_text(f"{balance:.2f} RUB")

    @allure.title("Принудительное закрытие заявки на продажу пакетного предложения")
    @allure.description("Выполняется проверка закрытия заявки во время подключения пакетного предложения")
    @allure.id(585997)
    def test_close_inquiry_connect_package_offers(self, base_url: str) -> None:
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_data.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_first_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.product_offer_form.SEARCH_BTN.click()

        bundle = self.inquiries_page.choose_product_offer_with_name(self.bundle_name)

        with allure.step("Нажать кнопку 'Добавить'"):
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.check_view_bundle_products([bundle], self.product_names)

        self.inquiries_page.auto_reserve_all_resources()
        self.inquiries_page.check_configuration()
        self.inquiries_page.check_technical_feasibility()

        with allure.step(
            "Нажать кнопку 'Далее', в выпадающем меню выбрать 'Автоматическое управление Договором/ДС и ЛС'"
        ):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.AUTO_AGREEMENT_BTN.click()

        with allure.step(
            "Не дожидаясь автоматического закрытия заявки, нажать кнопку 'Закрыть заявку' и в открывшемся окне нажать 'Закрыть'"
        ):
            self.inquiries_page.locators.LOAD_SPIN_FIRST.wait_to_be_visible()
            self.inquiries_page.locators.CLOSE_INQUIRY_BTN.click()
            self.close_inquiry_form.FORM.wait_to_be_visible()
            self.close_inquiry_form.TITLE.wait_to_have_text("Закрытие заявки")
            self.close_inquiry_form.INNER_ACCEPT_BTN.click()
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text("Автоматическое управление Договором/ДС и ЛС")
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто")

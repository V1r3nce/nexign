import copy

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.payments_requests import PaymentInfo, PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import generate_random_number
from pages.client_profile_page import ClientProfilePage
from pages.locators.inquiries_page import InquiriesPage
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.personal_account_page import PersonalAccountPage


@allure.suite("Процесс продажи")
@allure.sub_suite("E2E_43 Подключение пакетных предложений")
class TestConnectPackageOffers:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_organization: int,
    ) -> None:
        self.personal_account_api = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)

        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)

        self.product_offer_form = SelectProductOffersForm(nexign_ui_stand_login)
        self.user_id = create_organization

    @allure.title("Фильтрация пакетных предложений")
    @allure.tag("can_aurh", "success")
    @allure.description(
        "Выполняется проверка фильтрации пакетных предложений на этапе выбора продуктовых предложений для продажи"
    )
    @allure.id(583451)
    def test_filter_package_offers(self, base_url: str) -> None:
        bundle_name = "Все для бизнеса"
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_firs_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

        with allure.step("Выбрать тип 'Монопродукт' и нажать кнопку 'Найти'"):
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

        with allure.step(
            "Выбрать тип 'Пакетное предложение' и категории 'Интернет', 'Мобильная связь', 'Технические услуги', нажать кнопку 'Найти'"
        ):
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Пакетное предложение")
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Интернет")
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Мобильная связь")
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Технические услуги")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

        with allure.step("Убрать из фильтра по категории 'Интернет' и нажать кнопку 'Найти'"):
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

        with allure.step("Убрать из фильтра по категории 'Мобильная связь' и нажать кнопку 'Найти'"):
            self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.select_by_value("Мобильная связь")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_not_contain_text_in_all([bundle_name])

        with allure.step("Сбросить фильтр, нажав кнопку 'Сбросить'"):
            self.product_offer_form.CLEAR_FILTER_BTN.click()
            assert_that(
                lambda: self.product_offer_form.PRODUCT_TYPE.checked_value == "Пакетное предложение",
                "Не выбран тип 'Пакетное предложение'",
            )
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

        with allure.step("В фильтре по технологии выбрать 'GSM', 'xDSL', нажать кнопку 'Найти'"):
            self.product_offer_form.TECHNOLOGY.select_by_value("GSM")
            self.product_offer_form.TECHNOLOGY.select_by_value("xDSL")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_not_contain_text_in_all([bundle_name])

        with allure.step("В фильтр по технологии добавить 'xPON', нажать кнопку 'Найти'"):
            self.product_offer_form.TECHNOLOGY.select_by_value("xPON")
            self.product_offer_form.SEARCH_BTN.click()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

    @allure.title("Копирование монопродуктов при подключении пакетных предложений")
    @allure.tag("can_aurh", "success")
    @allure.description("Выполняется проверка подключения пакетного предложения со скопированным монопродуктом")
    @allure.id(585279)
    def test_connect_package_offer_with_copy_monoproduct(self, base_url: str) -> None:
        bundle_name = "Все для бизнеса"
        product_names = ["Интернет в офис", "Гибкий бизнес", "Телефонная связь"]
        balance = 10
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_firs_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()

        with allure.step("Выбрать пакетное предложение из списка"):
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])
            bundle = self.inquiries_page.choose_product_offer_with_name(bundle_name)
            index = self.product_offer_form.PRODUCT_CARD_NAME.text_list.index(bundle.bundle_name)
            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[index].wait_to_have_text("Удалить")
            self.product_offer_form.SHOW_ONLY_CHOOSE_BTN.wait_to_have_text("Показать только выбранные (1)")
            self.product_offer_form.ADD_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.ADDED_BUNDLE.wait_to_have_count(1)
            self.inquiries_page.ADDED_MONOPRODUCT.wait_to_have_count(len(bundle.products))
            self.inquiries_page.ADDED_BUNDLE_NAMES.wait_for_text_in_all([bundle_name])
            self.inquiries_page.ADDED_PRODUCT_NAMES.wait_for_text_in_all(product_names)
            self.inquiries_page.set_products_charge(bundle)

        with allure.step("У одного из монопродуктов навести курсор на три точки и нажать 'Копировать'"):
            self.inquiries_page.ADDED_PRODUCT_MENU_BTN[-1].click(force=True)
            self.inquiries_page.COPY_BTN.click()
            bundle.add_product(copy.deepcopy(bundle.products[-1]))
            self.inquiries_page.ADDED_MONOPRODUCT.wait_to_have_count(len(bundle.products))
            self.inquiries_page.TOTAL_ONE_TIME_PAYMENT.wait_to_have_text(f"{bundle.one_time_payment:.2f}")
            self.inquiries_page.TOTAL_SUBSCRIPTION_FEE.wait_to_have_text(f"{bundle.subscription_fee:.2f}")

        self.inquiries_page.auto_reserve_all_resources()

        with allure.step("Нажать кнопку 'Проверить конфигурацию' и дождаться выполнения проверки"):
            self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                "Продукты заказа настроены корректно.", timeout=10000
            )

        with allure.step(
            "Нажать кнопку 'Проверить техническую возможность' "
            "и дождаться выполнения проверки технической возможности подключения продуктов"
        ):
            self.inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                "Для всех продуктов заказа есть техническая возможность подключения. "
                'Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".',
                timeout=10000,
            )

        with allure.step(
            "Нажать кнопку 'Далее', в выпадающем меню выбрать 'Автоматическое управление Договором/ДС и ЛС'"
        ):
            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.AUTO_AGREEMENT_BTN.click()

        with allure.step("Дождаться подключения выбранных пакетных предложений и закрытия заявки"):
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=350000)
            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Закрыто")

        self.inquiries_page.set_products_subscriber(bundle)

        with allure.step("Перейти на карточку клиента на вкладку 'Продукты'"):
            account_id = self.personal_account_api.get_personal_accounts("customer", self.user_id).json()["items"][0][
                "accountId"
            ]
            payment_data = PaymentInfo(
                document_number=generate_random_number(8),
                account_id=account_id,
                amount=bundle.subscription_fee + bundle.one_time_payment + balance + 450,
            )
            self.payment_api.wait_check_create_payment(payment_data)
            self.payment_api.create_payment(payment_data).json()
            self.payment_api.wait_last_payment_successful(account_id)
            self.personal_account_api.wait_check_current_main_balance(account_id, balance)

            self.client_profile.locators.CLIENT_FIO_BTN.click()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.PRODUCTS_LIST.wait_to_be_visible()
            self.client_profile.check_all_products(bundle.products)

        with allure.step("Проверить баланс пользователя на вкладке 'Обзор'"):
            self.client_profile.locators.OVERVIEW_TAB.click()
            self.client_profile.locators.BALANCE[0].wait_to_have_text(f"{balance:.2f} RUB")

    @allure.title("Невозможность перехода на следующий этап заявки на продажу до выполнения проверок")
    @allure.tag("can_aurh", "success")
    @allure.description(
        "Выполняется проверка невозможности перехода на следующий этап заявки на продажу до выполнения обязательных проверок"
    )
    @allure.id(585786)
    def test_block_transition_until_complete_checks(self, base_url: str) -> None:
        bundle_name = "Все для бизнеса"
        product_names = ["Интернет в офис", "Гибкий бизнес", "Телефонная связь"]
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.user_id}/overview")

        with allure.step("Создать новую заявку на продажу и управление услугами"):
            self.inquiries_page.sale_initialization()
            self.inquiries_page.check_firs_step_sale_titles()

        with allure.step("Нажать кнопку 'Добавить'"):
            self.inquiries_page.ADD_SALE_BTN.click()
            self.inquiries_page.check_product_offer_form()
            self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([bundle_name])

        with allure.step("Выбрать пакетное предложение и нажать кнопку 'Добавить'"):
            bundle = self.inquiries_page.choose_product_offer_with_name(bundle_name)
            self.product_offer_form.ADD_BTN.click()
            self.inquiries_page.ADDED_BUNDLE.wait_to_have_count(1)
            self.inquiries_page.ADDED_MONOPRODUCT.wait_to_have_count(len(bundle.products))
            self.inquiries_page.ADDED_BUNDLE_NAMES.wait_for_text_in_all([bundle_name])
            self.inquiries_page.ADDED_PRODUCT_NAMES.wait_for_text_in_all(product_names)

        self.inquiries_page.auto_reserve_all_resources()

        with allure.step("Нажать кнопку 'Далее'"):
            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.NO_TRANSITION_FOUND.wait_to_be_visible()

        with allure.step("Нажать кнопку 'Проверить конфигурацию' и дождаться выполнения проверки"):
            self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                "Продукты заказа настроены корректно.", timeout=10000
            )

        with allure.step("Нажать кнопку 'Далее'"):
            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.NO_TRANSITION_FOUND.wait_to_be_visible()

        with allure.step(
            "Нажать кнопку 'Проверить техническую возможность' и дождаться выполнения проверки технической возможности подключения продуктов"
        ):
            self.inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".',
                timeout=10000,
            )

        with allure.step("Нажать кнопку 'Далее'"):
            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.AUTO_AGREEMENT_BTN.wait_to_be_visible()

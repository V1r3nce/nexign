import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import get_current_datetime_string
from common.helpers.time_helpers import delay
from models.user import IndividualClient
from pages.base_page import BasePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import ContractCreate, CreateSalesAndServiceManagement
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_list import InquiriesList
from pages.locators.select_product_offers_form import SelectProductOffersForm


@allure.suite("Процесс продажи")
@allure.sub_suite("E2E_63 Продажа клиенту B2C")
class TestB2CSaleWithAutoContractProcess:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login: Page) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.home_page = HomePage(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.inquiries_page = InquiriesPage(page)
        self.inquiries_list_page = InquiriesList(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.create_contract_form = ContractCreate(page)

    @allure.title("Продажа B2C клиенту с прерыванием процесса, а затем продолжением")
    @allure.tag("CAN_AUTH")
    @allure.description(
        "При регистрации продажи, Клиент прервался (вышел из процесса регистрации продажи), а затем нашёл заявку и продолжил."
    )
    @allure.id(484018)
    @pytest.mark.regress
    def test_b2b_interrupt_sale_with_manual_contract_process(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        new_client = create_user_with_agreement_and_account
        delay(3, "Требуется время, для обработки создания пользователя, договора и ЛС")
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client.user_id}/overview")

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.PRIORITY.select_by_value("Средний")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Вручную")

            self.create_request_form.SAVE_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами")
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=10000)

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.")

            self.inquiries_page.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            inquiry_id = self.inquiries_page.locators.INQUIRY_ID.text
            self.inquiries_page.locators.HOME_BTN.click()
            self.home_page.WIDGET.wait_to_have_count(4)
            self.home_page.WIDGET_LABEL[2].click()

            self.inquiries_list_page.PAGE_TITLE.wait_to_have_text("Заявки")
            self.inquiries_list_page.IN_PROCESS_BTN.click()

            self.inquiries_list_page.SEARCH_FIELD.fill(inquiry_id)
            self.inquiries_list_page.FOUNDED_INQUIRIES.wait_to_have_count(1, timeout=10000)
            self.inquiries_list_page.FOUNDED_INQUIRIES[0].to_contain_text(inquiry_id)
            self.inquiries_list_page.FOUNDED_INQUIRIES[0].click()

            self.inquiries_list_page.NEXT_STEP_BTN.click()

            self.inquiries_list_page.CONTRACTS.wait_to_have_count(1, timeout=10000)
            self.inquiries_list_page.CONTRACTS[0].click()

            self.inquiries_list_page.CHOICE_CONTRACT_BTN.click()
            self.inquiries_list_page.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_list_page.CONTRACT_INFO.wait_to_have_text("Выбран договор: ")
            self.inquiries_list_page.RIGHT_ARROW_BTN.click()

            self.inquiries_list_page.ADDRESSES_ON_ACCOUNT.wait_to_have_count(1, timeout=10000)
            self.inquiries_list_page.ADDRESSES_ON_ACCOUNT_CHECKBOX[0].click()
            self.inquiries_list_page.SAVE_DISTRIBUTION_BTN.click()

            self.inquiries_list_page.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_list_page.RIGHT_ARROW_BTN.select_by_value("Формирование и подписание документа Договор/ДС")

            self.inquiries_list_page.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_list_page.RIGHT_ARROW_BTN.click()
            self.inquiries_list_page.LOAD_SPIN.not_to_be_visible(timeout=10000)

            self.inquiries_list_page.RIGHT_ARROW_BTN.click()
            self.inquiries_list_page.LOAD_SPIN.not_to_be_visible(timeout=240000)

            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

    @allure.title("Продажа B2C выбранному клиенту с ручным выбором договора и ЛС")
    @allure.tag("CAN_AUTH")
    @allure.description(
        "При регистрации продажи, Клиент выбрал ручное создание Договора/ЛС, а затем выбрал существующие Договор и ЛС в процессе продажи."
    )
    @allure.id(483285)
    @pytest.mark.regress
    def test_b2b_sale_with_manual_contract_and_account_process(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        new_client = create_user_with_agreement_and_account
        delay(3, "Требуется время, для обработки создания пользователя, договора и ЛС")
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client.user_id}/overview")

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.PRIORITY.select_by_value("Средний")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Вручную")

            self.create_request_form.SAVE_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами")
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=10000)

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.")

            self.inquiries_page.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_list_page.NEXT_STEP_BTN.click()

            self.inquiries_page.locators.CONTRACTS.wait_to_have_count(1, timeout=10000)
            self.inquiries_page.locators.CONTRACTS[0].click()

            self.inquiries_page.locators.CHOICE_CONTRACT_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.CONTRACT_INFO.wait_to_have_text("Выбран договор: ")
            self.inquiries_page.locators.RIGHT_ARROW_BTN.click()

            self.inquiries_page.locators.ADDRESSES_ON_ACCOUNT.wait_to_have_count(1, timeout=10000)
            self.inquiries_page.locators.ADDRESSES_ON_ACCOUNT_CHECKBOX[0].click()
            self.inquiries_page.locators.SAVE_DISTRIBUTION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)

            self.inquiries_page.locators.RIGHT_ARROW_BTN.select_by_value(
                "Формирование и подписание документа Договор/ДС"
            )
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)

            delay(1, "Требуется время, для стабильного перехода на следующий шаг")
            self.inquiries_page.locators.RIGHT_ARROW_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)

            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

    @allure.title("Продажа B2C выбранному клиенту с ручным созданием договора и ЛС")
    @allure.tag("CAN_AUTH")
    @allure.description(
        "При регистрации продажи, Клиент выбрал ручное создание Договора/ЛС, а затем создал Договор и ЛС в процессе продажи."
    )
    @allure.id(480799)
    @pytest.mark.regress
    def test_b2b_sale_with_manual_create_contract_and_account_process(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        new_client = create_user_with_agreement_and_account
        delay(3, "Требуется время, для обработки создания пользователя, договора и ЛС")
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client.user_id}/overview")

        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.PRIORITY.select_by_value("Средний")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Вручную")

            self.create_request_form.SAVE_BTN.click()

        with allure.step("Создание продажи"):
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Продажа и управление услугами")
            )
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=10000)

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)

            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.locators.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.")

            self.inquiries_page.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.locators.NEXT_STEP_BTN.click()

            delay(1, "Требуется ожидание, иначе форма не открывается")
            self.inquiries_page.locators.ADD_CONTRACT_BTN.click()

            self.create_contract_form.CONTRACT_SIGN_DATE.to_contain_text(
                get_current_datetime_string(is_full_format=False)
            )

            self.create_contract_form.OPERATOR_LAST_NAME.fill("ФамилияОператора")
            self.create_contract_form.OPERATOR_FIRST_NAME.fill("ИмяОператора")
            self.create_contract_form.OPERATOR_BANK_DATA.select_by_value("ПАО Сбербанк, 40702978428375519784")
            self.create_contract_form.CREATE_BTN.click()

            self.inquiries_page.locators.CONTRACTS.wait_to_have_count(2, timeout=10000)
            self.inquiries_page.locators.CONTRACTS[1].click()

            self.inquiries_page.locators.CHOICE_CONTRACT_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.CONTRACT_INFO.wait_to_have_text("Выбран договор: ")
            self.inquiries_page.locators.RIGHT_ARROW_BTN.click()

            self.inquiries_page.locators.ADDRESSES_ON_ACCOUNT.wait_to_have_count(1, timeout=10000)
            self.inquiries_page.locators.ADDRESSES_ON_ACCOUNT_CHECKBOX[0].click()
            self.inquiries_page.locators.SAVE_DISTRIBUTION_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)

            self.inquiries_page.locators.RIGHT_ARROW_BTN.select_by_value(
                "Формирование и подписание документа Договор/ДС"
            )
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=10000)

            delay(1, "Требуется время, для стабильного перехода на следующий шаг")
            self.inquiries_page.locators.RIGHT_ARROW_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)

            self.inquiries_page.locators.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

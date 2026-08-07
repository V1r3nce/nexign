import allure
import pytest

from models.client import IndividualClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ContractCreate, CreateSalesAndServiceManagement
from pages.locators.nbss.home_page_elements import HomePageElements
from pages.locators.nbss.inquiries_list import InquiriesListElements
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.nbss.inquiries_page import InquiriesPage


@allure.suite("Процесс продажи")
@allure.sub_suite("E2E_63 Продажа клиенту B2C")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestB2CSaleWithAutoContractProcess:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.home_page = HomePageElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.inquiries_page = InquiriesPage()
        self.inquiries_list_page = InquiriesListElements()
        self.product_offer_form = SelectProductOffersFormElements()
        self.create_contract_form = ContractCreate()

    def create_application_add_product_and_check(self) -> None:
        with allure.step("Создание продажи"):
            self.inquiries_page.sale_initialization(priority="Средний", create_add_agreement="manual")

            self.inquiries_page.locators.ADD_SALE_BTN.click()
            self.product_offer_form.TITLE.to_contain_text("Выбор продуктов")
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.inquiries_page.choose_product_offer_with_name("Скоростной Уют")
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)
            self.inquiries_page.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.check_configuration()
            self.inquiries_page.check_technical_feasibility()

            self.inquiries_page.locators.REFRESH_BTN.click()
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.locators.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

    @allure.title("Продажа B2C клиенту с прерыванием процесса, а затем продолжением")
    @allure.description(
        "При регистрации продажи, Клиент прервался (вышел из процесса регистрации продажи), а затем нашёл заявку и продолжил."
    )
    @allure.id(484018)
    def test_b2c_interrupt_sale_with_manual_contract_process(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        new_client = create_user_with_agreement_and_account
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client.user_id}/overview")
        self.create_application_add_product_and_check()

        with allure.step("Прерывание процесса продажи"):
            inquiry_id = self.inquiries_page.locators.INQUIRY_ID.text
            self.inquiries_page.locators.HOME_BTN.click()
            self.home_page.WIDGETS.wait_to_have_count(4)
            self.home_page.WIDGET_LABEL[2].click()

            self.inquiries_list_page.PAGE_TITLE.wait_to_have_text("Заявки")
            self.inquiries_list_page.IN_PROCESS_BTN.click()

            self.inquiries_list_page.SEARCH_FIELD.fill(inquiry_id)
            self.inquiries_list_page.FOUNDED_INQUIRIES.wait_to_have_count(1, timeout=10000)
            self.inquiries_list_page.FOUNDED_INQUIRIES[0].to_contain_text(inquiry_id)
            self.inquiries_list_page.FOUNDED_INQUIRIES[0].click()

        with allure.step("Продолжение процесса продажи"):
            self.inquiries_page.click_next("Регистрация/Выбор договора")
            self.inquiries_page.choose_agreement()
            self.inquiries_page.click_next("Распределение продуктов заказа по ЛС")
            self.inquiries_page.choose_account()
            self.inquiries_page.click_next("Формирование и подписание документа Договор/ДС")
            self.inquiries_list_page.AGREEMENT.wait_to_have_count(1)
            self.inquiries_list_page.RIGHT_ARROW_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(False, False)

    @allure.title("Продажа B2C выбранному клиенту с ручным выбором договора и ЛС")
    @allure.description(
        "При регистрации продажи, Клиент выбрал ручное создание Договора/ЛС, а затем выбрал существующие Договор и ЛС в процессе продажи."
    )
    @allure.id(483285)
    def test_b2c_sale_with_manual_contract_and_account_process(
        self, base_url: str, create_user_with_agreement_and_account: IndividualClient
    ) -> None:
        new_client = create_user_with_agreement_and_account
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client.user_id}/overview")
        self.create_application_add_product_and_check()

        with allure.step("Продолжение процесса продажи"):
            self.inquiries_page.click_next("Регистрация/Выбор договора")
            self.inquiries_page.choose_agreement()
            self.inquiries_page.click_next("Распределение продуктов заказа по ЛС")
            self.inquiries_page.choose_account()

            self.inquiries_page.click_next("Формирование и подписание документа Договор/ДС")
            self.inquiries_page.locators.AGREEMENT.wait_to_have_count(1)
            self.inquiries_page.locators.RIGHT_ARROW_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(False, False)

    @allure.title("Продажа B2C выбранному клиенту с ручным созданием договора и ЛС")
    @allure.description(
        "При регистрации продажи, Клиент выбрал ручное создание Договора/ЛС, а затем создал Договор и ЛС в процессе продажи."
    )
    @allure.id(480799)
    def test_b2c_sale_with_manual_create_contract_and_account_process(
        self, base_url: str, create_individual_user: IndividualClient
    ) -> None:
        new_client = create_individual_user
        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{new_client.user_id}/overview")
        self.create_application_add_product_and_check()

        with allure.step("Продолжение процесса продажи"):
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.ADD_CONTRACT_BTN.click()

            self.create_contract_form.OPERATOR_FIO.select_by_value("Иванов Иван Иванович")
            self.create_contract_form.OPERATOR_BANK_DATA.select_by_value(new_client.operator_bank_details)
            self.create_contract_form.SAVE_BTN.click()

            self.inquiries_page.choose_agreement()
            self.inquiries_page.click_next("Распределение продуктов заказа по ЛС")

            self.inquiries_page.locators.ADD_ACCOUNT_BTN.click()
            self.create_contract_form.SAVE_BTN.click()

            self.inquiries_page.choose_account()
            self.inquiries_page.click_next("Формирование и подписание документа Договор/ДС")
            self.inquiries_page.locators.AGREEMENT.wait_to_have_count(1)
            self.inquiries_page.locators.RIGHT_ARROW_BTN.click()
            self.inquiries_page.wait_connect_package_offers_and_close_inquiry(False, False)

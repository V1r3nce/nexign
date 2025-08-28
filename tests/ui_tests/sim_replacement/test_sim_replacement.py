import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests.client_requests import InfoAboutProduct
from api.requests.inquiry_requests import InquiryRequests
from api.requests.lis_requests.sim_cards import SimCardsRequests
from api.requests.payments_requests import PaymentsRequests
from api.requests.personal_account_requests import PersonalAccountRequests
from common.helpers.string_helper import sim_price_parse
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.inquiries_page import InquiriesPage
from pages.locators.client_profile import ClientProfile
from pages.locators.dynamic_form_elements import ProductInfo, ReplaceResource
from pages.locators.home_page_elements import HomePage


@allure.epic("E2E_44 Замена SIM-карты абонента")
@allure.suite("E2E_44 Замена SIM-карты абонента")
@pytest.mark.usefixtures(
    "nexign_ui_stand_login",
    "create_user_with_agreement_and_account",
)
class TestSIMReplacement:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        page: Page,
        nexign_ui_stand_login,
        api_request_auth_context: APIRequestContext,
        create_user_with_agreement_and_account,
    ):
        self.base_page = BasePage(nexign_ui_stand_login)
        self.home_page = HomePage(page)
        self.client_profile = ClientProfile(page)
        self.inquiries_page = InquiriesPage(page)
        self.personal_account = PersonalAccountRequests(api_request_auth_context)
        self.payment_api = PaymentsRequests(api_request_auth_context)
        self.sim_cards = SimCardsRequests(api_request_auth_context)
        self.new_client = create_user_with_agreement_and_account
        self.resources_form = ReplaceResource(page)
        self.dynamic_product = ProductInfo(page)
        self.inquiry_api = InquiryRequests(api_request_auth_context)
        self.payment_amount = 5000

    @allure.step("Проведение заявки")
    def request_close_check_balance(self, base_url: str, product: InfoAboutProduct, price_sim_change: float) -> None:
        delay(2, "Время для создания заявки")
        with allure.step("Открытие заявок клиента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/inquiries")
            self.client_profile.REQUEST_NUMBER[-1].click()
        with allure.step("Открытие страницы с заявкой и ее выполнение"):
            delay(4, "Время для прогрузки и правльного определния локатора")
            self.inquiries_page.locators.INQUIRY_ID.wait_to_be_visible()
            inquiry_id = self.inquiries_page.locators.INQUIRY_ID.text
            self.inquiries_page.locators.NEXT_STEP_BTN.wait_to_be_visible()
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_FORWARD.click()
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_DUE_DATE_INPUT.wait_to_be_visible()
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_DUE_DATE_INPUT.click()
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_DUE_DATE_TODAY.click()
            delay(3, "Избежать ошибки Объект находится в состоянии WAIT")
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_APPLY_BTN.click()
        with allure.step("Проверка статуса заявки"):
            self.inquiry_api.wait_inquiry_status(inquiry_id)
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_REFRESH_BTN.click()
            self.inquiries_page.locators.RESOURCE_REPLACEMENT_STATUS.wait_to_have_text("Закрыто")
        with allure.step("Проверка баланса"):
            self.personal_account.wait_check_current_main_balance(
                self.new_client.agreements[0].accounts[0].id,
                self.payment_amount - product.one_time_payment - product.subscription_fee - price_sim_change,
            )

    @allure.title("Замена SIM-карты из панели главной страницы")
    @allure.id(589661)
    @allure.description(
        "Выполняется проверка замены SIM-карты абонента из панели на главной страницы системы управления партнёрами"
    )
    @allure.link(url="jira.nexign.com/browse/TUDS-2921", name="TUDS-2921")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=663203127",
        name="KP Замена SIM-карты абонента (Детальное)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=694465667",
        name="Замена SIM-карты. Общее описание процесса",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_sim_replacement_main_page(self, base_url: str):
        with allure.step("Подготовка клиента"):
            self.payment_api.create_default_payment(self.new_client.agreements[0].accounts[0].id, self.payment_amount)
            product = self.inquiries_page.sale_phone_number(client=self.new_client)

        with allure.step("Получение списка доступных SIM карт"):
            sims = self.sim_cards.get_sim_card_list(status_id=[1], state_id=[9], is_reserved=False)
            sims_data = self.sim_cards.get_sim_cards_data(sims)
            icc = sims_data[0].icc

        self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
        self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)

        self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
        self.home_page.RIGHT_SIDE_BTN.click(3)

        with allure.step("Создание заявки 'Замена ресурса' на главной странице"):
            self.resources_form.SUBSCRIBER_SELECT.select_by_value(product.phone_number)
            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc)
            self.resources_form.ICC_CHECK_BTN.click()
            self.resources_form.ICC_SUCCESS_WINDOW.wait_to_be_visible()
            self.resources_form.ICC_SUCCESS_WINDOW.to_contain_text("Стоимость:")
            with allure.step("Получение стоимости замены"):
                window_text = self.resources_form.ICC_SUCCESS_WINDOW.text
                price_sim_change = sim_price_parse(window_text)
            self.resources_form.APPLY_BTN.click()

        self.request_close_check_balance(base_url, product, price_sim_change)

        with allure.step("Проверка изменения ICC у абонента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)
            self.client_profile.PRODUCTS_SIDEBAR_OPEN.click()
            self.dynamic_product.RESOURCES_TAB.wait_to_be_visible()
            self.dynamic_product.RESOURCES_TAB.click()
            self.dynamic_product.RESOURCE_SIM_ICC.to_contain_text(icc)

        with allure.step("Проверка изменения статуса SIM карты"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(3)

            self.resources_form.SUBSCRIBER_SELECT.select_by_value(product.phone_number)
            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc)
            self.resources_form.ICC_CHECK_BTN.click()
            self.resources_form.ICC_INFO_WINDOW.wait_to_be_visible()
            self.resources_form.ICC_INFO_WINDOW.to_contain_text("Продана")

    @allure.title("Замена SIM-карты из продуктового профиля")
    @allure.id(589753)
    @allure.description("Выполняется проверка замены SIM-карты абонента из продуктового профиля")
    @allure.link(url="jira.nexign.com/browse/TUDS-2921", name="TUDS-2921")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=663203127",
        name="KP Замена SIM-карты абонента (Детальное)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=694465667",
        name="Замена SIM-карты. Общее описание процесса",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_sim_client_products(self, base_url):
        with allure.step("Подготовка клиента"):
            self.payment_api.create_default_payment(self.new_client.agreements[0].accounts[0].id, self.payment_amount)
            product = self.inquiries_page.sale_phone_number(client=self.new_client)

        with allure.step("Получение списка доступных SIM карт"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/overview")
            sims = self.sim_cards.get_sim_card_list(status_id=[1], state_id=[9], is_reserved=False)
            sims_data = self.sim_cards.get_sim_cards_data(sims)
            icc = sims_data[0].icc

        with allure.step("Создание заявки 'Замена ресурса' в продуктовом профиле клиента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)

            self.client_profile.PRODUCTS_SIDEBAR_OPEN.click(force=True)
            self.dynamic_product.RESOURCES_TAB.click()
            self.dynamic_product.PRODUCT_SIDEBAR_RESOURCES_SIM_MORE_BTN.click()
            self.dynamic_product.REPLACE_BTN.click()

            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc)
            self.resources_form.ICC_CHECK_BTN.click()
            self.resources_form.ICC_SUCCESS_WINDOW.wait_to_be_visible()

            self.resources_form.ICC_SUCCESS_WINDOW.to_contain_text("Стоимость:")
            with allure.step("Получение стоимости замены"):
                window_text = self.resources_form.ICC_SUCCESS_WINDOW.text
                price_sim_change = sim_price_parse(window_text)
            self.resources_form.APPLY_BTN.click()

        self.request_close_check_balance(base_url, product, price_sim_change)

        with allure.step("Проверка изменения ICC у абонента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)
            self.client_profile.PRODUCTS_SIDEBAR_OPEN.click(force=True)
            self.dynamic_product.RESOURCES_TAB.wait_to_be_visible()
            self.dynamic_product.RESOURCES_TAB.click()
            self.dynamic_product.RESOURCE_SIM_ICC.to_contain_text(icc)

    @allure.title("Замена SIM-карты на дефектную")
    @allure.id(590130)
    @allure.description(
        "Выполняется проверка невозможности замены SIM-карты абонента при выборе дефектной или проданной SIM"
    )
    @allure.link(url="jira.nexign.com/browse/TUDS-2921", name="TUDS-2921")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=663203127",
        name="KP Замена SIM-карты абонента (Детальное)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=694465667",
        name="Замена SIM-карты. Общее описание процесса",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_sim_not_allowed_sims(self, base_url):
        with allure.step("Подготовка клиента"):
            self.payment_api.create_default_payment(self.new_client.agreements[0].accounts[0].id, self.payment_amount)
            product = self.inquiries_page.sale_phone_number(client=self.new_client)

        with allure.step("Получение списка дефектных SIM карт"):
            sims_broken = self.sim_cards.get_sim_card_list(status_id=[1], state_id=[6], is_reserved=False)
            sims_data_broken = self.sim_cards.get_sim_cards_data(sims_broken)
            icc_broken = sims_data_broken[0].icc
        with allure.step("Получение списка проданых SIM карт"):
            sims_sold = self.sim_cards.get_sim_card_list(status_id=[2], state_id=[10], is_reserved=False)
            sims_data_sold = self.sim_cards.get_sim_cards_data(sims_sold)
            icc_sold = sims_data_sold[0].icc

        with allure.step("Создание заявки 'Замена ресурса' на главной странице"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)

            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(3)

            self.resources_form.SUBSCRIBER_SELECT.select_by_value(product.phone_number)
            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc_broken)
            self.resources_form.ICC_CHECK_BTN.click()

        with allure.step("Проверка недоступности замены SIM карты по причине выбранная карта дефектная"):
            self.resources_form.ICC_INFO_WINDOW.wait_to_be_visible()
            self.resources_form.ICC_INFO_WINDOW.to_contain_text("Дефектная")

        with allure.step("Создание заявки 'Замена ресурса' на главной странице"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(3)

            self.resources_form.SUBSCRIBER_SELECT.select_by_value(product.phone_number)
            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc_sold)
            self.resources_form.ICC_CHECK_BTN.click()

        with allure.step("Проверка недоступности замены SIM карты по причине выбранная карта дефектная"):
            self.resources_form.ICC_INFO_WINDOW.wait_to_be_visible()
            self.resources_form.ICC_INFO_WINDOW.to_contain_text("Продана")

    @allure.title("Замена SIM-карты при недостатке денежных средств")
    @allure.id(590111)
    @allure.description("Выполняется проверка невозможности замены SIM-карты абонента при нехватке средств")
    @allure.link(url="jira.nexign.com/browse/TUDS-2921", name="TUDS-2921")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=663203127",
        name="KP Замена SIM-карты абонента (Детальное)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=694465667",
        name="Замена SIM-карты. Общее описание процесса",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_sim_not_enough_funds(self, base_url):
        delay(2, "Для успешного создания продажи")
        product = self.inquiries_page.sale_phone_number(client=self.new_client)

        with allure.step("Вычисление суммы, достаточной для активации продукта, но недостаточной для смены SIM карты"):
            self.payment_amount = product.one_time_payment + product.subscription_fee + 1
        self.payment_api.create_default_payment(self.new_client.agreements[0].accounts[0].id, self.payment_amount)
        self.personal_account.wait_check_current_main_balance(self.new_client.agreements[0].accounts[0].id, 1)
        with allure.step("Получение списка доступных SIM карт"):
            sims = self.sim_cards.get_sim_card_list(status_id=[1], state_id=[9], is_reserved=False)
            sims_data = self.sim_cards.get_sim_cards_data(sims)
            icc = sims_data[0].icc

        with allure.step("Создание заявки 'Замена ресурса' на главной странице"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)

            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(3)

            self.resources_form.SUBSCRIBER_SELECT.select_by_value(product.phone_number)
            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc)
            self.resources_form.ICC_CHECK_BTN.click()

        with allure.step("Проверка недоступности замены SIM карты по причине недостаточно средств"):
            self.resources_form.ICC_NOT_ENOUGH_FUNDS.wait_to_be_visible()
            self.resources_form.ICC_NOT_ENOUGH_FUNDS.to_contain_text("недостаточно средств")

    @allure.title("Замена SIM-карты при нескольких ЛС")
    @allure.id(590133)
    @allure.description(
        "Выполняется проверка правильности замены SIM-карты абонента, при условии, что у клиента два абонента и ЛС"
    )
    @allure.link(url="jira.nexign.com/browse/TUDS-2921", name="TUDS-2921")
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=663203127",
        name="KP Замена SIM-карты абонента (Детальное)",
    )
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=694465667",
        name="Замена SIM-карты. Общее описание процесса",
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_sim_few_accounts(self, base_url):
        with allure.step("Подготовка первого абонента"):
            self.payment_api.create_default_payment(self.new_client.agreements[0].accounts[0].id, self.payment_amount)
            product = self.inquiries_page.sale_phone_number(client=self.new_client)

        with allure.step("Подготовка второго абонента"):
            self.new_client_another = self.personal_account.create_agreement_and_account(self.new_client)
            self.payment_api.create_default_payment(
                self.new_client_another.agreements[0].accounts[0].id, self.payment_amount
            )
            self.inquiries_page.sale_phone_number(client=self.new_client_another)

        with allure.step("Получение списка доступных SIM карт"):
            sims = self.sim_cards.get_sim_card_list(status_id=[1], state_id=[9], is_reserved=False)
            sims_data = self.sim_cards.get_sim_cards_data(sims)
            icc = sims_data[0].icc

        with allure.step("Создание заявки 'Замена ресурса' на главной странице для первого абонента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)

            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(3)

            self.resources_form.SUBSCRIBER_SELECT.select_by_value(product.phone_number)
            self.resources_form.ICC_INPUT.wait_to_be_visible()
            self.resources_form.ICC_INPUT.fill(icc)
            self.resources_form.ICC_CHECK_BTN.click()
            self.resources_form.ICC_SUCCESS_WINDOW.wait_to_be_visible()
            self.resources_form.ICC_SUCCESS_WINDOW.to_contain_text("Стоимость:")
            with allure.step("Получение стоимости замены"):
                window_text = self.resources_form.ICC_SUCCESS_WINDOW.text
                price_sim_change = sim_price_parse(window_text)
            self.resources_form.APPLY_BTN.click()

        self.request_close_check_balance(base_url, product, price_sim_change)

        with allure.step("Проверка изменения ICC у абонента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.new_client.user_id}/products")
            self.client_profile.SUBSCRIBER.wait_to_be_visible(timeout=10000)
            self.client_profile.PRODUCTS_SIDEBAR_OPEN.click(force=True)
            self.dynamic_product.RESOURCES_TAB.wait_to_be_visible()
            self.dynamic_product.RESOURCES_TAB.click()
            self.dynamic_product.RESOURCE_SIM_ICC.to_contain_text(icc)

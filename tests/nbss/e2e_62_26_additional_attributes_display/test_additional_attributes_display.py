import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.inquiry import InquiryStep, InquiryTab
from common.enums.topic import TestTopic
from models.client import OrganizationClient
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.dynamic_form_elements import (
    DynamicForms,
    ForwardInquiryForm,
)
from pages.nbss.client.client_product_profile_page import ClientProductProfilePage
from pages.nbss.client.client_profile_inquiries_page import ClientProfileInquiriesPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.dynamic_forms.panel_toolbar_page import PanelToolbarPage
from pages.nbss.inquiries_page import InquiriesPage

DESCRIPTION_GROUP = "Описание"
AGREEMENT_AND_ACCOUNT_GROUP = "Договор и ЛС"
REPLACEMENT_GROUPS = ["Заменяемый ресурс", "Условия замены", "Ресурс на замену"]
CALCULATION_INFO_GROUP = "Информация по расчетам"


@allure.epic("E2E_62 Продажа клиенту B2B")
@allure.suite("E2E_62 Продажа клиенту B2B")
@allure.feature(
    "E2E_62_26 Продажа клиенту B2B. (Изменить отображение доп атрибутов заявки на вкладке Карточка продажи и Обзор)"
)
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=858159082",
    name="RMBSS-14581. ФС. Отображение доп атрибутов заявки на вкладке Карточка продажи и Обзор",
)
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAdditionalAttributesDisplay:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization_with_agreement_and_account: OrganizationClient) -> None:
        self.client_profile_page = ClientProfilePage()
        self.client_product_profile_page = ClientProductProfilePage()
        self.client_profile_inquiries_page = ClientProfileInquiriesPage()
        self.panel_toolbar_page = PanelToolbarPage()
        self.inquiries_page = InquiriesPage()
        self.client_inquiry_api = ClientInquiriesRequests()
        self.payment_api = PaymentsRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.dynamic_forms = DynamicForms()
        self.forward_inquiry = ForwardInquiryForm()
        self.client = create_organization_with_agreement_and_account
        self.payment_amount = 5000

    @allure.title("01. Просмотр доп.атрибутов на карточке продажи")
    @allure.id(955742)
    def test_sale_card_additional_attributes(self) -> None:
        with allure.step("Перейти к клиенту и создать продажу"):
            self.client_profile_page.open_client_overview_page(self.client.user_id)
            self.inquiries_page.sale_initialization(self.client)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.ManageOrderStructure)

        with allure.step("Перейти на вкладку 'Карточка продажи'"):
            self.inquiries_page.click_tab(InquiryTab.SaleCard)
            self.inquiries_page.check_attribute_groups(displayed=[DESCRIPTION_GROUP, AGREEMENT_AND_ACCOUNT_GROUP])

    @allure.title("02. Просмотр доп.атрибутов при замене ресурсов")
    @allure.id(955743)
    def test_resource_replacement_additional_attributes(self) -> None:
        with allure.step("Продажа ПП с возможностью замены ресурсов, пополнение ЛС и активация продукта"):
            account_id = self.client.agreement.account.id
            self.payment_api.create_default_payment(account_id, self.payment_amount)
            inquiry = self.client_inquiry_api.product_sale(self.client, prepare_inquiries("mobile"))
            self.personal_account_api.wait_check_current_main_balance(
                account_id, self.payment_amount - inquiry.product.one_time_payment - inquiry.product.subscription_fee
            )

        with allure.step("Перейти к продуктам клиента"):
            self.client_product_profile_page.open_products_page_and_check(
                self.client.user_id, product_list=[inquiry.product]
            )

        with allure.step("Открыть ресурсы ПП, нажав на продукт и выбрав вкладку 'Ресурсы'"):
            self.client_product_profile_page.open_product_resources()

        with allure.step("Нажать 'Заменить' у ресурса SIM-карта и выполнить замену"):
            self.client_product_profile_page.replace_product_resource()

        with allure.step("Перейти в созданную заявку"):
            self.client_profile_inquiries_page.open_last_client_inquiry(self.client.user_id)

        with allure.step("Проверить состав коллапсов на вкладке 'Обзор'"):
            self.inquiries_page.click_tab(InquiryTab.Overview)
            self.inquiries_page.check_attribute_groups(displayed=[DESCRIPTION_GROUP, REPLACEMENT_GROUPS])

    @allure.title("03. Просмотр доп. атрибутов при заявке на тестировании атрибутов")
    @allure.id(956733)
    def test_test_attributes_inquiry_additional_attributes(self) -> None:
        with allure.step("Создать второй договор и ЛС клиента"):
            self.personal_account_api.create_agreement_and_account(self.client)

        with allure.step("Перейти к договору и ЛС клиента"):
            self.client_profile_page.open_client_overview_page(self.client.user_id)

        with allure.step(f"Открыть заявку с темой '{TestTopic.AttributesKeep}', заполнить договор1 и ЛС1, сохранить"):
            self.panel_toolbar_page.create_inquiry_with_agreement_and_account(
                [TestTopic.Group, TestTopic.AttributesKeep]
            )

        with allure.step("Проверить состав коллапсов на вкладке 'Обзор'"):
            self.inquiries_page.click_tab(InquiryTab.Overview)
            self.inquiries_page.check_attribute_groups(
                displayed=[DESCRIPTION_GROUP, CALCULATION_INFO_GROUP, AGREEMENT_AND_ACCOUNT_GROUP]
            )

        with allure.step("Нажать кнопку 'Редактировать'"):
            self.inquiries_page.locators.ATTRIBUTES_EDIT_BTN.click()
            self.inquiries_page.locators.BTN_OPEN_DROPDOWN_AGREEMENT_AND_ACCOUNT.wait_to_be_visible(timeout=15000)
            self.inquiries_page.locators.BTN_OPEN_DROPDOWN_AGREEMENT_AND_ACCOUNT[1].click()
            self.inquiries_page.locators.ATTRIBUTES_DESCRIPTION.to_be_enabled()
            self.inquiries_page.locators.ATTRIBUTES_AGREEMENT.to_be_enabled()

        with allure.step("Изменить описание, заменить договор1 и ЛС1 на договор2 и ЛС2, сохранить"):
            self.inquiries_page.locators.ATTRIBUTES_AGREEMENT.select_by_index(1)
            self.inquiries_page.locators.ATTRIBUTES_ACCOUNT.select_by_index(1)
            self.inquiries_page.locators.ATTRIBUTES_SAVE_BTN.click()

        with allure.step("Проверить, что поля недоступны для редактирования и значения изменились"):
            self.inquiries_page.locators.ATTRIBUTES_EDIT_BTN.wait_to_be_visible(timeout=15000)
            self.inquiries_page.locators.SALE_AGREEMENT.to_contain_text(self.client.agreements[1].number)
            self.inquiries_page.locators.SALE_ACCOUNT.to_contain_text(str(self.client.agreements[1].account.number))

    @allure.title("04. Просмотр обновленных коллапсов при продаже продукта")
    @allure.id(957600)
    def test_sale_collapses(self) -> None:
        with allure.step("Создать заявку на продажу"):
            self.client_profile_page.open_client_overview_page(self.client.user_id)
            self.inquiries_page.sale_initialization(self.client, add_kp="no")
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.ManageOrderStructure)

        with allure.step("Добавить ПП в заказ"):
            product = self.inquiries_page.add_product_offer_to_commercial_order(test_context.client.inquiry.product)
            self.inquiries_page.locators.ADDED_PRODUCT.wait_to_have_count(1, timeout=10000)

        with allure.step("Забронировать ресурсы и проверить конфигурацию"):
            self.inquiries_page.auto_reserve_all_resources()
            self.inquiries_page.check_configuration()

        with allure.step("Перейти на 'Карточку продажи'"):
            self.inquiries_page.click_tab(InquiryTab.SaleCard)
            self.inquiries_page.check_attribute_groups(displayed=[DESCRIPTION_GROUP])

        with allure.step("Завершить продажу"):
            self.inquiries_page.click_tab(InquiryTab.ActiveStep)
            self.inquiries_page.locators.NEXT_STEP_BTN.click()
            self.inquiries_page.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)
            self.inquiries_page.locators.SUCCESS_COMPLITED.wait_to_be_visible(timeout=120000)
            self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.SaleCompletion)

        with allure.step("Перейти на вкладку 'Продукты' ЮЛ клиента"):
            self.client_product_profile_page.open_products_page_and_check(self.client.user_id, product_list=[product])

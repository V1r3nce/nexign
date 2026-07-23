import allure
import pytest
from playwright.sync_api import Page

from api.nbss.agreement_requests import AgreementRequests
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.adjustment_requests import AdjustmentRequests
from api.nbss.finances.billing_requests import BillingRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountRequests
from common.enums.inquiry import InquiryStep
from common.enums.user import User
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ChooseRequestTopic, ForwardInquiryForm, RequestCreate
from pages.locators.nbss.inquiries_elements import CloseInquiryForm, EditTerminationForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.debt_restructuring import DebtRestructuringPage
from pages.nbss.finances.payments_page import PaymentsPage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_55 Расторжение договора B2B")
@allure.suite("E2E_55 Расторжение договора B2B")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestTerminateContract:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login: Page,
        organization_user_data: OrganizationClient,
    ) -> None:
        self.base_page = BasePage()
        self.client_profile = ClientProfilePage()
        self.client_api = ClientRequests()
        self.client_inquiries_api = ClientInquiriesRequests()
        self.inquiries_page = InquiriesPage()
        self.agreement_api = AgreementRequests()
        self.request_create = RequestCreate()
        self.choose_request_topic = ChooseRequestTopic()
        self.forward_inquiry_form = ForwardInquiryForm()
        self.payments_page = PaymentsPage()
        self.edit_termination_form = EditTerminationForm()
        self.payment_api = PaymentsRequests()
        self.billing_api = BillingRequests()
        self.adjustment_api = AdjustmentRequests()
        self.personal_account_api = PersonalAccountRequests()
        self.debt_page = DebtRestructuringPage()
        self.init_payment = 50
        self.close_inquiry_form = CloseInquiryForm()

    @allure.step("Процесс создания заявки на Расторжение Договора")
    def process_create_inquiry_request(self):
        with allure.step("В правом сайдбаре выбрать пункт 'Создание заявки'"):
            self.client_profile.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step('Выбрать тему (Обязательно): Нажать на "..."'):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.wait_to_be_visible()

        with allure.step("Выбрать тему: 'Претензия' - 'Не согласен с расчетами'"):
            self.choose_request_topic.REQUEST_TOPIC_NAME.wait_for_text_in_all(["Действия"])
            topic_index = self.choose_request_topic.REQUEST_TOPIC_NAME.text_list.index("(5) 05 Действия")
            self.choose_request_topic.EXPAND_BTN.click(topic_index)
            self.choose_request_topic.REQUEST_TOPIC_NAME.wait_for_text_in_all(["Расторжение договора"])
            topic_index = self.choose_request_topic.REQUEST_TOPIC_NAME.text_list.index(
                "(AGREEMENT_TERMINATION) Расторжение договора"
            )
            self.choose_request_topic.REQUEST_TOPIC_NAME.click(topic_index)

        with allure.step("Нажать 'Применить'"):
            self.choose_request_topic.ACCEPT_BTN.wait_to_be_enabled()
            self.choose_request_topic.ACCEPT_BTN.click()
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.EMAIL.check_attribute_not_contain_value("aria-required", "true")
            self.request_create.PHONE.check_attribute_not_contain_value("aria-required", "true")
            self.request_create.DESCRIPTION.check_attribute_not_contain_value("aria-required", "true")

        with allure.step("Нажать 'Передать' на форме 'Создание заявки'"):
            self.forward_inquiry_form.REASON_TERMINATE_FIELD.wait_to_be_visible(timeout=10000)
            self.forward_inquiry_form.REASON_TERMINATE_FIELD.select_by_value("По инициативе клиента")
            self.forward_inquiry_form.TERMINATE_CONTRACT_FIELD.select_by_index(0)
            self.forward_inquiry_form.SAVE_BTN.click()

    @allure.title("01 Расторжение договора текущей датой")
    @allure.id(745921)
    def test_terminate_contract(self, organization_user_data) -> None:
        with allure.step("Прекондишн: Создание организации с договором"):
            self.client_api.create_organization_with_agreement_and_account(organization_user_data)

            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")

            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )
            self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=10000)

        self.process_create_inquiry_request()

        self.inquiries_page.locators.INFO_TERMINATE_CONTRACT.wait_to_be_visible(timeout=60000)
        self.inquiries_page.refresh_page("networkidle")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=45000)

    @allure.title("02 Расторжение текущей датой договора с блокирующими сущностями")
    @allure.id(745916)
    def test_terminate_contract_with_block_entity(self, organization_user_data) -> None:
        with allure.step("Прекондишн: Создание организации с договором и балансом на лиц.счёте."):
            self.client_api.create_client_with_payment(organization_user_data, 5000)

            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")

            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )
            self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=20000)
        self.process_create_inquiry_request()
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.SearchBlockingEntities, timeout=30000)
        inquiry_id = self.client_inquiries_api._get_inquiries(user_id=test_context.client.user_id)[0]
        self.client_inquiries_api.assert_custom_property_bool_by_code(
            inquiry_id=inquiry_id,
            custom_property_code="agtrmIgnorCreditAccounts",
            expected_value=False,
        )
        self.inquiries_page.locators.ERROR_NOTIFICATIONS.to_contain_text_in_any(
            "Обнаружены лицевые счета с ненулевым балансом.", timeout=15
        )

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/accounts")
        self.client_profile.locators.CURRENT_PERSONAL_ACCOUNT_LINK.wait_to_be_enabled(timeout=15000)
        self.client_profile.locators.CURRENT_PERSONAL_ACCOUNT_LINK.click()
        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Платежи")
        self.payments_page.payment_elements.CHECK_NUM_FIELDS.wait_to_have_count(1, timeout=10000)
        self.payments_page.payment_elements.STATUS_FIELDS[0].click()
        self.payments_page.fill_annul_form()
        self.payments_page.payment_elements.USER_BALANCE.wait_to_have_text("0.00", timeout=20000)

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/inquiries")
        self.client_profile.locators.REQUEST_NUMBER.wait_to_have_count(1, timeout=10000)
        self.client_profile.locators.REQUEST_NUMBER[0].click()
        self.inquiries_page.locators.LEFT_ARROW_BTN.wait_to_be_enabled(timeout=7000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.click()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.wait_to_be_visible()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.click()
        self.inquiries_page.locators.INFO_TERMINATE_CONTRACT.wait_to_be_visible(timeout=60000)
        self.inquiries_page.refresh_page("networkidle")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=30000)

    @allure.title(
        "03 Расторжение текущей датой договора с выключенной проверкой на активные ЛС с отрицательным балансом"
    )
    @allure.id(745917)
    def test_terminate_contract_with_negative_balance(self, organization_user_data) -> None:
        with allure.step(
            "Прекондишн: Создание организации с договором и отриц. балансом на лиц.счёте. Выключена проверка на отриц. баланс"
        ):
            self.client_api.create_client_with_payment(organization_user_data, 1000)

            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")

            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )
            billing_profile_id = self.billing_api.get_billing_profile_id(
                test_context.client.agreements[0].accounts[0].id
            )
            self.adjustment_api.create_adjustment(
                adjustment_type_id=13,
                adjustment_reason_id=18,
                amount=2000,
                billing_profile_id=billing_profile_id,
                bill_detail_id=100088,
                account_financial_profile_id=test_context.client.agreements[0].accounts[0].id,
            )
            self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=10000)

        self.process_create_inquiry_request()
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.SearchBlockingEntities, timeout=30000)
        inquiry_id = self.client_inquiries_api._get_inquiries(user_id=test_context.client.user_id)[0]
        self.client_inquiries_api.assert_custom_property_bool_by_code(
            inquiry_id=inquiry_id,
            custom_property_code="agtrmIgnorDebitAccounts",
            expected_value=False,
        )
        self.client_inquiries_api.update_inquiry_boolean_custom_property(
            inquiry_id=inquiry_id,
            property_code="agtrmIgnorDebitAccounts",
            value=True,
        )
        self.inquiries_page.locators.ERROR_NOTIFICATIONS.wait_to_be_visible(timeout=30000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.wait_to_be_enabled(timeout=7000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.click()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.wait_to_be_visible()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.click()
        self.inquiries_page.locators.INFO_TERMINATE_CONTRACT.wait_to_be_visible(timeout=45000)
        self.inquiries_page.refresh_page("networkidle")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=30000)

    @allure.title(
        "04 Расторжение текущей датой договора с выключенной проверкой на активные ЛС с положительным балансом"
    )
    @allure.id(745922)
    def test_terminate_contract_with_balance(self, organization_user_data) -> None:
        with allure.step(
            "Прекондишн: Создание организации с договором и балансом на лиц.счёте. Выключена проверка на наличие баланса"
        ):
            self.client_api.create_client_with_payment(organization_user_data, 1000)

            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")

            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )
        self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=20000)

        self.process_create_inquiry_request()
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.SearchBlockingEntities, timeout=30000)
        inquiry_id = self.client_inquiries_api._get_inquiries(user_id=test_context.client.user_id)[0]
        self.client_inquiries_api.assert_custom_property_bool_by_code(
            inquiry_id=inquiry_id,
            custom_property_code="agtrmIgnorCreditAccounts",
            expected_value=False,
        )
        self.client_inquiries_api.update_inquiry_boolean_custom_property(
            inquiry_id=inquiry_id,
            property_code="agtrmIgnorCreditAccounts",
            value=True,
        )
        self.inquiries_page.locators.ERROR_NOTIFICATIONS.wait_to_be_visible(timeout=30000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.wait_to_be_enabled(timeout=7000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.click()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.wait_to_be_visible()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.click()
        self.inquiries_page.locators.INFO_TERMINATE_CONTRACT.wait_to_be_visible(timeout=45000)
        self.inquiries_page.refresh_page("networkidle")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=30000)

    @allure.title("06 Расторжение текущей датой договора с выключенной проверкой на активные рассрочки")
    @allure.id(745919)
    def test_terminate_contract_with_installment(self, organization_user_data) -> None:
        with allure.step(
            "Прекондишн: Создание организации с договором и рассрочкой. Выключена проверка на наличие рассрочек"
        ):
            self.client = self.client_api.create_client_with_payment(organization_user_data, 1000)
            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")
            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)
            billing_profile_id = self.billing_api.get_billing_profile_id(
                test_context.client.agreements[0].accounts[0].id
            )
            self.adjustment_api.create_adjustment(
                adjustment_type_id=13,
                adjustment_reason_id=18,
                amount=2000,
                billing_profile_id=billing_profile_id,
                bill_detail_id=100088,
                account_financial_profile_id=test_context.client.agreements[0].accounts[0].id,
            )
            self.adjustment_api.wait_adjustment_status(test_context.client.agreements[0].accounts[0].id)
            self.billing_api.run_unscheduled_billing(billing_profile_id=billing_profile_id)
            self.billing_api.wait_billing(billing_profile_id=billing_profile_id)
            self.billing_api.wait_finish_billing(billing_profile_id=billing_profile_id)

            inquiry_id = self.debt_page.inquiry_create(self.client)
            self.debt_page.installment_create([150])
            delay(2, "Не успевает появиться в списке")
            self.debt_page.locators.REFRESH_INSTALLMENTS_BTN.click()
            self.debt_page.locators.INSTALLMENTS.wait_to_have_count(1)
            self.debt_page.locators.INSTALLMENTS[0].click()
            self.debt_page.locators.PAYMENT_HEADER.wait_to_have_count(1)
            self.debt_page.locators.PAYMENT_HEADER.to_contain_text_in_any(str(self.init_payment))
            self.debt_page.inquiry_forward(inquiry_id)

            self.payment_api.create_default_payment(test_context.client.agreements[0].accounts[0].id, 1000)
            self.personal_account_api.wait_check_current_main_balance(
                test_context.client.agreements[0].accounts[0].id, 0
            )
            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )
        self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=10000)
        self.client_profile.locators.CREATE_REQUEST.click()
        self.request_create.CREATE_FORM.wait_to_be_visible()
        self.request_create.TOPIC.click()
        self.choose_request_topic.REQUEST_TOPIC_NAME.wait_for_text_in_all(["Действия"])
        topic_index = self.choose_request_topic.REQUEST_TOPIC_NAME.text_list.index(
            "(2) 02 Расчетно-справочное обслуживание"
        )
        self.choose_request_topic.EXPAND_BTN.click(topic_index)
        self.base_page.refresh_page("networkidle")

        self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=10000)
        self.process_create_inquiry_request()
        self.inquiries_page.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.SearchBlockingEntities, timeout=30000)
        inquiry_id = self.client_inquiries_api._get_inquiries(user_id=test_context.client.user_id)[1]
        self.client_inquiries_api.assert_custom_property_bool_by_code(
            inquiry_id=inquiry_id,
            custom_property_code="agtrmIgnorActiveInstallments",
            expected_value=False,
        )
        self.client_inquiries_api.update_inquiry_boolean_custom_property(
            inquiry_id=inquiry_id,
            property_code="agtrmIgnorActiveInstallments",
            value=True,
        )
        self.inquiries_page.locators.ERROR_NOTIFICATIONS.wait_to_be_visible(timeout=30000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.wait_to_be_enabled(timeout=7000)
        self.inquiries_page.locators.LEFT_ARROW_BTN.click()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.wait_to_be_visible()
        self.edit_termination_form.ACCEPT_OUT_FIND_ENTITY_BTN.click()
        self.inquiries_page.locators.INFO_TERMINATE_CONTRACT.wait_to_be_visible(timeout=45000)
        self.inquiries_page.refresh_page("networkidle")
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=30000)

    @allure.title("08 Проверка возможности расторжения договора на пользователе (без прав)")
    @allure.id(745920)
    @pytest.mark.user(User.FINANCE_TEST)
    def test_terminate_contract_without_permission(self, organization_user_data) -> None:
        with allure.step("Прекондишн: Создание организации с договором"):
            self.client_api.create_organization_with_agreement_and_account(organization_user_data)

            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")

            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )
        self.client_profile.locators.CREATE_REQUEST.not_to_be_visible()

    @allure.title("07 Отмена заявки на расторжение договора")
    @allure.id(745923)
    def test_terminate_contract_cancel(self, organization_user_data) -> None:
        with allure.step("Прекондишн: Создание организации с договором"):
            self.client = self.client_api.create_client_with_payment(organization_user_data, 1000)
            self.client_api.create_linked_person(test_context.client.user_id, "Иван Иваныч")

            agreement_id = test_context.client.agreements[0].id

            self.agreement_api.sign_agreement(agreement_id)

            self.base_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/agreements"
            )

        self.client_profile.locators.DOCUMENTS_LINE.wait_to_have_count(1, timeout=10000)

        self.process_create_inquiry_request()
        self.inquiries_page.locators.ERROR_NOTIFICATIONS.to_contain_text_in_any(
            "Обнаружены лицевые счета с ненулевым балансом.", timeout=15
        )
        self.inquiries_page.locators.CLOSE_INQUIRY_BTN.click()
        self.close_inquiry_form.INNER_ACCEPT_BTN.click()
        self.inquiries_page.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто")

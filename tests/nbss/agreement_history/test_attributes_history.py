import allure
import pytest

from common.helpers.env_helper import BASE_URL
from models.address_info import BasicSystemAddress
from models.client import IndividualClient
from models.context import test_context
from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import AddRelatedPersonForms, PersonalAccountForm
from pages.nbss.agreement_page import AgreementPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.suite("E2E_54 История изменения атрибутов объекта")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=762057702",
    name="RMBSS-682. ГФС. История изменения атрибутов объекта",
)
@pytest.mark.nbss_portal
@pytest.mark.regress
class TestAgreementAttributeHistory:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.personal_account_page = PersonalAccountPage()
        self.client_profile_page = ClientProfilePage()
        self.agreement_page = AgreementPage()
        self.base_elements = BaseElements()
        self.add_related_person_form = AddRelatedPersonForms()
        self.personal_account_form = PersonalAccountForm()

    @allure.title("Просмотр истории изменения атрибутов Договора")
    @allure.id(644258)
    def test_agreement_history_sidebar_displays_records(
        self,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        agreement_id = test_context.client.agreements[0].id
        with allure.step("Arrange: открыть страницу договора для клиента, созданного через API"):
            self.agreement_page.open(f"{BASE_URL}customer-hierarchy-management/agreements/{agreement_id}/agreement")
            self.client_profile_page.locators.EDIT_AGREEMENT_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.EDIT_AGREEMENT_BTN.click()
            self.agreement_page.locators.SIGNING_DATE.wait_to_be_visible(timeout=60000)
        with allure.step("Act: изменить атрибуты договора (кроме даты подписания)"):
            self.agreement_page.locators.AGREEMENT_TYPE.wait_to_be_visible(timeout=60000)
            self.agreement_page.locators.AGREEMENT_TYPE.select_by_value("Агентский договор")
            self.personal_account_page.dynamic_form.SAVE_BTN.wait_to_be_visible(timeout=30000)
            self.personal_account_page.dynamic_form.SAVE_BTN.click()
        with allure.step(
            "Assert: открыть историю изменений и убедиться, что записи с изменёнными атрибутами присутствуют"
        ):
            self.agreement_page.locators.HISTORY_BTN.wait_to_be_visible(timeout=30000)
            self.agreement_page.locators.HISTORY_BTN.click()
            self.agreement_page.locators.HISTORY_SIDEBAR_TITLE.wait_to_be_visible(timeout=10000)
            self.agreement_page.locators.REFRESH_BTN.wait_to_be_visible(timeout=10000)
            self.agreement_page.locators.REFRESH_BTN.click()
            self.agreement_page.locators.HISTORY_TABLE_CELLS.wait_elements_visible(element_index=0, timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all(["Агентский договор"], timeout=30000)

    @allure.title("Просмотр истории изменения атрибутов Клиента")
    @allure.id(644252)
    def test_client_history_sidebar_displays_records(
        self,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        with allure.step("Arrange: открыть карточку клиента, созданного через API"):
            self.client_profile_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile_page.click_tab("Персональные данные")
        with allure.step("Act: отредактировать несколько атрибутов клиента и сохранить"):
            self.client_profile_page.locators.EDIT_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.EDIT_BTN.click()
            self.client_profile_page.edit_client_form.SURNAME_INPUT.wait_to_be_visible(timeout=30000)
            surname = "Николаев"
            name = "Алексей"
            new_birth_place = "АвтотестыИсторияГорода"
            new_document_issuer = "Орган Истории Автотестов"
            self.client_profile_page.edit_client_form.SURNAME_INPUT.clear_input()
            self.client_profile_page.edit_client_form.SURNAME_INPUT.fill(surname)
            self.client_profile_page.edit_client_form.NAME_INPUT.clear_input()
            self.client_profile_page.edit_client_form.NAME_INPUT.fill(name)
            self.client_profile_page.edit_client_form.BIRTH_PLACE.clear_input()
            self.client_profile_page.edit_client_form.BIRTH_PLACE.fill(new_birth_place)
            self.client_profile_page.edit_client_form.DOCUMENT_PROVIDE_BY.clear_input()
            self.client_profile_page.edit_client_form.DOCUMENT_PROVIDE_BY.fill(new_document_issuer)
            self.personal_account_page.dynamic_form.SAVE_BTN.wait_to_be_visible(timeout=30000)
            self.personal_account_page.dynamic_form.SAVE_BTN.click()
        with allure.step("Assert: открыть историю и проверить, что новые значения присутствуют в записях"):
            self.client_profile_page.locators.HISTORY_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.HISTORY_BTN.click()
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.to_contain_text("История изменений")
            self.client_profile_page.locators.HISTORY_TABLE_CELLS.wait_elements_visible(element_index=0, timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all([surname], timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all([name], timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all([new_birth_place], timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all([new_document_issuer], timeout=30000)

    @allure.title("Просмотр истории изменения атрибутов Связанного лица")
    @allure.id(644337)
    def test_related_person_history_sidebar_displays_records(
        self,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        with allure.step("Arrange: открыть карточку клиента и добавить связанное лицо через UI"):
            self.client_profile_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=30000)
            self.personal_account_page.locators.RELATED_PERSONS_TAB.click()
            self.personal_account_page.locators.ADD_RELATED_PERSON_BTN.click()
            self.add_related_person_form.TITLE.wait_to_be_visible(timeout=30000)
            linked_person_name = "мать драконов"
            self.add_related_person_form.fill_data_for_related_person(
                type_related_person="Обезличенное",
                name_related_person=linked_person_name,
                function="Выгодоприобретатель",
                email="autotест@example.com",
            )
            self.client_profile_page.locators.RELATED_PERSON_NAME.wait_to_have_text(linked_person_name)
        with allure.step("Act: отредактировать поля SPEAKING_LANGUAGE и NOTE у связанного лица"):
            self.client_profile_page.locators.EDIT_BTN.click()
            new_speaking_language = "Английский"
            self.add_related_person_form.SPEAKING_LANGUAGE.select_by_value(new_speaking_language)
            self.personal_account_page.dynamic_form.SAVE_BTN.wait_to_be_visible(timeout=30000)
            self.personal_account_page.dynamic_form.SAVE_BTN.click()
        with allure.step("Assert: открыть сайдбар 'История изменений' и проверить наличие изменений"):
            self.client_profile_page.locators.HISTORY_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.HISTORY_BTN.click()
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.to_contain_text("История изменений")
            self.client_profile_page.locators.HISTORY_TABLE_CELLS.wait_elements_visible(element_index=0, timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all([linked_person_name], timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all([new_speaking_language], timeout=30000)

    @allure.title("Просмотр истории изменения атрибутов Лицевого счета")
    @allure.id(644259)
    def test_personal_account_history_sidebar_displays_records(
        self,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        with allure.step("Arrange: открыть страницу ЛС клиента, созданного через API"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
            )
        with allure.step("Act: изменить атрибут ЛС и сохранить"):
            self.client_profile_page.locators.EDIT_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.EDIT_BTN.click(timeout=30000)
            self.personal_account_form.PAYMENT_METHOD.wait_to_be_visible(timeout=30000)
            self.personal_account_form.PAYMENT_METHOD.select_by_value("Постоплатный")
            self.personal_account_page.dynamic_form.SAVE_BTN.click(timeout=30000)
        with allure.step(
            "Assert: открыть сайдбар 'История изменений' и проверить наличие записей и изменённых значений"
        ):
            self.client_profile_page.locators.HISTORY_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.HISTORY_BTN.click()
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.to_contain_text("История изменений")
            self.client_profile_page.locators.HISTORY_TABLE_CELLS.wait_elements_visible(element_index=0, timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all(["2"], timeout=30000)

    @allure.title("Адреса клиента: отображение сайдбара 'История изменений' и записей истории")
    @allure.id(644338)
    def test_client_addresses_history_sidebar_displays_records(
        self,
        create_user_with_agreement_and_account: IndividualClient,
    ) -> None:
        with allure.step("Arrange: открыть карточку клиента и перейти на вкладку Адреса"):
            self.client_profile_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview"
            )
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=30000)
            self.client_profile_page.click_tab("Персональные данные")
            self.client_profile_page.locators.ADDRESSES_TAB.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.ADDRESSES_TAB.click(timeout=30000)
            self.client_profile_page.locators.ADD_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.ADD_BTN.click(timeout=30000)
            self.client_profile_page.add_address_form.TITLE.to_contain_text("Добавление адреса")
            self.client_profile_page.add_address_form.ADDRESS_TYPE_FIELD.select_by_value("Фактический адрес")
            self.client_profile_page.add_address_form.ADDRESS_INPUT.fill(BasicSystemAddress.address)
            self.client_profile_page.add_address_form.ADDRESS_OPTION.wait_elements_visible(0)
            self.client_profile_page.add_address_form.ADDRESS_OPTION[0].to_contain_text(BasicSystemAddress.address)
            self.client_profile_page.add_address_form.ADDRESS_OPTION[0].click()
            self.client_profile_page.add_address_form.SAVE_BTN.to_be_enabled()
            self.client_profile_page.add_address_form.SAVE_BTN.click()
        with allure.step("Act: открыть сайдбар 'История изменений' для адресов"):
            self.client_profile_page.locators.HISTORY_BTN.wait_to_be_visible(timeout=30000)
            self.client_profile_page.locators.HISTORY_BTN.click()
        with allure.step("Assert: заголовок сайдбара и наличие записей истории по адресам клиента"):
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.HISTORY_SIDEBAR_TITLE.to_contain_text("История изменений")
            self.client_profile_page.locators.HISTORY_TABLE_CELLS.wait_elements_visible(element_index=0, timeout=30000)
            self.agreement_page.locators.HISTORY_TABLE_ROWS.wait_for_text_in_all(["Адрес"], timeout=30000)

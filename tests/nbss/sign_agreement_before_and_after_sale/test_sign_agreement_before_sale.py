import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import get_current_datetime_string, get_shifted_datetime_string
from models.user import OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.agreement_form import AgreementForm
from pages.locators.nbss.client.client_profile import ClientProfile
from pages.locators.nbss.dynamic_form_elements import AddRelatedPersonForms
from pages.nbss.agreement_page import AgreementPage


@allure.epic("E2E_62_17 Продажа клиенту B2B: Подписание Договора после завершения продажи")
@allure.suite("E2E_62_17 Продажа клиенту B2B: Подписание Договора после завершения продажи")
@allure.sub_suite("E2E_62_35 Продажа клиенту B2B (Подписание договора на клиенте до прохождения процесса продажи)")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=719296060",
    name="CLM-XXXXXX.ГФС:Подписание договора после завершения продажи",
)
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestSignAgreementBeforeSale:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        create_organization_with_agreement_and_account: OrganizationClient,
        base_url: str,
    ) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_info = create_organization_with_agreement_and_account
        self.client_requests = ClientRequests(api_request_context)
        self.client_profile = ClientProfile(nexign_ui_stand_login)
        self.agreement_form = AgreementForm(nexign_ui_stand_login)
        self.agreement_page = AgreementPage(nexign_ui_stand_login)
        self.add_related_person_form = AddRelatedPersonForms(nexign_ui_stand_login)
        self.today_date = get_current_datetime_string(is_full_format=False)

    @allure.title("01. Подписание договора до завершения продажи")
    @allure.id(666621)
    def test_sign_agreement_before_sale(self, base_url: str, remove_file_from_download_folder: list) -> None:
        with allure.step("Подготовка тестовых данных"):
            self.client_requests.create_linked_person(self.client_info.user_id, self.client_info.name_related_person)
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{self.client_info.agreements[0].id}/agreement"
            )
            self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Договор"], timeout=10000)

        with allure.step("Нажать кнопку 'Подписать договор'"):
            self.client_profile.SIGN_AGREEMENT_BTN.click()
            self.agreement_form.TITLE.wait_to_be_visible()

        with allure.step("Заполнить обязательные поля"):
            file_name = f"Agreement_{self.client_info.agreements[0].number}.txt"
            file_path = self.agreement_page.create_agreement_text_file(file_name)
            self.agreement_page.fill_sign_agreement_form(
                self.today_date, self.client_info.name_related_person, [file_path]
            )
            self.agreement_form.INNER_ACCEPT_BTN.click()
            self.agreement_form.TITLE.not_to_be_visible()
            remove_file_from_download_folder.append(file_path)
            self.client_profile.AGREEMENT_STATUS.wait_to_have_text("Действующий")
            self.client_profile.SIGN_AGREEMENT_BTN.not_to_be_visible()

    @allure.title("02. Подписание договора до завершения продажи (нет связанного лица)")
    @allure.id(666623)
    def test_sign_agreement_before_sale_without_link_person(
        self, base_url: str, remove_file_from_download_folder: list
    ) -> None:
        with allure.step("Подготовка тестовых данных"):
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{self.client_info.agreements[0].id}/agreement"
            )
            self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Договор"], timeout=10000)

        with allure.step("Нажать кнопку 'Подписать договор'"):
            self.client_profile.SIGN_AGREEMENT_BTN.click()
            self.agreement_form.TITLE.wait_to_be_visible()

        with allure.step("Создать связанное лицо"):
            self.agreement_form.NO_LINK_PERSON_ATTENTION.wait_to_be_visible()
            self.agreement_form.CREATE_LINK_PERSON_BTN.click()
            self.add_related_person_form.TITLE.wait_to_be_visible()
            self.add_related_person_form.fill_data_for_related_person(
                name_related_person=f"{self.client_info.name_related_person}",
                function="Подписант договора",
            )
            self.add_related_person_form.TITLE.not_to_be_visible(timeout=10000)

        with allure.step("Нажать кнопку 'Подписать договор'"):
            self.client_profile.SIGN_AGREEMENT_BTN.click()
            self.agreement_form.TITLE.wait_to_be_visible()

        with allure.step("Заполнить обязательные поля"):
            file_name = f"Agreement_{self.client_info.agreements[0].number}.txt"
            file_path = self.agreement_page.create_agreement_text_file(file_name)
            self.agreement_page.fill_sign_agreement_form(
                self.today_date, self.client_info.name_related_person, [file_path]
            )
            self.agreement_form.INNER_ACCEPT_BTN.click()
            self.agreement_form.TITLE.not_to_be_visible()
            remove_file_from_download_folder.append(file_path)
            self.client_profile.AGREEMENT_STATUS.wait_to_have_text("Действующий")
            self.client_profile.SIGN_AGREEMENT_BTN.not_to_be_visible()

    @allure.title("03. Редактирование договора до завершения продажи")
    @allure.id(666622)
    def test_edit_agreement_before_sale(self, base_url: str) -> None:
        with allure.step("Подготовка тестовых данных"):
            self.client_requests.create_linked_person(self.client_info.user_id, self.client_info.name_related_person)
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{self.client_info.agreements[0].id}/agreement"
            )
            self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Договор"], timeout=10000)

        with allure.step("Нажать кнопку 'Редактировать'"):
            self.client_profile.EDIT_AGREEMENT_BTN.click()
            self.agreement_form.TITLE.wait_to_be_visible()

        with allure.step("Изменить поле 'Дата расторжения договора' и поле 'Тип договора'"):
            self.agreement_form.INDEFINITE_CHECKBOX.wait_to_be_visible()
            self.agreement_form.INDEFINITE_CHECKBOX.click()
            self.agreement_form.EXPIRATION_DATE.wait_to_be_visible()
            expiration_date_future = get_shifted_datetime_string("+30d", False)
            self.agreement_form.EXPIRATION_DATE.type(expiration_date_future)
            self.agreement_form.AGREEMENT_TYPE.select_by_value("Агентский договор")

        with allure.step("Нажать кнопку 'Сохранить'"):
            self.agreement_form.SAVE_BTN.click()
            self.agreement_form.TITLE.not_to_be_visible()

        with allure.step("Проверить, что в карточке договора отобразилась новая дата расторжения договора"):
            self.client_profile.AGREEMENT_EXPIRATION_DATE.to_have_value(expiration_date_future)
            self.client_profile.AGREEMENT_TYPE.to_have_value("Агентский договор")

    @allure.title("04. Подписание договора до завершения продажи. Не заполнены обязательные поля")
    @allure.id(681397)
    def test_sign_agreement_before_sale_without_filling_required_fields(self, base_url: str) -> None:
        with allure.step("Подготовка тестовых данных"):
            self.client_requests.create_linked_person(self.client_info.user_id, self.client_info.name_related_person)
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{self.client_info.agreements[0].id}/agreement"
            )
            self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Договор"], timeout=10000)

        with allure.step("Нажать кнопку 'Подписать договор'"):
            self.client_profile.SIGN_AGREEMENT_BTN.click()
            self.agreement_form.TITLE.wait_to_be_visible()

        with allure.step("Нажать кнопку подписать"):
            self.agreement_form.INNER_ACCEPT_BTN.click()
            self.agreement_form.CLIENT_REPRESENTATIVE_NAME.check_attribute_by_value("aria-invalid", "true")
            self.agreement_form.CLIENT_REPRESENTATIVE_NAME_NOT_FILLED_ERROR.wait_to_be_visible()
            self.agreement_form.ATTACH_DOCUMENT_FIELD_NOT_FILLED_ERROR.wait_to_be_visible()

    @allure.title(
        "05. Редактирование договора до завершения продажи. Дата расторжения договора меньше даты подписания договора"
    )
    @allure.id(682462)
    def test_edit_agreement_before_sale_expiration_date_less_than_signing_date(self, base_url: str) -> None:
        with allure.step("Подготовка тестовых данных"):
            self.client_requests.create_linked_person(self.client_info.user_id, self.client_info.name_related_person)
            self.base_page.open(
                f"{base_url}customer-hierarchy-management/agreements/{self.client_info.agreements[0].id}/agreement"
            )
            self.base_page.base_elements.CONTEXT_ELEMENT.wait_for_text_in_all(["Договор"], timeout=10000)

        with allure.step("Нажать кнопку 'Редактировать'"):
            self.client_profile.EDIT_AGREEMENT_BTN.click()
            self.agreement_form.TITLE.wait_to_be_visible()

        with allure.step("Изменить поле 'Дата расторжения договора'"):
            self.agreement_form.INDEFINITE_CHECKBOX.wait_to_be_visible()
            self.agreement_form.INDEFINITE_CHECKBOX.click()
            self.agreement_form.EXPIRATION_DATE.wait_to_be_visible()
            expiration_date_past = get_shifted_datetime_string("-30d", False)
            self.agreement_form.EXPIRATION_DATE.type(expiration_date_past)
            self.agreement_form.TITLE.click()

        with allure.step("Нажать кнопку 'Сохранить'"):
            self.agreement_form.SAVE_BTN.click()
            self.agreement_form.MODAL.wait_to_be_visible()
            self.agreement_form.MODAL_BODY_TEXT.wait_to_have_text("Некорректная дата расторжения договора.")

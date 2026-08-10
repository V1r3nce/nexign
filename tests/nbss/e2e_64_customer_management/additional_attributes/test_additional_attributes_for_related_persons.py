import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.linked_person import LinkedPersonFunction
from common.helpers.data_generator import generate_russian_string
from models.client import IndividualClient
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import ClientProfileElements, ClientRelatedPersons
from pages.locators.nbss.dynamic_form_elements import RelatedPersonForms
from pages.nbss.client.client_linked_persons_page import ClientLinkedPersonsPage
from pages.nbss.client.client_profile_page import ClientProfilePage


@allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAdditionalAttributesForRelatedPersons:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.client_profile = ClientProfileElements()
        self.related_person_form = RelatedPersonForms()
        self.client_related_persons = ClientRelatedPersons()
        self.client_related_persons_page = ClientLinkedPersonsPage()
        self.client_api = ClientRequests()

        self.related_person_function = LinkedPersonFunction.beneficiary
        self.related_person_note = f"Дополнительный атрибут: {generate_russian_string(8)}"

    @allure.title("01. Добавление доп.атрибутов при создании связанного лица")
    @allure.id(956497)
    def test_add_related_person_with_additional_attributes(
        self, create_individual_user: IndividualClient, individual_user_data
    ):
        related_person = individual_user_data

        with allure.step("Перейти на вкладку 'Связанные лица' клиента"):
            self.client_profile_page.open_linked_person_page(test_context.client.user_id)

        self.client_related_persons_page.add_individual_related_person(related_person, comment=self.related_person_note)
        self.client_related_persons_page.fill_related_person_function_and_contacts(
            self.related_person_function, related_person.contact_phone
        )

        self.client_related_persons_page.check_related_person_card(related_person, self.related_person_note)

    @allure.title("02. Редактирование доп.атрибутов связанного лица")
    @allure.id(956600)
    def test_related_person_edit_additional_attributes(
        self, create_individual_user: IndividualClient, individual_user_data: IndividualClient
    ):
        related_person = individual_user_data

        with allure.step("Создание связанного лица"):
            self.client_api.create_linked_person(test_context.client.user_id, linked_person=related_person)

        with allure.step("Перейти на вкладку 'Связанные лица' клиента"):
            self.client_profile_page.open_linked_person_page(test_context.client.user_id)

        self.client_related_persons_page.select_related_person_in_list()
        self.client_related_persons_page.edit_related_person_additional_attribute(self.related_person_note)

        self.client_related_persons_page.check_related_person_card(related_person, self.related_person_note)

    @allure.title("03. Отображение доп.атрибутов существующего связанного лица при добавлении")
    @allure.id(956601)
    def test_related_person_view_existing_additional_attributes(
        self, create_individual_user: IndividualClient, individual_user_data: IndividualClient
    ):
        related_person = individual_user_data
        related_person_name = f"{related_person.sur_name} {related_person.first_name} {related_person.patronymic}"

        with allure.step("Создание связанного лица"):
            self.client_api.create_linked_person(
                test_context.client.user_id, linked_person=related_person, note=self.related_person_note
            )

        with allure.step("Перейти на вкладку 'Связанные лица' клиента"):
            self.client_profile_page.open_linked_person_page(test_context.client.user_id)

        self.client_related_persons_page.open_add_related_person_form()
        self.client_related_persons_page.select_related_person_in_form(related_person_name)
        self.client_related_persons_page.check_related_person_on_form_and_proceed(
            related_person, self.related_person_note
        )

        self.client_related_persons_page.fill_related_person_function_and_contacts(
            self.related_person_function, related_person.contact_phone
        )
        self.client_related_persons_page.check_related_person_card(
            related_person, self.related_person_note, expected_count=2
        )

    @allure.title("04. Просмотр доп.атрибутов связанного лица")
    @allure.id(956633)
    def test_related_person_view_additional_attributes(
        self, create_individual_user: IndividualClient, individual_user_data: IndividualClient
    ):
        related_person = individual_user_data

        with allure.step("Создание связанного лица"):
            self.client_api.create_linked_person(
                test_context.client.user_id, linked_person=related_person, note=self.related_person_note
            )

        with allure.step("Перейти на вкладку 'Связанные лица' клиента"):
            self.client_profile_page.open_linked_person_page(test_context.client.user_id)

        with allure.step("Выбрать связанное лицо с заполненными дополнительными атрибутами"):
            self.client_related_persons_page.select_related_person_in_list()

        self.client_related_persons_page.check_related_person_card(related_person, self.related_person_note)

    @allure.title("05. Создание обезличенного связанного лица")
    @allure.id(956825)
    def test_related_person_create_impersonal(self, create_individual_user: IndividualClient) -> None:
        related_person_name = test_context.client.linked_person_name
        related_person_phone = test_context.client.linked_person_phone

        with allure.step("Перейти на вкладку 'Связанные лица' клиента"):
            self.client_profile_page.open_linked_person_page(test_context.client.user_id)

        self.client_related_persons_page.add_impersonal_related_person(related_person_name)
        self.client_related_persons_page.fill_related_person_function_and_contacts(
            self.related_person_function, related_person_phone
        )

        with allure.step("Проверить заполненные данные обезличенного связанного лица"):
            self.client_profile.RELATED_PERSONS.wait_to_have_count(1)
            self.client_profile.RELATED_PERSON_BENEFICIARY_NAME.to_contain_text(related_person_name)
            self.client_related_persons.EDIT_RELATED_PERSONS_BTN.wait_to_be_enabled()
            self.client_related_persons.HISTORY_RELATED_PERSONS_BTN.wait_to_be_enabled()

        with allure.step("Блок дополнительных атрибутов не отображается"):
            self.related_person_form.COMMENT_FIELD.not_to_be_visible_for()

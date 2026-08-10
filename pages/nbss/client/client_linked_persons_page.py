import allure

from common.enums.linked_person import LinkedPersonType
from common.helpers.time_helpers import delay
from models.client import IndividualClient
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import (
    ClientProfileElements,
    ClientRelatedPersons,
)
from pages.locators.nbss.dynamic_form_elements import (
    RelatedPersonForms,
)
from pages.nbss.client.client_profile_page import ClientProfilePage


class ClientLinkedPersonsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProfileElements()
        self.client_related_persons = ClientRelatedPersons()
        self.client_profile_page = ClientProfilePage()
        self.related_person_form = RelatedPersonForms()

    @allure.step("Открыть форму 'Добавление связанного лица'")
    def open_add_related_person_form(self) -> None:
        self.locators.ADD_RELATED_PERSON_BTN.click()
        self.related_person_form.ADD_NEW_RELATED_PERSON_BTN.wait_to_be_visible()
        self.related_person_form.NEXT_BTN.not_to_be_enabled()

    @allure.step("Открыть форму добавления связанного лица типа {related_person_type}")
    def open_add_related_person_form_and_select_type(self, related_person_type: str) -> None:
        self.open_add_related_person_form()
        self.related_person_form.ADD_NEW_RELATED_PERSON_BTN.click()
        self.related_person_form.TYPE_RELATED_PERSON.wait_to_be_visible()
        self.related_person_form.TYPE_RELATED_PERSON.select_by_value(related_person_type)

    @allure.step("Заполнить данные связанного лица (физическое лицо)")
    def fill_data_for_individual_related_person(self, user_data: IndividualClient, comment: str | None = None) -> None:
        self.related_person_form.LAST_NAME.fill(user_data.sur_name)
        self.related_person_form.NAME.fill(user_data.first_name)
        self.related_person_form.PATRONYMIC.fill(user_data.patronymic)
        self.related_person_form.GENDER.select_by_value(user_data.gender)
        self.related_person_form.DOCUMENT_TYPE.select_by_value(user_data.document_type)
        self.related_person_form.DOCUMENT_SERIAL.fill(user_data.document_serial)
        self.related_person_form.DOCUMENT_NUM.fill(user_data.document_num)
        self.related_person_form.DOCUMENT_PROVIDE_BY.fill(user_data.document_provide_by)
        self.related_person_form.DOCUMENT_DIVISION_CODE.fill(user_data.document_division_code)
        self.related_person_form.DOCUMENT_DATE.fill(user_data.issue_date)
        self.related_person_form.DOCUMENT_VALID_DATE.fill(user_data.document_valid_date)
        self.related_person_form.BIRTH_PLACE.fill(user_data.birth_place)
        self.related_person_form.BIRTH_DATE.fill(user_data.birth_date)
        self.related_person_form.NATIONALITY.select_by_value(user_data.nationality)
        self.related_person_form.SPEAKING_LANGUAGE.select_by_value(user_data.speaking_language)
        self.related_person_form.REGISTRATION_ADDRESS.select_by_value(
            user_data.registration_address, include_last_symbol=True
        )
        self.related_person_form.INN.fill(user_data.inn)
        self.related_person_form.SNILS.fill(user_data.snils)
        if user_data.is_resident:
            self.related_person_form.RESIDENT.click()
        self.related_person_form.COMMENT_FIELD.wait_to_be_visible()
        if comment:
            self.related_person_form.COMMENT_FIELD.fill(comment)

    @allure.step("Заполнить и подтвердить данные нового физического связанного лица")
    def add_individual_related_person(self, user_data: IndividualClient, comment: str) -> None:
        self.open_add_related_person_form_and_select_type(LinkedPersonType.individual)
        self.fill_data_for_individual_related_person(user_data, comment)
        self.related_person_form.NEXT_BTN.wait_to_be_enabled()
        self.related_person_form.NEXT_BTN.click()

    @allure.step("Заполнить и подтвердить данные нового обезличенного связанного лица")
    def add_impersonal_related_person(self, related_person_name: str) -> None:
        self.open_add_related_person_form_and_select_type(LinkedPersonType.impersonal)

        with allure.step("Блок 'Дополнительные атрибуты' не отображается"):
            self.related_person_form.COMMENT_FIELD.not_to_be_visible_for()

        self.related_person_form.NAME_RELATED_PERSON.fill(related_person_name)
        self.related_person_form.NEXT_BTN.wait_to_be_enabled()
        self.related_person_form.NEXT_BTN.click()

    @allure.step("Выбрать функцию связанного лица на форме добавления")
    def fill_related_person_function(self, related_person_function: str) -> None:
        self.related_person_form.FUNCTION_RELATED_PERSON.wait_to_be_visible()
        self.related_person_form.FUNCTION_RELATED_PERSON.select_by_value(related_person_function)
        self.related_person_form.NEXT_BTN.wait_to_be_enabled()
        self.related_person_form.NEXT_BTN.click()

    @allure.step("Заполнить контактные данные связанного лица на форме добавления")
    def fill_related_person_contacts(self, phone: str) -> None:
        self.related_person_form.CONTACT_PHONE.wait_to_be_visible()
        self.related_person_form.CONTACT_PHONE.fill(phone)
        self.related_person_form.ADD_BTN.click()
        self.related_person_form.TITLE.not_to_be_visible(timeout=10000)

    @allure.step("Выбрать функцию связанного лица на форме добавления")
    def fill_related_person_function_and_contacts(self, related_person_function: str, phone: str) -> None:
        self.fill_related_person_function(related_person_function)
        self.fill_related_person_contacts(phone)

    @allure.step("Проверить дополнительный атрибут на форме связанных лиц")
    def check_related_person_additional_attribute(self, comment: str) -> None:
        self.locators.RELATED_PERSON_TABLE_NAME.wait_to_be_visible(timeout=10000)
        self.locators.RELATED_NOTE_ADDITIONAL_ATTRIBUTE[0].to_contain_text(comment)

    @allure.step("Проверить заполненные данные связанного лица и доступность кнопок")
    def check_related_person_card(self, related_person: IndividualClient, comment: str, expected_count: int = 1) -> None:
        self.locators.RELATED_PERSONS.wait_to_have_count(expected_count)
        self.client_profile_page.check_related_person(related_person)
        self.check_related_person_additional_attribute(comment)
        self.client_related_persons.EDIT_RELATED_PERSONS_BTN.wait_to_be_enabled()
        self.client_related_persons.HISTORY_RELATED_PERSONS_BTN.wait_to_be_enabled()

    @allure.step("Проверить данные на форме создания связанного лица")
    def check_related_person_on_form(self, user_data: IndividualClient, comment: str) -> None:
        self.related_person_form.NAME.to_contain_text(
            f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}"
        )
        self.related_person_form.SPEAKING_LANGUAGE.to_have_value(user_data.speaking_language)
        self.related_person_form.NATIONALITY.to_have_value(user_data.nationality)
        self.related_person_form.BIRTH_DATE.to_have_value(user_data.birth_date)
        self.related_person_form.BIRTH_PLACE.to_contain_text(user_data.birth_place)
        self.related_person_form.GENDER.to_have_value(user_data.gender)
        self.related_person_form.DOCUMENT_TYPE.to_have_value(user_data.document_type)
        self.related_person_form.DOCUMENT_NUM.to_have_value(f"{user_data.document_serial} {user_data.document_num}")
        self.related_person_form.DOCUMENT_DATE.to_have_value(user_data.issue_date)
        self.related_person_form.DOCUMENT_PROVIDE_BY.to_have_value(user_data.document_provide_by)
        self.related_person_form.DOCUMENT_VALID_DATE.to_have_value(user_data.document_valid_date)
        self.related_person_form.DOCUMENT_DIVISION_CODE.to_have_value(user_data.document_division_code)
        self.related_person_form.INN.to_have_value(user_data.inn)

        self.related_person_form.COMMENT_FIELD.to_have_value(comment)

    @allure.step("Проверить данные на форме создания связанного лица и перейти на следующий шаг")
    def check_related_person_on_form_and_proceed(self, user_data: IndividualClient, comment: str) -> None:
        self.check_related_person_on_form(user_data, comment)
        self.related_person_form.NEXT_BTN.wait_to_be_enabled()
        self.related_person_form.NEXT_BTN.click()

    @allure.step("Редактировать дополнительный атрибут связанного лица")
    def edit_related_person_additional_attribute(self, new_comment: str) -> None:
        self.client_related_persons.EDIT_RELATED_PERSONS_BTN.wait_to_be_enabled(timeout=10000)
        self.client_related_persons.EDIT_RELATED_PERSONS_BTN.click()
        self.related_person_form.COMMENT_FIELD.wait_to_be_visible(timeout=10000)
        self.related_person_form.COMMENT_FIELD.fill(new_comment)
        self.locators.SAVE_BTN.wait_to_be_enabled(timeout=10000)
        self.locators.SAVE_BTN.click()
        self.locators.SAVE_BTN.not_to_be_visible(timeout=10000)

    @allure.step("Выбрать существующее связанное лицо с индексом {index} в списке")
    def select_related_person_in_list(self, index: int = 0) -> None:
        self.locators.RELATED_PERSONS.wait_to_have_count(index + 1)
        self.locators.RELATED_PERSONS[index].click()
        self.locators.RELATED_PERSON_TABLE_NAME.wait_to_be_visible(timeout=10000)

    @allure.step("Выбрать существующее связанное лицо с именем {person_name} на форме добавления")
    def select_related_person_in_form(self, person_name: str) -> None:
        self.related_person_form.EXISTING_PERSONS_NAMES.to_contain_text_in_any(person_name)
        person_index = [e.text for e in self.related_person_form.EXISTING_PERSONS_NAMES].index(person_name)
        delay(1, reason="Без паузы UI отображает данные некорректно")
        self.related_person_form.EXISTING_PERSONS_LIST[person_index].click()
        self.related_person_form.NEXT_BTN.wait_to_be_enabled()
        self.related_person_form.NEXT_BTN.click()

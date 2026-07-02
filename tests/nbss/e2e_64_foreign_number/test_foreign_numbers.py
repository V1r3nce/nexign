import re

import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.enums.user import User
from common.helpers.data_generator import faker
from pages.locators.nbss.dynamic_form_elements import CreateSalesAndServiceManagement, DynamicForms
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage
from pages.nbss.inquiries_page import InquiriesPage


@pytest.mark.regress
@pytest.mark.nbss_portal
class TestLinkedPersonForeignNumber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login):
        self.home_page = HomePage()
        self.client_profile_page = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.dynamic_form = DynamicForms()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.client_api = ClientRequests()

    @allure.title("01. Добавление иностранного номера верного формата и размерности при созданиии клиента")
    @allure.id(889399)
    def test_client_create_with_foreign_number(self, organization_user_data):
        with allure.step("Подготовка клиента"):
            client = organization_user_data
            country_code, phone = faker.phone_number_foreign()
            client.contact_phone_code = country_code
            client.contact_phone = phone
            self.home_page.create_customer_with_type(customer_type="organization", user_data=client)
        with allure.step("Переход в Связанные лица и проверка"):
            self.client_profile_page.click_tab("Связанные лица")
            self.client_profile_page.check_linked_person_contacts(client)

    @allure.title("02. Добавление иностранного номера верного формата и размерности связанному лицу")
    @allure.id(889398)
    def test_linked_person_add_foreign_number(self, create_organization_with_linked_person):
        with allure.step("Подготовка клиента"):
            client = create_organization_with_linked_person
            country_code, phone = faker.phone_number_foreign()
            client.contact_phone_code = country_code
            client.contact_phone = phone
        with allure.step("Переход в Связанные лица и редактирование контактов"):
            self.client_profile_page.open_linked_person_page(create_organization_with_linked_person.user_id)
            self.client_profile_page.edit_linked_person_contacts(
                phone_code=country_code, phone_number=client.contact_phone
            )
        with allure.step("Переход в Связанные лица и проверка отображения изменений"):
            self.client_profile_page.open_linked_person_page(client.user_id)
            self.client_profile_page.check_linked_person_contacts(client)

    @allure.title("03. Добавление иностранного номера неверной размерности")
    @allure.id(889400)
    def test_linked_person_add_wrong_phone_number(self, create_organization_with_linked_person):
        with allure.step("Подготовка клиента"):
            client = create_organization_with_linked_person
            country_code, phone = faker.phone_number_foreign()
            client.contact_phone_code = country_code
            client.contact_phone = f"{phone}1"
        with allure.step("Переход в Связанные лица и редактирование контактов"):
            self.client_profile_page.open_linked_person_page(create_organization_with_linked_person.user_id)
            self.client_profile_page.edit_linked_person_contacts(
                phone_code=country_code, phone_number=client.contact_phone
            )
        with allure.step("Проверка отображения сообщения об ошибке"):
            self.client_profile_page.locators.CONTACT_PHONE_EDIT_INFO.wait_to_be_visible()
            self.client_profile_page.locators.CONTACT_PHONE_EDIT_INFO.to_contain_text(
                re.compile(r"(Номер слишком длинный)|(Неверный формат \(длина\) номера)|(Обязательно для заполнения)")
            )

    @allure.title("04. Добавление иностранного номера при отсутствующей роли")
    @allure.id(889404)
    @pytest.mark.user(User.CUSTOMER_CARE_TEST)
    def test_linked_person_add_foreign_number_role_missing(self, create_organization_with_linked_person):
        with allure.step("Подготовка клиента"):
            client = create_organization_with_linked_person
            country_code, phone = faker.phone_number_foreign()
            client.contact_phone_code = country_code
            client.contact_phone = phone
        with allure.step("Открытие Связанных лиц клиента и проверка возможности редактирования"):
            self.client_profile_page.open_linked_person_page(create_organization_with_linked_person.user_id)
            self.client_profile_page.locators.CONTACT_DATA_EDIT_BTN.not_to_be_visible()

    @allure.title("05. Вставка номера из буфера обмена")
    @allure.id(889810)
    def test_linked_person_add_foreign_number_paste(self, create_organization_with_linked_person):
        with allure.step("Подготовка клиента"):
            client = create_organization_with_linked_person
            country_code, phone = faker.phone_number_foreign()
            client.contact_phone_code = country_code
            client.contact_phone = phone
        with allure.step("Открытие Связанных лиц клиента и редактирование"):
            self.client_profile_page.open_linked_person_page(create_organization_with_linked_person.user_id)
            self.client_profile_page.edit_linked_person_contacts(phone_number=f"{country_code}{client.contact_phone}")
            self.dynamic_form.TITLE.not_to_be_visible()
        with allure.step("Переход в Связанные лица и проверка отображения изменений"):
            self.client_profile_page.open_linked_person_page(client.user_id)
            self.client_profile_page.check_linked_person_contacts(client)

    @allure.title("06. Изменение контактных данных на иностранный номер в заявке")
    @allure.id(891316)
    def test_add_foreign_number_inquiry_form(self, organization_user_data):
        with allure.step("Создание клиента"):
            client = organization_user_data
            country_code, phone = faker.phone_number_foreign()
            client.contact_phone_code = country_code
            client.contact_phone = phone
            client.linked_person_phone = f"{country_code}{phone}"
            self.client_api.create_organization_with_linked_person(client_data=client)
        with allure.step("Перейти в контекст клиента и перейти на форму создания продажи"):
            self.client_profile_page.open_linked_person_page(client.user_id)
            self.inquiries_page.locators.CREATE_APPLICATION.click()
        with allure.step("Заполнить форму и проверить корректность телефона"):
            self.inquiries_page.fill_inquiry_create_form(select_contact_person=True)
            self.dynamic_form.CONTACT_PHONE_CODE.to_have_value(country_code)
            self.dynamic_form.CONTACT_PHONE.to_contain_value(phone, separated=True)
            self.create_request_form.SAVE_BTN.click()
        self.inquiries_page.check_open_sale_inquiry()
        with allure.step("Проверка значения в карточке продажи"):
            self.inquiries_page.click_tab("Карточка продажи")
            self.inquiries_page.locators.CONTACT_PHONE.to_contain_text(text=client.linked_person_phone, separated=True)

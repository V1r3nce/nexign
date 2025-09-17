import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_english_string, generate_random_number
from common.helpers.time_helpers import delay
from pages.additional_attributes import AdditionalAttributesPage
from pages.base_page import BasePage
from pages.client_profile_page import ClientProfilePage
from pages.locators.additional_attributes import AdditionalAttributes
from pages.locators.base_elements import BaseElements
from pages.locators.client_profile import ClientProfile
from pages.locators.dynamic_form_elements import AddRelatedPersonForms, CreateOrganization
from pages.locators.home_page_elements import HomePage
from pages.personal_account_page import PersonalAccountPage


class Attribute:
    def __init__(self, attr_type: str = ""):
        self.attr_type = attr_type
        self.name = "test_" + generate_english_string(7)


@allure.suite("E2E_54 Управление атрибутами клиента")
class TestAttributeManagement:
    @pytest.fixture(autouse=True)
    def setup(
        self, page: Page, api_request_auth_context: APIRequestContext, nexign_ui_stand_login, organization_user_data
    ) -> None:
        self.home_page = HomePage(page)
        self.base_page = BasePage(page)
        self.user = organization_user_data
        self.client_requests = ClientRequests(api_request_auth_context)
        self.attribute_locators = AdditionalAttributes(page)
        self.attribute_page = AdditionalAttributesPage(page)
        self.personal_account_page = PersonalAccountPage(page, self.user)
        self.organization_create_form = CreateOrganization(page)
        self.add_related_person_form = AddRelatedPersonForms(page)
        self.client_profile = ClientProfile(page)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.base_elements = BaseElements(page)
        self.attribute = Attribute()

    @allure.title("Добавление дополнительного атрибута на сущность")
    @allure.id(586775)
    @allure.description("Выполняется проверка добавления дополнительного атрибута на сущность")
    @pytest.mark.regress
    def test_add_additional_attribute(self, delete_additional_attributes: list) -> None:
        self.attribute.attr_type = "customer_individual"
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - физическое лицо")
        self.attribute_page.check_attribute_added(self.attribute.name)

    @allure.title("Добавление дополнительного атрибута с существующим кодом")
    @allure.id(587953)
    @allure.description("Выполняется проверка невозможности создания дополнительного атрибута с уже существующим кодом")
    @pytest.mark.regress
    def test_add_existing_additional_attribute(self, delete_additional_attributes: list) -> None:
        self.attribute.attr_type = "customer_individual"
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - физическое лицо")
        self.attribute_page.check_attribute_added(self.attribute.name)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - физическое лицо")
        self.base_elements.MODAL_BODY_TEXT[0].to_contain_text(self.attribute.name)

    @allure.title("Изменение дополнительного атрибута после его применения")
    @allure.id(588469)
    @allure.description("Выполняется проверка обновления атрибута на карточке клиента после его редактирования")
    @pytest.mark.regress
    def test_edit_applied_attribute(
        self, base_url: str, api_request_auth_context, page: Page, delete_additional_attributes: list
    ):
        self.attribute.attr_type = "customer_organization"
        attribute_old = Attribute(attr_type="customer_organization")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(attribute_old)
        self.attribute_page.add_attribute(attribute_old.name, "Клиент - юридическое лицо")
        self.base_page.open(base_url)
        self.personal_account_page.create_customer_with_type("organization")
        random_int = str(generate_random_number(4))
        locator = self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.get_element_by_value(attribute_old.name)
        locator.type(random_int)
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.client_profile.CLIENT_FIO.wait_to_be_visible()
        created_client = page.url
        self.base_page.open(f"{base_url}additional-attributes/attributes")
        self.attribute_page.choose_attribute(attribute_old.name)
        self.attribute_locators.EDIT_BUTTON.click()
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.clear_names_edit_sidebar()
        self.attribute_locators.NAME.type(self.attribute.name)
        self.attribute_locators.APPLY_EDIT_BUTTON.click()
        self.attribute_page.check_attribute_added(self.attribute.name)
        self.base_page.open(created_client)
        self.client_profile.CLIENT_TAB.click()
        delay(3, "Прогрузка атрибутов в профиле клиента")
        locator_profile = self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.get_element_by_value(self.attribute.name)
        locator_profile.to_contain_text(random_int, separated=True)

    @allure.title("Удаление дополнительного атрибута")
    @allure.id(586988)
    @allure.description("Выполняется проверка удаления дополнительного атрибута")
    @pytest.mark.regress
    def test_delete_attribute(self, base_url: str, api_request_auth_context, delete_additional_attributes: list):
        self.attribute.attr_type = "customer_individual"
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - физическое лицо")
        self.attribute_page.delete_attribute(self.attribute.name, base_url)

    @allure.title("Недоступность удаления и редактирования удалённого дополнительного атрибута")
    @allure.id(588119)
    @allure.description(
        "Выполняется проверка недоступности кнопок удаления и редактирования дополнительного атрибута после его удаления"
    )
    @pytest.mark.regress
    def test_edit_deleted_attribute(self, base_url: str, api_request_auth_context):
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        self.attribute_locators.STATUS_BUTTON.wait_to_be_visible()
        self.attribute_locators.STATUS_BUTTON.select_by_value("Удален")
        self.attribute_locators.ATTRIBUTE_CODE_LIST.select_by_value("test_")
        self.attribute_locators.EDIT_BUTTON.not_to_be_enabled()

    @allure.title("Фильтрация дополнительных атрибутов")
    @allure.id(588708)
    @allure.description("Выполняется проверка фильтрации дополнительных атрибутов")
    @pytest.mark.regress
    def test_filter_attribute(self, base_url: str):
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        self.attribute_locators.ENTITY_BUTTON.wait_to_be_visible()
        self.attribute_locators.ENTITY_BUTTON.select_by_value("Клиент - юридическое лицо")
        self.attribute_locators.ENTITY_TYPE[0].wait_to_have_text("Клиент - юридическое лицо")
        self.attribute_locators.ENTITY_TYPE.to_contain_text_in_all("Клиент - юридическое лицо")
        self.attribute_locators.RESET_FILTER.click()
        self.attribute_locators.STATUS_BUTTON.wait_to_be_visible()
        self.base_page.open(f"{base_url}additional-attributes/attributes")
        self.attribute_locators.STATUS_BUTTON.wait_to_be_visible()
        self.attribute_locators.STATUS_BUTTON.select_by_value("Действующий")
        self.attribute_locators.ENTITY_STATUS[0].wait_to_have_text("Действующий")
        self.attribute_locators.ENTITY_STATUS.to_contain_text_in_all("Действующий")
        self.attribute_locators.RESET_FILTER.click()
        self.attribute_locators.ENTITY_CODE[0].wait_to_be_visible()
        random_code = self.attribute_locators.ENTITY_CODE[0].text
        self.attribute_locators.ENTITY_SEARCH.type(random_code)
        self.attribute_locators.ENTITY_CODE.wait_to_have_count(1)
        self.attribute_locators.RESET_FILTER.click()

    @allure.title("Сортировка дополнительных атрибутов")
    @allure.id(588747)
    @allure.description("Выполняется проверка сортировки дополнительных атрибутов")
    @pytest.mark.regress
    def test_sort_attribute(self):
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        self.attribute_locators.ENTITY_SORT[1].wait_to_be_visible()
        self.attribute_locators.ENTITY_SORT[1].click()
        self.attribute_locators.ENTITY_CODE[0].wait_to_have_text(re.compile(r"^a.*$"))
        self.attribute_page.check_if_elements_sorted(self.attribute_locators.ENTITY_CODE)
        self.attribute_locators.ENTITY_SORT[0].wait_to_be_visible()
        self.attribute_locators.ENTITY_SORT[0].click()
        self.attribute_locators.ENTITY_TYPE[0].wait_to_have_text(re.compile(r"^A.*$"))
        self.attribute_page.check_if_elements_sorted(self.attribute_locators.ENTITY_TYPE)

    @allure.title("Создание шаблона дополнительного атрибута")
    @allure.id(589207)
    @allure.description("Выполняется проверка создания и применения дополнительного атрибута")
    @pytest.mark.regress
    def test_add_template(self, base_url: str, page: Page, delete_additional_attributes: list):
        self.attribute.attr_type = "template"
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - физическое лицо", variant="template")
        self.attribute_page.check_attribute_added(self.attribute.name)
        self.base_page.open(f"{base_url}additional-attributes/attributes")
        self.attribute_locators.ADD_BUTTON.wait_to_be_visible()
        self.attribute_locators.ADD_BUTTON.click()
        self.attribute_locators.TEMPLATE.select_by_value(self.attribute.name)
        self.attribute_locators.CODE.to_have_value(self.attribute.name)
        self.attribute_locators.SIDEBAR_DICTIONARY.wait_to_be_visible()
        self.attribute_locators.MIN_CARDINALITY.to_have_value("0")
        self.attribute_locators.MAX_CARDINALITY.to_have_value("100")
        self.attribute_locators.CLOSE.click()

    @allure.title("Редактирование дополнительного атрибута")
    @allure.id(586981)
    @allure.description("Выполняется проверка редактирования дополнительного атрибута")
    @pytest.mark.regress
    def test_edit_attribute(self, base_url, delete_additional_attributes: list):
        self.attribute.attr_type = "customer_organization"
        attribute_old = Attribute("customer_organization")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(attribute_old)
        self.attribute_page.add_attribute(attribute_old.name, "Клиент - юридическое лицо")
        self.base_page.open(f"{base_url}additional-attributes/attributes")
        self.attribute_page.choose_attribute(attribute_old.name)
        self.attribute_locators.EDIT_BUTTON.click()
        delete_additional_attributes.append(self.attribute)
        self.attribute_locators.NAME.wait_to_be_visible()
        self.attribute_locators.NAME.fill(self.attribute.name)
        self.attribute_locators.APPLY_EDIT_BUTTON.click()
        self.attribute_locators.ENTITY_SEARCH.type(attribute_old.name)
        self.attribute_locators.ENTITY_CODE.wait_to_have_count(1)

    @allure.title("Обязательность дополнительного атрибута")
    @allure.id(589010)
    @allure.description(
        "Выполняется проверка обязательности дополнительного атрибута в зависимости от значения поля 'Количество значений', указанного при создании атрибута"
    )
    @pytest.mark.regress
    def test_mandatory_attribute(self, base_url, page: Page, delete_additional_attributes: list):
        self.attribute.attr_type = "customer_organization"
        another_attribute = Attribute("customer_organization")
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - юридическое лицо", variant="mandatory_1")
        delete_additional_attributes.append(another_attribute)
        self.attribute_page.add_attribute(another_attribute.name, "Клиент - юридическое лицо", variant="mandatory_2")
        self.attribute_page.check_attribute_added(another_attribute.name)
        self.base_page.open(base_url)
        self.personal_account_page.create_customer_with_type("organization")
        self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.find_and_required_check(self.attribute.name, False)
        self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.find_and_required_check(another_attribute.name, True)
        self.personal_account_page.organization_create_form.SAVE_BTN.click()

    @allure.title("Отображение дополнительного атрибута с подсказкой")
    @allure.id(589041)
    @allure.description("Выполняется проверка отображения дополнительного атрибута с подсказкой")
    @pytest.mark.regress
    def test_hint_attribute(self, base_url, page: Page, delete_additional_attributes: list):
        self.attribute.attr_type = "customer_organization"
        delete_additional_attributes.append(self.attribute)
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - юридическое лицо", variant="hint")
        self.attribute_page.check_attribute_added(self.attribute.name)
        self.base_page.open(base_url)
        self.home_page.CREATE_ORG_BTN.click()
        self.organization_create_form.INN.fill(self.user.inn)
        self.organization_create_form.KPP.fill(self.user.kpp)
        self.organization_create_form.NEXT_BTN.click()
        delay(2, "Поля видны но идет подгрузка, данные не вводятся. Требуется ожидание")
        self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.check_hint_contain_text(
            self.attribute.name, f"hint_{self.attribute.name}"
        )

    @allure.title("Применение дополнительного атрибута после его создания_Атрибут видимый и нередактируемый")
    @allure.id(588113)
    @allure.description(
        "Выполняется проверка применения видимого и нередактируемого дополнительного атрибута на сущность"
    )
    @pytest.mark.regress
    def test_apply_attribute_uneditable(self, base_url, page: Page, delete_additional_attributes: list):
        self.attribute.attr_type = "customer_organization"
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - юридическое лицо", variant="uneditable")
        self.attribute_page.check_attribute_added(self.attribute.name)
        self.base_page.open(base_url)
        self.personal_account_page.create_customer_with_type("organization")
        self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.find_and_enable_check(self.attribute.name, False)
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.client_profile.CLIENT_FIO.wait_to_be_visible()
        self.client_profile.CLIENT_TAB.click()
        delay(3, "Прогрузка атрибутов в профиле клиента")
        locator_profile = self.attribute_locators.ATTRIBUTES_PROFILE_CHECKBOX.get_element_by_value(self.attribute.name)
        locator_profile.to_contain_text("Нет")

    @allure.title("Применение дополнительного атрибута после его создания_Атрибут видимый и редактируемый")
    @allure.id(588035)
    @allure.description("Выполняется проверка применения видимого и редактируемого дополнительного атрибута на сущность")
    @pytest.mark.regress
    def test_apply_attribute_editable(self, base_url, page: Page, delete_additional_attributes: list):
        self.attribute.attr_type = "customer_organization"
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        delete_additional_attributes.append(self.attribute)
        self.attribute_page.add_attribute(self.attribute.name, "Клиент - юридическое лицо", variant="editable")
        self.attribute_page.check_attribute_added(self.attribute.name)
        self.base_page.open(base_url)
        self.personal_account_page.create_customer_with_type("organization")
        self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.wait_to_be_visible()
        self.attribute_locators.ATTRIBUTES_CREATE_CLIENT_FORM.select_by_value(self.attribute.name)
        self.personal_account_page.organization_create_form.SAVE_BTN.click()
        self.client_profile.CLIENT_FIO.wait_to_be_visible()
        self.client_profile.CLIENT_TAB.click()
        delay(3, "Прогрузка атрибутов в профиле клиента")
        locator_profile = self.attribute_locators.ATTRIBUTES_PROFILE_CHECKBOX.get_element_by_value(self.attribute.name)
        locator_profile.to_contain_text("Да")

    @allure.title("Проверка обязательности полей при добавлении дополнительного атрибута на сущность")
    @allure.id(586989)
    @allure.description("Выполняется проверка обязательности полей при создании нового атрибута")
    @pytest.mark.regress
    def test_mandatory_params_add_attribute(self):
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Настройки > Дополнительные атрибуты")
        self.attribute_locators.ADD_BUTTON.click()
        self.attribute_locators.APPLY_BUTTON.click()
        self.attribute_locators.NAME_FILL_ERROR.wait_to_have_count(2)
        self.attribute_locators.FILL_ERROR.wait_to_have_count(5)

import datetime
import re

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import faker_ru
from common.helpers.time_helpers import delay
from models.user import OrgUser
from pages.locators.client_profile import ClientProfile
from pages.locators.client_search import ClientSearch
from pages.locators.dynamic_form_elements import ClientChoice, CreateOrganization, CreateSalesAndServiceManagement
from pages.locators.home_page_elements import HomePage
from pages.locators.inquiries_page import InquiriesPage, ProductEditForm
from pages.locators.select_product_offers_form import SelectProductOffersForm


@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestOrganizationCustomerCreate:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.home_page = HomePage(page)
        self.organization_create_form = CreateOrganization(page)
        self.client_search_page = ClientSearch(page)
        self.create_request_form = CreateSalesAndServiceManagement(page)
        self.client_choice = ClientChoice(page)
        self.client_profile = ClientProfile(page)
        self.inquiries_page = InquiriesPage(page)
        self.product_offer_form = SelectProductOffersForm(page)
        self.product_edit_form = ProductEditForm(page)
        self.user = OrgUser
        self.registration_date = faker_ru.date_between(datetime.date(1990, 1, 1), datetime.date(2020, 12, 31))

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание ЮЛ клиента, заполнены все поля")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description("Создание ЮЛ клиента, заполнены все поля")
    @allure.id(484785)
    @pytest.mark.regress
    def test_organization_create(self, base_url: str) -> None:
        with allure.step('Пользователь нажимает на "Создать клиента ЮЛ"'):
            self.home_page.CREATE_ORG_BTN.click()
            self.organization_create_form.INN.wait_to_be_visible()
        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(
                inn=self.user.inn,
                customer_name=self.user.customer_name,
                registration_document=self.user.registration_document,
                registration_date=self.registration_date.strftime("%d.%m.%Y"),
                registration_num=self.user.registration_num,
                okpo=self.user.okpo,
                okato=self.user.okato,
                okved=self.user.okved,
                ogrn=self.user.ogrn,
                kpp=self.user.kpp,
                note=self.user.note,
            )
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()
            self.organization_create_form.INN.not_to_be_visible()

            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text("Юридическое лицо")
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.customer_name)
            self.client_profile.RESIDENT.to_contain_text("Да")
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text("Русский")
            self.client_profile.NATIONALITY.to_contain_text("Россия")
            self.client_profile.BUSINESS_ACTIVITY.to_contain_text("Агент")
            self.client_profile.NOTE.to_contain_text(self.user.note)
            self.client_profile.REPUTATION.to_contain_text("Автотестовая репутация")
            self.client_profile.REGISTRATION_DOCUMENT.to_contain_text(self.user.registration_document)
            self.client_profile.REGISTRATION_DATE.to_contain_text(self.registration_date.strftime("%Y-%m-%d"))
            self.client_profile.REGISTRATION_NUM.to_contain_text(self.user.registration_num)
            self.client_profile.TAX_SCHEME.to_contain_text("Схема налогообложения по умолчанию")

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.CUSTOMER_NAME.fill(self.user.customer_name)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

        with allure.step("Проверка связанного лица"):
            self.create_request_form.CLIENT.click()
            self.client_profile.RELATED_PERSONS_TAB.click()
            self.client_profile.RELATED_PERSONS.not_to_be_visible()

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание B2B с типом ЮЛ заполняя все поля")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.description(
        "Проверить, что из процесса продажи (быстрое создание клиента) корректно создается B2B клиент с типом ЮЛ, "
        "при этом все поля заполнены"
    )
    @allure.id(533614)
    @pytest.mark.regress
    @pytest.mark.smoke
    def test_b2b_organization_create(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(3, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(
                inn=self.user.inn,
                customer_name=self.user.customer_name,
                registration_document=self.user.registration_document,
                registration_date=self.registration_date.strftime("%d.%m.%Y"),
                registration_num=self.user.registration_num,
                okpo=self.user.okpo,
                okato=self.user.okato,
                okved=self.user.okved,
                ogrn=self.user.ogrn,
                kpp=self.user.kpp,
                note=self.user.note,
            )
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()
            self.organization_create_form.INN.not_to_be_visible()

            self.create_request_form.CLIENT.to_contain_text(self.user.customer_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Автоматически")
            self.create_request_form.PRIORITY.select_by_value("Низкий")

            self.create_request_form.SAVE_BTN.click()

            self.inquiries_page.CLIENT.to_contain_text(self.user.customer_name)
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"))
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

    @allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
    @allure.title("Создание ЮЛ клиента заполняя все поля + продажа")
    @allure.tag("CAN_AUTH", "SUCCESS")
    @allure.id(485729)
    @allure.description("Сценарий создания клиента ЮЛ из процесса продажи (быстрое создание клиента)")
    @pytest.mark.regress
    def test_create_organization_customer_from_process_sale(self, base_url: str) -> None:
        with allure.step("Пользователь нажал на кнопку создание продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(3, timeout=10000)
            self.home_page.RIGHT_SIDE_BTN.click(1)

        self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Создать ЮЛ")

        with allure.step("В открывшейся форме пользователь вводит данные клиента"):
            self.organization_create_form.fill_data_for_organization_client(
                inn=self.user.inn,
                customer_name=self.user.customer_name,
                registration_document=self.user.registration_document,
                registration_date=self.registration_date.strftime("%d.%m.%Y"),
                registration_num=self.user.registration_num,
                okpo=self.user.okpo,
                okato=self.user.okato,
                okved=self.user.okved,
                ogrn=self.user.ogrn,
                kpp=self.user.kpp,
                note=self.user.note,
            )
        with allure.step("Сохранить клиента"):
            self.organization_create_form.SAVE_BTN.click()
            self.organization_create_form.INN.not_to_be_visible()

            self.create_request_form.CLIENT.to_contain_text(self.user.customer_name)

        with allure.step('Заполнить контактные данные нажать на кнопку "сохранить"'):
            self.create_request_form.EMAIL.fill(self.user.contact_email)
            self.create_request_form.PHONE.fill(self.user.contact_phone)
            self.create_request_form.PRIORITY.select_by_value("Высокий")
            self.create_request_form.ADD_SALE_TYPE.select_by_value("Автоматически")

            self.create_request_form.SAVE_BTN.click()

            self.inquiries_page.CLIENT.to_contain_text(self.user.customer_name)
            self.inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"))
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible()

            self.inquiries_page.ADD_SALE_BTN.click()
            self.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.product_offer_form.SEARCH_BTN.click()

            self.product_offer_form.PRODUCT_CARD.wait_to_have_count(2)
            self.product_offer_form.PRODUCT_CARD[0].to_contain_text("Интернет в офис")
            self.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
            self.product_offer_form.ADD_BTN.click()

            self.inquiries_page.ADDED_PRODUCT.wait_to_have_count(1)
            self.inquiries_page.ADDED_PRODUCT[0].to_contain_text("Интернет в офис")

            self.inquiries_page.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            self.inquiries_page.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            self.inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

            self.inquiries_page.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            self.product_edit_form.SPECIFICATION_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SPECIFICATION.wait_to_be_visible()

            self.product_edit_form.SERVICES_TAB.click()
            self.product_edit_form.SERVICES_TAB.to_have_class(re.compile(r".+active"))
            self.product_edit_form.SERVICES.wait_to_be_visible()

            self.product_edit_form.INNER_CANCEL_BTN.click()

            self.inquiries_page.CHECK_CONFIGURATION_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.")

            self.inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.REFRESH_BTN.click()
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            self.inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

            self.inquiries_page.NEXT_STEP_BTN.click()
            self.inquiries_page.DROPDOWN_MENU.select_by_value("Автоматическое управление Договором/ДС и ЛС")
            self.inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=240000)

            self.inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)

        with allure.step('Переходим на вкладку "Клиент" клиентской карточки'):
            self.inquiries_page.CLIENT.click()
            self.client_profile.CLIENT_TAB.click()
            self.client_profile.CLIENT_TYPE.to_contain_text("Юридическое лицо")
            self.client_profile.CLIENT_FIO.to_contain_text(self.user.customer_name)
            self.client_profile.RESIDENT.to_contain_text("Да")
            self.client_profile.SPEAKING_LANGUAGE.to_contain_text("Русский")
            self.client_profile.NATIONALITY.to_contain_text("Россия")
            self.client_profile.BUSINESS_ACTIVITY.to_contain_text("Агент")
            self.client_profile.NOTE.to_contain_text(self.user.note)
            self.client_profile.REPUTATION.to_contain_text("Автотестовая репутация")
            self.client_profile.REGISTRATION_DOCUMENT.to_contain_text(self.user.registration_document)
            self.client_profile.REGISTRATION_DATE.to_contain_text(self.registration_date.strftime("%Y-%m-%d"))
            self.client_profile.REGISTRATION_NUM.to_contain_text(self.user.registration_num)
            self.client_profile.TAX_SCHEME.to_contain_text("Схема налогообложения по умолчанию")

        with allure.step("Ищем клиента"):
            self.home_page.HOME_BTN.click()
            self.home_page.CUSTOMER_NAME.fill(self.user.customer_name)
            self.home_page.HEADER_SEARCH_BTN.click()

            self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible()
            self.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий")
            self.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен")
            delay(2, "Не успевает примениться фильтр")
            self.client_search_page.SEARCH_BTN.click()
            self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible()

        with allure.step("Открываем форму продажи"):
            self.home_page.RIGHT_SIDE_BTN.wait_to_have_count(5)
            self.home_page.RIGHT_SIDE_BTN.click(1)
            self.create_request_form.SELECT_CLIENT_BTN.select_by_value("Выбрать клиента")

            self.client_choice.INN.fill(self.user.inn)
            self.client_choice.FIND_BTN.click()

            self.client_choice.FOUNDED_CUSTOMER.wait_elements_visible(0, timeout=10000)
            self.client_choice.FOUNDED_CUSTOMER.click(0)
            self.client_choice.INNER_ACCEPT_BTN.click()

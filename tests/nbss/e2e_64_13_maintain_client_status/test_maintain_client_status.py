import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number
from models.client import OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import CreateOrganization
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite('E2E_64_13 Создание и управление клиентом и его иерархиями (Поддержать статус Клиента "Потенциальный")')
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestMaintainClientStatus:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, organization_user_data: OrganizationClient) -> None:
        self.base_page = BasePage()
        self.home_page = HomePage()
        self.form_create_organization = CreateOrganization()
        self.client_profile_page = ClientProfilePage()
        self.client_requests = ClientRequests()
        self.user = organization_user_data
        self.type_client = "Потенциальный"

    @allure.id(818955)
    @allure.title(
        "07. Создание клиента ЮЛ, без проверки дублей, используется автозаполнение атрибутов по данным внешней системы"
    )
    @pytest.mark.skip(reason="Кейс требует PartyUnique = 0 на стенде")
    def test_create_organization_without_duplicate_check_with_autofill(self) -> None:
        """Шаги кейса:

        1. Заполнить обязательные для статуса "Потенциальный" поля, ИНН и КПП.
        2. Нажать "Заполнить атрибуты по ИНН" — найдено одно ЮЛ, поля заполнены его атрибутами.
        3. Нажать "Далее" — поиск дублей не производится, открыта форма контактных данных.
        4. Заполнить контакт, нажать "Создать" — клиент создан в статусе "Потенциальный".
        """

    @allure.id(818603)
    @allure.title("08. Создание клиента/партнера ЮЛ, включена функциональность проверки дублей (ввод данных вручную)")
    def test_create_legal_entity_client_or_partner_with_duplicate_check_manual_input(self) -> None:
        with allure.step("Заполнить данные клиента ЮЛ вручную и создать клиента"):
            self.home_page.create_customer_with_type(user_data=self.user, customer_type="organization")

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_created_client_card(self.type_client)

    @allure.id(818605)
    @allure.title(
        "09. Создание клиента/партнера ЮЛ, включена функциональность проверки дублей (ввод данных вручную, в том числе ИНН и КПП, есть дубликат)"
    )
    def test_create_organization_client_or_partner_duplicate_check_manual_inn_kpp_duplicate_found(self) -> None:
        with allure.step("Подготовка тестовых данных: клиент с такими же ИНН и КПП уже существует"):
            duplicate = self.client_requests.create_organization(client_data=OrganizationClient())

        with allure.step("Заполнить данные дубликата и нажать 'Далее', найден дубль"):
            self.home_page.open_create_customer_form_and_fill("organization", duplicate)
            self.form_create_organization.NEXT_BTN.wait_to_be_visible()
            self.form_create_organization.NEXT_BTN.click()
            self.form_create_organization.MODAL.wait_to_be_visible(timeout=15000)

        with allure.step("Заполнить корректные данные и создать клиента"):
            self.home_page.refresh_page(wait="load")
            self.home_page.organization_create_form.fill_data_for_organization_client(user_data=self.user)
            self.form_create_organization.CREATE_BTN.wait_to_be_visible()
            self.form_create_organization.CREATE_BTN.click()

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_created_client_card(self.type_client)

    @allure.id(818608)
    @allure.title(
        "10. Создание клиента/партнера ЮЛ, включена функциональность проверки дублей (ввод данных вручную, в том числе ИНН и КПП, нет дубликатов)"
    )
    def test_create_organization_client_or_partner_duplicate_check_manual_inn_kpp_no_duplicates_found(self) -> None:
        with allure.step("Заполнить данные клиента ЮЛ вручную и создать клиента"):
            self.home_page.create_customer_with_type(user_data=self.user, customer_type="organization")

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_created_client_card(self.type_client)

    @allure.id(818609)
    @allure.title(
        "11. Создание клиента ЮЛ, функциональность проверки дублей выключена, без автозаполнения данных клиента"
    )
    @pytest.mark.skip(reason="Кейс требует PartyUnique = 0 на стенде")
    def test_create_organization_without_duplicate_check_and_autofill(self) -> None:
        """Шаги кейса:

        1. Заполнить обязательные для статуса "Потенциальный" поля, нажать "Далее" —
           поиск дублей не производится, открыта форма контактных данных.
        2. Заполнить контакт, нажать "Создать" — клиент создан в статусе "Потенциальный".
        """

    @allure.id(818961)
    @allure.title(
        "12. Редактирование клиента ЮЛ, включена функциональность проверки дублей, используется автозаполнение атрибутов по данным внешней системы"
    )
    def test_edit_organization_with_duplicate_check_no_duplicates(self, create_organization: OrganizationClient) -> None:
        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_organization.user_id)

        with allure.step("Отредактировать атрибуты клиента и нажать 'Сохранить', дублей не найдено"):
            new_inn = str(generate_random_number(10))
            self.client_profile_page.edit_organization_identification(new_inn)

        with allure.step("Отредактированные атрибуты клиента сохранены"):
            self.client_profile_page.check_client_inn(new_inn)

    @allure.id(818965)
    @allure.title(
        "13. Редактирование клиента ЮЛ, включена функциональность проверки дублей, используется автозаполнение атрибутов по данным внешней системы (есть дубликат)"
    )
    def test_edit_organization_with_duplicate_check_duplicate_found(
        self, create_organization: OrganizationClient
    ) -> None:
        with allure.step("Подготовка тестовых данных: в системе есть второй клиент ЮЛ"):
            duplicate = self.client_requests.create_organization(client_data=OrganizationClient())

        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_organization.user_id)

        with allure.step("Указать ИНН и КПП существующего клиента и нажать 'Сохранить', найден дубликат"):
            self.client_profile_page.edit_organization_identification(
                duplicate.inn, duplicate.kpp, wait_form_closed=False
            )

        with allure.step("Закрыть модальное окно, отредактировать данные и нажать 'Сохранить'"):
            self.form_create_organization.close_duplicate_modal()
            new_inn = str(generate_random_number(10))
            self.client_profile_page.edit_organization_identification(new_inn)

        with allure.step("Отредактированные атрибуты клиента сохранены"):
            self.client_profile_page.check_client_inn(new_inn)

    @allure.id(822464)
    @allure.title("14. Редактирование клиента ЮЛ (без проверки дублей, без автозаполнения)")
    @pytest.mark.skip(reason="Кейс требует PartyUnique = 0 и autofillAttributes = 0 на стенде")
    def test_edit_organization_without_duplicate_check_and_autofill(
        self, create_organization: OrganizationClient
    ) -> None:
        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_organization.user_id)

        with allure.step("Отредактировать атрибуты клиента и нажать 'Сохранить', измененные данные сохранены"):
            new_inn = str(generate_random_number(10))
            self.client_profile_page.edit_organization_identification(new_inn)
            self.client_profile_page.check_client_inn(new_inn)

    @allure.id(967579)
    @allure.title("32. Создание клиента ЮЛ, включена функциональность проверки дублей (не указано ни одного контакта)")
    @pytest.mark.skip(reason="Кейс требует autofillAttributes = 0 на стенде")
    def test_create_organization_without_autofill_and_without_contacts(self) -> None:
        with allure.step("Заполнить обязательные для статуса 'Потенциальный' поля и нажать 'Далее'"):
            self.home_page.open_create_customer_form_and_fill("organization", self.user)
            self.form_create_organization.go_to_contacts_page()

        with allure.step("Нажать 'Создать', не указав ни одного контакта, показано модальное окно об ошибке"):
            self.form_create_organization.CREATE_BTN.click()
            self.form_create_organization.close_main_contacts_modal()
            self.form_create_organization.CONTACT_PERSON.wait_to_be_visible(timeout=15000)

        with allure.step("Заполнить контакт и нажать 'Создать'"):
            self.form_create_organization.fill_contacts_and_create_client(self.user)

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_created_client_card(self.type_client)

    @allure.id(967581)
    @allure.title(
        "33. Создание клиента ЮЛ, включена функциональность проверки дублей (есть дубликат, переход на карточку дубликата)"
    )
    @pytest.mark.skip(reason="Кейс требует autofillAttributes = 0 на стенде")
    def test_create_organization_without_autofill_go_to_found_duplicate(self) -> None:
        with allure.step("Подготовка тестовых данных: клиент с такими же ИНН и КПП уже существует"):
            duplicate = self.client_requests.create_organization(client_data=OrganizationClient())

        with allure.step("Заполнить обязательные для статуса 'Потенциальный' поля, ИНН и КПП, нажать 'Далее'"):
            self.base_page.open_home_page()
            self.home_page.open_create_customer_form_and_fill("organization", duplicate)
            self.form_create_organization.NEXT_BTN.click()

        with allure.step("Нажать 'Перейти к найденному дубликату', открыта карточка найденного клиента"):
            self.form_create_organization.go_to_found_duplicate()
            self.client_profile_page.check_opened_duplicate_card(duplicate.user_id)

    @allure.id(968495)
    @allure.title("36. Редактирование клиента ЮЛ, включена функциональность проверки дублей")
    @pytest.mark.skip(reason="Кейс требует autofillAttributes = 0 на стенде")
    def test_edit_organization_without_autofill_no_duplicates(self, create_organization: OrganizationClient) -> None:
        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_organization.user_id)

        with allure.step("Отредактировать атрибуты клиента и нажать 'Сохранить', дублей не найдено"):
            new_inn = str(generate_random_number(10))
            self.client_profile_page.edit_organization_identification(new_inn)
            self.client_profile_page.check_client_inn(new_inn)

    @allure.id(968496)
    @allure.title("37. Редактирование клиента ЮЛ, включена функциональность проверки дублей (есть дубликат)")
    @pytest.mark.skip(reason="Кейс требует autofillAttributes = 0 на стенде")
    def test_edit_organization_without_autofill_duplicate_found(self, create_organization: OrganizationClient) -> None:
        with allure.step("Подготовка тестовых данных: в системе есть второй клиент ЮЛ"):
            duplicate = self.client_requests.create_organization(client_data=OrganizationClient())

        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_organization.user_id)

        with allure.step("Указать ИНН и КПП существующего клиента и нажать 'Сохранить', найден дубликат"):
            self.client_profile_page.edit_organization_identification(
                duplicate.inn, duplicate.kpp, wait_form_closed=False
            )

        with allure.step("Закрыть модальное окно, отредактировать данные и нажать 'Сохранить'"):
            self.form_create_organization.close_duplicate_modal()
            new_inn = str(generate_random_number(10))
            self.client_profile_page.edit_organization_identification(new_inn)
            self.client_profile_page.check_client_inn(new_inn)

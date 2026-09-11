import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import generate_random_number
from models.client import IndividualClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import DUPLICATE_FOUND_TEXT, IndividualCustomerCreate
from pages.nbss.client.client_card_page import ClientCardPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.home_page import HomePage


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite('E2E_64_13 Создание и управление клиентом и его иерархиями (Поддержать статус Клиента "Потенциальный")')
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestMaintainIndividualClientStatus:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, individual_user_data: IndividualClient) -> None:
        self.base_page = BasePage()
        self.home_page = HomePage()
        self.form_create_individual = IndividualCustomerCreate()
        self.client_profile_page = ClientProfilePage()
        self.client_card_page = ClientCardPage()
        self.client_requests = ClientRequests()
        self.user = individual_user_data
        self.type_client = "Потенциальный"

    @allure.id(966483)
    @allure.title("19. Создание клиента ФЛ, включена функциональность проверки дублей")
    def test_create_individual_with_duplicate_check(self) -> None:
        with allure.step("Заполнить обязательные поля и поля документа, нажать 'Далее', дублей не найдено"):
            self.home_page.open_create_customer_form_and_fill("individual", self.user)
            self.form_create_individual.go_to_contacts_page()

        with allure.step("Заполнить контакт и нажать 'Создать'"):
            self.form_create_individual.fill_contacts_and_create_client(self.user)

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_client_status_and_linked_persons(self.type_client)

    @allure.id(966652)
    @allure.title("20. Создание клиента ФЛ, включена функциональность проверки дублей (Найден дубликат)")
    def test_create_individual_duplicate_found_and_corrected(self) -> None:
        with allure.step("Подготовка тестовых данных: клиент с такими же данными документа уже существует"):
            duplicate = self.client_requests.create_individual_client(client_data=IndividualClient())

        with allure.step("Заполнить обязательные поля и поля документа дубликата, нажать 'Далее'"):
            self.base_page.open_home_page()
            self.home_page.open_create_customer_form_and_fill("individual", duplicate)
            self.form_create_individual.NEXT_BTN.click()

        with allure.step("Найден дубликат, появилось модальное окно"):
            self.form_create_individual.MODAL_BODY_TEXT.to_contain_text_in_any(DUPLICATE_FOUND_TEXT)

        with allure.step("Нажать 'Закрыть', отредактировать данные документа, нажать 'Далее'"):
            self.form_create_individual.close_duplicate_modal()
            self.form_create_individual.DOCUMENT_SERIAL.fill(self.user.document_serial)
            self.form_create_individual.DOCUMENT_NUM.fill(self.user.document_num)
            self.form_create_individual.go_to_contacts_page()

        with allure.step("Заполнить контакт и нажать 'Создать'"):
            self.form_create_individual.fill_contacts_and_create_client(self.user)

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_client_status_and_linked_persons(self.type_client)

    @allure.id(966700)
    @allure.title(
        "21. Создание клиента ФЛ, включена функциональность проверки дублей (Найден дубликат, переход к дубликату)"
    )
    def test_create_individual_duplicate_found_go_to_found_duplicate(self) -> None:
        with allure.step("Подготовка тестовых данных: клиент с такими же данными документа уже существует"):
            duplicate = self.client_requests.create_individual_client(client_data=IndividualClient())

        with allure.step("Заполнить обязательные поля и поля документа дубликата, нажать 'Далее'"):
            self.base_page.open_home_page()
            self.home_page.open_create_customer_form_and_fill("individual", duplicate)
            self.form_create_individual.NEXT_BTN.click()

        with allure.step("Найден дубликат, появилось модальное окно"):
            self.form_create_individual.MODAL_BODY_TEXT.to_contain_text_in_any(DUPLICATE_FOUND_TEXT)

        with allure.step("Нажать 'Перейти к найденному дубликату', открыта карточка найденного клиента"):
            self.form_create_individual.go_to_found_duplicate()
            self.client_profile_page.check_duplicate_card_opened(duplicate.user_id)
            self.client_profile_page.locators.CLIENT_FIO.to_contain_text(duplicate.sur_name)

    @allure.id(966739)
    @allure.title("22. Создание клиента ФЛ, включена функциональность проверки дублей (не указано ни одного контакта)")
    def test_create_individual_with_duplicate_check_without_contacts(self) -> None:
        with allure.step("Заполнить обязательные поля и поля документа, нажать 'Далее', дублей не найдено"):
            self.home_page.open_create_customer_form_and_fill("individual", self.user)
            self.form_create_individual.go_to_contacts_page()

        with allure.step("Нажать 'Создать', не указав ни одного контакта, показаны ошибки обязательных полей"):
            self.form_create_individual.create_client_without_contacts()

        with allure.step("Заполнить контакт и нажать 'Создать'"):
            self.form_create_individual.fill_contacts_and_create_client(self.user)

        with allure.step("Открыта карточка клиента в статусе 'Потенциальный' со связанным лицом"):
            self.client_profile_page.check_client_status_and_linked_persons(self.type_client)

    @allure.id(966487)
    @allure.title(
        "24. Редактирование клиента ФЛ (включена функциональность проверки дублей, изменение обязательных атрибутов)"
    )
    def test_edit_individual_change_document_no_duplicates(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_individual_user.user_id)

        with allure.step("Изменить данные документа и нажать 'Сохранить', дублей не найдено"):
            new_document_num = str(generate_random_number(6))
            self.client_profile_page.edit_individual_document(new_document_num)

        with allure.step("Измененные данные сохранены"):
            self.client_card_page.open_client_tab()
            self.client_card_page.check_client_attributes(document_num=new_document_num)

    @allure.id(966749)
    @allure.title(
        "25. Редактирование клиента ФЛ (включена функциональность проверки дублей, без изменения обязательных атрибутов)"
    )
    def test_edit_individual_without_document_change(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_individual_user.user_id)

        with allure.step("Изменить атрибуты, кроме данных документа, нажать 'Сохранить', поиск дублей не выполняется"):
            new_surname = f"{create_individual_user.sur_name}-RENAMED"
            self.client_profile_page.edit_individual_surname(new_surname)

        with allure.step("Измененные данные сохранены"):
            self.client_card_page.open_client_tab()
            self.client_card_page.check_client_attributes(surname=new_surname)

    @allure.id(966751)
    @allure.title("26. Редактирование клиента ФЛ (включена функциональность проверки дублей, найден дубль)")
    def test_edit_individual_duplicate_found_and_corrected(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Подготовка тестовых данных: в системе есть второй клиент ФЛ"):
            duplicate = self.client_requests.create_individual_client(client_data=IndividualClient())

        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_individual_user.user_id)

        with allure.step("Указать данные документа существующего клиента и нажать 'Сохранить', найден дубликат"):
            self.client_profile_page.edit_individual_document(
                duplicate.document_num, duplicate.document_serial, wait_form_closed=False
            )

        with allure.step("Закрыть модальное окно, откорректировать данные и нажать 'Сохранить'"):
            self.form_create_individual.close_duplicate_modal()
            new_document_num = str(generate_random_number(6))
            self.client_profile_page.edit_individual_document(new_document_num)

        with allure.step("Измененные данные сохранены"):
            self.client_card_page.open_client_tab()
            self.client_card_page.check_client_attributes(document_num=new_document_num)

    @allure.id(966760)
    @allure.title(
        "27. Редактирование клиента ФЛ (включена функциональность проверки дублей, найден дубль, переход к дубликату)"
    )
    def test_edit_individual_duplicate_found_go_to_found_duplicate(
        self, create_individual_user: IndividualClient
    ) -> None:
        with allure.step("Подготовка тестовых данных: в системе есть второй клиент ФЛ"):
            duplicate = self.client_requests.create_individual_client(client_data=IndividualClient())

        with allure.step("Нажать кнопку 'Редактировать', открыта форма редактирования атрибутов клиента"):
            self.client_profile_page.open_client_edit_form(create_individual_user.user_id)

        with allure.step("Указать данные документа существующего клиента и нажать 'Сохранить', найден дубликат"):
            self.client_profile_page.edit_individual_document(
                duplicate.document_num, duplicate.document_serial, wait_form_closed=False
            )

        with allure.step("Открыть детали ошибки, перейти к клиенту, открыта карточка найденного клиента"):
            self.form_create_individual.go_to_duplicate_from_error_details()
            self.client_profile_page.check_duplicate_card_opened(duplicate.user_id)

        with allure.step("Изменения редактируемого клиента не произошло"):
            self.client_profile_page.open_client_profile_page(create_individual_user.user_id)
            self.client_card_page.open_client_tab()
            self.client_card_page.check_client_attributes(document_num=create_individual_user.document_num)

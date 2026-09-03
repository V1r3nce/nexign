import allure
import pytest

from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.data_generator import get_current_datetime_string
from models.client import IndividualClient, OrganizationClient
from pages.nbss.agreement_page import AgreementPage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage

LINKED_PERSON_NAME_B2C = "Связанное лицо ФЛ"
PRODUCT_NAME_B2B = "Гибкий бизнес"


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite('E2E_64_13 Создание и управление клиентом и его иерархиями (Поддержать статус Клиента "Потенциальный")')
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.praim
class TestClientStatusTransition:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.agreement_page = AgreementPage()
        self.client_requests = ClientRequests()
        self.today_date = get_current_datetime_string(is_full_format=False)

    @allure.id(902222)
    @allure.title('15. Перевод клиента из статуса "Потенциальный" в статус "Действующий"')
    def test_organization_transition_from_potential_to_active(
        self,
        create_potential_organization_with_filled_attributes: OrganizationClient,
        remove_file_from_download_folder: list,
    ) -> None:
        client = create_potential_organization_with_filled_attributes
        with allure.step("Подготовка тестовых данных: у клиента есть связанное лицо"):
            self.client_requests.create_linked_person(client.user_id, client.name_related_person)

        with allure.step("Нажать кнопку 'Добавить' на вкладке 'Договоры' и заполнить форму создания договора"):
            self.client_profile_page.open_client_agreements_tab(client.user_id)
            self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text("Потенциальный", timeout=20000)
            self.client_profile_page.create_agreement(client, self.today_date)

        with allure.step("Договор создан в статусе 'Оформлен', клиент остался в статусе 'Потенциальный'"):
            self.client_profile_page.check_agreement_and_client_status("Оформлен", "Потенциальный")

        with allure.step("Нажать 'Подписать договор', загрузить документ и нажать 'Подписать'"):
            self.agreement_page.sign_agreement(
                self.today_date,
                client.name_related_person,
                f"Agreement_{client.customer_name}.txt",
                remove_file_from_download_folder,
            )

        with allure.step("Договор в статусе 'Действующий', клиент сменил статус на 'Действующий'"):
            self.client_profile_page.locators.AGREEMENT_STATUS.wait_to_have_text("Действующий", timeout=30000)
            self.client_requests.wait_customer_lifecycle_status(client.user_id, "Действующий")
            self.client_profile_page.open_client_card_tab(client.user_id)
            self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text("Действующий", timeout=30000)

        with allure.step("Нажать 'История изменений', отображено изменение статуса клиента"):
            self.client_profile_page.check_client_changes_history_displayed()

    @allure.id(966490)
    @allure.title('29. Перевод клиента из статуса "Потенциальный" в статус "Действующий"(B2C)')
    def test_individual_transition_from_potential_to_active(
        self, create_potential_individual_user: IndividualClient, remove_file_from_download_folder: list
    ) -> None:
        with allure.step("Подготовка тестовых данных: у клиента есть связанное лицо"):
            self.client_requests.create_linked_person(create_potential_individual_user.user_id, LINKED_PERSON_NAME_B2C)

        with allure.step("Нажать кнопку 'Добавить' на вкладке 'Договоры' и заполнить форму создания договора"):
            self.client_profile_page.open_client_agreements_tab(create_potential_individual_user.user_id)
            self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text("Потенциальный", timeout=20000)
            self.client_profile_page.create_agreement(
                create_potential_individual_user, self.today_date, with_client_bank_details=False
            )

        with allure.step("Договор создан в статусе 'Оформлен', клиент остался в статусе 'Потенциальный'"):
            self.client_profile_page.check_agreement_and_client_status("Оформлен", "Потенциальный")

        with allure.step("Нажать 'Подписать договор', загрузить документ и нажать 'Подписать'"):
            self.agreement_page.sign_agreement(
                self.today_date,
                LINKED_PERSON_NAME_B2C,
                f"Agreement_{create_potential_individual_user.sur_name}.txt",
                remove_file_from_download_folder,
            )

        with allure.step("Договор в статусе 'Действующий', клиент сменил статус на 'Действующий'"):
            self.client_profile_page.locators.AGREEMENT_STATUS.wait_to_have_text("Действующий", timeout=30000)
            self.client_requests.wait_customer_lifecycle_status(create_potential_individual_user.user_id, "Действующий")
            self.client_profile_page.open_client_card_tab(create_potential_individual_user.user_id)
            self.client_profile_page.locators.CLIENT_STATUS.wait_to_have_text("Действующий", timeout=30000)

        with allure.step("Нажать 'История изменений', отображено изменение статуса клиента"):
            self.client_profile_page.check_client_changes_history_displayed()

    @allure.id(927843)
    @allure.title("16. Успешное создание и подписание договора во время продажи")
    def test_create_and_sign_agreement_during_sale(self, create_organization: OrganizationClient) -> None:
        with allure.step("Подготовка тестовых данных: у клиента есть связанное лицо, создана продажа"):
            self.client_requests.create_linked_person(
                create_organization.user_id, create_organization.name_related_person
            )
            self.inquiries_page.start_sale_with_product(create_organization, product_name=PRODUCT_NAME_B2B)

        with allure.step("Нажать 'Далее', совершен переход на шаг 'Регистрация/Выбор договора'"):
            self.inquiries_page.click_next("Регистрация/Выбор договора")

        with allure.step("Создать договор, выбрать его, создать ЛС и согласовать документы"):
            self.inquiries_page.agreement_and_account_steps_pass()

        with allure.step("Выполнены автоматические шаги, заявка успешно завершена и закрыта"):
            self.inquiries_page.wait_close_inquiry()

        with allure.step("Отображен договор в статусе 'Действующий', статус клиента - 'Действующий'"):
            self.client_profile_page.open_client_agreements_tab(create_organization.user_id)
            self.client_profile_page.check_active_agreement_in_list()
            self.client_requests.check_customer_lifecycle_status(create_organization.user_id, "Действующий")

    @allure.id(966488)
    @allure.title("30. Успешное создание и подписание договора во время продажи (B2C, ручное формирование документов)")
    def test_create_and_sign_agreement_during_sale_b2c(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Подготовка тестовых данных: у клиента есть связанное лицо, создана продажа"):
            self.client_requests.create_linked_person(create_individual_user.user_id, LINKED_PERSON_NAME_B2C)
            self.inquiries_page.start_sale_with_product(create_individual_user)

        with allure.step("Нажать 'Далее', совершен переход на шаг 'Регистрация/Выбор договора'"):
            self.inquiries_page.click_next("Регистрация/Выбор договора")

        with allure.step("Создать договор, выбрать его, создать ЛС и согласовать документы"):
            self.inquiries_page.agreement_and_account_steps_pass()

        with allure.step("Выполнены автоматические шаги, заявка успешно завершена и закрыта"):
            self.inquiries_page.wait_close_inquiry()

        with allure.step("Отображен договор в статусе 'Действующий', статус клиента - 'Действующий'"):
            self.client_profile_page.open_client_agreements_tab(create_individual_user.user_id)
            self.client_profile_page.check_active_agreement_in_list()
            self.client_requests.check_customer_lifecycle_status(create_individual_user.user_id, "Действующий")

    @allure.id(927859)
    @allure.title(
        "18. Создание и подписание договора во время продажи (Заполнены не все обязательные данные, автоматическое формирование документов)"
    )
    def test_fill_organization_attributes_and_repeat_agreement_check(
        self, create_potential_organization_with_linked_person: OrganizationClient
    ) -> None:
        with allure.step("Подготовка тестовых данных: клиент 'Потенциальный' без обязательных атрибутов"):
            client = create_potential_organization_with_linked_person
            inquiry_url = self.inquiries_page.start_sale_with_product(
                client, product_name=PRODUCT_NAME_B2B, create_add_agreement="auto"
            )

        with allure.step("Нажать 'Далее', на шаге проверки появилась ошибка, кнопка 'Далее' неактивна"):
            self.inquiries_page.check_agreement_creation_forbidden()

        with allure.step("Перейти в карточку клиента, нажать 'Редактировать', заполнить данные и сохранить"):
            # TODO: уточнить полный набор обязательных для создания договора атрибутов по HTML формы (TUDS-6163)
            self.client_profile_page.open_client_card_tab(client.user_id)
            self.client_profile_page.edit_organization_client(ogrn=client.ogrn, tax_scheme=client.tax_scheme)

        with allure.step("Вернуться в заявку и повторить проверку, заявка успешно завершена"):
            self.inquiries_page.open_inquiry_on_agreement_check_step(inquiry_url)
            self.inquiries_page.repeat_agreement_check()

        with allure.step("Отображен договор в статусе 'Действующий', статус клиента - 'Действующий'"):
            self.client_profile_page.open_client_agreements_tab(client.user_id)
            self.client_profile_page.check_active_agreement_in_list()

    @allure.id(966489)
    @allure.title(
        "31. Создание и подписание договора во время продажи (В2С, заполнены не все обязательные данные, автоматическое формирование документов)"
    )
    @pytest.mark.skip(reason="Баг https://jira.nexign.com/browse/RMBSS-18239")
    def test_fill_individual_attributes_and_repeat_agreement_check(
        self, create_potential_individual_user_without_birth_date: IndividualClient
    ) -> None:
        client = create_potential_individual_user_without_birth_date
        with allure.step("Подготовка тестовых данных: у клиента ФЛ не заполнена дата рождения"):
            self.client_requests.create_linked_person(client.user_id, LINKED_PERSON_NAME_B2C)
            inquiry_url = self.inquiries_page.start_sale_with_product(client, create_add_agreement="auto")

        with allure.step("Нажать 'Далее', на шаге проверки появилась ошибка, кнопка 'Далее' неактивна"):
            self.inquiries_page.check_agreement_creation_forbidden()

        with allure.step("Перейти в карточку клиента, нажать 'Редактировать', заполнить данные и сохранить"):
            self.client_profile_page.open_client_card_tab(client.user_id)
            self.client_profile_page.edit_individual_client(
                surname=client.sur_name, tax_scheme=client.tax_scheme, birth_date=client.birth_date
            )

        with allure.step("Вернуться в заявку и повторить проверку, заявка успешно завершена"):
            self.inquiries_page.open_inquiry_on_agreement_check_step(inquiry_url)
            self.inquiries_page.repeat_agreement_check()

        with allure.step("Отображен договор в статусе 'Действующий', статус клиента - 'Действующий'"):
            self.client_profile_page.open_client_agreements_tab(client.user_id)
            self.client_profile_page.check_active_agreement_in_list()

    @allure.id(967602)
    @allure.title(
        "34. Создание и подписание договора во время продажи (Заполнены не все обязательные данные, не формировать документы)"
    )
    def test_fill_organization_attributes_and_repeat_check_without_documents(
        self, create_potential_organization_with_linked_person: OrganizationClient
    ) -> None:
        with allure.step("Подготовка тестовых данных: клиент 'Потенциальный' без обязательных атрибутов"):
            client = create_potential_organization_with_linked_person
            inquiry_url = self.inquiries_page.start_sale_with_product(
                client, product_name=PRODUCT_NAME_B2B, create_add_agreement="no"
            )

        with allure.step("Нажать 'Далее', на шаге проверки появилась ошибка, кнопка 'Далее' неактивна"):
            self.inquiries_page.check_agreement_creation_forbidden()

        with allure.step("Перейти в карточку клиента, нажать 'Редактировать', заполнить данные и сохранить"):
            # TODO: уточнить полный набор обязательных для создания договора атрибутов по HTML формы (TUDS-6163)
            self.client_profile_page.open_client_card_tab(client.user_id)
            self.client_profile_page.edit_organization_client(ogrn=client.ogrn, tax_scheme=client.tax_scheme)

        with allure.step("Вернуться в заявку и повторить проверку, заявка успешно завершена"):
            self.inquiries_page.open_inquiry_on_agreement_check_step(inquiry_url)
            self.inquiries_page.repeat_agreement_check()

        with allure.step("Отображен договор в статусе 'Действующий', статус клиента - 'Действующий'"):
            self.client_profile_page.open_client_agreements_tab(client.user_id)
            self.client_profile_page.check_active_agreement_in_list()

    @allure.id(967607)
    @allure.title(
        "35. Создание и подписание договора во время продажи (B2C, заполнены не все обязательные данные, не формировать документы)"
    )
    def test_fill_individual_attributes_and_repeat_check_without_documents(
        self, create_potential_individual_user_without_birth_date: IndividualClient
    ) -> None:
        client = create_potential_individual_user_without_birth_date
        with allure.step("Подготовка тестовых данных: у клиента ФЛ не заполнена дата рождения"):
            self.client_requests.create_linked_person(client.user_id, LINKED_PERSON_NAME_B2C)
            inquiry_url = self.inquiries_page.start_sale_with_product(client, create_add_agreement="no")

        with allure.step("Нажать 'Далее', на шаге проверки появилась ошибка, кнопка 'Далее' неактивна"):
            self.inquiries_page.check_agreement_creation_forbidden()

        with allure.step("Перейти в карточку клиента, нажать 'Редактировать', заполнить данные и сохранить"):
            self.client_profile_page.open_client_card_tab(client.user_id)
            self.client_profile_page.edit_individual_client(
                surname=client.sur_name, tax_scheme=client.tax_scheme, birth_date=client.birth_date
            )

        with allure.step("Вернуться в заявку и повторить проверку, заявка успешно завершена"):
            self.inquiries_page.open_inquiry_on_agreement_check_step(inquiry_url)
            self.inquiries_page.repeat_agreement_check()

        with allure.step("Отображен договор в статусе 'Действующий', статус клиента - 'Действующий'"):
            self.client_profile_page.open_client_agreements_tab(client.user_id)
            self.client_profile_page.check_active_agreement_in_list()

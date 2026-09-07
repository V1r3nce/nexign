import allure
import pytest

from api.nbss.agreement_requests import AgreementRequests
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.checker import assert_that, wait_that
from common.helpers.data_generator import generate_random_number
from models.client import IndividualClient
from models.inquiry import prepare_inquiries

LINKED_PERSON_NAME = "Связанное лицо ФЛ"


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite("E2E_64_13 Создание и управление клиентом и его иерархиями (Поддержать статус Клиента «Потенциальный»)")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.back
class TestOapiMaintainIndividualClient:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login) -> None:
        self.client_requests = ClientRequests()
        self.agreement_api = AgreementRequests()
        self.inquiries_api = ClientInquiriesRequests()

    @allure.title("Создание клиента ФЛ (OAPI) — статус «Потенциальный»")
    def test_oapi_create_individual_minimal_potential_status(self, individual_user_data: IndividualClient) -> None:
        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
        customer_id = individual_user_data.user_id
        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

    @allure.title("Создание клиента ФЛ (есть дубликаты) (OAPI) — поиск по данным документа")
    def test_oapi_create_individual_duplicate_found_by_document(self, individual_user_data: IndividualClient) -> None:
        with allure.step("До создания клиента по данным его документа никто не находится"):
            found = self.client_requests.search_customers_by_document(
                individual_user_data.document_num, individual_user_data.document_serial
            )
            assert_that(lambda: found == [], lambda: f"По данным документа найден лишний клиент: {found}")

        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)

        with allure.step("После создания по тем же данным документа находится ровно этот клиент"):
            duplicates = self.client_requests.search_customers_by_document(
                individual_user_data.document_num, individual_user_data.document_serial
            )
            assert_that(
                lambda: len(duplicates) == 1,
                lambda: f"Ожидался один дубликат по данным документа, найдено {len(duplicates)}",
            )
            assert_that(
                lambda: duplicates[0]["customerId"] == individual_user_data.user_id,
                lambda: f"Найден чужой клиент {duplicates[0].get('customerId')}, ожидался {individual_user_data.user_id}",
            )

    @allure.title("Редактирование данных клиента ФЛ (OAPI) — изменение данных документа")
    def test_oapi_edit_individual_document_data(self, individual_user_data: IndividualClient) -> None:
        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
        customer_id = individual_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

        with allure.step("Редактирование: атрибут вне идентификации (фамилия)"):
            new_surname = f"{individual_user_data.sur_name}-RENAMED"
            self.client_requests.put_individual_customer(individual_user_data, surname=new_surname)
            wait_that(
                lambda: self.client_requests.get_client_data(customer_id).json()["party"]["nameInfo"]["surname"]
                == new_surname,
                timeout=15,
                sleep_seconds=0.5,
                exception=AssertionError,
                message="После PUT фамилия в GET не совпала с ожидаемой за отведённое время",
            )

        with allure.step("Редактирование: смена данных документа, дубликатов нет"):
            new_document_num = str(generate_random_number(6))
            self.client_requests.put_individual_customer(individual_user_data, document_num=new_document_num)
            wait_that(
                lambda: self.client_requests.get_individual_identification_document(customer_id)[1] == new_document_num,
                timeout=15,
                sleep_seconds=0.5,
                exception=AssertionError,
                message="После PUT номер документа в GET не совпал с ожидаемым за отведённое время",
            )

    @allure.title("Создание договора клиента ФЛ (OAPI) — подписание переводит клиента в «Действующий»")
    def test_oapi_create_and_sign_agreement_individual_client(self, individual_user_data: IndividualClient) -> None:
        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
        customer_id = individual_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

        with allure.step("Создание связанного лица"):
            linked_person_id = self.client_requests.create_linked_person(customer_id, LINKED_PERSON_NAME)

        with allure.step("Создание договора"):
            agreement_id, agreement_number = self.client_requests.personal_account_api.create_agreement(
                individual_user_data
            )
            assert_that(
                lambda: agreement_id is not None and agreement_number is not None,
                lambda: f"Договор не создан: agreement_id={agreement_id}, agreement_number={agreement_number}",
            )

        with allure.step("Клиент остаётся «Потенциальным», пока договор не подписан"):
            self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")

        with allure.step("Подписание договора; статус клиента «Действующий»"):
            self.agreement_api.sign_agreement(
                agreement_id,
                agent_signer_id=linked_person_id,
                client=individual_user_data,
            )
            self.client_requests.wait_customer_lifecycle_status(customer_id, "Действующий")

    @allure.title("Создание связанного лица на клиенте ФЛ (OAPI)")
    def test_oapi_create_linked_person_on_potential_individual_client(
        self, individual_user_data: IndividualClient
    ) -> None:
        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
        customer_id = individual_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")

        linked_person_id = self.client_requests.create_linked_person(customer_id, LINKED_PERSON_NAME)
        assert_that(
            lambda: linked_person_id is not None and linked_person_id > 0,
            lambda: f"Связанное лицо не создано, linked_person_id={linked_person_id}",
        )

    @allure.title("20. Создание клиента ФЛ (найден дубликат, данные исправлены) (OAPI)")
    def test_oapi_create_individual_after_duplicate_corrected(self, individual_user_data: IndividualClient) -> None:
        with allure.step("Подготовка тестовых данных: клиент с такими же данными документа уже существует"):
            duplicate = self.client_requests.create_individual_client(IndividualClient(), is_potential_customer=True)

        with allure.step("По данным документа дубликата находится существующий клиент"):
            found = self.client_requests.search_customers_by_document(duplicate.document_num, duplicate.document_serial)
            assert_that(
                lambda: len(found) == 1 and found[0]["customerId"] == duplicate.user_id,
                lambda: f"По данным документа не найден созданный клиент {duplicate.user_id}: {found}",
            )

        with allure.step("После исправления данных документа дубликатов нет и клиент создаётся"):
            corrected = self.client_requests.search_customers_by_document(
                individual_user_data.document_num, individual_user_data.document_serial
            )
            assert_that(lambda: corrected == [], lambda: f"По новым данным документа найден лишний клиент: {corrected}")

            self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
            self.client_requests.check_customer_lifecycle_status(individual_user_data.user_id, "Потенциальный")

    @allure.title("31. Создание договора клиента ФЛ без даты рождения (OAPI) — отказ, затем успех после дозаполнения")
    def test_oapi_create_agreement_individual_without_birth_date_fill_then_success(
        self, individual_user_data: IndividualClient
    ) -> None:
        with allure.step("Подготовка тестовых данных: у клиента ФЛ не заполнена дата рождения"):
            self.client_requests.create_individual_client(
                individual_user_data, is_potential_customer=True, without_birth_date=True
            )
            customer_id = individual_user_data.user_id
            self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")

        with allure.step("Создание договора при неполных атрибутах — отказ"):
            self.client_requests.personal_account_api.create_agreement(individual_user_data, is_successful=False)

        with allure.step("Дозаполнение даты рождения"):
            # Дата рождения есть в модели клиента и не попала только в тело создания,
            # поэтому PUT без переопределений как раз её и дозаполняет.
            self.client_requests.put_individual_customer(individual_user_data)

        with allure.step("Повторное создание договора — успех"):
            agreement_id, agreement_number = self.client_requests.personal_account_api.create_agreement(
                individual_user_data
            )
            assert_that(
                lambda: agreement_id is not None and agreement_number is not None,
                lambda: f"Договор не создан после дозаполнения: agreement_id={agreement_id}",
            )

    @allure.title("30. Создание и подписание договора во время продажи B2C (OAPI) — клиент становится «Действующим»")
    def test_oapi_sale_transfers_individual_to_active(self, individual_user_data: IndividualClient) -> None:
        with allure.step("Подготовка тестовых данных: клиент ФЛ «Потенциальный»"):
            self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
            customer_id = individual_user_data.user_id
            self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")

        with allure.step("Продажа продукта: заявка проходит до конца"):
            inquiry = self.inquiries_api.product_sale(individual_user_data, prepare_inquiries("internet"))
            assert_that(
                lambda: inquiry is not None and inquiry.is_completed,
                lambda: f"Заявка на продажу не завершена: {inquiry}",
            )

        with allure.step("Статус клиента — «Действующий»"):
            self.client_requests.wait_customer_lifecycle_status(customer_id, "Действующий")

    @allure.title("21. Создание клиента ФЛ (найден дубликат, переход к дубликату) (OAPI)")
    def test_oapi_create_individual_duplicate_go_to_found_duplicate(
        self, individual_user_data: IndividualClient
    ) -> None:
        with allure.step("Подготовка тестовых данных: клиент с такими же данными документа уже существует"):
            duplicate = self.client_requests.create_individual_client(IndividualClient(), is_potential_customer=True)

        with allure.step("По данным документа найден дубликат"):
            found = self.client_requests.search_customers_by_document(duplicate.document_num, duplicate.document_serial)
            assert_that(
                lambda: len(found) == 1,
                lambda: f"Ожидался один дубликат по данным документа, найдено {len(found)}",
            )

        with allure.step("Найденный дубликат — тот самый клиент: переход ведёт на его карточку"):
            # Переход по интерфейсу открывает карточку по customerId из ответа поиска,
            # поэтому на бэкенде проверяем, что поиск отдал идентификатор и ФИО нужного клиента.
            assert_that(
                lambda: found[0]["customerId"] == duplicate.user_id,
                lambda: f"Поиск отдал клиента {found[0].get('customerId')}, ожидался {duplicate.user_id}",
            )
            assert_that(
                lambda: found[0]["party"]["nameInfo"]["surname"] == duplicate.sur_name,
                lambda: f"Фамилия найденного клиента не совпала: {found[0]['party']['nameInfo']['surname']}",
            )
            self.client_requests.get_client_data(duplicate.user_id, check_status=True)

    @allure.title("26. Редактирование клиента ФЛ (найден дубликат) (OAPI)")
    def test_oapi_edit_individual_duplicate_document_returns_error(self, individual_user_data: IndividualClient) -> None:
        """Проверяет, что дубликат по документу не даёт сохранить изменения клиента ФЛ.

        Тест красный намеренно: на PUT с данными документа существующего клиента бэкенд отвечает 200
        и сохраняет изменения, тогда как у ЮЛ на то же самое приходит 400 identificationCustomerFound.
        """
        with allure.step("Подготовка тестовых данных: в системе есть второй клиент ФЛ"):
            duplicate = self.client_requests.create_individual_client(IndividualClient(), is_potential_customer=True)

        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
        customer_id = individual_user_data.user_id
        original_document = self.client_requests.get_individual_identification_document(customer_id)

        with allure.step("Указать данные документа существующего клиента — изменения отклонены"):
            self.client_requests.put_individual_customer(
                individual_user_data,
                document_num=duplicate.document_num,
                document_serial=duplicate.document_serial,
                is_successful=False,
            )

        with allure.step("Данные редактируемого клиента не изменились"):
            assert_that(
                lambda: self.client_requests.get_individual_identification_document(customer_id) == original_document,
                lambda: f"Данные документа изменились на данные дубликата: {original_document}",
            )

    @allure.title("27. Редактирование клиента ФЛ (найден дубликат, переход к дубликату) (OAPI)")
    def test_oapi_edit_individual_duplicate_go_to_found_duplicate(self, individual_user_data: IndividualClient) -> None:
        """Проверяет отказ при редактировании на дубликат и то, что найденный дубликат — существующий клиент.

        Тест красный намеренно по той же причине, что и кейс 26: бэкенд принимает такое редактирование.
        """
        with allure.step("Подготовка тестовых данных: в системе есть второй клиент ФЛ"):
            duplicate = self.client_requests.create_individual_client(IndividualClient(), is_potential_customer=True)

        self.client_requests.create_individual_client(individual_user_data, is_potential_customer=True)
        customer_id = individual_user_data.user_id
        original_document = self.client_requests.get_individual_identification_document(customer_id)

        with allure.step("Указать данные документа существующего клиента — изменения отклонены"):
            self.client_requests.put_individual_customer(
                individual_user_data,
                document_num=duplicate.document_num,
                document_serial=duplicate.document_serial,
                is_successful=False,
            )

        with allure.step("Найденный дубликат — тот самый клиент: переход ведёт на его карточку"):
            found = self.client_requests.search_customers_by_document(duplicate.document_num, duplicate.document_serial)
            assert_that(
                lambda: len(found) == 1 and found[0]["customerId"] == duplicate.user_id,
                lambda: f"Поиск по документу не отдал клиента {duplicate.user_id}: {found}",
            )
            self.client_requests.get_client_data(duplicate.user_id, check_status=True)

        with allure.step("Изменения редактируемого клиента не произошло"):
            assert_that(
                lambda: self.client_requests.get_individual_identification_document(customer_id) == original_document,
                lambda: f"Данные документа изменились на данные дубликата: {original_document}",
            )

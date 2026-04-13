import allure
import pytest

from api.nbss.agreement_requests import AgreementRequests
from api.nbss.client_requests.client_requests import ClientRequests
from common.helpers.checker import assert_that, wait_that
from common.helpers.data_generator import generate_random_number
from models.client import OrganizationClient


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite("E2E_64_13 Создание и управление клиентом и его иерархиями (Поддержать статус Клиента «Потенциальный»)")
@pytest.mark.regress
@pytest.mark.nbss_portal
@pytest.mark.back
class TestOapiMaintainClient:
    @pytest.fixture(autouse=True)
    def setup(self, sso_stand_login) -> None:
        self.client_requests = ClientRequests()
        self.agreement_api = AgreementRequests()

    @allure.id(669971)
    @allure.title("21. Создание клиента (OAPI) — ЮЛ, статус «Потенциальный»")
    def test_oapi_create_organization_minimal_potential_status(self, organization_user_data: OrganizationClient) -> None:
        self.client_requests.create_organization(organization_user_data, is_potential_customer=True)
        customer_id = organization_user_data.user_id
        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

    @allure.id(670005)
    @allure.title("22. Создание клиента (есть дубликаты) (OAPI) — повтор запроса, 400")
    def test_oapi_create_organization_duplicate_second_request_returns_400(
        self, organization_user_data: OrganizationClient
    ) -> None:
        self.client_requests.create_organization(organization_user_data, is_potential_customer=True)
        self.client_requests._create_organization(
            organization_user_data,
            is_potential_customer=True,
            is_successful=False,
        )

    @allure.id(669980)
    @allure.title("23. Редактирование данных клиента (OAPI)")
    def test_oapi_edit_organization_customer_data(self, organization_user_data: OrganizationClient) -> None:
        self.client_requests.create_organization(organization_user_data, is_potential_customer=True)
        customer_id = organization_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

        with allure.step("Редактирование: не-null атрибуты без смены идентификаторов (наименование)"):
            new_name = f"{organization_user_data.customer_name}-RENAMED"
            self.client_requests.put_organization_customer(organization_user_data, corporate_name=new_name)
            wait_that(
                lambda: self.client_requests.get_organization_corporate_name(customer_id) == new_name,
                timeout=15,
                sleep_seconds=0.5,
                exception=AssertionError,
                message="После PUT наименование в GET не совпало с ожидаемым за отведённое время",
            )

        with allure.step("Редактирование: изменение идентификации (новый уникальный ИНН), дубликатов нет"):
            new_inn = str(generate_random_number(10))
            organization_user_data.inn = new_inn
            self.client_requests.put_organization_customer(organization_user_data, corporate_name=new_name)
            wait_that(
                lambda: self.client_requests.get_organization_tax_identification_number(customer_id) == new_inn,
                timeout=15,
                sleep_seconds=0.5,
                exception=AssertionError,
                message="После PUT ИНН в GET не совпал с ожидаемым за отведённое время",
            )

    @allure.id(669989)
    @allure.title("24. Редактирование данных клиента (данные не обновлены) (OAPI)")
    def test_oapi_edit_organization_null_required_attributes_returns_error(
        self, organization_user_data: OrganizationClient
    ) -> None:
        self.client_requests.create_organization(organization_user_data, is_potential_customer=True)
        customer_id = organization_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

        payload = self.client_requests.build_put_organization_null_required_attributes_payload(organization_user_data)
        self.client_requests.put_customer(customer_id, payload, is_successful=False)

    @allure.id(669991)
    @allure.title("25. Создание договора клиента (OAPI)")
    def test_oapi_create_agreement_potential_client_fill_then_success(
        self, organization_user_data: OrganizationClient
    ) -> None:
        self.client_requests.create_organization(organization_user_data, is_potential_customer=True)
        customer_id = organization_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")
        self.client_requests.check_customer_has_no_personal_accounts(customer_id)

        with allure.step("Создание договора при неполных атрибутах — 400"):
            self.client_requests.personal_account_api.create_agreement(
                organization_user_data,
                is_successful=False,
            )

        with allure.step("Дозаполнение обязательных атрибутов (PUT + код авторизации + схема + адрес)"):
            self.client_requests.fill_organization_attributes_for_agreement_after_potential(organization_user_data)

        with allure.step("Создание связанного лица"):
            linked_person_id = self.client_requests.create_linked_person(customer_id, "Иван Иваныч")

        with allure.step("Повторное создание договора — успех"):
            agreement_id, agreement_number = self.client_requests.personal_account_api.create_agreement(
                organization_user_data
            )
            assert agreement_id is not None
            assert agreement_number is not None

        with allure.step("Подписание договора; статус клиента «Действующий»"):
            self.agreement_api.sign_agreement(
                agreement_id,
                agent_signer_id=linked_person_id,
                client=organization_user_data,
            )
            self.client_requests.wait_customer_lifecycle_status(
                customer_id,
                "Действующий",
            )

    @allure.id(670000)
    @allure.title("26. Создание связанного лица на Клиенте (OAPI)")
    def test_oapi_create_linked_person_on_potential_client(self, organization_user_data: OrganizationClient) -> None:
        self.client_requests.create_organization(organization_user_data, is_potential_customer=True)
        customer_id = organization_user_data.user_id

        self.client_requests.check_customer_lifecycle_status(customer_id, "Потенциальный")

        linked_person_id = self.client_requests.create_linked_person(customer_id, "Бухгалтерия Ромашка")
        assert_that(
            lambda: linked_person_id is not None and linked_person_id > 0,
            lambda: f"Связанное лицо не создано, linked_person_id={linked_person_id}",
        )

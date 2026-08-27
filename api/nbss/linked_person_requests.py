import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API
from models.client import IndividualClient
from models.context import test_context


class LinkedPersonRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()

    @allure.step("API: Получение связанных лиц клиента")
    def get_linked_person(self, user_id: int) -> list:
        """
        Получение связанных лиц клиента
        :param user_id: id клиента
        :return: список объектов с информацией о связанных лицах клиента
        """
        body_person = {
            "entity": {"code": "customer", "id": user_id},
            "linkedPerson": {},
            "linkedPersonFunctionStatusIds": [1],
        }
        response_person = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/linkedPersonFunctions/search?returnCount=true&limit=60&offset=0",
            json=body_person,
        )
        self.check_response_status(response_person, 200, "Не удалось получить связанные лица клиента")
        return response_person.json()["items"]

    @allure.step("API: Создание связанного лица")
    def make_linked_person(self, date: str, user_id: int) -> int:
        """
        Создание связанного лица
        :param date: строка с датой создания вида "05/12/2025-15:31:05"
        :param user_id: id клиента, созданного фикстурой create_user
        :return: id связанного лица клиента
        """
        body_person = {
            "party": {
                "type": "IMPERSONAL",
                "nameInfo": {"impersonalName": f"IMPERSONAL - {date}"},
                "speakingLanguage": {"languageId": 3},
            }
        }
        response_person = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{user_id}/linkedPersons", json=body_person
        )
        self.check_response_status(response_person, 200, "Не получилось добавить связанное лицо клиенту")
        return response_person.json()["linkedPersonId"]

    @allure.step("API: Добавление связанного лица в UDS")
    def add_linked_person_to_uds(self, user_id: int, linked_person_id: int) -> None:
        """
        Добавление связанного лица в UDS
        :param user_id: id клиента, созданного фикстурой create_user
        :param linked_person_id: id связанного лица из make_linked_person
        Упадет с ошибкой, если добавление не завершилось успешно
        """
        body_uds = {
            "entity": {"code": "customer", "id": user_id},
            "linkedPersonFunctionType": "CONTACT_PERSON",
            "specializationTypes": [
                {"specializationTypeId": 1},
                {"specializationTypeId": 2},
                {"specializationTypeId": 3},
                {"specializationTypeId": 4},
            ],
            "emailContacts": [{"email": "mail@mail.ru", "isMain": True}],
        }
        response_uds = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/linkedPersonFunctions",
            json=body_uds,
        )
        self.check_response_status(response_uds, 200, "Связанное лицо не добавлено в UDS")
        assert response_uds.json()["linkedPersonFunctionId"] is not None

    @allure.step("API: Добавление конечного пользователя к абоненту")
    def create_end_user_to_subscriber(self, client: IndividualClient) -> None:
        payload = {
            "customerId": test_context.client.user_id,
            "items": [{"addressString": client.registration_address, "externalAddressId": client.external_address_id}],
            "party": {
                "birthDate": client.birth_date_for_api,
                "gender": {"genderId": client.gender_id},
                "identificationDocument": {
                    "number": client.document_num,
                    "type": {"identificationTypeId": client.document_type_id},
                },
                "isResident": client.is_resident_bool,
                "nameInfo": {
                    "firstName": client.first_name,
                    "patronymic": client.patronymic,
                    "surname": client.sur_name,
                },
                "nationality": {"nationalityId": client.nationality_id},
                "publicOfficial": client.is_public_bool,
                "speakingLanguage": {"languageId": client.speaking_language_id},
                "type": "INDIVIDUAL",
            },
        }
        response_uds = self.post(
            url=f"{BASE_URL_API}/openapi/v1/tailored_nbss/subscribers/{test_context.client.inquiry.product.subs_id}/linkedPersons/functions/endUsers/create",
            json=payload,
        )
        self.check_response_status(response_uds, 200, "Конечный пользователь не добавлен")

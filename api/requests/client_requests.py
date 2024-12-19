import allure
from playwright.sync_api import APIRequestContext

from common.env_helper import BASE_URL_API
from models.address_info import BasicSystemAddress


class ClientRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}'")
    def create_linked_person(self, client_id: str, name: str):
        payload = {"party": {"nameInfo": {"impersonalName": name}, "note": None,
                             "speakingLanguage": {"languageId": 3}, "type": "IMPERSONAL"}}
        response = (self.api_request_auth_context.
                    post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/linkedPersons",
                         data=payload))
        assert response.status == 200, "Не привязалось связанное лицо"
        linked_person_id = response.json()["linkedPersonId"]
        payload_add_funk = {"entity": {"code": "customer", "id": client_id},
                            "linkedPersonFunctionType": "CONTACT_PERSON",
                            "specializationTypes": [{"specializationTypeId": 4}]}
        response_add_func = (self.api_request_auth_context.
                             post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/"
                                      f"linkedPersonFunctions",
                                  data=payload_add_funk))
        assert response_add_func.status == 200, "Не привязалась функция связанного лица"

    @allure.step("Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}' и базовым "
                 "адресом регистрации")
    def create_linked_person_with_registration_address(self, client_id: str, name: str):
        payload = {"party": {"nameInfo": {"impersonalName": name}, "note": None,
                             "speakingLanguage": {"languageId": 3}, "type": "IMPERSONAL"}}
        response = (self.api_request_auth_context.
                    post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/linkedPersons",
                         data=payload))
        assert response.status == 200, "Не привязалось связанное лицо"
        linked_person_id = response.json()["linkedPersonId"]
        payload_add_funk = {"entity": {"code": "customer", "id": client_id},
                            "linkedPersonFunctionType": "CONTACT_PERSON",
                            "specializationTypes": [{"specializationTypeId": 4}]}
        response_add_func = (self.api_request_auth_context.
                             post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/"
                                      f"linkedPersonFunctions",
                                  data=payload_add_funk))
        assert response_add_func.status == 200, "Не привязалась функция связанного лица"
        payload_add_places = {"addressString": BasicSystemAddress.address,
                              "entity": {"code": "linkedPerson", "id": linked_person_id},
                              "externalAddressId": BasicSystemAddress.external_address_id,
                              "type": {"placeTypeId": 1}}
        places = self.api_request_auth_context.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places",
                                                    data=payload_add_places)
        assert places.status == 200, "Не добавлен адрес регистрации для связанного лица"

import allure
from playwright.sync_api import APIRequestContext

from common.env_helper import BASE_URL_API


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

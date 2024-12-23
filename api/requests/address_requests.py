import allure
from playwright.sync_api import APIRequestContext
from common.env_helper import BASE_URL_API
from models.address_info import BasicSystemAddress


class AddressRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Создать адрес регистрации для связанного лица '{linked_person_id}'")
    def add_registry_address_linked_person(self, linked_person_id: int):
        """
        Метод добавляет адрес регистрации для связанного лица.

        Parameters:
        linked_person_id (int): id связанного лица.

        Returns:
        Response: объект ответа API.
        """
        payload_add_places = {"addressString": BasicSystemAddress.address,
                              "entity": {"code": "linkedPerson", "id": linked_person_id},
                              "externalAddressId": BasicSystemAddress.external_address_id,
                              "type": {"placeTypeId": 1}}
        places = self.api_request_auth_context.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places",
                                                    data=payload_add_places)
        assert places.status == 200, "Не добавлен адрес регистрации для связанного лица"
        return places

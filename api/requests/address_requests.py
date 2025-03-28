import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.exceptions import LinkedPersonPullAddressException
from api.requests.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from models.address_info import BasicSystemAddress


class AddressRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Создать адрес регистрации для связанного лица '{linked_person_id}'")
    def add_registry_address_linked_person(self, linked_person_id: int, map_url: list[None | str]) -> APIResponse:
        """
        Метод добавляет адрес регистрации для связанного лица.

        Parameters:
        linked_person_id (int): id связанного лица.

        Returns:
        Response: объект ответа API.
        """
        payload_add_places = {
            "addressString": BasicSystemAddress.address,
            "entity": {"code": "linkedPerson", "id": linked_person_id},
            "externalAddressId": BasicSystemAddress.external_address_id,
            "type": {"placeTypeId": 1},
        }
        if map_url:
            payload_add_places["addressUrl"] = map_url
        places = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places", data=payload_add_places)
        self.check_response_status(places, 200, "Не добавлен адрес регистрации для связанного лица")
        wait_that(
            lambda: len(self.get_linked_person_addresses(linked_person_id).json()["items"]) >= 1,
            timeout=10,
            sleep_seconds=0.5,
            exception=LinkedPersonPullAddressException,
            message="Не сформирован пул адресов связанного лица в установленное время",
        )
        return places

    @allure.step("API: Получить данные по адресам Клиента '{customer_id}'")
    def get_client_addresses(self, customer_id: int) -> APIResponse:
        """
        Получить данные по адресам Клиента
        """
        params = {"returnCount": True, "limit": 10, "sort": "type.name", "offset": 0}
        payload_get_places = {"entity": {"code": "customer", "id": customer_id}}
        address = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/search", params=params, data=payload_get_places
        )
        self.check_response_status(address, 200, "Не получены данные по адресам Клиента")
        return address

    @allure.step("API: Получить данные по адресам связного лица '{linked_person_id}'")
    def get_linked_person_addresses(self, linked_person_id: int) -> APIResponse:
        """
        Получить данные по адресам связного лица
        """
        params = {"returnCount": True, "limit": 10, "sort": "type.name", "offset": 0}
        payload_get_places = {"entity": {"code": "linkedPerson", "id": linked_person_id}}
        address = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/search", params=params, data=payload_get_places
        )
        self.check_response_status(address, 200, "Не получены данные по адресам Клиента")
        return address

    @allure.step("API: Обновить адрес '{place_id}' Клиента")
    def update_client_address(
        self, place_id: int, address: str, address_url: str, external_address_id: int
    ) -> APIResponse:
        """
        Получить данные по адресам Клиента
        """
        payload_set_place = {
            "addressString": address,
            "addressUrl": address_url,
            "externalAddressId": external_address_id,
        }
        response = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/{place_id}", data=payload_set_place
        )
        self.check_response_status(response, 200, "Не обновился адрес Клиента")
        return response

    def get_russia_parent_id(self) -> int:
        """
        Получить parent_id для России, если нет атрибута, то создать
        """
        russia_search_payload = {
            "classifierCode": "addresses",
            "filters": [{"attributeCode": "name", "value": "Россия%"}],
            "typeCode": "country",
        }
        russia_search = self.post(
            url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses/elements/search",
            params={"limit": 100, "offset": 0},
            data=russia_search_payload,
        )
        self.check_response_status(russia_search, 200, "Запрос на поиск выполнен не корректно")
        russia_id = [
            item["addressId"]
            for item in russia_search.json()["items"]
            if item["addressString"] == "Россия" and item["typeCode"] == "country"
        ]
        if len(russia_id) > 0:
            return russia_id[0]
        else:
            create_russia_payload = {
                "classifierCode": "addresses",
                "elements": {"country": {"attributes": {"name": {"ru": "Россия"}}}},
            }
            russia_create = self.post(
                url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", data=create_russia_payload
            )
            self.check_response_status(russia_create, 200, "Запрос на создание атрибута Россия выполнен не корректно")
            parent_address_id = russia_create.json()["addressId"]
            return parent_address_id

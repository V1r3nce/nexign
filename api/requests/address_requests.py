import allure
from playwright.sync_api import APIRequestContext
from common.helpers.env_helper import BASE_URL_API
from models.address_info import BasicSystemAddress
from waiting import wait


class AddressRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Создать адрес регистрации для связанного лица '{linked_person_id}'")
    def add_registry_address_linked_person(self, linked_person_id: int, map_url: [None, str]):
        """
        Метод добавляет адрес регистрации для связанного лица.

        Parameters:
        linked_person_id (int): id связанного лица.

        Returns:
        Response: объект ответа API.
        """
        payload_add_places = {"addressString": BasicSystemAddress.address,
                              "entity": {"code": "linkedPerson", "id": linked_person_id},
                              "externalAddressId": BasicSystemAddress.external_address_id, "type": {"placeTypeId": 1}}
        if map_url:
            payload_add_places["addressUrl"] = map_url
        places = self.api_request_auth_context.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places",
                                                    data=payload_add_places)
        assert places.status == 200, "Не добавлен адрес регистрации для связанного лица"
        wait(
            lambda: len(self.get_linked_person_addresses(linked_person_id).json()["items"]) >= 1,
            timeout_seconds=10, sleep_seconds=0.5,
            waiting_for="Не сформирован пул адресов связанного лица в установленное время")
        return places

    @allure.step("Получить данные по адресам Клиента '{customer_id}'")
    def get_client_addresses(self, customer_id: int):
        """
        Получить данные по адресам Клиента, возвращает объект типа Response
        """
        params = {"returnCount": True, "limit": 10, "sort": "type.name", "offset": 0}
        payload_get_places = {"entity": {"code": "customer", "id": customer_id}}
        address = self.api_request_auth_context.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/search",
                                                     params=params, data=payload_get_places)
        assert address.status == 200, "Не получены данные по адресам Клиента"
        return address

    @allure.step("Получить данные по адресам связного лица '{linked_person_id}'")
    def get_linked_person_addresses(self, linked_person_id: int):
        """
        Получить данные по адресам связного лица, возвращает объект типа Response
        """
        params = {"returnCount": True, "limit": 10, "sort": "type.name", "offset": 0}
        payload_get_places = {"entity": {"code": "linkedPerson", "id": linked_person_id}}
        address = self.api_request_auth_context.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/search",
                                                     params=params, data=payload_get_places)
        assert address.status == 200, "Не получены данные по адресам Клиента"
        return address

    @allure.step("Обновить адрес '{place_id}' Клиента")
    def update_client_address(self, place_id: int, address: str, address_url: str, external_address_id: int):
        """
        Получить данные по адресам Клиента, возвращает объект типа Response
        """
        payload_set_place = {"addressString": address, "addressUrl": address_url,
                             "externalAddressId": external_address_id}
        address = self.api_request_auth_context.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/{place_id}", data=payload_set_place)
        assert address.status == 200, "Не обновился адрес Клиента"
        return address

    def get_russia_parent_id(self):
        """
        Получить parent_id для России, если нет атрибута, то создать
        """
        russia_search_payload = {"classifierCode": "addresses",
                                 "filters": [{"attributeCode": "name", "value": "Россия%"}], "typeCode": "country"}
        russia_search = self.api_request_auth_context.post(
            url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses/elements/search",
            params={"limit": 100, "offset": 0}, data=russia_search_payload)
        assert russia_search.status == 200, "Запрос на поиск выполнен не корректно"
        russia_id = [item["addressId"] for item in russia_search.json()["items"] if
                     item['addressString'] == "Россия" and item["typeCode"] == "country"]
        if len(russia_id) > 0:
            return russia_id[0]
        else:
            create_russia_payload = {"classifierCode": "addresses",
                                     "elements": {"country": {"attributes": {"name": {"ru": "Россия"}}}}}
            russia_create = self.api_request_auth_context.post(
                url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses",
                data=create_russia_payload)
            assert russia_create.status == 200, "Запрос на создание атрибута Россия выполнен не корректно"
            parent_address_id = russia_create.json()["addressId"]
            return parent_address_id

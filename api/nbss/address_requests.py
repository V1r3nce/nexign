import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import LinkedPersonPullAddressException
from common.helpers.checker import wait_that
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL_API
from models.address_info import BasicSystemAddress
from models.playwright_bridge import GeneralResponse


class AddressRequests(BaseRequests):
    @pytest.mark.praim
    @allure.step("API: Создать адрес регистрации для связанного лица '{linked_person_id}'")
    def add_registry_address_linked_person(self, linked_person_id: int, map_url: list[None | str]) -> GeneralResponse:
        """
        Метод добавляет адрес регистрации для связанного лица.

        Args:
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
        places = self.post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/places", json=payload_add_places)
        self.check_response_status(places, 200, "Не добавлен адрес регистрации для связанного лица")
        wait_that(
            lambda: len(self.get_linked_person_addresses(linked_person_id).json()["items"]) >= 1,
            timeout=10,
            sleep_seconds=0.5,
            exception=LinkedPersonPullAddressException,
            message="Не сформирован пул адресов связанного лица в установленное время",
        )
        return places

    @pytest.mark.praim
    @allure.step("API: Получить данные по адресам Клиента '{customer_id}'")
    def get_client_addresses(self, customer_id: int) -> GeneralResponse:
        """
        Получить данные по адресам Клиента
        """
        params = {"returnCount": True, "limit": 10, "sort": "type.name", "offset": 0}
        payload_get_places = {"entity": {"code": "customer", "id": customer_id}}
        address = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/search", params=params, json=payload_get_places
        )
        self.check_response_status(address, 200, "Не получены данные по адресам Клиента")
        return address

    @pytest.mark.praim
    @allure.step("API: Получить данные по адресам связного лица '{linked_person_id}'")
    def get_linked_person_addresses(self, linked_person_id: int) -> GeneralResponse:
        """
        Получить данные по адресам связного лица
        """
        params = {"returnCount": True, "limit": 10, "sort": "type.name", "offset": 0}
        payload_get_places = {"entity": {"code": "linkedPerson", "id": linked_person_id}}
        address = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/search", params=params, json=payload_get_places
        )
        self.check_response_status(address, 200, "Не получены данные по адресам Клиента")
        return address

    @pytest.mark.praim
    @allure.step("API: Обновить адрес '{place_id}' Клиента")
    def update_client_address(
        self, place_id: int, address: str, address_url: str, external_address_id: int
    ) -> GeneralResponse:
        """
        Получить данные по адресам Клиента
        """
        payload_set_place = {
            "addressString": address,
            "addressUrl": address_url,
            "externalAddressId": external_address_id,
        }
        response = self.put(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places/{place_id}", json=payload_set_place
        )
        self.check_response_status(response, 200, "Не обновился адрес Клиента")
        return response

    @pytest.mark.lam
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
            json=russia_search_payload,
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
                url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", json=create_russia_payload
            )
            self.check_response_status(russia_create, 200, "Запрос на создание атрибута Россия выполнен не корректно")
            parent_address_id = russia_create.json()["addressId"]
            return parent_address_id

    @pytest.mark.praim
    @pytest.mark.lam
    def add_base_address_to_client(self, address: str, customer_id: int) -> GeneralResponse | None:
        """
        Добавить базовый адрес клиенту. Если адреса не существует на стенде создать базовый адрес.
        """
        params_search = {"searchProfileCode": "addresses", "searchString": address, "limit": 100, "offset": 0}
        headers_add_places = {"Content-Type": "application/json"}
        search = self.get(url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", params=params_search)
        self.check_response_status(search, 200, "Не удалось получить информацию о адресах")
        needed_address_data = [item for item in search.json()["items"] if item["addressString"] == address]
        if len(needed_address_data) > 0:
            payload_add_places = {
                "addressString": address,
                "entity": {"code": "customer", "id": customer_id},
                "externalAddressId": needed_address_data[0]["addressId"],
                "type": {"placeTypeId": 1},
            }
        else:
            create_base_address_payload = {
                "classifierCode": "addresses",
                "elements": {"country": {"attributes": {"name": {"en": address, "ru": address}}}},
            }
            create_base_address = self.post(
                url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", json=create_base_address_payload
            )
            self.check_response_status(
                create_base_address, 200, "Запрос на создание базового адреса выполнен не корректно"
            )
            search = self.get(url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", params=params_search)
            self.check_response_status(search, 200, "Не удалось получить данные по адресу")
            needed_address_data_new_address = [
                item for item in search.json()["items"] if item["addressString"] == address
            ]
            payload_add_places = {
                "addressString": address,
                "entity": {"code": "customer", "id": customer_id},
                "externalAddressId": needed_address_data_new_address[0]["addressId"],
                "type": {"placeTypeId": 1},
            }
        places = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/places",
            headers=headers_add_places,
            json=payload_add_places,
        )
        self.check_response_status(places, 200, "Не добавлен адрес регистрации для созданного клиента")
        return places

    @pytest.mark.lam
    def add_new_address_to_lam(self) -> dict:
        """Возвращает созданный адрес в виде словаря {'addressId': int, 'addressString': str}"""
        headers = {"Content-Type": "application/json"}
        api_addresses = AddressRequests()
        russia_address_id = api_addresses.get_russia_parent_id()
        random_number = generate_random_number(3)
        payload = {
            "classifierCode": "addresses",
            "elements": {
                "region": {
                    "attributes": {"name": {"ru": "Самарская область"}, "regionType": {"enumerationCode": "obl."}}
                },
                "city": {"attributes": {"name": {"ru": "Самара"}, "cityType": {"enumerationCode": "g."}}},
                "street": {"attributes": {"name": {"ru": "Полевая"}, "streetType": {"enumerationCode": "ul."}}},
                "house": {"attributes": {"houseType": {"enumerationCode": "d."}, "number": {"ru": random_number}}},
            },
            "parentAddressId": russia_address_id,
        }
        try:
            request = self.post(
                url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", headers=headers, json=payload
            )
            api_addresses.check_response_status(request, 200, "Не выполнен запрос на создание нового адреса в LAM")
        except AssertionError:
            payload["elements"]["house"]["attributes"]["number"]["ru"] = random_number + 1
            request = self.post(
                url=f"{BASE_URL_API}/openapi/v1/locationManagement/addresses", headers=headers, json=payload
            )
            api_addresses.check_response_status(request, 200, "Не выполнен запрос на создание нового адреса в LAM")
        response = request.json()
        return response

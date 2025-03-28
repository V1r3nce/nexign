import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.exceptions import LinkedPersonException, LinkedPersonFunctionException, LinkedPersonPullAddressException
from api.requests.address_requests import AddressRequests
from api.requests.base_requests import BaseRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay


class ClientRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Получить данные по клиенту '{customer_id}'")
    def get_client_data(self, customer_id: int) -> APIResponse:
        """
        Получить данные по клиенту.

        Parameters:
        customer_id (int): id Клиента.

        Returns:
        Response: объект ответа API с данными клиента.
        """
        client = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}")
        return client

    @allure.step("API: Получить данные по связанному лицу '{linked_person_id}'")
    def get_linked_person_data(self, linked_person_id: int) -> APIResponse:
        """
        Получить данные по связанному лицу.

        Parameters:
        linked_person_id (int): id связанного лица.

        Returns:
        Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.get(url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}")
        return linked_person

    @allure.step("API: Получить данные по специализации связанного лица '{linked_function_id}'")
    def get_linked_person_specialisation(self, linked_function_id: int) -> APIResponse:
        """
        Получить данные по специализации связанного лица.

        Parameters:
        linked_function_id (int): id функции связанного лица.

        Returns:
        Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.get(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/linkedPersonFunctions/{linked_function_id}"
        )
        return linked_person

    @allure.step("API: Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}'")
    def create_linked_person(self, client_id: int, name: str) -> int:
        """
        Метод создает обезличенное связанное лицо

        Parameters:
        client_id (int): id Клиента.
        name (str): название связанного лица.

        Returns:
        int: id связанного лица.
        """
        payload = {
            "party": {
                "nameInfo": {"impersonalName": name},
                "note": None,
                "speakingLanguage": {"languageId": 3},
                "type": "IMPERSONAL",
            }
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/linkedPersons", data=payload
        )
        self.check_response_status(response, 200, "Не привязалось связанное лицо")
        delay(0.5, "Нужно время на сохранение данных")
        linked_person_id = response.json()["linkedPersonId"]
        payload_add_funk = {
            "entity": {"code": "customer", "id": client_id},
            "linkedPersonFunctionType": "CONTACT_PERSON",
            "specializationTypes": [{"specializationTypeId": 4}],
        }
        response_add_func = self.post(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/linkedPersonFunctions",
            data=payload_add_funk,
        )
        self.check_response_status(response, 200, "Не привязалась функция связанного лица")
        linked_function_id = response_add_func.json()["linkedPersonFunctionId"]
        wait_that(
            lambda: self.get_linked_person_data(linked_person_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonException,
            message="Связанное лицо не было создано в установленное время",
        )
        wait_that(
            lambda: self.get_linked_person_specialisation(linked_function_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonFunctionException,
            message="Функция связанного лица не была создана в установленное время",
        )
        api_addresses = AddressRequests(self.api_request_auth_context)
        wait_that(
            lambda: api_addresses.get_client_addresses(linked_person_id).status == 200,
            timeout=5,
            sleep_seconds=0.5,
            exception=LinkedPersonPullAddressException,
            message="Не сформирован пул адресов связанного лица",
        )
        delay(1, reason="Даже при наличии нового связного лица через API, на UI возникает ошибка если рано перейти")
        return linked_person_id

    @allure.step(
        "API: Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}' и базовым "
        "адресом регистрации"
    )
    def create_linked_person_with_registration_address(
        self, client_id: int, name: str, map_url: list[None | str] = None
    ) -> int:
        """
        Метод создает обезличенное связанное лицо с адресом регистрации

        Parameters:
        client_id (int): id Клиента.
        name (str): название связанного лица.

        Returns:
        int: id связанного лица.
        """
        linked_person_id = self.create_linked_person(client_id=client_id, name=name)
        api_addresses = AddressRequests(self.api_request_auth_context)
        api_addresses.add_registry_address_linked_person(linked_person_id=linked_person_id, map_url=map_url)
        return linked_person_id

    @allure.step("Найти клиента")
    def search_client(
        self, account_status_ids: list, agreement_status_ids: list, customer_status_ids: list, customer_name: str
    ) -> APIResponse:
        params = {"hierarchyLevel": "account", "limit": "60", "offset": 0}
        payload = {
            "accountStatusIds": account_status_ids,
            "agreementStatusIds": agreement_status_ids,
            "customerName": f"%{customer_name}%",
            "customerStatusIds": customer_status_ids,
        }
        search_data = self.post(
            url=f"{BASE_URL_API}/ps/v1/tailored-rm/integration/searchGeneral", params=params, data=payload
        )
        self.check_response_status(search_data, 200, "Не получен список поиска")
        return search_data

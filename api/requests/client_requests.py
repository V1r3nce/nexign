import allure
from playwright.sync_api import APIRequestContext
from waiting import wait

from api.requests.address_requests import AddressRequests
from common.env_helper import BASE_URL_API
from common.time_helpers import delay


class ClientRequests:
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Получить данные по клиенту '{customer_id}'")
    def get_client_data(self, customer_id: int):
        """
        Получить данные по клиенту.

        Parameters:
        customer_id (int): id Клиента.

        Returns:
        Response: объект ответа API с данными клиента.
        """
        client = self.api_request_auth_context.get(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{customer_id}")
        return client

    @allure.step("Получить данные по связанному лицу '{linked_person_id}'")
    def get_linked_person_data(self, linked_person_id: int):
        """
        Получить данные по связанному лицу.

        Parameters:
        linked_person_id (int): id связанного лица.

        Returns:
        Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.api_request_auth_context.get(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}")
        return linked_person

    @allure.step("Получить данные по специализации связанного лица '{linked_function_id}'")
    def get_linked_person_specialisation(self, linked_function_id: int):
        """
        Получить данные по специализации связанного лица.

        Parameters:
        linked_function_id (int): id функции связанного лица.

        Returns:
        Response: объект ответа API с данными связанного лица.
        """
        linked_person = self.api_request_auth_context.get(
            url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/linkedPersonFunctions/{linked_function_id}")
        return linked_person

    @allure.step("Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}'")
    def create_linked_person(self, client_id: int, name: str):
        """
        Метод создает обезличенное связанное лицо

        Parameters:
        client_id (int): id Клиента.
        name (str): название связанного лица.

        Returns:
        int: id связанного лица.
        """
        payload = {"party": {"nameInfo": {"impersonalName": name}, "note": None,
                             "speakingLanguage": {"languageId": 3}, "type": "IMPERSONAL"}}
        response = (self.api_request_auth_context.
                    post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/customers/{client_id}/linkedPersons",
                         data=payload))
        assert response.status == 200, "Не привязалось связанное лицо"
        delay(1, "Нужно время на сохранение данных")
        linked_person_id = response.json()["linkedPersonId"]
        payload_add_funk = {"entity": {"code": "customer", "id": client_id},
                            "linkedPersonFunctionType": "CONTACT_PERSON",
                            "specializationTypes": [{"specializationTypeId": 4}]}
        response_add_func = (self.api_request_auth_context.
                             post(url=f"{BASE_URL_API}/openapi/v1/customerManagement/linkedPersons/{linked_person_id}/"
                                      f"linkedPersonFunctions",
                                  data=payload_add_funk))
        assert response_add_func.status == 200, "Не привязалась функция связанного лица"
        linked_function_id = response_add_func.json()["linkedPersonFunctionId"]
        wait(
            lambda: self.get_linked_person_data(linked_person_id).status == 200,
            timeout_seconds=5, sleep_seconds=0.5,
            waiting_for="Связанное лицо не было создано в установленное время")
        wait(
            lambda: self.get_linked_person_specialisation(linked_function_id).status == 200,
            timeout_seconds=5, sleep_seconds=0.5,
            waiting_for="Функция связанного лица не была создана в установленное время")
        api_addresses = AddressRequests(self.api_request_auth_context)
        wait(
            lambda: api_addresses.get_client_addresses(linked_person_id).status == 200,
            timeout_seconds=5, sleep_seconds=0.5,
            waiting_for="Не сформирован пул адресов связанного лица")
        delay(1.5, reason="Даже при наличии нового связного лица через API, на UI возникает ошибка если рано перейти")
        return linked_person_id

    @allure.step("Создать 'Обезличенное' связанное лицо для клиента '{client_id}' с названием '{name}' и базовым "
                 "адресом регистрации")
    def create_linked_person_with_registration_address(self, client_id: int, name: str, map_url: [None, str] = None):
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

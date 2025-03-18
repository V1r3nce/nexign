from playwright.sync_api import APIRequestContext

from api.requests.base_requests import BaseRequests


class TableRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.headers = {"Content-Type": "application/json"}

    def get_table_by_reverse_status(self, base_url_api: str) -> tuple[list[str], list[int]]:
        """Запрашивает обновленные данные таблицы и возвращает список id"""

        response = self.post(
            f"{base_url_api}/ps/v1/logicalResources/IPAddresses/search?limit=50&macroRegionIds=0&macroRegionIds=1&offset=0&sort=-statusDate",
            headers=self.headers)

        self.check_response_status(response, 200, "Не выполнен запрос на обновленные данные таблицы.")

        data = response.json()
        id_list = [item["IPAddressId"] for item in data.get("items", [])]
        ip_list = [item["IPAddress"] for item in data.get("items", [])]

        assert id_list is not None, "Список id не получен"
        assert int(id_list[0]) >= 0, "Необходимый id не является числом"

        return ip_list, id_list

    def put_ip_addresses_into_service(self, base_url_api: str, ip_address_id: int) -> None:
        """ВВод IP-адреса в эксплуатацию
        :param ip_address_id: id необходимого IP-адреса
        """

        payload = {
            "IPAddressIds": [ip_address_id],
            "macroRegionId": 0
        }

        response = self.post(url=f"{base_url_api}/ps/v1/logicalResources/private/IPAddresses/inUseBulk",
                             headers=self.headers, data=payload)

        self.check_response_status(response, 200, "Не выполнен запрос на ввод IP-адреса в эксплуатацию.")

import allure
from playwright.sync_api import APIRequestContext

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_RFD


class ReferenceRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Обновить название элемента справочника")
    def update_reference_item_name(self, reference_name: str, item_code: str, ru_name: str, en_name: str) -> None:
        """
        Обновить название элемента справочника
        :param reference_name: Название справочника
        :param item_code: Код элемента справочника
        :param ru_name: Новое имя элемента на русском языке
        :param en_name: Новое имя элемента на английском языке
        """
        payload = {
            "referenceItemCode": item_code,
            "name": {
                "defaultValue": ru_name,
                "localizedStrings": [{"language": "RU", "value": ru_name}, {"language": "EN", "value": en_name}],
                "view": ru_name + "{RU, EN}",
            },
        }

        response = self.put(
            url=f"{BASE_URL_RFD}/OAPI_REFDATA/references/{reference_name}/items/{item_code}",
            data=payload,
        )
        self.check_response_status(
            response, 200, f"Не удалось обновить элемент {item_code} в справочнике {reference_name}"
        )

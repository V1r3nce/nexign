from playwright.sync_api import APIRequestContext, APIResponse

from api.requests.base_requests import BaseRequests


class AttributeRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    def attribute_update_request(
        self, api_request_auth_context: APIRequestContext, base_url_api: str, attribute_name: str, payload: dict
    ) -> APIResponse:
        """Отправка запроса на обновление статуса атрибута
        :param api_request_auth_context: контекст
        :param base_url_api: базовый url с которым работаем.
        :param attribute_name: имя атрибута, который изменяется
        :param payload: body запроса
        :return: response на запрос
        """
        return api_request_auth_context.put(f"{base_url_api}/ps/v1/ats/attributes/{attribute_name}/update", data=payload)

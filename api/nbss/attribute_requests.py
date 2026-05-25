from api.base_requests import BaseRequests
from models.playwright_bridge import GeneralResponse


class AttributeRequests(BaseRequests):
    def attribute_update_request(self, base_url_api: str, attribute_name: str, payload: dict) -> GeneralResponse:
        """Отправка запроса на обновление статуса атрибута
        :param base_url_api: базовый url с которым работаем.
        :param attribute_name: имя атрибута, который изменяется
        :param payload: body запроса
        :return: response на запрос
        """
        return self.put(url=f"{base_url_api}/ps/v1/ats/attributes/{attribute_name}/update", json=payload)

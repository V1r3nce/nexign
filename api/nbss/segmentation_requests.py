import allure

from api.base_requests import BaseRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import delay


class SegmentationRequests(BaseRequests):
    @allure.step("API: Запустить автоматическую сегментацию")
    def auto_segmentation(self, entity_type_code: str, entity_ids: list[str], is_specified_ids: bool = True) -> None:
        """
        Массовая сегментация экземпляров сущностей.

        Args:
            entity_type_code (str): тип сущностей "customer" и т.д.
            entity_ids (list[str]): список идентификаторов сущностей в строковом формате
            is_specified_ids: признак cегментации для указанных экземпляров сущностей
        """
        correlation_id = generate_random_number(36)
        params = {"replyTo": "amqp://?exchange=nx.nsg.entitymanager.exchange&key=1", "correlationId": correlation_id}
        payload = {"entityTypeCode": entity_type_code, "isSpecifiedIds": is_specified_ids, "entityIds": entity_ids}
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/segmentation/entities/runSegmentation/async", params=params, json=payload
        )
        self.check_response_status(response, 202, "Не запущен процесс сегментации")
        delay(1, reason="Ожидание обновления в БД данных по результатам выполнения асинхронного API запроса")

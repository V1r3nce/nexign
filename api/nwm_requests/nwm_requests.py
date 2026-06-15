from datetime import datetime

import allure
import pytest

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API
from models.playwright_bridge import GeneralResponse


class NwmRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()

    @pytest.mark.nwm
    @allure.step("API: Принудительная активация продукта")
    def forced_write_off_request(
        self, product_offering_id: int, subscriber_id: int, min_write_off_date: datetime, max_write_off_date: datetime
    ) -> GeneralResponse:
        payload = {
            "minWriteOffDate": min_write_off_date.date().isoformat(),
            "maxWriteOffDate": max_write_off_date.date().isoformat(),
            "productOffering": {"productOfferingId": product_offering_id},
        }

        response = self.post(
            url=f"{BASE_URL_API}/limited/v1/common/partyRoleManagement/subscribers/{subscriber_id}/forcedWriteOff",
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось активировать продукт")
        return response

import allure

from api.base_requests import BaseRequests
from api.nbss.inquiry_requests.commercial_order_requests import CommercialOrderRequests
from common.enums.user import User
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context
from models.inquiry import InquiryInfo
from models.playwright_bridge import GeneralResponse


class TechnicalOrderRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.commercial_order_requests = CommercialOrderRequests()

        test_context.switch_api_context_to_user(User.ADMIN)

    @allure.step("API: Получение id технического заказа")
    def get_technical_order_id_and_code(self, inquiry: InquiryInfo) -> tuple[int | None, str | None]:
        """
        :return: technical_order_id или None, если такового нет
        """
        commercial_order_info = self.commercial_order_requests.get_commercial_order_info(inquiry)
        if commercial_order_info is not None:
            tech_order_id = commercial_order_info.get("lastTechOrderId")
            code = commercial_order_info.get("stage", {}).get("code")
            if tech_order_id is not None:
                test_context.client.inquiry.technical_order_id = tech_order_id
                return int(tech_order_id), code
            return tech_order_id, code
        return None, None

    def get_technical_order_info(self, technical_order_id: int) -> GeneralResponse:
        payload = {"orderIds": [technical_order_id]}
        response = self.post(f"{BASE_URL_API}/openapi/v2/orders/search", json=payload)
        self.check_response_status(response, 200, "Не получена информация по техническому заказу")
        return response

    def get_technical_order_status(self, technical_order_id: int) -> str | None:
        return self.get_response_content_by_jsonpath(
            "$.items[0].status.code", self.get_technical_order_info(technical_order_id)
        )

    def get_technical_order_error(self, technical_order_id: int) -> str | None:
        return self.get_response_content_by_jsonpath(
            "$.items[0].orderError", self.get_technical_order_info(technical_order_id)
        )

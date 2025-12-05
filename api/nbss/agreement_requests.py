import allure

from api.base_requests import BaseRequests
from api.exceptions import AgreementNotCompletedException
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API


class AgreementRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.client_api = ClientInquiriesRequests()

    @allure.step("API: Получение типов документов требуемых для заявки")
    def get_inquiry_document_type_ids(self, inquiry_id: int) -> list:
        inquiry = self.client_api.get_inquiry_info(inquiry_id).json()
        res = ["8", "8"]
        first_declaration_code = "documentTypeIdAgreementAdd"
        second_declaration_code = first_declaration_code
        if inquiry["topic"]["topicCode"] == "SALE_TOPIC":
            first_declaration_code = "documentTypeIdAgreement"
            second_declaration_code = "documentTypeIdGuarantDoc"
        for custom_property in inquiry["customProperties"]:
            if custom_property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == first_declaration_code:
                res[0] = custom_property["textValue"]
            if custom_property["customPropertyDeclaration"]["customPropertyDeclarationCode"] == second_declaration_code:
                res[1] = custom_property["textValue"]
        return res

    @allure.step("API: Проверка завершения подготовки договора")
    def check_agreement_complete(self, inquiry_id: int) -> None:
        payload = {
            "documentTypeIds": self.get_inquiry_document_type_ids(inquiry_id),
            "recipients": [{"recipientType": "inquiry", "recipientId": inquiry_id}],
        }
        status_timeout = 60
        wait_that(
            lambda: (self.post(url=f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", data=payload)).status
            == 200
            and (self.post(url=f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", data=payload)).json()["items"][
                0
            ]["documentStatus"]["code"]
            == "COMPLETED",
            timeout=status_timeout,
            sleep_seconds=1.5,
            exception=AgreementNotCompletedException,
            message=f"Подготовка договора не завершилась за {status_timeout} сек.",
        )

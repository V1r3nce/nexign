import allure
from playwright.async_api import APIRequestContext

from api.requests.base_requests import BaseRequests
from api.requests.client_requests import ClientRequests
from common.helpers.env_helper import BASE_URL_API


class AgreementRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.client_api = ClientRequests(api_request_auth_context)

    @allure.step("API: Получение типов документов требуемых для заявки")
    def get_inquiry_document_type_ids(self, inquiry_id: int) -> list:
        inquiry = self.client_api.get_inquiry(inquiry_id).json()
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
    def is_completed(self, inquiry_id: int) -> bool:
        payload = {
            "documentTypeIds": self.get_inquiry_document_type_ids(inquiry_id),
            "recipients": [{"recipientType": "inquiry", "recipientId": inquiry_id}],
        }
        agreements = self.post(url=f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", data=payload)
        self.check_response_status(agreements, 200, "Не удалось получить список соглашений")
        return agreements.json()["items"][0]["documentStatus"]["code"] == "COMPLETED"

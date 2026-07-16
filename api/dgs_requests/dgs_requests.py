from datetime import datetime

import allure

from api.base_requests import BaseRequests
from api.exceptions import DocumentGenerationTimeoutException
from common.enums.dgs import DocumentStatuses, DocumentTypes, RecipientTypes
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_API
from models.document import Document


class DGSRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()

    @allure.step("API: Поиск документов")
    def document_search(
        self,
        recipient_id: int,
        document_type_ids: list | None = None,
        recipient_type: RecipientTypes = RecipientTypes.inquiry,
    ) -> list[Document]:
        if document_type_ids is None:
            document_type_ids = [
                DocumentTypes.act.id,
                DocumentTypes.agreement.id,
                DocumentTypes.guarantee_document.id,
                DocumentTypes.additional_agreement.id,
            ]
        params = {"limit": 20, "offset": 0}
        payload = {
            "recipients": [{"recipientId": recipient_id, "recipientType": recipient_type}],
            "document_type_ids": document_type_ids,
        }
        response = self.post(f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", params=params, json=payload)
        self.check_response_status(response, 200, "Ошибка поиска документов")
        result = []
        for doc in response.json().get("items", []):
            result.append(Document.model_validate(doc))
        return result

    @allure.step("API: Поиск последнего документа")
    def document_search_by_type(
        self,
        recipient_id: int,
        document_type_ids: list | None = None,
        recipient_type: RecipientTypes = RecipientTypes.inquiry,
        document_type: DocumentTypes = DocumentTypes.agreement,
    ) -> Document | None:
        if document_type_ids is None:
            document_type_ids = [
                DocumentTypes.act.id,
                DocumentTypes.agreement.id,
                DocumentTypes.guarantee_document.id,
                DocumentTypes.additional_agreement.id,
            ]
        for document in self.document_search(
            recipient_id=recipient_id, document_type_ids=document_type_ids, recipient_type=recipient_type
        ):
            if document.document_type.code == document_type:
                return document
        return None

    @allure.step("API: Согласование документа")
    def approve_document(self, document: Document) -> None:
        document.approve_date = datetime.now().isoformat()
        payload = {"document": document.model_dump_json()}
        response = self.post(f"{BASE_URL_API}/openapi/v1/reports/digital/files/{document.file_id}/approve", json=payload)
        self.check_response_status(response, 200, "Ошибка согласования документа")

    @allure.step("API: Ожидание формирования документа")
    def wait_document_generation(
        self, recipient_id: int, document_type: DocumentTypes = DocumentTypes.agreement
    ) -> Document:
        call_result: Document | None = None

        def search_call() -> Document | None:
            nonlocal call_result
            call_result = self.document_search_by_type(recipient_id=recipient_id, document_type=document_type)
            return call_result

        wait_that(
            lambda: search_call() is not None and call_result.document_status.code == DocumentStatuses.completed,
            timeout=60,
            sleep_seconds=2.5,
            exception=DocumentGenerationTimeoutException,
            message="Договор не был успешно сформирован",
        )

        return call_result  # type: ignore

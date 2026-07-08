from __future__ import annotations

import allure

from api.base_requests import BaseRequests
from api.exceptions import AgreementNotCompletedException
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.checker import assert_that, wait_that
from common.helpers.env_helper import BASE_URL_API
from models.client import BaseClient
from models.context import test_context


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

        def _agreement_ready() -> bool:
            response = self.post(url=f"{BASE_URL_API}/openapi/v1/reports/digital/files/search", json=payload)
            if response.status_code != 200:
                return False
            items = response.json().get("items", [])
            if not items:
                return False
            return items[0].get("documentStatus", {}).get("code", "") == "COMPLETED"

        wait_that(
            _agreement_ready,
            timeout=status_timeout,
            sleep_seconds=1.5,
            exception=AgreementNotCompletedException,
            message=f"Подготовка договора не завершилась за {status_timeout} сек.",
        )

    @allure.step("API: Подписать договор")
    def sign_agreement(
        self,
        agreement_id: int,
        agreement_category_id: int = 1,
        status_id: int = 7,
        agent_signer_id: int | None = None,
        client: BaseClient | None = None,
    ) -> dict:
        """
        Подписывает договор через integration-service.

        :param agreement_id: идентификатор договора.
        :param agreement_category_id: идентификатор категории договора.
        :param status_id: целевой статус договора после подписания.
        :param agent_signer_id: идентификатор подписанта-агента; если не задан — из ``client.inquiry.linked_person_id``.
        :param client: клиент-владелец договора; если не задан — используется ``test_context.client``.
        :return: тело ответа API после успешного подписания (dict).
        """
        _client = client if client is not None else test_context.client
        assert_that(lambda: _client is not None, lambda: "Не задан client и test_context.client пустой")
        assert_that(lambda: _client.user_id is not None, lambda: "Не задан user_id клиента для подписания договора")

        agreement_number = _client.get_agreement(agreement_id=agreement_id).number

        if agent_signer_id is None:
            agent_signer_id = getattr(_client.inquiry, "linked_person_id", 0)
        assert_that(
            lambda: agent_signer_id != 0,
            lambda: "linked_person_id (agent_signer_id) равен 0, сначала создай linkedPerson для клиента",
        )

        signing_user = {
            "id": agent_signer_id,
            "firstName": _client.operator_first_name,
            "surname": _client.operator_surname,
        }

        payload = {
            "entityTypeCode": "AGREEMENT",
            "extEntityId": agreement_id,
            "agreementId": agreement_id,
            "agreementNumber": agreement_number,
            "agreementCategoryId": agreement_category_id,
            "signingDate": _client.date_for_api,
            "bankDetailsId": _client.bank_id,
            "signingUser": signing_user,
            "agentSignerId": agent_signer_id,
            "customerId": _client.user_id,
            "statusId": status_id,
        }

        response = self.post(
            url=f"{BASE_URL_API}/ps/v1/integration-service/agreements/{agreement_id}/sign",
            json=payload,
        )
        self.check_response_status(
            response,
            200,
            "Не удалось подписать договор через integration-service",
        )
        return response.json()

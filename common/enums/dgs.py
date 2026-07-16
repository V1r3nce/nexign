from enum import StrEnum

from common.enums.ats import CustomEnum


class RecipientTypes(StrEnum):
    inquiry = "inquiry"
    account = "account"


class DocumentTypes(CustomEnum):
    act = ("Act", 1)
    agreement = ("Agreement", 3)
    additional_agreement = ("AdditionalAgreement", 8)
    guarantee_document = ("GuaranteeDocument", 9)


class DocumentStatuses(StrEnum):
    completed = "COMPLETED"

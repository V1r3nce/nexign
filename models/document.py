from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class LangValue(BaseModel):
    lang: str
    value: str


class DeliveryType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    delivery_type_id: int
    name: list[LangValue]


class DocumentStatus(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    document_status_id: int
    name: list[LangValue]


class DocumentType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    document_type_id: int
    name: list[LangValue]


class FileOrigin(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    file_origin_id: int
    name: list[LangValue]


class RecipientType(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    code: str
    recipient_type_id: int
    name: list[LangValue]


class Document(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    approve_date: str | None
    create_user: str
    date_processed: str | None
    delivery_type: DeliveryType
    document_status: DocumentStatus
    document_type: DocumentType
    file_id: str
    file_name: str
    file_origin: FileOrigin
    file_type: list[LangValue]
    recipient_id: int
    recipient_type: RecipientType

from dataclasses import dataclass
from typing import Optional


@dataclass
class B2BProducts:
    internet: int = 500001
    mobile: int = 500017


@dataclass
class B2CProducts:
    internet: int = 500004
    mobile: int = 500012


def get_default_offering_id(product_category: str) -> int | None:
    """Возвращает ID продукта по умолчанию для указанной категории в зависимости от типа клиента.
    :param product_category: Категория продукта
    :return: ID продукта по умолчанию"""
    from models.context import test_context

    if test_context.client:
        if test_context.client.category == "b2c":
            return getattr(B2CProducts, product_category)
        if test_context.client.category == "b2b":
            return getattr(B2BProducts, product_category)
    return None


@dataclass
class ProductInfo:
    """Данные о продукте"""

    category: str = "mobile"
    agreement_id: Optional[int] = None
    account_id: Optional[int] = None
    subs_id: Optional[int] = None
    product_name: Optional[str] = None
    phone_number: Optional[str] = None
    internet_number: Optional[str] = None
    one_time_payment: float = 0
    subscription_fee: float = 0
    total_amount: float = 0
    product_id: Optional[int] = None
    product_offering_id: Optional[int] = None

    def __init__(
        self,
        product_category: str | None = None,
        product_offering_id: int | None = None,
        agreement_id: int | None = None,
        account_id: int | None = None,
    ) -> None:
        self.category = product_category or self.category
        self.agreement_id = agreement_id or self.agreement_id
        self.account_id = account_id or self.account_id
        self.product_offering_id = product_offering_id

    def __getattribute__(self, name: str) -> object:
        if name == "product_offering_id":
            product_offering_id = super().__getattribute__("product_offering_id")
            if product_offering_id is None:
                return get_default_offering_id(self.category)
        return super().__getattribute__(name)

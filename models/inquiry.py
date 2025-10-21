from dataclasses import dataclass
from typing import List, Optional

from common.helpers.checker import check_that
from common.helpers.data_generator import get_current_datetime_string

default_offering_ids = {"internet": 500004, "mobile": 500012}


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
    one_time_payment: Optional[float] = None
    subscription_fee: Optional[float] = None
    total_amount: Optional[float] = None
    product_id: Optional[int] = None
    product_offering_id: int = 500012

    def __init__(
        self,
        product_category: str | None = None,
        product_offering_id: int | None = None,
        agreement_id: int | None = None,
        account_id: int | None = None,
    ) -> None:
        self.category = product_category or self.category
        self.product_offering_id = (
            default_offering_ids[product_category]
            if product_category and not product_offering_id
            else product_offering_id or self.product_offering_id
        )
        self.agreement_id = agreement_id or self.agreement_id
        self.account_id = account_id or self.account_id


@dataclass
class InquiryInfo:
    """Данные о заявке. Содержит данные о продукте и заявке"""

    product: ProductInfo | List[ProductInfo]
    commercial_order: int
    commercial_order_number: int
    id: int
    product_id: list[int]
    linked_person_id: int
    date: str

    def __init__(
        self,
        product_category: str | None = None,
        product_offering_id: int | None = None,
        agreement_id: int | None = None,
        account_id: int | None = None,
    ) -> None:
        self.product = ProductInfo(product_category, product_offering_id, agreement_id, account_id)
        self.commercial_order = 0
        self.commercial_order_number = 0
        self.id = 0
        self.product_id = [0]
        self.linked_person_id: int | None = 0
        self.date = get_current_datetime_string().replace(" ", "-").replace(".", "/")


def prepare_inquiry_for_product_sale(category: str, product_offering_id: int) -> InquiryInfo:
    """Вспомогательная функция, которая отдает заявку с продуктом по указанной категории и id продукта.
    :param category: Категория
    :param product_offering_id: id продукта
    :return: Заявка."""
    inquiry = InquiryInfo()
    inquiry.product.category = category
    inquiry.product.product_offering_id = product_offering_id
    return inquiry


def prepare_inquiry_list_for_product_sale(
    category_list: List[str], product_offering_id_list: List[int]
) -> List[InquiryInfo]:
    """Вспомогательная функция, которая отдает список заявок с продуктами по указанным категориям и id продукта. Списки должны быть одинаковой длинны.
    :param category_list: Список категорий
    :param product_offering_id_list: Список id продуктов
    :return: Список заявок."""
    check_that(
        lambda: len(category_list) == len(product_offering_id_list),
        ValueError,
        "Количество категорий и продуктов не совпадает",
    )
    inquiries = [
        prepare_inquiry_for_product_sale(category, offering_id)
        for category, offering_id in zip(category_list, product_offering_id_list)
    ]
    return inquiries

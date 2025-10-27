from dataclasses import dataclass, field
from typing import List

from common.helpers.checker import check_that
from common.helpers.data_generator import get_current_datetime_string
from models.product import ProductInfo


@dataclass
class InquiryInfo:
    """Данные о заявке. Содержит данные о продукте и заявке
    product - это текущий продукт (поинтер), с которым работает тест. По умолчанию это первый элемент product_list.
    product_list - список продуктов. Для работы с одним из продуктов, переключается поинтер product на нужного из списка.
    """

    product: ProductInfo | None = field(default_factory=lambda: None)
    product_list: List[ProductInfo] | None = field(default_factory=lambda: [])
    commercial_order: int = field(default_factory=lambda: 0)
    commercial_order_number: int = field(default_factory=lambda: 0)
    id: int = field(default_factory=lambda: 0)
    product_id: list[int] = field(default_factory=lambda: [0])
    linked_person_id: int = field(default_factory=lambda: 0)
    date: str = field(default_factory=lambda: get_current_datetime_string().replace(" ", "-").replace(".", "/"))

    def __getattribute__(self, name: str) -> ProductInfo | object:
        """По умолчанию product - первый элемент списка product_list."""
        if name == "product":
            product = super().__getattribute__("product")
            product_list = super().__getattribute__("product_list")
            if product is None and product_list:
                return product_list[0]
        return super().__getattribute__(name)


def prepare_inquiries(
    category: str | List[str], product_offering_id: int | List[int] = None, as_list: bool = True
) -> InquiryInfo | List[InquiryInfo]:
    """Вспомогательная функция, которая отдает одну или несколько заявок по указанным категория и id продукта.
    Example:
            self.client_api.product_sale(self.client, prepare_inquiries("internet")) - продажа одной заявки с одним продуктом.
            self.client_api.product_sale(self.client, prepare_inquiries(["mobile", "mobile", "internet"])) - продажа 3х заявок с одним продуктом в каждой.
            self.client_api.product_sale(self.client, prepare_inquiries(["mobile", "mobile", "internet"], as_list=False)) - продажа одной заявки с 3мя продуктами.

    :param category: Категория или список категорий
    :param product_offering_id: Id продукта или список id продуктов. По умолчанию берется дефолтный id продукта из ProductInfo.
    :param as_list: Если True — возвращает список заявок, в каждой по одному продукту. Если False — одну заявку с несколькими продуктами.
    :return: Заявка или список заявок."""

    category = [category] if isinstance(category, str) else category
    product_offering_id = [product_offering_id] if isinstance(product_offering_id, int) else product_offering_id

    if category and not product_offering_id:
        product_offering_id = [None] * len(category)  # type: ignore
    else:
        check_that(
            lambda: len(category) == len(product_offering_id),
            ValueError,
            "Список категорий и список id продуктов должны быть одинаковой длинны.",
        )

    if as_list:
        inquiry_list = []
        for category, product_id in zip(category, product_offering_id):
            inquiry = InquiryInfo()
            product = ProductInfo(product_category=category, product_offering_id=product_id)
            inquiry.product_list.append(product)
            inquiry_list.append(inquiry)
        return inquiry_list
    else:
        inquiry = InquiryInfo()
        for category, product_offering_id in zip(category, product_offering_id):
            product = ProductInfo(product_category=category, product_offering_id=product_offering_id)
            inquiry.product_list.append(product)
        return inquiry

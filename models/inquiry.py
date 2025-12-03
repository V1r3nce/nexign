from dataclasses import dataclass, field
from typing import Dict, List, Optional

from common.helpers.checker import check_that
from common.helpers.data_generator import get_current_datetime_string
from models.product import AdditionalProduct, MainProduct


@dataclass
class InquiryInfo:
    """Данные о заявке. Содержит данные о продукте и заявке
    Attributes:
        product: это текущий продукт (поинтер), с которым работает тест. По умолчанию это первый элемент product_list.
        product_list: список продуктов. Для работы с одним из продуктов, переключается поинтер product на нужного из списка.
        available_additional_products_by_main_product: словарь из id основных продуктов, содержащий доступные к выбору дополнительные продукты.
    """

    agreement_id: int = field(default_factory=lambda: None)
    agreement_number: int = field(default_factory=lambda: None)
    product: MainProduct | None = field(default_factory=lambda: None)
    product_list: List[MainProduct] | None = field(default_factory=lambda: [])
    commercial_order: int | None = field(default_factory=lambda: 0)
    commercial_order_number: int = field(default_factory=lambda: 0)
    id: int = field(default_factory=lambda: 0)
    product_id: list[int] = field(default_factory=lambda: [0])
    linked_person_id: int = field(default_factory=lambda: 0)
    date: str = field(default_factory=lambda: get_current_datetime_string().replace(" ", "-").replace(".", "/"))
    region_id: int = field(default_factory=lambda: 100004)
    address_id: int = field(default_factory=lambda: None)
    available_additional_products_by_main_product: Optional[Dict] = field(default_factory=lambda: {})

    def __getattribute__(self, name: str) -> MainProduct | object:
        """По умолчанию product - первый элемент списка product_list."""
        if name == "product":
            product = super().__getattribute__("product")
            product_list = super().__getattribute__("product_list")
            if product is None and product_list:
                return product_list[0]
        return super().__getattribute__(name)


def prepare_inquiries(
    category: str | List[str],
    product_offering_id: int | List[int] = None,
    additional_product: str | List[str] | List[List[str] | str | None] = None,
    as_list: bool = True,
) -> InquiryInfo | List[InquiryInfo]:
    """Вспомогательная функция, которая отдает одну или несколько заявок по указанным категория и id продукта.

    :param category: Категория или список категорий
    :param product_offering_id: Id продукта или список id продуктов. По умолчанию берется дефолтный id продукта из ProductInfo.
    :param additional_product: Имя дополнительного продукта (если основной продукт один) или список имен дополнительных продуктов (если для каждого основного продукта,
    по одному дополнительному) или список из списков дополнительных продуктов (если для каждого основного продукта, по несколько дополнительных).
    :param as_list: Если True — возвращает список заявок, в каждой по одному продукту. Если False — одну заявку с несколькими продуктами.
    :return: Заявка или список заявок.

    Example:
            prepare_inquiries("internet") - продажа одной заявки с одним продуктом.
            prepare_inquiries("internet", additional_product="+2 ГБ") - продажа одной заявки с одним продуктом. У продукта доп. продукт.
            prepare_inquiries("internet", additional_product=[["+2 ГБ", "+100 минут"]]) - продажа одной заявки с одним продуктом. У продукта два доп. продукта.
            prepare_inquiries(["mobile", "mobile", "internet"]) - продажа 3х заявок с одним продуктом в каждой.
            prepare_inquiries(["mobile", "mobile", "internet"], product_offering_id=[500017, 500017, 500001]) - продажа 3х заявок с одним продуктом в каждой. Кастомные id продуктов.
            prepare_inquiries(["mobile", "mobile", "internet"], as_list=False) - продажа одной заявки с 3мя продуктами.
            prepare_inquiries(["mobile", "mobile", "internet"], additional_product=[None, "+2 ГБ", "+2 ГБ"], as_list=False) - продажа одной заявки с 3мя продуктами. У двух из продуктов есть доп. продукт.
            prepare_inquiries(["mobile", "mobile", "internet"], additional_product=[None, "+2 ГБ", ["+2 ГБ", "+2 ГБ"]], as_list=False) - продажа одной заявки с 3мя продуктами. У одного продукта 1 доп. продукт, у другого 2 доп. продукта.
    """
    category = [category] if isinstance(category, str) else category
    product_offering_id = [product_offering_id] if isinstance(product_offering_id, int) else product_offering_id
    additional_product = [additional_product] if isinstance(additional_product, str) else additional_product

    if category and not product_offering_id:
        product_offering_id = [None] * len(category)  # type: ignore
    else:
        check_that(
            lambda: len(category) == len(product_offering_id),
            ValueError,
            "Список категорий и список id продуктов должны быть одинаковой длинны.",
        )

    if not additional_product:
        additional_product = [None] * len(category)  # type: ignore
    else:
        check_that(
            lambda: len(category) == len(additional_product),
            ValueError,
            "Список категорий и список дополнительных продуктов должны быть одинаковой длинны.",
        )

    if as_list:
        inquiry_list = []
        for category, product_id, add_product_name_list in zip(category, product_offering_id, additional_product):
            inquiry = InquiryInfo()
            product = MainProduct()
            product.category = category
            product.product_offering_id = product_offering_id

            add_product_name_list = (
                add_product_name_list if isinstance(add_product_name_list, list) else [add_product_name_list]  # type: ignore
            )
            additional_products = [
                AdditionalProduct(product_name=add_product_name)
                for add_product_name in add_product_name_list
                if add_product_name is not None
            ]

            for additional_product in additional_products:
                product.additional_product_list.append(additional_product)

            inquiry.product_list.append(product)
            inquiry_list.append(inquiry)
        return inquiry_list
    else:
        inquiry = InquiryInfo()
        for category, product_id, add_product_name_list in zip(category, product_offering_id, additional_product):
            product = MainProduct()
            product.category = category
            product.product_offering_id = product_offering_id

            add_product_name_list = (
                add_product_name_list if isinstance(add_product_name_list, list) else [add_product_name_list]  # type: ignore
            )
            additional_products = [
                AdditionalProduct(product_name=add_product_name)
                for add_product_name in add_product_name_list
                if add_product_name is not None
            ]

            for additional_product in additional_products:
                product.additional_product_list.append(additional_product)

            inquiry.product_list.append(product)
        return inquiry

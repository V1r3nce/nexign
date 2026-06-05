from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

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

    type: str = field(default_factory=lambda: "sale")
    agreement_id: int = field(default_factory=lambda: None)
    agreement_number: int = field(default_factory=lambda: None)
    product: MainProduct | None = field(default_factory=lambda: None)
    product_list: List[MainProduct] | None = field(default_factory=lambda: [])
    commercial_order: int | None = field(default_factory=lambda: 0)
    commercial_order_number: int = field(default_factory=lambda: 0)
    technical_order_id: int | None = field(default_factory=lambda: None)
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
    activation_date: datetime | List[datetime] = None,
    as_list: bool = True,
    individualized_subs_fee: int | List[int] | None = None,
    additional_individualized_subs_fee: List[List[int] | None] = None,
) -> InquiryInfo | List[InquiryInfo]:
    """Вспомогательная функция, которая отдает одну или несколько заявок по указанным категория и id продукта.

    :param category: Категория или список категорий
    :param product_offering_id: Id продукта или список id продуктов. По умолчанию берется дефолтный id продукта из ProductInfo.
    :param additional_product: Имя дополнительного продукта (если основной продукт один) или список имен дополнительных продуктов (если для каждого основного продукта,
    по одному дополнительному) или список из списков дополнительных продуктов (если для каждого основного продукта, по несколько дополнительных).
    :param as_list: Если True — возвращает список заявок, в каждой по одному продукту. Если False — одну заявку с несколькими продуктами.
    :individualized_subs_fee: Стоимость или список стоимостей продуктов в заявке которые необходимо индивидуализировать
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
            prepare_inquiries("internet", individualized_subs_fee=30000) - - продажа одной заявки с одним продуктом и индивидуализацией цены для него
            prepare_inquiries(["mobile", "mobile", "internet"], individualized_subs_fee=[None, 30000, None]) - продажа 3х заявок с одним продуктом в каждой и индивидуализация второго продукта.
            prepare_inquiries(["mobile", "mobile", "internet"], individualized_subs_fee=[30000, 30000, None], as_list=False) - продажа 3х заявок с одним продуктом в каждой и индивидуализация первого и второго продукта.
            prepare_inquiries(["mobile", "mobile", "internet"], additional_product=[None, "+2 ГБ", "+2 ГБ"], additional_individualized_subs_fee=[None, 30000, None]) - продажа 3х заявок с одним продуктом в каждой и индивидуализация второго продукта.
            prepare_inquiries(["mobile", "mobile", "internet"], additional_product=[None, "+2 ГБ", "+2 ГБ"], additional_individualized_subs_fee=[30000, 30000, None], as_list=False) - продажа 3х заявок с одним продуктом в каждой и индивидуализация первого и второго продукта.
            prepare_inquiries(["mobile", "mobile", "internet"], additional_product=[None, "+2 ГБ", ["+2 ГБ", "+2 ГБ"]], additional_individualized_subs_fee=[None, None, [30000, 30000]], as_list=False) - продажа одной заявки с 2мя индивидуализациями цени. Индивидуализация для 2х доп продуктов у 3 продукта.
            prepare_inquiries("internet", activation_date="2026-01-01") - продажа одного продукта с указанием даты активации
            prepare_inquiries("internet", "mobile"], activation_date=["2026-01-01", "2026-01-01"], as_list=False) - продажа одной заявки с двумя продуктами с указанием даты активации у каждого
    """
    category = [category] if isinstance(category, str) else category
    product_offering_id = [product_offering_id] if isinstance(product_offering_id, int) else product_offering_id
    additional_product = [additional_product] if isinstance(additional_product, str) else additional_product
    individualized_subs_fee = (
        [individualized_subs_fee] if isinstance(individualized_subs_fee, int) else individualized_subs_fee
    )
    additional_individualized_subs_fee = (
        [additional_individualized_subs_fee]
        if isinstance(additional_individualized_subs_fee, int)  # type: ignore
        else additional_individualized_subs_fee
    )
    activation_date = [activation_date] if isinstance(activation_date, datetime) else activation_date

    def generate_none_list_for_empty_entity(entity: Any, entity_name: str) -> list:
        if not entity:
            entity = [None] * len(category)
        else:
            check_that(
                lambda: len(category) == len(entity),
                ValueError,
                f"Список категорий и список '{entity_name}' должны быть одинаковой длинны.",
            )
        return entity

    if category:
        product_offering_id = generate_none_list_for_empty_entity(product_offering_id, "id продуктов")
    additional_product = generate_none_list_for_empty_entity(additional_product, "дополнительные продукты")
    activation_date = generate_none_list_for_empty_entity(activation_date, "даты активации")

    if not additional_individualized_subs_fee:
        additional_individualized_subs_fee = [None] * len(category)
    else:
        check_that(
            lambda: len(category) == len(additional_individualized_subs_fee),
            ValueError,
            "Список категорий и список продуктов для индивидуализации должны быть одинаковой длинны.",
        )

    if not individualized_subs_fee:
        individualized_subs_fee = [None] * len(category)  # type: ignore
    else:
        check_that(
            lambda: len(category) == len(individualized_subs_fee),
            ValueError,
            "Список категорий и список продуктов для индивидуализации должны быть одинаковой длинны.",
        )

    if as_list:
        inquiry_list = []
        for category, po_id, add_product_name_list, subs_fee, add_subs_fee_list, activation_date in zip(
            category,
            product_offering_id,
            additional_product,
            individualized_subs_fee,
            additional_individualized_subs_fee,
            activation_date,
        ):
            inquiry = InquiryInfo()
            product = MainProduct()
            product.category = category
            product.product_offering_id = po_id
            product.individualized_subs_fee = subs_fee
            product.activation_date = activation_date

            add_product_name_list = (
                add_product_name_list if isinstance(add_product_name_list, list) else [add_product_name_list]
            )
            add_subs_fee_list = add_subs_fee_list if isinstance(add_subs_fee_list, list) else [add_subs_fee_list]
            additional_products = [
                AdditionalProduct(product_name=add_product_name, individualized_subs_fee=add_subs_fee)
                for add_product_name, add_subs_fee in zip(add_product_name_list, add_subs_fee_list)
                if add_product_name is not None
            ]

            for additional_product in additional_products:
                product.additional_product_list.append(additional_product)

            inquiry.product_list.append(product)
            inquiry_list.append(inquiry)
        return inquiry_list
    else:
        inquiry = InquiryInfo()
        for category, po_id, add_product_name_list, subs_fee, add_subs_fee_list, activation_date in zip(
            category,
            product_offering_id,
            additional_product,
            individualized_subs_fee,
            additional_individualized_subs_fee,
            activation_date,
        ):
            product = MainProduct()
            product.category = category
            product.product_offering_id = po_id
            product.individualized_subs_fee = subs_fee
            product.activation_date = activation_date

            add_product_name_list = (
                add_product_name_list if isinstance(add_product_name_list, list) else [add_product_name_list]
            )
            add_subs_fee_list = add_subs_fee_list if isinstance(add_subs_fee_list, list) else [add_subs_fee_list]
            additional_products = [
                AdditionalProduct(product_name=add_product_name, individualized_subs_fee=add_subs_fee)
                for add_product_name, add_subs_fee in zip(add_product_name_list, add_subs_fee_list)
                if add_product_name is not None
            ]

            for additional_product in additional_products:
                product.additional_product_list.append(additional_product)

            inquiry.product_list.append(product)
        return inquiry

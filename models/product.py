from dataclasses import dataclass
from typing import Optional

from api.lis_requests.equipment import EquipmentRequests


@dataclass
class B2BProducts:
    internet: int = 500001
    mobile: int = 500017
    satellite_sale: int = 500055
    satellite_rent: int = 500068


@dataclass
class B2CProducts:
    internet: int = 500004
    mobile: int = 500012


@dataclass
class DefaultStandardId:
    mobile: int = 1
    satellite_sale: int = 100001
    satellite_rent: int = 100001


@dataclass
class DefaultEquipmentId:
    mobile: int = 100001
    satellite_sale: int = 100003
    satellite_rent: int = 100003


def get_default_offering_id(product_category: str) -> int | None:
    """Возвращает ID продукта по умолчанию для указанной категории в зависимости от типа клиента.
    :param product_category: Категория продукта
    :return: ID продукта по умолчанию"""
    from models.context import test_context

    if test_context.client:
        if hasattr(test_context.client, "category"):
            if test_context.client.category == "b2c":
                return getattr(B2CProducts, product_category)
            if test_context.client.category == "b2b":
                return getattr(B2BProducts, product_category)
    return None


def get_default_equipment_id(product_category: str) -> int | None:
    """Возвращает ID оборудования по умолчанию для указанной категории
    :param product_category: Категория продукта
    :return: ID продукта по умолчанию"""
    from models.context import test_context

    if test_context.client:
        if product_category != "internet":
            return getattr(DefaultEquipmentId, product_category)
    return None


def get_default_standard_id(product_category: str) -> int | None:
    """Возвращает ID стандарта по умолчанию для указанной категории.
    :param product_category: Категория продукта
    :return: ID продукта по умолчанию"""
    from models.context import test_context

    if test_context.client:
        if product_category != "internet":
            return getattr(DefaultStandardId, product_category)
    return None


@dataclass
class ProductInfo:
    """Данные о продукте
    Attributes:
        category (str): категория продукта.
        account_id (int): id лицевого счета на который подключается продукт.
        account_number (int): номер лицевого счета на который подключается продукт.
        subs_id (int): id абонента.
        product_name (str): название подключаемого продукта.
        phone_number (str): msisdn/номер телефона.
        internet_number (str): номер интернета.
        serial_number (str): серийный номер оборудования.
        one_time_payment (float): разовый плтаеж за продукт.
        subscription_fee (float): абонентская плата за продукт.
        total_amount (float): общая сумма за продукт.
        product_id (str): id подключаемого продукта(инстанс в КЗ).
        product_offering_id (int): id подключаемого продуктового предложения.
        sim_order_resource_id (int): id sim ресурса КЗ.
        number_order_resource_id (int): id msisdn ресурса КЗ.
        equipment_order_resource_id (int): id ресурса оборудование в КЗ.
        switch_name (str): название коммутатора.
        switch_id (int): id коммутатора.
        standard_id (int): id стандарта связи.
        equipment_type_id (int): id типа оборудования
        partner_point_id (int): id точки партнера
    """

    category: str = "mobile"
    account_id: Optional[int] = None
    account_number: Optional[int] = None
    subs_id: Optional[int] = None
    product_name: Optional[str] = None
    phone_number: Optional[str] = None
    internet_number: Optional[str] = None
    serial_number: Optional[str] = None
    one_time_payment: float = 0
    subscription_fee: float = 0
    total_amount: float = 0
    product_id: Optional[int] = None
    product_offering_id: Optional[int] = None
    sim_order_resource_id: Optional[int] = None
    number_order_resource_id: Optional[int] = None
    equipment_order_resource_id: Optional[int] = None
    switch_name: Optional[str] = None
    switch_id: Optional[int] = None
    standard_id: Optional[int] = None
    equipment_type_id: int = 1
    partner_point_id: int = 100001

    def __init__(
        self,
        product_category: str | None = None,
        product_offering_id: int | None = None,
        product_name: str | None = None,
    ) -> None:
        self.category = product_category or self.category
        self.product_name = product_name or self.product_name
        self.product_offering_id = product_offering_id

    def __getattribute__(self, name: str) -> object:
        match name:
            case "product_offering_id":
                product_offering_id = super().__getattribute__("product_offering_id")
                if product_offering_id is None:
                    if self.product_name == "Спутник L Продажа":
                        return get_default_offering_id("satellite_sale")
                    if self.product_name == "Спутник L Аренда":
                        return get_default_offering_id("satellite_rent")
                    return get_default_offering_id(self.category)
            case "switch_name":
                return self.get_switch_name()
            case "switch_id":
                return get_default_equipment_id(product_category=self.category)
            case "standard_id":
                return get_default_standard_id(product_category=self.category)
        return super().__getattribute__(name)

    def get_switch_name(self) -> str | None:
        """
        Получение названия коммутатора для продукта
        :return: название коммутатора
        """
        from models.context import test_context

        api = test_context.api_context
        if not api:
            return None
        lis_api = EquipmentRequests(api)
        equipment_id = get_default_equipment_id(product_category=self.category)
        if not api:
            return None
        standard_list = [get_default_standard_id(product_category=self.category)]
        type_list = [self.equipment_type_id]
        try:
            return lis_api.get_equipment(standard_id=standard_list, equipment_type_id=type_list)[equipment_id]
        except AssertionError:
            return None

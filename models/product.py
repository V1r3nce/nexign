import dataclasses
from dataclasses import dataclass, field, is_dataclass
from typing import Any, List, Optional

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


product_names_map = {
    500055: "Спутник L Продажа",
    500068: "Спутник L Аренда",
    500001: "Интернет в офис",
    500017: "Гибкий бизнес",
    500004: "Скоростной Уют",
    500012: "На связи",
}


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


@dataclass
class Resources:
    """
    Attributes:
        sim_card_id (int): id sim ресурса КЗ.
        phone_number (int): id msisdn ресурса КЗ.
        equipment (int): id ресурса оборудование в КЗ.
        city_phone_number (int): id ресурса городского номера в КЗ.
        apn (int): id ресурса VPN в КЗ.
    """

    sim_card_id: Optional[int] = None
    phone_number: Optional[int] = None
    equipment: Optional[int] = None
    city_phone_number: Optional[int] = None
    apn: Optional[int] = None


def get_filled_attributes(obj: Any) -> list:
    """
    Метод для получения заполненных ресурсов у продукта
    :return: список имен атрибутов
    """
    if not is_dataclass(obj):
        raise TypeError
    res = []
    for class_field in dataclasses.fields(obj):
        if getattr(obj, class_field.name) is not None:
            res.append(class_field.name)
    return res


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
class ProductBase:
    """Данные о продукте
    Attributes:
        category (str): категория продукта.
        product_name (str): название подключаемого продукта.
        one_time_payment (float): разовый плтаеж за продукт.
        subscription_fee (float): абонентская плата за продукт.
        total_amount (float): общая сумма за продукт.
        product_id (str): id подключаемого продукта(инстанс в КЗ).
        product_offering_id (int): id подключаемого продуктового предложения.
        phone_number (str): msisdn/номер телефона.
        internet_number (str): номер интернета.
        serial_number (str): серийный номер оборудования.
    """

    category: str = "mobile"
    product_name: Optional[str] = None
    one_time_payment: float = 0
    subscription_fee: float = 0
    total_amount: float = 0
    product_id: Optional[int] = None
    product_offering_id: Optional[int] = None
    phone_number: Optional[str] = None
    internet_number: Optional[str] = None
    serial_number: Optional[str] = None
    resources: Optional[Resources] = None


@dataclass
class AdditionalProduct(ProductBase):
    """Данные о дополнительном продукте (опции)
    Attributes:
        segments: список сегментов, к которому относится доп. продукт (B2B, B2C)
        main_product_relationships_ids: список id основных продуктов, которые могут быть связаны с данным доп. продуктом
        technologies: список технологий, к которым относится доп. продукт (GSM, LTE)
    """

    segments: Optional[List[str]] = None
    main_product_relationships_ids: Optional[List[int]] = None
    technologies: Optional[List[str]] = None

    def __init__(self, product_name: str | None = None):
        self.product_name = product_name


@dataclass
class MainProduct(ProductBase):
    """Данные о продукте
    Attributes:
        switch_name (str): название коммутатора.
        switch_id (int): id коммутатора.
        account_id (int): id лицевого счета на который подключается продукт.
        account_number (int): номер лицевого счета на который подключается продукт.
        subs_id (int): id абонента.
        standard_id (int): id стандарта связи.
        equipment_type_id (int): id типа оборудования
        partner_point_id (int): id точки партнера
    """

    switch_name: Optional[str] = None
    switch_id: Optional[int] = None
    additional_product_list: List[AdditionalProduct] = field(default_factory=lambda: [])
    additional_product: Optional[AdditionalProduct] = None
    standard_id: Optional[int] = None
    equipment_type_id: int = 1
    partner_point_id: int = 100001
    account_id: Optional[int] = None
    account_number: Optional[int] = None
    subs_id: Optional[int] = None

    def get_switch_name(self) -> str | None:
        """
        Получение названия коммутатора для продукта
        :return: название коммутатора
        """
        lis_api = EquipmentRequests()
        equipment_id = get_default_equipment_id(product_category=self.category)
        if not equipment_id:
            return None
        standard_list = [get_default_standard_id(product_category=self.category)]
        type_list = [self.equipment_type_id]
        try:
            return lis_api.get_equipment(standard_id=standard_list, equipment_type_id=type_list)[equipment_id]
        except AssertionError:
            return None

    def __getattr__(self, name: str) -> object:
        if name == "switch_name":
            if self.switch_id and self.standard_id:
                switch_name = self.get_switch_name()
                self.switch_name = switch_name
                return switch_name
            return None
        return super().__getattribute__(name)

    def __getattribute__(self, name: str) -> object:
        match name:
            case "product_offering_id":
                return get_default_offering_id(self.category)
            case "switch_id":
                return get_default_equipment_id(product_category=self.category)
            case "standard_id":
                return get_default_standard_id(product_category=self.category)
            case "product_name":
                if not super().__getattribute__("product_name") and self.product_offering_id:
                    return product_names_map[self.product_offering_id]
            case "additional_product":
                product = super().__getattribute__("additional_product")
                additional_product_list = super().__getattribute__("additional_product_list")
                if product is None and additional_product_list:
                    return additional_product_list[0]
        return super().__getattribute__(name)

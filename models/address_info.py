from dataclasses import dataclass


@dataclass
class BasicSystemAddress:
    address: str = "ул Уральская, Россия, Санкт-Петербург г, ул Уральская г."
    short_address: str = "г. Санкт-петербург, ул. Уральская"
    add_address_name: str = "ул Уральская, Россия, Санкт-Петербург"
    external_address_id: int = 6


@dataclass
class AddressInfo:
    address: str = "Россия, Самарская область обл., г. Самара, ул. Полевая, д. 88"
    map_link: str = "https://yandex.ru/maps/-/CHEk7OKr"

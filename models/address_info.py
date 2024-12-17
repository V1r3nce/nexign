from dataclasses import dataclass


@dataclass
class AddressInfo:
    address: str = "Россия, Самарская область обл., г. Самара, ул. Полевая, д. 88"
    map_link: str = "https://yandex.ru/maps/-/CHEk7OKr"

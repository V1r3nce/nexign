from dataclasses import dataclass

from common.helpers.env_helper import BASE_URL_API


@dataclass
class BasicSystemAddress:
    address: str = "Россия, Санкт-Петербург г, ул Уральская"
    short_address: str = "Санкт-петербург, ул Уральская"
    external_address_id: int = 6


@dataclass
class AddressInfo:
    address: str = "Россия, Самарская область обл., г. Самара, ул. Полевая, д. 88"
    map_link: str = "https://yandex.ru/maps/-/CHEk7OKr"
    available_link: str = f"{BASE_URL_API}/rm-ui/all/billing-settings/packaging-attributes"

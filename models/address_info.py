from dataclasses import dataclass

from common.helpers.env_helper import BASE_URL_API


class BaseAddress:
    def __getattribute__(self, name: str) -> object:
        match name:
            case "country":
                return AddressInfo.address.split(", ")[0]
            case "region":
                return AddressInfo.address.split(", ")[1]
            case "city":
                return AddressInfo.address.split(", ")[2]
            case "street":
                return AddressInfo.address.split(", ")[3]
        return super().__getattribute__(name)


@dataclass
class BasicSystemAddress(BaseAddress):
    address: str = "Россия, Санкт-Петербург г., ул. Уральская, д. 4"
    short_address: str = "Санкт-Петербург г., ул. Уральская, д. 4"
    external_address_id: int = 6


@dataclass
class AddressInfo(BaseAddress):
    address: str = "Россия, Самарская обл., г. Самара, ш. Московское, д. 88"
    map_link: str = "https://yandex.ru/maps/-/CHEk7OKr"
    available_link: str = f"{BASE_URL_API}/nbss/billing/financial-reports"

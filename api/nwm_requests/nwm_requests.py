from datetime import datetime
from enum import StrEnum
from typing import Self

import allure
import pytest

from api.base_requests import BaseRequests
from api.psc_requests.offerings_requests import ProductOfferingRequests
from common.helpers.data_generator import generate_random_number, get_shifted_datetime_string
from common.helpers.env_helper import BASE_URL_API, BASE_URL_NWM
from models.product import AdditionalProduct, MainProduct


class TrafficType(StrEnum):
    MOBILE_INTERNET = ("internet", "105", 1, "totalVolume")
    SATELLITE_INTERNET = ("satellite_internet", "21", 2121, "totalVolume")
    LANDLINE_INTERNET = ("landline_internet", "7", 777, "totalVolume")
    MOBILE = ("mobile", "101", 1001, "time")
    SMS = ("sms", "103", 1003, "serviceSpecificUnits")

    def __new__(cls, type: str, service_specification_info: str, rating_group: int, unit_key: str) -> Self:
        traffic_type_obj = str.__new__(cls, type)
        traffic_type_obj._value_ = type
        traffic_type_obj.service_spec = service_specification_info
        traffic_type_obj.rating_group = rating_group
        traffic_type_obj.unit_key = unit_key
        return traffic_type_obj


class NwmRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()

        self.psc_requests = ProductOfferingRequests()

    @pytest.mark.nwm
    @allure.step("API: Принудительная активация продукта")
    def forced_write_off_request(
        self, product_offering_id: int, subscriber_id: int, min_write_off_date: datetime, max_write_off_date: datetime
    ) -> dict:
        payload = {
            "minWriteOffDate": min_write_off_date.date().isoformat(),
            "maxWriteOffDate": max_write_off_date.date().isoformat(),
            "productOffering": {"productOfferingId": product_offering_id},
        }

        response = self.post(
            url=f"{BASE_URL_API}/limited/v1/common/partyRoleManagement/subscribers/{subscriber_id}/forcedWriteOff",
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось активировать продукт")
        return response.json()

    @pytest.mark.nwm
    @allure.step("API: Потребление трафика")
    def generate_charge(self, subscriber_id: int, amount: int, traffic_type: TrafficType) -> None:
        invocation_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        payload = {
            "subscriberIdentifier": f"subs-{subscriber_id}",
            "nfConsumerIdentification": {"nodeFunctionality": "AMF"},
            "invocationTimeStamp": invocation_timestamp,
            "invocationSequenceNumber": 1,
            "oneTimeEvent": True,
            "oneTimeEventType": "IEC",
            "serviceSpecificationInfo": traffic_type.service_spec,
            "multipleUnitUsage": [
                {"ratingGroup": traffic_type.rating_group, "requestedUnit": {traffic_type.unit_key: amount}}
            ],
            "pDUSessionChargingInformation": {
                "userLocationinfo": {
                    "eutraLocation": {
                        "tai": {"plmnId": {"mcc": "250", "mnc": "02"}, "tac": "003E"},
                        "ecgi": {"plmnId": {"mcc": "250", "mnc": "02"}, "eutraCellId": "5D41"},
                    }
                },
                "uetimeZone": "+03:00",
            },
        }

        response = self.post(
            url=f"{BASE_URL_NWM}/nchf_convergedcharging/v3/chargingdata/",
            json=payload,
        )
        self.check_response_status(response, 201, "Не удалось сгенерировать потребление трафика")

    @pytest.mark.nwm
    @allure.step("API: Активация продукта")
    def activate_product(self, product: MainProduct | AdditionalProduct, inquiry_id: int) -> dict:
        action_date = get_shifted_datetime_string(shift="+10s", template="%Y-%m-%dT%H:%M:%S")
        start_date_time = get_shifted_datetime_string(shift="+10s", template="%Y-%m-%dT%H:%M:%S+03:00")
        product_specification_id = str(self.psc_requests.get_po_by_name(product.product_name)["productSpecificationId"])

        params = {
            "customerOrderId": inquiry_id,
            "correlationId": f"nwm-add-product-for-product-level-order-{generate_random_number(5)}-00000-000",
            "replyTo": "",
        }

        payload = [
            {
                "id": product.product_id,
                "isBundle": False,
                "productOrder": {
                    "customerOrderId": inquiry_id,
                    "action": "update",
                    "actionDate": action_date,
                },
                "productOffering": {
                    "id": product.product_offering_id,
                    "type": "main" if isinstance(product, MainProduct) else "additional",
                },
                "productSpecification": {
                    "id": product_specification_id,
                },
                "relatedParties": [
                    {
                        "id": product.subs_id,
                        "role": "user",
                        "validFor": {
                            "startDateTime": start_date_time,
                            "endDateTime": "2999-12-31T23:59:59+03:00",
                        },
                    }
                ],
            }
        ]

        response = self.post(
            url=f"{BASE_URL_API}/ps/v1/nwm-gateway/inventoryManagement/products",
            params=params,
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось активировать продукт")
        return response.json()

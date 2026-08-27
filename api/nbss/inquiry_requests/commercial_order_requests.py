import allure
import pytest

from api.base_requests import BaseRequests
from api.exceptions import (
    CommercialOrderIdNotFoundException,
    CommercialOrderNumberNotFoundException,
    ProductOfferingPriceIdNotFoundException,
)
from api.nbss.inquiry_requests.inquiry_requests import InquiriesRequests
from common.enums.product import ProductClassification
from common.enums.user import User
from common.helpers.checker import assert_that, wait_that
from common.helpers.env_helper import BASE_URL_API
from models.context import test_context
from models.inquiry import InquiryInfo
from models.product import AdditionalProduct, MainProduct, Resources


class CommercialOrderRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.inquiry_api = InquiriesRequests()

        test_context.switch_api_context_to_user(User.ADMIN)

    @pytest.mark.csm
    @allure.step("API: Получение идентификатора коммерческого заказа")
    def get_commercial_order_id(self, inquiry_id: int) -> int:
        """
        Возвращает id ком заказа
        :param inquiry_id: id заявки из register_inquiry
        :return: id ком заказа
        """
        wait_that(
            lambda: (
                True
                in [
                    custom_property.customPropertyDeclaration.customPropertyDeclarationCode == "commercialOrderId"
                    and len(str(custom_property.textValue)) > 0
                    for custom_property in self.inquiry_api.get_inquiry_info(inquiry_id).customProperties
                ]
            ),
            timeout=75,
            sleep_seconds=7.5,
            exception=AssertionError,
            message="Поиск не нашел созданного КЗ",
        )
        custom_properties = self.inquiry_api.get_inquiry_info(inquiry_id).customProperties
        for custom_property in custom_properties:
            if custom_property.customPropertyDeclaration.customPropertyDeclarationCode == "commercialOrderId":
                return int(str(custom_property.textValue))
        raise CommercialOrderIdNotFoundException(f'Не найден коммерческий заказ "{inquiry_id}"')

    @allure.step("API: Получение идентификатора заявки коммерческого заказа")
    def get_commercial_order_number(self, inquiry_id: int) -> int:
        """
        Возвращает id заявки ком заказа
        :param inquiry_id: id заявки из register_inquiry
        :return: id заявки ком заказа
        """
        response_commercial_order = self.inquiry_api.get_inquiry_info(inquiry_id).customProperties
        for custom_property in response_commercial_order:
            if custom_property.customPropertyDeclaration.customPropertyDeclarationCode == "orderInquiryId":
                return int(str(custom_property.textValue))
        raise CommercialOrderNumberNotFoundException(f'Не найдена заявка коммерческого заказа "{inquiry_id}"')

    @allure.step("API: Получение информации о продукте в коммерческом заказе")
    def get_order_product_info(self, product_id: int) -> dict:
        """
        Получение информации по продукту коммерческого заказа из csm.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :return: json словарь
        """
        response = self.get(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/{product_id}"
        )
        self.check_response_status(response, 200, "Невозможно получить информацию о продукте в коммерческом заказе")
        return response.json()

    @allure.step("API: Получение информации по продуктам КЗ")
    def get_order_products(self, payload: dict | None = None) -> dict:
        response = self.post(
            f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/search",
            json=payload,
        )
        self.check_response_status(response, 200, "Не получена информация по продуктам заказа")
        return response.json()

    def get_order_resources(self, product: MainProduct | AdditionalProduct) -> None:
        """
        Внутренний метод для заполнения id ресурсов бронирования коммерческого заказа.
        :param product: Продукт, который хотим добавить клиенту из select_product_offer.
        """
        order_resource_list = self.get_order_resource_ids(product.product_id)
        if len(order_resource_list) > 0:
            product.resources = Resources()
            for order_resource in order_resource_list:
                match order_resource["resource_type"]:
                    case "SIMCard":
                        product.resources.sim_card_id = order_resource["resource_id"]
                    case "defPhoneNumber":
                        product.resources.phone_number = order_resource["resource_id"]
                    case "equipment":
                        product.resources.equipment = order_resource["resource_id"]
                    case "accessPoint":
                        product.resources.apn = order_resource["resource_id"]
                    case "abcPhoneNumber":
                        product.resources.city_phone_number = order_resource["resource_id"]
                    case "ipAddress":
                        product.resources.ip_address = order_resource["resource_id"]

    @allure.step("API: Получение информации по ресурсам, которые нужно забронировать")
    def get_order_resource_ids(self, product_id: int) -> list:
        """
        Получение id ресурсов продукта, которые необходимо заполнить.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :return: список id ресурсов
        """
        resource_list = []
        for parameter in self.get_order_product_info(product_id)["orderCustomerFacingServices"]:
            if len(parameter["orderResources"]) > 0:
                for resource in parameter["orderResources"]:
                    resource_list.append(resource)
        for resource in self.get_order_product_info(product_id)["orderResources"]:
            if resource["resourceType"] not in resource_list:
                resource_list.append(resource)
        return [
            {"resource_type": resource["resourceType"], "resource_id": resource["orderResourceId"]}
            for resource in resource_list
        ]

    @allure.step("API: Получение кода номенклатуры для оборудования")
    def get_nomenclature(self, product_id: int) -> str:
        """
        Получение названия номенклатуры оборудования, необходимой для продукта.
        :param product_id: id продукта, который хотим инстанцировать клиенту из select_product_offer
        :return: строка - название
        """
        characteristics = self.get_order_product_info(product_id)["characteristics"]
        for characteristic in characteristics:
            if characteristic["code"] == "itemCode":
                return characteristic["values"][0]
        raise AssertionError("Не получен код номенклатуры")

    @allure.step("API: Индивидуализация продукта во время проведения продажи")
    def product_individualization(self, product: MainProduct | AdditionalProduct) -> None:
        payload = {
            "orderProducts": [
                {
                    "orderProductId": test_context.client.inquiry.product.product_id,
                    "characteristics": [],
                    "prices": [
                        {
                            "amount": test_context.client.inquiry.product.individualized_subs_fee,
                            "priceTypeCode": "RecurringChargeProdOfferPriceCharge",
                            "productOfferingPriceId": self.get_product_offering_subs_fee_price_id(product),
                        }
                    ],
                }
            ]
        }
        response = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/update/bulk",
            json=payload,
        )
        self.check_response_status(response, 200, "Не удалось получить шаблоны скидок")

    @allure.step("API: Получить productOfferingPriceId")
    def get_product_offering_subs_fee_price_id(self, product: MainProduct | AdditionalProduct) -> dict | None:
        response_data = self.get_order_product_info(product.product_id)
        charges = response_data.get("prices", {}).get("charges", [])
        for charge in charges:
            if (
                charge.get("priceTypeCode") == "RecurringChargeProdOfferPriceCharge"
                and "productOfferingChargeId" in charge
            ):
                return charge["productOfferingChargeId"]
        raise ProductOfferingPriceIdNotFoundException(
            f"Не найден productOfferingPriceId для продукта '{product.product_id}' "
        )

    @allure.step("Заполнить продукты в заявке")
    def create_products_in_inquiry(self, inquiry: InquiryInfo) -> None:
        if inquiry.product_list and len(inquiry.product_list) > 0:
            return
        test_context.client.inquiry = inquiry

        body_info_subs = {"params": {"limit": 100, "offset": 0}}
        subs_item = self.get_order_products(body_info_subs)["items"]
        holder_main_product_map = {}
        for item in subs_item:
            if item.get("classification", {}).get("code") == ProductClassification.main:
                new_product = MainProduct()
                new_product.product_name = item.get("name")
                new_product.product_offering_id = item.get("productOfferingId")
                new_product.product_id = item.get("orderProductId")
                holder_prototype_id = (
                    item.get("productPrototypes", [])[0].get("holderPrototype", {}).get("holderPrototypeId", -1)
                )
                assert_that(lambda: holder_prototype_id != -1, "Не получен holderPrototypeId")
                holder_main_product_map[holder_prototype_id] = new_product
                inquiry.product_list.append(new_product)

        for item in subs_item:
            if item.get("classification", {}).get("code") == ProductClassification.additional:
                new_additional_product = AdditionalProduct()
                holder_prototype_id = (
                    item.get("productPrototypes", [])[0].get("holderPrototype", {}).get("holderPrototypeId", -1)
                )
                assert_that(lambda: holder_prototype_id != -1, "Не получен holderPrototypeId")
                new_additional_product.product_name = item.get("name")
                new_additional_product.product_offering_id = item.get("productOfferingId")
                new_additional_product.product_id = item.get("orderProductId")
                main_product = holder_main_product_map.get(holder_prototype_id, None)
                if main_product is not None:
                    main_product.additional_product_list.append(new_additional_product)
                else:
                    inquiry.product_list.append(new_additional_product)

    @allure.step("API: Получение конфликтов коммерческого заказа")
    def get_commercial_order_conflicts(self) -> str:
        conflicts = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/conflicts/search",
            json={
                "objectIds": [prod.product_id for prod in test_context.client.inquiry.product.additional_product_list]
            },
        ).json()["conflicts"]
        if len(conflicts) > 0:
            return str([conflict["message"] for conflict in conflicts])
        return "Отсутствуют"

    @allure.step("API: Проверка статуса коммерческого заказа")
    def check_commercial_status(self) -> None:
        wait_that(
            lambda: self.get_commercial_status_state_code() == "SUCCEED",
            timeout=25,
            exception=AssertionError,
            message=lambda: (
                f"Статус коммерческого заказа не соответствует ожидаемому SUCCEED. Конфликты: {self.get_commercial_order_conflicts()}"
            ),
        )

    @allure.step("API: Получение статуса коммерческого заказа")
    def get_commercial_status_state_code(self) -> str | None:
        """
        :return: код статуса или None, если такового нет
        """
        response_state = self.get_commercial_order_info(test_context.client.inquiry).get("verificationState")
        assert_that(
            lambda: response_state is not None and response_state.get("code") is not None,
            "Информация по коммерческому заказу не получена",
        )
        return response_state.get("code")

    @allure.step("API: Получение информации о коммерческом заказе")
    def get_commercial_order_info(self, inquiry: InquiryInfo) -> dict | None:
        if inquiry.commercial_order is not None:
            response = self.get(
                url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{inquiry.commercial_order}/commonInfo"
            )
            self.check_response_status(response, 200, "Не удалось получить информацию по коммерческому заказу")
            return response.json()
        return None

    @allure.step("API: Заполнить product_id для продукта")
    def fill_product_id_for_product(self, product: MainProduct | AdditionalProduct) -> None:
        products_info = self.get_order_products().get("items", [])
        for product_info in products_info:
            if product_info.get("productOfferingId", -1) == product.product_offering_id:
                product_id = product_info.get("orderProductId", None)
                assert_that(lambda: product_id is not None, "Получен некорректный orderProductId")
                product.product_id = product_id
                return

    @allure.step("API: Заполнить контекст КЗ по inquiry_id")
    def fill_commercial_order_context(
        self, user_id: int, topic_name: str, product: MainProduct | AdditionalProduct
    ) -> None:
        """
        Заполняет commercial_order в контексте, а также product_id для переданного продукта.
        Ищет заявку клиента по topic_name. Если не найдена - создаёт новую.
        """
        inquiries = self.inquiry_api.get_inquiry_by_topic(user_id, topic_name)
        if not inquiries:
            inquiry_id = self.inquiry_api.form_and_register_inquiry(need_spd=False)
        else:
            inquiry_id = inquiries[0]
        test_context.client.inquiry.commercial_order = self.get_commercial_order_id(inquiry_id)
        self.fill_product_id_for_product(product)

    @allure.step("API: Ожидание бронирования ресурса в КЗ")
    def wait_for_resource_reservation(self, product_id: int, resource_value: str, timeout: int = 15) -> None:
        """
        Поллит API, ожидая появления забронированного ресурса в ресурсах продукта.
        :param product_id: id продукта коммерческого заказа
        :param resource_value: значение ресурса, ожидаемое в characteristics
        :param timeout: максимальное время ожидания в секундах
        """

        def _resource_reserved() -> bool:
            customer_services = self.get_order_product_info(product_id).get("orderCustomerFacingServices", [])
            for service in customer_services:
                for resource in service.get("orderResources", []):
                    for characteristic in resource.get("characteristics", []):
                        values = characteristic.get("values", [])
                        if resource_value in values:
                            return True
            return False

        wait_that(
            _resource_reserved,
            timeout=timeout,
            sleep_seconds=5,
            exception=AssertionError,
            message=f"Ресурс {resource_value} не забронирован в продукте {product_id} за {timeout} секунд.",
        )

    @allure.step("API: Добавление продукта в заказ")
    def _select_product_offer(self, product: MainProduct | AdditionalProduct) -> list[int]:
        """
        Возвращает id продукта выбранного ПП для проведения заявки
        :param product: продукт
        :return: список id продуктов для подключения
        """
        body_prod_select = {
            "addProductsParameters": [
                {
                    "productParameters": {
                        "addressId": test_context.client.inquiry.address_id,
                        "productOfferingId": product.product_offering_id,
                        "regionId": test_context.client.inquiry.region_id,
                    }
                }
            ],
            "operation": "CONNECT_ADDITIONAL_FOR_ORDER_PRODUCT"
            if isinstance(product, AdditionalProduct)
            else "CONNECT_INDEPENDENT_PRODUCT",
        }
        if isinstance(product, AdditionalProduct):
            body_prod_select.update(
                {"mainProduct": {"mainOrderProductId": test_context.client.inquiry.product.product_id}}  # type: ignore
            )
        if "equipment" in product.category:
            body_prod_select["addProductsParameters"][0]["productParameters"].update(
                {
                    "characteristics": [
                        {
                            "code": "typeOfSale",
                            "values": [
                                {
                                    "code": "Rent" if product.category == "equipment_rent" else "Sale",
                                    "name": "Аренда" if product.category == "equipment_rent" else "Продажа",
                                }
                            ],
                            "valueType": "dictionary",
                        }
                    ]
                }
            )
        response_product = self.post(
            url=f"{BASE_URL_API}/openapi/v1/productManagement/commercialOrders/{test_context.client.inquiry.commercial_order}/orderProducts/add/bulk",
            json=body_prod_select,
        )
        self.check_response_status(response_product, 200, "Не получен список продуктов")
        return [product["productId"] for product in response_product.json()["addedProducts"]]

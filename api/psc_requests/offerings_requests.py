from typing import Tuple

import allure
from playwright.sync_api import APIRequestContext

from api.base_requests import BaseRequests
from api.exceptions import (
    PSCOfferingIsNotCloned,
    PSCOfferingNotFound,
    PSCOfferingPriceIsNotChanged,
    PSCOfferingPriceNotFound,
    PSCOfferingSubscriptionNotFound,
)
from common.helpers.checker import check_that, wait_that
from common.helpers.env_helper import BASE_URL_PSC
from common.helpers.time_helpers import get_current_day_psc


class ProductOfferingRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)

    @allure.step("API: Подготовка тела с параметрами нового продуктового предложения")
    def _prepare_new_po(self, source_product_offering_id: int) -> dict:
        """
        Внутренний метод для формирования тела в запрос с клонированием продуктового предложения.
        Требуется заполнить информацию об исходном ПП, его проекте и ПП, который планируется создать
        :param source_product_offering_id: идентификатор клонируемого продуктового предложения
        :return: тело для запроса
        """
        product_offerings = self.get_po_list(size=100)
        po_name = "Копия "
        source_po_specification_id = None
        source_po_specification_name = None
        source_po_type = None
        source_po_start_date = None
        source_project = None
        for product_offering in product_offerings["content"]:
            if product_offering["id"] == source_product_offering_id:
                source_po_name = product_offering["title"]
                po_name += source_po_name
                source_po_specification_id = product_offering["productSpecificationId"]
                source_po_specification_name = product_offering["productSpecificationName"]
                source_po_type = product_offering["productType"]
                source_po_start_date = product_offering["startDate"]
                source_project = product_offering["project"]
                break
        check_that(
            lambda: source_project is not None, PSCOfferingNotFound, "Продуктовое предложение для копирования не найдено"
        )
        new_po = {
            "project": {
                "id": None,
                "title": po_name,
                "description": None,
                "lifecycleStatus": "EDITING",
                "firstPublicationDate": source_project["firstPublicationDate"],
                "publicationType": "PROJECT",
                "startDate": get_current_day_psc(),
                "sourceProjectId": source_project["id"],
                "user": {"code": "admin", "displayTitle": "Администратор"},
                "productOfferingsNumber": 1,
                "availableOperations": ["PUBLISH", "EDIT"],
                "isDraft": False,
            },
            "productOffering": {
                "isBundle": False,
                "id": None,
                "title": po_name,
                "description": None,
                "isArchival": False,
                "productType": source_po_type,
                "startDate": source_po_start_date,
                "endDate": None,
                "productSpecificationId": source_po_specification_id,
                "productSpecificationName": source_po_specification_name,
                "availableOperations": ["COPY"],
                "project": source_project,
                "drafts": [],
                "editingProject": None,
                "isFullImport": True,
                "bisId": None,
                "isLegacy": False,
                "serviceProviderCodes": ["DEFAULT"],
                "changeType": "CREATE",
                "lifecycleStatus": "NotPublished",
            },
            "copyParams": {
                "availability": True,
                "relations": True,
                "offerCharacteristics": True,
                "specCharacteristics": True,
                "tags": True,
                "policySets": True,
                "priceTypes": [
                    "AllowanceProdOfferPriceAlteration",
                    "DiscountProdOfferPriceAlteration",
                    "FeeProdOfferingPrice",
                    "LimitProdOfferPriceAlteration",
                    "PartnerFeeProdOfferingPrice",
                    "RecurringChargeProdOfferPriceCharge",
                    "ReplaceProdOfferPriceAlteration",
                    "StartBalancePrice",
                    "TariffUsageProdOfferPriceCharge",
                    "PAYGProdOfferPriceAlteration",
                    "RecurringChargeForRecalculationProdOfferPriceCharge",
                    "ExternalCounterProdOfferPrice",
                    "LimitBalanceProdOfferPrice",
                ],
            },
        }
        return new_po

    @allure.step("API: Создание заявки на клонирование продуктового предложения")
    def _clone_product_offering(self, source_product_offering_id: int) -> str:
        """
        Внутренний метод для отправки заявки на клонирование ПП
        :param source_product_offering_id: идентификатор клонируемого продуктового предложения
        :return: название нового ПП
        """
        payload = self._prepare_new_po(source_product_offering_id)
        response = self.post(
            f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/productOfferings/{source_product_offering_id}", data=payload
        )
        self.check_response_status(response, 202, "Не получилось создать заявку на клонирование предложения")
        return payload["productOffering"]["title"]

    @allure.step("API: Получение списка продуктовых предложений")
    def get_po_list(self, size: int = 30) -> dict:
        """
        Метод для получения списка ПП в PSC.
        Выводит первые size ПП, отсортированные по убыванию id
        :param size: количество выводимых ПП
        :return: информация о ПП
        """
        payload = {"page": 0, "size": size, "sortBy": "id", "sortDirection": "desc"}
        response = self.post(f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/productOfferings/filter", data=payload)
        self.check_response_status(response, 200, "Не удалось получить список предложений")
        return response.json()

    @allure.step("API: Получение идентификаторов неопубликованного продуктового предложения и его проекта")
    def get_unpublished_po_by_name(self, name: str) -> Tuple[int, int] | None:
        """
        Метод для получения id неопубликованного ПП с названием name и его проекта
        :param name: строка с названием ПП
        :return: id ПП, id его проекта
        """
        po_list = self.get_po_list()
        for po in po_list["content"]:
            if po["title"] == name and po["lifecycleStatus"] == "NotPublished":
                return po["id"], po["project"]["id"]
        return None

    @allure.step("API: Ожидание выполнения заявки на клонирование продуктового предложения")
    def _wait_cloned_po(self, name: str) -> Tuple[int, int] | None:
        """
        Внутренний метод для ожидания успешного завершения клонирования ПП и его появления в списке ПП PSC
        :param name: название ПП
        :return: id ПП, id его проекта
        """
        clone_timeout = 120
        wait_that(
            lambda: self.get_unpublished_po_by_name(name) is not None,
            timeout=clone_timeout,
            sleep_seconds=5,
            exception=PSCOfferingIsNotCloned,
            message=f"Предложение не было склонировано за {clone_timeout}",
        )
        return self.get_unpublished_po_by_name(name)

    @allure.step("API: Клонирование продуктового предложения")
    def clone_po_and_wait_success(self, product_offering_id: int) -> Tuple[int, int] | None:
        """
        Метод для клонирования продуктового предложения
        :param product_offering_id: id продуктового предложения
        :return: id клона продуктового предложения, id проекта клона продуктового предложения
        """
        name = self._clone_product_offering(product_offering_id)
        return self._wait_cloned_po(name)

    @allure.step("API: Получение цен продуктового предложения")
    def get_po_prices(self, product_offering_id: int, project_id: int) -> dict:
        """
        Метод для получения цен ПП с идентификатором product_offering_id
        :param product_offering_id: идентификатор ПП
        :param project_id: идентификатор проекта, в котором находится ПП
        :return: информация о ценах
        """
        params = {"projectId": project_id, "productOfferingId": product_offering_id}
        response = self.post(
            f"{BASE_URL_PSC}/ProductCatalog/api/v3/secured/priceTemplates/ACTIVE/search",
            params=params,
            data={"filters": []},
        )
        self.check_response_status(response, 200, "Не удалось получить цены продуктового предложения")
        return response.json()

    @allure.step("API: Получение идентификатора цены с типом {price_type}")
    def get_price_id_by_type(self, product_offering_id: int, project_id: int, price_type: str) -> int:
        """
        Получение идентификатора цены ПП с идентификатором product_offering_id по типу price_type
        :param product_offering_id: id ПП
        :param project_id: id проекта, в котором находится ПП
        :param price_type: тип искомой цены
        :return: id цены
        """
        prices = self.get_po_prices(product_offering_id, project_id)
        for price in prices["content"]:
            if price["priceGroup"] == price_type and price["status"] == "VALID":
                return price["id"]
        raise PSCOfferingSubscriptionNotFound

    @allure.step("API: Получение информации о цене")
    def get_po_price_info(self, product_offering_id: int, project_id: int, price_id: int) -> dict:
        params = {"projectId": project_id, "productOfferingId": product_offering_id}
        payload = [price_id]
        response = self.post(
            f"{BASE_URL_PSC}/ProductCatalog/api/v3/secured/priceTemplates/selected", params=params, data=payload
        )
        self.check_response_status(response, 200, "Не удалось получить информацию о цене")
        return response.json()[0]

    @allure.step("API: Проверка изменения стоимости цены")
    def _check_price_changed(
        self, product_offering_id: int, project_id: int, price_id: int, new_amount: str, attribute_code: str = "price"
    ) -> None:
        """
        Внутренний метод для ожидания изменения значения цены с идентификатором price_id
        :param product_offering_id: id ПП
        :param project_id: id проекта, в котором находится ПП.
        :param price_id: id цены, у которой изменили значение
        :param new_amount: ожидаемое значение цены
        :param attribute_code: код атрибута изменяемой цены
        """
        change_timeout = 15
        wait_that(
            lambda: self.get_price_amount(product_offering_id, project_id, price_id, attribute_code) == new_amount,
            timeout=change_timeout,
            sleep_seconds=5,
            exception=PSCOfferingPriceIsNotChanged,
            message=f"Значение цены продуктового предложения не было изменено за {change_timeout}",
        )

    def _find_price_property_by_attribute_code(self, attributes: dict, attribute_code: str = "price") -> dict | None:
        """
        Внутренний метод возвращающий свойства атрибута с кодом attribute_code.
        Возвращается словарь по причине того, чтобы после изменения атрибута словаря изменения отразились в исходном.
        По сути объединяет функциональность для методов использующих данный
        :param attributes: атрибуты по которым происходит поиск
        :param attribute_code: код искомого атрибута
        :return: словарь свойства
        """
        for attribute_index, attribute in enumerate(attributes["attributes"]):
            if attribute["code"] == attribute_code:
                for attribute_property_index, attribute_property in enumerate(attribute["properties"]):
                    if attribute_property["code"] == "amount":
                        return attributes["attributes"][attribute_index]["properties"][attribute_property_index]
        return None

    @allure.step("API: Получение значения цены")
    def get_price_amount(
        self, product_offering_id: int, project_id: int, price_id: int, attribute_code: str = "price"
    ) -> str:
        """
        Метод для получения значения цены с идентификатором price_id
        :param product_offering_id: id ПП
        :param project_id: id проекта, в котором находится ПП.
        :param price_id: id искомой цены
        :param attribute_code: код атрибута искомой цены
        :return: значение цены
        """
        full_price = self.get_po_price_info(product_offering_id, project_id, price_id)
        find_result = self._find_price_property_by_attribute_code(full_price, attribute_code)["values"]
        if find_result is not None:
            if len(find_result) > 0:
                return find_result[0]
            else:
                return ""
        raise PSCOfferingPriceNotFound

    @allure.step("API: Изменение значения цены")
    def reprice_product_offering_price(
        self, product_offering_id: int, project_id: int, new_amount: str, price_type: str = "recurringCharge"
    ) -> None:
        """
        Метод для изменения цены продуктового предложения.
        Для указания цены используется ее тип
        :param product_offering_id: идентификатор продуктового предложения
        :param project_id: идентификатор проекта продуктового предложения
        :param new_amount: новое значение цены
        :param price_type: строка с типом цены. Возможные варианты: абонентская плата - "recurringCharge", разовое списание - "feeProdOfferingPrice", объем - "priceAlteration", трафик - "trafficUsage"
        """
        price_id = self.get_price_id_by_type(product_offering_id, project_id, price_type)
        params = {"projectId": project_id, "productOfferingId": product_offering_id}
        payload = self.get_po_price_info(product_offering_id, project_id, price_id)
        attribute_code = "price"
        if price_type == "priceAlteration":
            attribute_code = "unitOfMeasure"
        attribute_value = self._find_price_property_by_attribute_code(payload, attribute_code)
        attribute_value["values"] = [new_amount]
        payload = [payload]
        response = self.put(f"{BASE_URL_PSC}/ProductCatalog/api/v3/secured/priceTemplates", params=params, data=payload)
        self.check_response_status(response, 202, "Не удалось сделать заявку на репрайс")
        self._check_price_changed(product_offering_id, project_id, price_id, new_amount, attribute_code)

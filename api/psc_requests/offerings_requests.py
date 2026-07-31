import json
import random
import uuid
from typing import Any, Literal, Tuple

import allure

from api.base_requests import BaseRequests
from api.exceptions import (
    PSCOfferingIsNotCloned,
    PSCOfferingNotFound,
    PSCOfferingPriceIsNotChanged,
    PSCOfferingPriceNotFound,
    PSCOfferingSubscriptionNotFound,
)
from common.exceptions import PSCImportContainsErrors, PSCOfferingExportMismatch
from common.helpers.checker import check_that, wait_that
from common.helpers.env_helper import BASE_URL_PSC
from common.helpers.json_utils import find_object_by_inner_value
from common.helpers.time_helpers import get_current_day_psc


class ProductOfferingRequests(BaseRequests):
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
            f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/productOfferings/{source_product_offering_id}", json=payload
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
        response = self.post(f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/productOfferings/filter", json=payload)
        self.check_response_status(response, 200, "Не удалось получить список предложений")
        return response.json()

    @allure.step('API: Поиск продуктового предложения "{name}" со статусом "{status}"')
    def get_po_by_name(
        self,
        name: str,
        status: str | None = None,
        size: int = 100,
        return_ids_only: bool = False,
    ) -> dict | tuple[int, int] | None:
        """
        Ищет продуктовое предложение по названию с учётом (или без учёта) статуса.
        :param name: название предложения
        :param status: фильтр по lifecycleStatus (если None, статус не учитывается)
        :param size: количество записей, запрашиваемых из каталога
        :param return_ids_only: если True, возвращает (id предложения, id проекта)
        :return: либо полный объект предложения, либо кортеж с id, либо None
        """
        po_list = self.get_po_list(size=size)
        for po in po_list.get("content", []):
            if po.get("title") == name and (status is None or po.get("lifecycleStatus") == status):
                if return_ids_only:
                    return po["id"], po["project"]["id"]
                return po
        return None

    @allure.step("API: Ожидание выполнения заявки на клонирование продуктового предложения")
    def _wait_cloned_po(self, name: str) -> Tuple[int, int]:
        """
        Внутренний метод для ожидания успешного завершения клонирования ПП и его появления в списке ПП PSC
        :param name: название ПП
        :return: id ПП, id его проекта
        """
        clone_timeout = 120

        wait_that(
            lambda: (
                self.get_po_by_name(
                    name=name,
                    status="NotPublished",
                    return_ids_only=True,
                )
                is not None
            ),
            timeout=clone_timeout,
            sleep_seconds=5,
            exception=PSCOfferingIsNotCloned,
            message=f"Предложение не было склонировано за {clone_timeout} секунд",
        )

        result = self.get_po_by_name(
            name=name,
            status="NotPublished",
            return_ids_only=True,
        )
        assert isinstance(result, tuple)
        return result

    @allure.step("API: Клонирование продуктового предложения")
    def clone_po_and_wait_success(self, product_offering_id: int) -> Tuple[int, int, str] | None:
        """
        Метод для клонирования продуктового предложения (ПП)
        :param product_offering_id: id ПП
        :return: id клона ПП, id проекта клона ПП, название ПП
        """
        name = self._clone_product_offering(product_offering_id)
        result = self._wait_cloned_po(name)
        return result[0], result[1], name

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
            json={"filters": []},
        )
        self.check_response_status(response, 200, "Не удалось получить цены продуктового предложения")
        return response.json()

    @allure.step("API: Получение идентификатора цены с типом {price_type}")
    def get_price_id_by_type(self, product_offering_id: int, project_id: int, price_type: str, is_volume: bool) -> int:
        """
        Получение идентификатора цены ПП с идентификатором product_offering_id по типу price_type
        :param product_offering_id: id ПП
        :param project_id: id проекта, в котором находится ПП
        :param price_type: тип искомой цены
        :param is_volume: флаг говорящий о том, что нужная цена отвечает за объем
        :return: id цены
        """
        prices = self.get_po_prices(product_offering_id, project_id)
        for price in prices["content"]:
            if price["priceGroup"] == price_type and price["status"] == "VALID":
                if price_type == "trafficUsage":
                    if (price.get("baseId") == 29 and is_volume) or (not is_volume and price.get("baseId") == 9):
                        return price["id"]
                else:
                    if price.get("baseId") in [1, 12]:
                        return price["id"]
        raise PSCOfferingSubscriptionNotFound

    @allure.step("API: Получение информации о цене")
    def get_po_price_info(self, product_offering_id: int, project_id: int, price_id: int) -> dict:
        params = {"projectId": project_id, "productOfferingId": product_offering_id}
        payload = [price_id]
        response = self.post(
            f"{BASE_URL_PSC}/ProductCatalog/api/v3/secured/priceTemplates/selected", params=params, json=payload
        )
        self.check_response_status(response, 200, "Не удалось получить информацию о цене")
        return response.json()[0]

    @allure.step("API: Проверка изменения стоимости цены")
    def _check_price_changed(
        self,
        product_offering_id: int,
        project_id: int,
        price_type: str,
        new_amount: str,
        is_volume: bool,
        attribute_code: str = "price",
    ) -> None:
        """
        Внутренний метод для ожидания изменения значения цены с идентификатором price_id
        :param product_offering_id: id ПП
        :param project_id: id проекта, в котором находится ПП.
        :param price_type: Тип цены, у которой изменили значение.
        :param new_amount: Ожидаемое значение цены.
        :param attribute_code: Код атрибута изменяемой цены.
        """
        change_timeout = 60
        wait_that(
            lambda: (
                self.get_price_amount(product_offering_id, project_id, price_type, is_volume, attribute_code)
                == new_amount
            ),
            timeout=change_timeout,
            sleep_seconds=10,
            exception=PSCOfferingPriceIsNotChanged,
            message=lambda: (
                f"Значение цены продуктового предложения не было изменено за {change_timeout}\nТекущая цена - {self.get_price_amount(product_offering_id, project_id, price_type, is_volume, attribute_code)}"
            ),
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
        self, product_offering_id: int, project_id: int, price_type: str, is_volume: bool, attribute_code: str = "price"
    ) -> str:
        """
        Метод для получения значения цены с идентификатором price_id
        :param product_offering_id: id ПП
        :param project_id: id проекта, в котором находится ПП.
        :param price_type: Тип искомой цены.
        :param is_volume: Флаг говорящий о том, что нужная цена отвечает за объем.
        :param attribute_code: Код атрибута искомой цены
        :return: значение цены
        """
        price_id = self.get_price_id_by_type(product_offering_id, project_id, price_type, is_volume)
        full_price = self.get_po_price_info(product_offering_id, project_id, price_id)
        find_result = self._find_price_property_by_attribute_code(full_price, attribute_code)
        if find_result is not None:
            if len(find_result) > 0:
                return find_result["values"][0]
            else:
                return ""
        raise PSCOfferingPriceNotFound

    @allure.step("Изменение значения цены у атрибутов для переданного словаря")
    def change_amount_of_property_with_code(
        self, attributes: dict, new_amount: str, attribute_code: str = "price"
    ) -> None:
        attribute_value = self._find_price_property_by_attribute_code(attributes, attribute_code)
        attribute_value["values"] = [new_amount]

    @allure.step("API: Изменение значения цены")
    def reprice_product_offering_price(
        self,
        product_offering_id: int,
        project_id: int,
        new_amount: str,
        price_type: str = "recurringCharge",
        is_volume: bool = False,
    ) -> None:
        """
        Метод для изменения цены продуктового предложения.
        Для указания цены используется ее тип
        :param product_offering_id: идентификатор продуктового предложения
        :param project_id: идентификатор проекта продуктового предложения
        :param new_amount: новое значение цены
        :param price_type: строка с типом цены. Возможные варианты: абонентская плата - "recurringCharge", разовое списание - "feeProdOfferingPrice", объем, трафик - "trafficUsage"
        :param is_volume: флаг говорящий о том, что нужная цена отвечает за объем
        """
        price_id = self.get_price_id_by_type(product_offering_id, project_id, price_type, is_volume=is_volume)
        params = {"projectId": project_id, "productOfferingId": product_offering_id}
        payload = self.get_po_price_info(product_offering_id, project_id, price_id)
        attribute_code = "price"
        if price_type == "trafficUsage" and is_volume:
            attribute_code = "maxVolume"
        self.change_amount_of_property_with_code(payload, new_amount, attribute_code)
        for price_index in range(len(payload["prices"])):
            self.change_amount_of_property_with_code(payload["prices"][price_index], new_amount, attribute_code)
        response = self.put(f"{BASE_URL_PSC}/ProductCatalog/api/v3/secured/priceTemplates", params=params, json=payload)
        self.check_response_status(response, 202, "Не удалось сделать заявку на репрайс")
        self._check_price_changed(product_offering_id, project_id, price_type, new_amount, is_volume, attribute_code)

    @allure.step("API: Экспорт продуктового предложения {product_offering_id}")
    def export_product_offering(self, product_offering_id: int, sync: bool = True) -> dict:
        corr_id = uuid.uuid4()
        params = {"correlationId": corr_id, "sync": str(sync).lower()}
        response = self.post(
            f"{BASE_URL_PSC}/ps/v1/psc-import/productOfferings/{product_offering_id}/export",
            params=params,
        )
        self.check_response_status(response, 200, "Не удалось экспортировать продуктовое предложение")
        return response.json()

    @allure.step("API: Получение продуктового предложения по идентификатору {product_offering_id}")
    def get_product_offering(self, product_offering_id: int, project_id: int) -> dict:
        params = {"projectId": project_id}
        response = self.get(
            f"{BASE_URL_PSC}/ProductCatalog/api/v2/secured/productOfferings/{product_offering_id}",
            params=params,
        )
        self.check_response_status(response, 200, "Не удалось получить продуктовое предложение")
        return response.json()

    @allure.step("API: Экспорт и проверка соответствия продуктового предложения с названием {name}")
    def export_and_validate_product_offering(self, name: str) -> tuple[int, str, str]:
        target_po = self.get_po_by_name(name=name)
        check_that(
            lambda: target_po is not None,
            PSCOfferingNotFound,
            f"Продуктовое предложение с названием {name} не найдено",
        )
        assert isinstance(target_po, dict)
        product_offering_id = target_po["id"]
        project_id = target_po["project"]["id"]
        exported = self.export_product_offering(product_offering_id)
        current = self.get_product_offering(product_offering_id, project_id)
        id_exported = exported.get("productOffering", {}).get("productOfferingId")
        name_exported = exported.get("productOffering", {}).get("name")
        specification_exported = exported.get("productOffering", {}).get("productSpecification", {}).get("name")
        check_that(
            lambda: id_exported == current.get("id"),
            PSCOfferingExportMismatch,
            "Идентификатор продукта из экспорта не совпадает с PSC",
        )
        check_that(
            lambda: name_exported == current.get("title"),
            PSCOfferingExportMismatch,
            "Название продукта из экспорта не совпадает с PSC",
        )
        check_that(
            lambda: exported.get("productOffering", {}).get("productOfferingType") == current.get("productType"),
            PSCOfferingExportMismatch,
            "Тип продукта из экспорта не совпадает с PSC",
        )
        check_that(
            lambda: specification_exported == current.get("productSpecificationName"),
            PSCOfferingExportMismatch,
            "Спецификация продукта из экспорта не совпадает с PSC",
        )
        if current.get("endDate") is not None:
            check_that(
                lambda: (
                    exported.get("productOffering", {}).get("validFor", {}).get("endDateTime", "").split("T")[0]
                    == current.get("endDate", "").split("T")[0]
                ),
                PSCOfferingExportMismatch,
                "Дата окончания действия продукта из экспорта не совпадает с PSC",
            )
        return id_exported, name_exported, specification_exported

    @allure.step("API: Получение названия продуктового предложения по ID")
    def get_product_offering_name_by_id(self, product_offering_id: int) -> str:
        """
        Возвращает название продуктового предложения по его ID.
        """
        response = self.get_po_list(size=100)

        for offering in response.get("content", []):
            if offering.get("id") == product_offering_id:
                name = offering.get("title")
                if isinstance(name, str):
                    return name

        raise PSCOfferingNotFound(f"Продуктовое предложение с id={product_offering_id} не найдено")

    @staticmethod
    def _extract_import_error_message(result: dict) -> str:
        """
        Достаёт текст ошибки из ответа migrationImport.
        """
        po_result = result.get("productOfferingResult") or {}
        msg = po_result.get("errorMessage")
        return str(msg) if msg is not None else ""

    @staticmethod
    def _is_duplicate_component_price_error(message: str) -> bool:
        """
        Определяет, что ошибка импорта связана с дублем component_price_pkey.
        """
        m = message.lower()
        return ("component_price_pkey" in m) or (
            "duplicate key value violates unique constraint" in m and "component_price" in m
        )

    @staticmethod
    def _regenerate_version_price_ids(payload: dict) -> None:
        """
        Перегенерирует versionProductOfferingPriceId в payload на значения в безопасном диапазоне int32.
        """
        root: Any = payload.get("productOffering", payload)
        if not isinstance(root, dict):
            return
        prices = root.get("productOfferingPrices")
        if not isinstance(prices, list) or not prices:
            return

        count = len(prices)
        base = random.randint(1_500_000_000, 1_900_000_000 - count - 1)

        for idx, price in enumerate(prices):
            if isinstance(price, dict) and "versionProductOfferingPriceId" in price:
                price["versionProductOfferingPriceId"] = base + idx

    @staticmethod
    def _replace_valid_for_start_datetime_to_today(node: Any) -> None:
        """
        Рекурсивно проходит по JSON и во всех объектах validFor заменяет startDateTime на сегодняшнюю дату
        (формат PSC: YYYY-MM-DDT00:00:00.000).
        """
        today_psc = get_current_day_psc()

        if isinstance(node, dict):
            valid_for = node.get("validFor")

            if isinstance(valid_for, dict) and "startDateTime" in valid_for:
                valid_for["startDateTime"] = today_psc

            if isinstance(valid_for, list):
                for item in valid_for:
                    if isinstance(item, dict) and "startDateTime" in item:
                        item["startDateTime"] = today_psc

            for value in node.values():
                ProductOfferingRequests._replace_valid_for_start_datetime_to_today(value)

        elif isinstance(node, list):
            for item in node:
                ProductOfferingRequests._replace_valid_for_start_datetime_to_today(item)

    @allure.step("API: Импорт продукта через migrationImport")
    def import_product_offering_migration(
        self,
        payload: dict,
        publish: bool = False,
        check_overwrite: bool = False,
        force_spec_override: bool = False,
        sync: bool = True,
        correlation_id: str | None = None,
        max_attempts: int = 3,
    ) -> dict:
        """
        Выполняет импорт продуктового предложения через эндпоинт migrationImport.

        Метод выполняет POST-запрос к PSC и ожидает успешный HTTP-ответ (200)
        и отсутствие ошибок в теле ответа (containsErrors == False).
        Перед каждой попыткой импорта обновляет значения validFor.startDateTime
        на текущую дату в формате PSC. В случае ошибки дублирования
        component_price_pkey выполняет повторную попытку импорта
        с новой генерацией versionProductOfferingPriceId.

        :param payload: JSON-тело продуктового предложения, передаваемое в migrationImport
        :param publish: признак публикации продукта после импорта
        :param check_overwrite: признак проверки и разрешения перезаписи существующего продукта
        :param force_spec_override: признак принудительной перезаписи спецификации
        :param sync: признак синхронного выполнения импорта
        :param correlation_id: идентификатор корреляции запроса; если не задан, генерируется автоматически
        :param max_attempts: максимальное количество попыток импорта при ошибках дублирования
        :return: JSON-ответ сервиса migrationImport при успешном импорте
        :raises PSCImportContainsErrors: если импорт завершился с ошибками или превышено число попыток
        """
        attempt = 1
        last_result: dict | None = None

        while attempt <= max_attempts:
            self._replace_valid_for_start_datetime_to_today(payload)

            corr_id = correlation_id or str(uuid.uuid4())
            params = {
                "checkOverwrite": str(check_overwrite).lower(),
                "publish": str(publish).lower(),
                "sync": str(sync).lower(),
                "forceSpecificationOverride": str(force_spec_override).lower(),
                "correlationId": corr_id,
            }
            response = self.post(
                f"{BASE_URL_PSC}/ps/v1/psc-import/productOfferings/migrationImport",
                params=params,
                json=payload,
            )
            self.check_response_status(response, 200, "Не удалось импортировать продуктовое предложение")
            result = response.json()
            last_result = result

            if result.get("containsErrors") in (False, None):
                return result

            message = self._extract_import_error_message(result)
            if self._is_duplicate_component_price_error(message) and attempt < max_attempts:
                self._regenerate_version_price_ids(payload)
                attempt += 1
                continue

            raise PSCImportContainsErrors(f"Импорт завершился с ошибками (attempt={attempt}/{max_attempts}): {message}")

        raise PSCImportContainsErrors(
            f"Импорт завершился с ошибками (attempt={max_attempts}/{max_attempts}): "
            f"{self._extract_import_error_message(last_result or {})}"
        )

    @allure.step("API: Копирование и импорт продуктового предложения {name}")
    def export_modify_and_import_product_offering(self, name: str) -> tuple[int, str, str]:
        """
        Экспортирует продуктовое предложение по имени, заменяет id на следующий максимальный,
        добавляет префикс 'Копия' и делает versionProductOfferingPriceId уникальными, затем импортирует.
        """
        po_list = self.get_po_list(size=100)
        id_name: int | None = None
        max_id: int = -1

        for po in po_list.get("content", []):
            po_id = po.get("id")
            if isinstance(po_id, int) and po_id > max_id:
                max_id = po_id
            if po.get("title") == name:
                id_name = po_id

        check_that(
            lambda: id_name is not None,
            PSCOfferingNotFound,
            f"Продуктовое предложение с названием {name} не найдено",
        )

        exported = self.export_product_offering(id_name)
        new_id = max_id + 1

        exported_str = json.dumps(exported, ensure_ascii=False)
        exported_str = exported_str.replace(str(id_name), str(new_id))
        modified = json.loads(exported_str)

        spec_name = modified.get("productOffering", modified).get("productSpecification", {}).get("name")
        po_dict: Any = modified.get("productOffering", modified)
        name_offer = "Копия " + po_dict["name"]
        if isinstance(po_dict.get("name"), str):
            po_dict["name"] = name_offer

        if isinstance(po_dict, dict):
            self._regenerate_version_price_ids(po_dict)

        self.import_product_offering_migration(modified)

        return new_id, name_offer, spec_name

    @allure.step("API: Получение ID проекта по идентификатору продуктового предложения")
    def get_project_id_by_product_offering_id(self, product_offering_id: int) -> int:
        """
        Возвращает идентификатор проекта для указанного продуктового предложения.

        Выполняет поиск среди всех продуктовых предложений, полученных
        методом ``search_product_offerings``, и находит запись, где ``id``
        совпадает с ``product_offering_id``. Затем возвращает значение
        ``id`` из вложенного объекта ``project``. Если предложение не
        найдено, возбуждается исключение ``PSCOfferingNotFound``.

        :param product_offering_id: идентификатор искомого продуктового предложения
        :return: идентификатор проекта, которому принадлежит указанное ПП
        :raises PSCOfferingNotFound: если ПП с таким id не найдено
        """
        po_list = self.get_po_list(size=100)
        for product_offering in po_list.get("content", []):
            if product_offering.get("id") == product_offering_id:
                project = product_offering.get("project")
                if project and isinstance(project, dict):
                    project_id = project.get("id")
                    if isinstance(project_id, int):
                        return project_id
        raise PSCOfferingNotFound(f"Проект для продуктового предложения с id={product_offering_id} не найден")

    @allure.step("Получить значение объема для продуктового предложения")
    def get_product_offering_volume(
        self, product_offering_id: int, volume_type: Literal["Интернет", "Минуты", "SMS"]
    ) -> int:
        project_id = self.get_project_id_by_product_offering_id(product_offering_id)
        prices = self.get_po_prices(product_offering_id, project_id)
        price = find_object_by_inner_value(objects=prices["content"], key="name", value=volume_type)

        max_volume = find_object_by_inner_value(objects=price.get("attributes", []), key="code", value="maxVolume")
        max_volume_amount = find_object_by_inner_value(
            objects=max_volume.get("properties", []), key="code", value="amount"
        )
        values = max_volume_amount.get("values", None)
        if not values:
            raise ValueError("Получено пустое поле 'values'")

        return int(values[0])

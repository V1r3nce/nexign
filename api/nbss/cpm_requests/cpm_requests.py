from __future__ import annotations

from urllib.parse import urlparse

import allure
from playwright.sync_api import APIResponse

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL, BASE_URL_CPM
from common.helpers.string_helper import convert_string_to_base64


class CustomPropertyRequests(BaseRequests):
    """
    Обёртка над CPM API для работы с кастом-атрибутами (customProperties)
    с встроенной авторизацией (получение access_token по BasicAuth).
    """

    SEARCH_PATH = "/cpmAdmin/topics/30/customProperties/tree/search"
    CUSTOM_PROPERTY_PATH = "/cpmAdmin/topics/customProperties"
    CACHE_CLEAR_PATH = "/oapi-cms-backend/backend/spring/cache/configuration/clear"

    def __init__(self) -> None:
        super().__init__()

        access_token = self._get_access_token()

        self._cpm_headers: dict[str, str] = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json, text/plain, */*",
        }

    @allure.step("API: Получение access_token для CPM через BasicAuth (Administrator/Administrator)")
    def _get_access_token(
        self,
        username: str = "Administrator",
        password: str = "Administrator",
    ) -> str:
        """
        Вызывает эндпоинт /cpmAdmin/users/token в CPM с BasicAuth и возвращает access_token.

        Args:
            username: Логин для CPM (по умолчанию 'Administrator').
            password: Пароль для CPM (по умолчанию 'Administrator').

        Returns:
            str: access_token, полученный от CPM.

        Raises:
            AssertionError: Если статус ответа не 200 или в теле нет поля 'access_token'.
        """
        url = f"{BASE_URL_CPM}/cpmAdmin/users/token"

        basic_raw = f"{username}:{password}"
        basic_encoded = convert_string_to_base64(basic_raw)
        headers = {
            "Authorization": f"Basic {basic_encoded}",
            "Accept": "application/json, text/plain, */*",
        }

        response: APIResponse = self.post(url=url, headers=headers)

        self.check_response_status(
            response,
            200,
            "Не удалось получить access_token для CPM по /cpmAdmin/users/token",
        )

        data = response.json()
        token = data.get("access_token")
        assert token, "В ответе CPM отсутствует поле 'access_token'"

        return token

    @allure.step("API: Поиск кастом-атрибута по имени в дереве customProperties ")
    def search_custom_property(self, name: str) -> int:
        """
        Ищет кастом-атрибут по имени в дереве customProperties и возвращает его ID.

        Args:
            name: Название кастом-атрибута (поле entity.name в дереве).

        Returns:
            int: Значение entityId для найденного кастом-атрибута.

        Raises:
            AssertionError: Если дерево недоступно или атрибут с таким именем не найден.
        """
        params = {"limit": 0, "isActive": "true"}
        url = f"{BASE_URL_CPM}{self.SEARCH_PATH}"
        response: APIResponse = self.get(url=url, params=params, headers=self._cpm_headers)

        self.check_response_status(
            response,
            200,
            "Не удалось получить дерево customProperties (search_custom_property)",
        )

        data = response.json()
        items = data.get("items", [])

        for item in items:
            if item.get("isGroup"):
                continue
            entity = item.get("entity") or {}
            if entity.get("name") == name:
                custom_property_id = entity.get("entityId")
                assert custom_property_id is not None, f"Для атрибута '{name}' не найден entityId в ответе search"
                return int(custom_property_id)

        raise AssertionError(f"Кастом-атрибут с именем '{name}' не найден в дереве customProperties")

    @allure.step("API: Получение описания кастом-атрибута")
    def get_custom_property(self, custom_property_id: int) -> dict:
        """
        Получает полное описание кастом-атрибута по его идентификатору.

        Args:
            custom_property_id: Идентификатор кастом-атрибута.

        Returns:
            dict: JSON-описание кастом-атрибута.

        Raises:
            AssertionError: Если ответ не 200 или тело ответа пустое.
        """
        url = f"{BASE_URL_CPM}{self.CUSTOM_PROPERTY_PATH}/{custom_property_id}"
        response: APIResponse = self.get(url=url, headers=self._cpm_headers)

        self.check_response_status(
            response,
            200,
            f"Не удалось получить описание кастом-атрибута {custom_property_id}",
        )

        data = response.json()

        if isinstance(data, list):
            assert data, f"Пустой ответ при получении кастом-атрибута {custom_property_id}"
            data = data[0]

        if isinstance(data, dict):
            data.setdefault("customPropertyId", custom_property_id)

        return data

    @allure.step("API: Обновление логического кастом-атрибута")
    def update_custom_property_bool(
        self,
        custom_property_id: int,
        custom_property: dict,
        value: bool,
    ) -> dict:
        """
        Обновляет описание логического кастом-атрибута, включая блок customAttributeDefault.

        Args:
            custom_property_id: Идентификатор кастом-атрибута.
            custom_property: Текущее описание атрибута (ответ GET).
            value: Новое логическое значение по умолчанию (True/False).

        Returns:
            dict: JSON-ответ CPM на запрос обновления.
        """
        fixed_value = "true" if value else "false"

        src_cpt = custom_property.get("customPropertyType") or {}
        src_dtype = src_cpt.get("customPropertyDataType") or {}

        custom_property_type = {
            "customPropertyDataType": {
                "name": "Логическое значение",
                "customPropertyDataTypeCode": src_dtype.get("customPropertyDataTypeCode", "BOOL"),
            },
            "customPropertyTypeCode": src_cpt.get("customPropertyTypeCode", "BOOL"),
            "parameterValues": src_cpt.get("parameterValues") or [],
            "outTransformation": src_cpt.get("outTransformation"),
            "multySelect": src_cpt.get("multySelect", False),
        }

        payload = {
            "name": custom_property.get("name"),
            "isActive": custom_property.get("isActive", True),
            "description": custom_property.get("description") or "",
            "customAttributeDefault": {
                "defaultType": custom_property.get("customAttributeDefault", {}).get(
                    "defaultType",
                    "FIXED",
                ),
                "fixedValue": [fixed_value],
            },
            "customPropertyCode": custom_property.get("customPropertyCode"),
            "customPropertyDataTypeCode": src_dtype.get("customPropertyDataTypeCode", "BOOL"),
            "customPropertyDataTypeName": "Системные типы → Логическое значение",
            "customPropertyDataTypeId": None,
            "customPropertyType": custom_property_type,
            "customPropertyGroup": {
                "customPropertyGroupId": custom_property.get(
                    "customPropertyGroup",
                    {},
                ).get("customPropertyGroupId"),
            },
            "readonly": custom_property.get("readonly"),
            "mandatory": custom_property.get("mandatory"),
            "hidden": custom_property.get("hidden"),
            "prompt": custom_property.get("prompt"),
            "regexpRule": custom_property.get("regexpRule"),
            "editMask": custom_property.get("editMask"),
            "extendedColumn": custom_property.get("extendedColumn"),
            "changeEntityBehavior": custom_property.get("changeEntityBehavior", "DEFAULT"),
        }

        url = f"{BASE_URL_CPM}{self.CUSTOM_PROPERTY_PATH}/{custom_property_id}"

        response: APIResponse = self.put(
            url=url,
            data=payload,
            headers=self._cpm_headers,
        )

        self.check_response_status(
            response,
            200,
            f"Не удалось обновить кастом-атрибут {custom_property_id}",
        )
        return response.json()

    @allure.step("API: Установка default-значения логического кастом-атрибута")
    def set_default_custom_property_bool(
        self,
        custom_property_id: int,
        value: bool,
    ) -> None:
        """
        Устанавливает default-значение логического кастом-атрибута
        через специализированный endpoint setDefault.

        Args:
            custom_property_id: Идентификатор кастом-атрибута.
            value: Новое логическое значение по умолчанию (True/False).
        """
        fixed_value = "true" if value else "false"

        payload = {
            "defaultType": "FIXED",
            "fixedValue": [fixed_value],
        }

        url = f"{BASE_URL_CPM}/cpmAdmin/customProperties/{custom_property_id}/setDefault"

        response: APIResponse = self.post(
            url=url,
            data=payload,
            headers=self._cpm_headers,
        )

        self.check_response_status(
            response,
            200,
            f"Не удалось установить default кастом-атрибута {custom_property_id}",
        )

    @allure.step("API: Очистка кэша конфигурации CMS")
    def clear_cache(self) -> None:
        """
        Очищает кэш конфигурации CMS на стенде.

        BASE_URL берется из env_helper и используется для вычисления имени стенда,
        после чего формируется адрес srv-app01.{stand}.res.nxcloud.nexign.com:18180.
        """
        parsed = urlparse(BASE_URL)

        host_parts = (parsed.hostname or "").split(".")
        stand = host_parts[1] if len(host_parts) >= 2 else ""

        assert stand, f"Не удалось определить название стенда из BASE_URL: {BASE_URL}"

        cache_host = f"srv-app01.{stand}.res.nxcloud.nexign.com:18180"
        cache_url = f"http://{cache_host}{self.CACHE_CLEAR_PATH}"

        headers = {"PSNaviUser": "Admin"}

        response: APIResponse = self.get(url=cache_url, headers=headers)
        self.check_response_status(
            response,
            [200, 204],
            f"Не удалось очистить кэш CMS по адресу {cache_url}",
        )

    @allure.step("API: Установка логического кастом-атрибута по имени и очистка кэша ")
    def set_custom_property_bool(self, name: str, value: bool) -> dict:
        """
        Высокоуровневый сценарий для установки логического кастом-атрибута по имени.

        Шаги:
          1. Поиск кастом-атрибута по имени (search_custom_property).
          2. Получение текущего описания (get_custom_property).
          3. Обновление сущности (update_custom_property_bool).
          4. Установка default-значения через setDefault (set_default_custom_property_bool).
          5. Очистка кэша CMS (clear_cache).

        Args:
            name: Имя кастом-атрибута.
            value: Новое логическое значение по умолчанию (True/False).

        Returns:
            dict: Сводный результат с данными до/после и ответами update/setDefault.
        """
        custom_property_id = self.search_custom_property(name)

        before = self.get_custom_property(custom_property_id)

        update_result = self.update_custom_property_bool(
            custom_property_id=custom_property_id,
            custom_property=before,
            value=value,
        )

        self.set_default_custom_property_bool(
            custom_property_id=custom_property_id,
            value=value,
        )

        self.clear_cache()

        after = self.get_custom_property(custom_property_id)

        return {
            "update": update_result,
            "before": before,
            "after": after,
        }

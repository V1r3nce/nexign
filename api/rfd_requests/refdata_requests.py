import allure

from api.base_requests import BaseRequests
from common.helpers.checker import assert_that
from common.helpers.env_helper import BASE_URL_RFD


class RefDataRequests(BaseRequests):
    @allure.step("API: Получение списка торговых точек (partnerPoints) из справочника")
    def _get_partner_points_list(
        self,
        add_address_string: bool = True,
        show_actual_only: bool = False,
        show_published_mode: str = "PUBLISHED_ONLY",
    ) -> list:
        """
        Получает список торговых точек (partnerPoints) из справочника.

        :param add_address_string: Добавить адрес (по умолчанию True)
        :param show_actual_only: Показывать только актуальные (по умолчанию False)
        :param show_published_mode: Показывать только опубликованные (по умолчанию PUBLISHED_ONLY)
        :return: Список торговых точек (items)
        """
        url = f"{BASE_URL_RFD}/OAPI_REFDATA/references/partnerPoints/items"
        params = {
            "addAddressString": str(add_address_string).lower(),
            "showActualOnly": str(show_actual_only).lower(),
            "showPublishedMode": show_published_mode,
        }
        response = self.get(url=url, params=params)
        self.check_response_status(response, 200, "Не удалось получить список торговых точек (partnerPoints)")
        data = response.json()
        return data.get("items", [])

    @allure.step("API: Поиск торговой точки по наименованию {name}")
    def _find_partner_point_by_name(self, items: list, name: str) -> dict | None:
        """
        Находит торговую точку в списке items по наименованию.

        :param items: Список торговых точек из ответа API
        :param name: Наименование торговой точки для поиска
        :return: Найденный элемент (dict) или None, если не найден
        """
        for item in items:
            item_name = item.get("name") or {}
            if item_name.get("valueInRequestedLanguage") == name or item_name.get("defaultValue") == name:
                return item
        return None

    @allure.step("API: Проверить наличие торговой точки с наименованием в справочнике partnerPoints")
    def assert_partner_point_exists_by_name(
        self,
        name: str,
        add_address_string: bool = True,
        show_actual_only: bool = False,
        show_published_mode: str = "PUBLISHED_ONLY",
    ) -> None:
        """
        Получить список торговых точек (partnerPoints) и убедиться, что в items
        есть элемент с переданным наименованием.
        :param name: Наименование торговой точки (например, "Торговая точка 1")
        :param add_address_string: Добавить адрес (по умолчанию True)
        :param show_actual_only: Показывать только актуальные (по умолчанию False)
        :param show_published_mode: Показывать только опубликованные (по умолчанию PUBLISHED_ONLY)
        """
        items = self._get_partner_points_list(
            add_address_string=add_address_string,
            show_actual_only=show_actual_only,
            show_published_mode=show_published_mode,
        )

        found_item = self._find_partner_point_by_name(items, name)
        assert_that(
            lambda: found_item is not None,
            message=(
                f"Торговая точка с наименованием '{name}' не найдена в списке partnerPoints. "
                f"Получено items: {len(items)}"
            ),
        )

    @allure.step("API: Проверить наличие торговой точки с наименованием и соответствие её статуса")
    def assert_partner_point_exists_by_name_and_status(
        self,
        name: str,
        status: str,
        add_address_string: bool = True,
        show_actual_only: bool = False,
        show_published_mode: str = "PUBLISHED_ONLY",
    ) -> None:
        """
        Получить список торговых точек (partnerPoints), убедиться, что есть элемент с переданным
        наименованием, и проверить, что его статус (partnerPointStatusId) совпадает с переданным.
        :param name: Наименование торговой точки
        :param status: Ожидаемое название статуса (например, "Закрыта", "Активна")
        :param add_address_string: addAddressString (по умолчанию True)
        :param show_actual_only: showActualOnly (по умолчанию False)
        :param show_published_mode: showPublishedMode (по умолчанию PUBLISHED_ONLY)
        """
        items = self._get_partner_points_list(
            add_address_string=add_address_string,
            show_actual_only=show_actual_only,
            show_published_mode=show_published_mode,
        )
        item = self._find_partner_point_by_name(items, name)
        assert_that(
            lambda: item is not None,
            message=(
                f"Торговая точка с наименованием '{name}' не найдена в списке partnerPoints. "
                f"Получено items: {len(items)}"
            ),
        )
        actual_status = None
        for prop in (item or {}).get("properties") or []:
            if prop.get("propertyCode") == "partnerPointStatusId":
                val = prop.get("value")
                if isinstance(val, dict):
                    actual_status = (val.get("name") or {}).get("defaultValue") or (val.get("name") or {}).get(
                        "valueInRequestedLanguage"
                    )
                break
        assert_that(
            lambda: actual_status == status,
            message=(f"Статус торговой точки '{name}' не совпадает: ожидался '{status}', получен '{actual_status}'"),
        )

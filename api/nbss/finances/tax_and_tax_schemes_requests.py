import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API


class TaxAndTaxSchemesRequests(BaseRequests):
    """Класс для работы с API налогов и схем налогообложения"""

    BATCH_SIZE: int = 50

    def __init__(self) -> None:
        super().__init__()

    @allure.step("API: Поиск налогов")
    def search_taxes(self, offset: int = 0, limit: int = 60) -> dict:
        """
        Получает список налогов через POST /bss-box/v2/billing/taxes/search.
        Возвращает полный ответ, включая listInfo для пагинации

        :param offset: Смещение для пагинации (по умолчанию 0)
        :param limit: Лимит количества результатов (по умолчанию 60)
        :return: Словарь с ответом API (items, listInfo)
        """
        payload = {
            "showAllTaxes": True,
            "params": {"limit": limit, "offset": offset},
        }
        params = {
            "isNeedAllLangs": "true",
            "limit": str(limit),
            "offset": str(offset),
        }
        response = self.post(url=f"{BASE_URL_API}/bss-box/v2/billing/taxes/search", json=payload, params=params)
        self.check_response_status(response, 200, "Ошибка при поиске налогов")

        return response.json()

    @allure.step("API: Поиск схем налогообложения")
    def search_tax_schemes(self, offset: int = 0, limit: int = 60) -> dict:
        """
        Получает список схем налогообложения через POST /bss-box/v2/billing/taxSchemes/search.
        Возвращает полный ответ, включая listInfo для пагинации

        :param offset: Смещение для пагинации (по умолчанию 0)
        :param limit: Лимит количества результатов (по умолчанию 60)
        :return: Словарь с ответом API (items, listInfo)
        """
        payload = {
            "showAllTaxSchemes": True,
            "params": {"limit": limit, "offset": offset},
        }
        params = {
            "isNeedAllLangs": "true",
            "limit": str(limit),
            "offset": str(offset),
        }
        response = self.post(url=f"{BASE_URL_API}/bss-box/v2/billing/taxSchemes/search", json=payload, params=params)
        self.check_response_status(response, 200, "Ошибка при поиске налоговых схем")

        return response.json()

    @allure.step("API: Поиск ID налога по названию '{tax_name}'")
    def find_tax_id_by_name(self, tax_name: str) -> int | None:
        """
        Ищет ID налога по названию с пагинацией.

        :param tax_name: Название налога для поиска
        :returns: ID найденного налога (taxId) или None, если налог не найден
        """
        offset = 0
        while True:
            taxes = self.search_taxes(offset=offset, limit=self.BATCH_SIZE)
            for tax in taxes.get("items", []):
                for name_entry in tax.get("taxName", []):
                    if name_entry.get("value") == tax_name:
                        return tax.get("taxId")
            total = taxes.get("listInfo", {}).get("count", 0)
            offset += self.BATCH_SIZE
            if offset >= total:
                return None

    @allure.step("API: Поиск ID схемы налогообложения по названию '{tax_scheme_name}'")
    def find_tax_scheme_id_by_name(self, tax_scheme_name: str) -> int | None:
        """
        Ищет ID схемы налогообложения по названию с пагинацией.

        :param tax_scheme_name: Название схемы налогообложения для поиска
        :returns: ID найденной схемы налогообложения (taxSchemeId) или None, если схема не найдена
        """
        offset = 0
        while True:
            tax_schemes = self.search_tax_schemes(offset=offset, limit=self.BATCH_SIZE)
            for scheme in tax_schemes.get("items", []):
                for name_entry in scheme.get("name", []):
                    if name_entry.get("value") == tax_scheme_name:
                        return scheme.get("taxSchemeId")
            total = tax_schemes.get("listInfo", {}).get("count", 0)
            offset += self.BATCH_SIZE
            if offset >= total:
                return None

    @allure.step("API: Удаление налога с ID {tax_id}")
    def delete_tax(self, tax_id: int) -> None:
        """
        Удаление налога по ID через DELETE /bss-box/v1/billing/taxes/{taxId}.

        :param tax_id: ID налога для удаления
        """
        response = self.delete(url=f"{BASE_URL_API}/bss-box/v1/billing/taxes/{tax_id}")
        self.check_response_status(response, 204, "Ошибка при удалении налога")

    @allure.step("API: Удаление схемы налогообложения с ID {tax_scheme_id}")
    def delete_tax_scheme(self, tax_scheme_id: int) -> None:
        """
        Удаление схемы налогообложения по ID через DELETE /bss-box/v1/billing/taxSchemes/{taxSchemeId}.

        :param tax_scheme_id: ID налога для удаления
        """
        # TODO: удалить запрос с PUT когда пофиксят https://jira.nexign.com/browse/RMBSS-18755
        payload = {"endDate": "2020-01-01"}
        response = self.put(f"{BASE_URL_API}/bss-box/v1/billing/taxSchemes/{tax_scheme_id}", json=payload)
        self.check_response_status(response, 200, "Ошибка при переведении схемы налогообложения в недействующую")

        response = self.delete(url=f"{BASE_URL_API}/bss-box/v1/billing/taxSchemes/{tax_scheme_id}")
        self.check_response_status(response, 204, "Ошибка при удалении схемы налогообложения")

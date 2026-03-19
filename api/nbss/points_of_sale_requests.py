import allure

from api.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_API
from models.playwright_bridge import GeneralResponse


class PointsOfSaleRequests(BaseRequests):
    """Класс для работы с API точек продажи"""

    @allure.step("API: Получение userId из SSO по login {login}")
    def get_user_id_by_login(
        self,
        login: str = "admin",
        user_type_ids: list[int] | None = None,
        limit: int = 60,
        offset: int = 0,
    ) -> int:
        """
        Получает userId пользователя из SSO API по логину.

        :param login: Логин пользователя для поиска (по умолчанию "admin")
        :param user_type_ids: Список ID типов пользователей для фильтрации (по умолчанию [250300001, 250300004])
        :param limit: Лимит количества результатов (по умолчанию 60)
        :param offset: Смещение для пагинации (по умолчанию 0)
        :return: userId найденного пользователя
        :raises: AssertionError если пользователь не найден
        """
        if user_type_ids is None:
            user_type_ids = [250300001, 250300004]

        url = f"{BASE_URL_API}/openapi/v2/users/search"
        params = {"limit": limit, "offset": offset}
        payload = {"userTypeIds": user_type_ids}

        response = self.post(url=url, params=params, data=payload)
        self.check_response_status(response, 200, "Не удалось получить список пользователей из SSO API")

        data = response.json()
        items = data.get("items", [])

        for item in items:
            credentials = item.get("credentials", [])
            for credential in credentials:
                if credential.get("credentialCode") == "LOGIN" and credential.get("value", "").lower() == login.lower():
                    user_id = item.get("userId")
                    if user_id:
                        return user_id

        raise AssertionError(f"Пользователь с логином '{login}' не найден в SSO API")

    @allure.step("API: Получение списка точек продажи, привязанных к пользователю {user_id}")
    def get_user_points_of_sale(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        sort: str = "name",
    ) -> list[int]:
        """
        Получает список всех точек продажи (partnerPointId), привязанных к указанному пользователю.

        :param user_id: ID пользователя
        :param limit: Лимит количества результатов (по умолчанию 10)
        :param offset: Смещение для пагинации (по умолчанию 0)
        :param sort: Поле для сортировки (по умолчанию "name")
        :return: Список partnerPointId точек продажи, привязанных к пользователю
        """
        url = f"{BASE_URL_API}/openapi/v1/tailored_nbss/partnerPoints/search"
        params = {
            "limit": limit,
            "offset": offset,
            "sorting": "[object Object]",
            "sort": sort,
        }
        payload = {"userId": user_id}

        response = self.post(url=url, params=params, data=payload)
        self.check_response_status(response, 200, f"Не удалось получить список точек продажи для пользователя {user_id}")

        data = response.json()
        items = data.get("items", [])

        partner_point_ids = [item.get("partnerPointId") for item in items if item.get("partnerPointId")]

        return partner_point_ids

    @allure.step("API: Отвязывание точки продажи {partner_point_id} от пользователя {user_id}")
    def unbind_point_of_sale_from_user(self, user_id: int, partner_point_id: int) -> GeneralResponse:
        """
        Отвязывает конкретную точку продажи от указанного пользователя.

        :param user_id: ID пользователя, от которого нужно отвязать точку продажи
        :param partner_point_id: ID точки продажи (partnerPointId), которую нужно отвязать
        :return: Ответ API на запрос отвязывания (статус 204)
        """
        url = f"{BASE_URL_API}/openapi/v1/tailored_nbss/users/{user_id}/partnerPoints/{partner_point_id}/delete"

        response = self.post(url=url, data={})
        self.check_response_status(
            response,
            204,
            f"Не удалось отвязать точку продажи {partner_point_id} от пользователя {user_id}",
        )
        return response

    @allure.step("API: Отвязывание всех точек продажи от пользователя {user_id}")
    def unbind_all_points_of_sale_from_user(self, user_id: int) -> None:
        """
        Отвязывает все точки продажи от указанного пользователя.
        Сначала получает список всех привязанных точек продажи, затем удаляет каждую из них.

        :param user_id: ID пользователя, от которого нужно отвязать точки продажи
        """
        partner_point_ids = self.get_user_points_of_sale(user_id)

        for partner_point_id in partner_point_ids:
            self.unbind_point_of_sale_from_user(user_id, partner_point_id)

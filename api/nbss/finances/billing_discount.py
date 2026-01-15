from datetime import timedelta

import allure

from api.base_requests import BaseRequests
from api.nbss.finances.billing_requests import BillingRequests
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import get_current_moscow_datetime
from models.context import test_context
from models.product import MainProduct


class BillingDiscountsRequests(BaseRequests):
    def __init__(self) -> None:
        super().__init__()
        self.billing_api = BillingRequests()
        self.billing_profile_id = None

    @allure.step("API: Создание биллинговой скидки")
    def add_billing_discount(
        self,
        amount: int,
        action_type: str,
        account_id: int | None = None,
        product: MainProduct | list[MainProduct] | None = None,
        priority: int | None = None,
        template_name: str | None = None,
        discount_threshold: int = 1000,
        subs_ids: list[int] | None = None,
    ) -> dict:
        """
        Создание биллинговой скидки.

        :param account_id: id клиента
        :param amount: сумма скидки
        :param product: продукт или список продуктов
        :param action_type: тип ("Скидка" | "Доначисление")
        :param priority: приоритет скидки
        :param template_name: название шаблона
        :param discount_threshold: порог суммы, с которой предоставляется скидка
        :param subs_ids: идентификатор(ы) абонента, если нужна скидка для конкретного(ых)
        """
        product = product or test_context.client.inquiry.product

        action_type_map = {
            "Скидка": 1,
            "Доначисление": 2,
        }
        assert action_type in action_type_map, f"Неизвестный action_type: {action_type}"

        if action_type == "Скидка" and not template_name:
            template_name = "Скидка по умолчанию"

        start_dt = get_current_moscow_datetime()
        start_date = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000")
        end_date = (start_dt + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.000")

        templates = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/billing/billingDiscountTemplates/search",
            params={"limit": 100, "offset": 0},
            data={"discountActionTypeId": action_type_map[action_type]},
        )
        self.check_response_status(templates, 200, "Не удалось получить шаблоны скидок")

        items = templates.json().get("items", [])
        assert items, f"Список шаблонов пуст (action_type={action_type})"

        template = next((t for t in items if t.get("name") == template_name), None)
        if not template:
            available_names = [t.get("name") for t in items]
            allure.attach(
                "\n".join(map(str, available_names)),
                name=f"Шаблон '{template_name}' не найден. Доступные шаблоны",
                attachment_type=allure.attachment_type.TEXT,
            )
            template = items[0]

        discount_template_id = template["billingDiscountTemplateId"]

        actions = template.get("billingDiscountTemplateActions", [])
        assert actions, f"У шаблона '{template.get('name')}' нет billingDiscountTemplateActions"

        required_action_id = action_type_map[action_type]
        action = next(
            (a for a in actions if a.get("billingDiscountActionId") == required_action_id),
            actions[0],
        )
        discount_template_action_id = action["billingDiscountTemplateActionId"]

        self.billing_profile_id = self.billing_api.get_billing_profile_id(
            account_id or test_context.client.agreements[0].accounts[0].id
        )

        if priority is None:
            priority = self.get_current_billing_discounts()["listInfo"]["count"] + 1

        action_params = (
            {"discountThreshold": discount_threshold, "discountValuePercentage": amount}
            if action_type == "Скидка"
            else {"amount": amount, "detailId": 3}
        )

        products = [product] if isinstance(product, MainProduct) else product

        payload = {
            "billingDiscountTemplate": {
                "billingDiscountTemplateId": discount_template_id,
                "billingDiscountTemplateActions": [
                    {
                        "billingDiscountActionId": required_action_id,
                        "billingDiscountActionParameters": action_params,
                        "billingDiscountTemplateActionId": discount_template_action_id,
                    }
                ],
            },
            "billingDiscountTemplateId": discount_template_id,
            "chargeFilterParams": {
                "subscriberIds": [p.subs_id for p in products] if subs_ids is None else subs_ids,
                "productOfferingIds": [p.product_offering_id for p in products],
            },
            "comment": "",
            "priority": priority,
            "validFor": {
                "startDateTime": start_date,
                "endDateTime": end_date,
            },
        }

        response = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/billing/billingProfiles/{self.billing_profile_id}/billingDiscounts",
            data=payload,
        )
        self.check_response_status(response, 201, "Не удалось добавить скидку")

        return response.json()

    @allure.step("API: Получение списка текущих скидок")
    def get_current_billing_discounts(self) -> dict:
        """Получение списка текущих скидок
        :return: список скидок"""

        params = {"limit": 30, "offset": 0}
        billing_discounts = self.get(
            url=f"{BASE_URL_API}/bss-box/v1/billing/billingProfiles/{self.billing_profile_id}/billingDiscounts/search",
            params=params,
        )
        self.check_response_status(billing_discounts, 200, "Не удалось получить список скидок")
        return billing_discounts.json()

    @allure.step("API: Получение списка шаблонов скидок")
    def get_billing_templates(self, action_type: int) -> dict:
        """Получение списка шаблонов скидок по типу
        :param action_type: тип скидки
        :return: список шаблонов скидок"""
        params = {"limit": 10, "offset": 0}
        payload = {"discountActionTypeId": action_type}
        billing_templates = self.post(
            url=f"{BASE_URL_API}/bss-box/v2/billing/billingDiscountTemplates/search", params=params, data=payload
        )
        self.check_response_status(billing_templates, 200, "Не удалось получить шаблонов")
        return billing_templates.json()

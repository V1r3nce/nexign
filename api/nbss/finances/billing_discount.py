import allure
from playwright.sync_api import APIRequestContext

from api.base_requests import BaseRequests
from api.nbss.client_requests.client_inquiries_requests import InfoAboutProduct
from api.nbss.finances.billing_requests import BillingRequests
from common.helpers.env_helper import BASE_URL_API
from common.helpers.time_helpers import get_current_moscow_datetime


class BillingDiscountsRequests(BaseRequests):
    def __init__(self, api_request_auth_context: APIRequestContext):
        super().__init__(api_request_auth_context)
        self.billing_api = BillingRequests(api_request_auth_context)
        self.billing_profile_id = None

    @allure.step("API: Создание биллинговой скидки")
    def add_billing_discount(
        self,
        account_id: int,
        amount: int,
        product: InfoAboutProduct,
        action_type: str,
        priority: int | None = None,
        template_name: str | None = None,
    ) -> None:
        """Создание биллинговой скидки
        :param account_id: id клиента
        :param amount: сумма скидки
        :param product: продукт
        :param action_type: тип (Скидка или доначисление)
        :param priority: приоритет скидки (последовательность применения)
        :param template_name: название шаблона. Для типа скидки, по умолчанию применяется шаблон "Скидка по умолчанию"
        """
        start_date = get_current_moscow_datetime().strftime("%Y-%m-%dT%H:%M:%S.000")
        action_type_map = {
            "Скидка": 1,
            "Доначисление": 2,
        }
        if not template_name and action_type == "Скидка":
            template_name = "Скидка по умолчанию"

        templates = self.get_billing_templates(action_type_map[action_type])
        template = [template for template in templates["items"] if template["name"] == template_name][0]
        discount_template_id = template["billingDiscountTemplateId"]
        discount_template_action_id = template["billingDiscountTemplateActions"][0]["billingDiscountTemplateActionId"]

        self.billing_profile_id = self.billing_api.get_billing_profile_id(account_id)

        if not priority:
            priority = self.get_current_billing_discounts()["listInfo"]["count"] + 1

        if action_type == "Скидка":
            action_params = {"discountThreshold": 1000, "discountValuePercentage": amount}
        else:
            action_params = {"amount": amount, "detailId": 3}

        payload = {
            "billingDiscountTemplate": {
                "billingDiscountTemplateActions": [
                    {
                        "billingDiscountActionId": action_type_map[action_type],
                        "billingDiscountActionParameters": action_params,
                        "billingDiscountTemplateActionId": discount_template_action_id,
                    }
                ],
                "billingDiscountTemplateId": discount_template_id,
            },
            "billingDiscountTemplateId": discount_template_id,
            "chargeFilterParams": {
                "subscriberIds": [product.subs_id],
                "productOfferingIds": [product.product_offering_id],
            },
            "comment": "",
            "priority": priority,
            "validFor": {"endDateTime": "2999-12-01T23:00:00.737", "startDateTime": start_date},
        }
        billing_discount = self.post(
            url=f"{BASE_URL_API}/bss-box/v1/billing/billingProfiles/{self.billing_profile_id}/billingDiscounts",
            data=payload,
        )
        self.check_response_status(billing_discount, 201, "Не удалось добавить скидку")
        return billing_discount.json()

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
            url=f"{BASE_URL_API}/bss-box/v1/billing/billingDiscountTemplates/search", params=params, data=payload
        )
        self.check_response_status(billing_templates, 200, "Не удалось получить шаблонов")
        return billing_templates.json()

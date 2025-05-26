import allure
from playwright.sync_api import APIRequestContext, APIResponse

from api.requests.base_requests import BaseRequests
from common.helpers.env_helper import BASE_URL_LIS


class NumberClassesRequests(BaseRequests):
    """
    Класс для управления классами номеров, шаблонами классов номеров и условиями шаблонов с помощью api запросов
    """

    def __init__(self, api_request_auth_context: APIRequestContext, macro_region_id: int = 999):
        super().__init__(api_request_auth_context)
        self.macro_region_id = macro_region_id
        self.macro_region_ids = (0, macro_region_id)

    @allure.step("API: Добавление нового элемента в справочник 'Классы номеров'")
    def add_number_class(self, name: str, service_provider_id: int = None, active: bool = None) -> int:
        """
        Метод добавляет элемент в справочник 'Классы номеров'

        Parameters:
        name (str): название нового элемента справочника
        macro_region_id (int): идентификатор макрорегиона (филиала) для нового элемента справочника, если элемент
                               справочника создаётся на федеральном уровне, то значение должно быть равно 0
        service_provider_id (int): идентификатор сервис-провайдера, указывается в случае если macroRegionId = 0
        active (bool): признак активности нового элемента справочника

        Returns:
        int: идентификатор созданного элемента
        """
        payload = {"name": name, "macroRegionId": self.macro_region_id}
        if service_provider_id:
            payload["serviceProviderId"] = service_provider_id
        if active is not None:
            payload["active"] = active
        add_class = self.post(url=f"{BASE_URL_LIS}/ps/v1/logicalResources/private/numberClasses", data=payload)
        self.check_response_status(add_class, 201, "Не удалось добавить класс номеров")
        return add_class.json()["numberClassId"]

    @allure.step("API: Получение списка классов номеров")
    def get_list_number_class(self, name: str = None, ids: list[int] = None, active: bool = None) -> list[dict]:
        """
        Метод получает список классов номеров

        Parameters:
        name (str): значение для поиска по наименованию элемента, параметр поддерживает нечеткий поиск
        ids (list[int]): список идентификаторов элементов справочника
        macro_region_ids (list[int]): список макрорегионов
        active (bool): признак активности класса номера

        Returns:
        list[dict]: список объектов с информацией о классах номеров
        """
        payload = {"macroRegionIds": self.macro_region_ids}
        if name:
            payload["name"] = name
        if ids:
            payload["ids"] = ids
        if active is not None:
            payload["numberClassIds"] = active
        get_info = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/dictionaries/logicalResources/numberClasses/search", data=payload
        )
        self.check_response_status(get_info, 200, "Не удалось получить список классов номеров")
        return get_info.json()["items"]

    @allure.step("API: Удаление элемента справочника 'Классы номеров'")
    def remove_number_class(self, number_class_id: int) -> None:
        """
        Метод удаляет элемент справочника 'Классы номеров'

        Parameters:
        number_class_id (int): идентификатор класса номера
        """
        params = {"macroRegionId": self.macro_region_id}
        remove_class = self.delete(
            url=f"{BASE_URL_LIS}/ps/v1/logicalResources/private/numberClasses/{number_class_id}", params=params
        )
        self.check_response_status(remove_class, 204, "Не удалось удалить класс номеров")

    @allure.step("API: Добавление шаблона разметки классов номеров")
    def add_number_class_template(self, name: str, number_class_id: int, priority: int, is_default: bool = False) -> int:
        """
        Метод добавляет шаблон разметки классов номеров

        Parameters:
        name (str): название нового шаблона
        number_class_id (int): идентификатор класса номеров
        priority (int): приоритет шаблона
        is_default (bool): использовать как шаблон по умолчанию
        macro_region_id (int): идентификатор макрорегиона для шаблона

        Returns:
        int: идентификатор шаблона
        """
        payload = {
            "name": name,
            "numberClassId": number_class_id,
            "priority": priority,
            "isDefault": is_default,
            "macroRegionId": self.macro_region_id,
        }
        add_template = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates", data=payload
        )
        self.check_response_status(add_template, 201, "Не удалось добавить шаблон разметки классов номеров")
        return add_template.json()["phoneNumberClassTemplateId"]

    @allure.step("API: Получение списка шаблонов разметки классов номеров")
    def get_list_number_class_template(
        self,
        name: str = None,
        number_class_id: int = None,
        priority: int = None,
        is_default: bool = None,
        phone_number_class_template_ids: list[int] = None,
    ) -> list[dict]:
        """
        Метод получает список шаблонов разметки классов номеров

        Parameters:
        name (str): наименование шаблона
        number_class_id (int): идентификатор класса номера
        priority (int): приоритет шаблона
        is_default (bool): признак использования шаблона по умолчанию
        macro_region_ids (list[int]): идентификаторы макрорегионов
        phone_number_class_template_ids (list[int]): идентификаторы шаблонов классов номеров

        Returns:
        list[dict]: список объектов с информацией о шаблонах разметки классов номеров
        """
        payload = {"macroRegionIds": self.macro_region_ids}
        if name:
            payload["name"] = name
        if number_class_id:
            payload["numberClassId"] = number_class_id
        if priority:
            payload["priority"] = priority
        if is_default is not None:
            payload["isDefault"] = is_default
        if phone_number_class_template_ids:
            payload["phoneNumberClassTemplateIds"] = phone_number_class_template_ids
        get_info = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/search", data=payload
        )
        self.check_response_status(get_info, 200, "Не удалось получить список шаблонов разметки классов номеров")
        return get_info.json()["items"]

    @allure.step("API: Удаление шаблона классов номеров")
    def remove_number_class_template(self, template_ids: list[int]) -> APIResponse:
        """
        Метод удаляет шаблон разметки классов номеров

        Parameters:
        template_ids list[int]: идентификатор шаблона разметки классов номеров

        Returns:
        APIResponse: объект ответа API с массивом конфликтов, возникших при удалении шаблона
        """
        payload = {"macroRegionId": self.macro_region_id}
        if template_ids:
            payload["phoneNumberClassTemplateIds"] = template_ids
        remove_template = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/deleteBulk", data=payload
        )
        self.check_response_status(remove_template, 200, "Не удалось удалить шаблон разметки классов номеров")
        return remove_template

    @allure.step("API: Добавление условия в шаблон для разметки класса номера")
    def add_template_rule(
        self,
        template_id: int,
        name: str,
        condition: str,
        is_active: bool = True,
        test_MSISDN: int = None,
    ) -> int:
        """
        Метод получает список условий шаблона класса номеров

        Parameters:
        template_id (int): идентификатор шаблона
        name (str): наименование условия
        condition (str): условие
        is_active (bool): признак активности нового условия
        test_MSISDN (int): тестовый номер условия
        macro_region_ids (int): идентификатор макрорегиона

        Returns:
        int: идентификатор условия шаблона
        """
        payload = {
            "name": name,
            "conditionString": condition,
            "isActive": is_active,
            "macroRegionId": self.macro_region_id,
        }
        if test_MSISDN:
            payload["testMSISDN"] = test_MSISDN
        add_rule = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/{template_id}/conditions",
            data=payload,
        )
        self.check_response_status(add_rule, 201, "Не удалось добавить условие шаблона класса номеров")
        return add_rule.json()["phoneNumberClassConditionId"]

    @allure.step("API: Получение списка условий шаблона класса номеров")
    def get_list_rule_templates(
        self,
        template_id: int,
        name: str = None,
        is_active: bool = None,
        test_MSISDN: int = None,
        phone_number_class_condition_ids: list[int] = None,
    ) -> list[dict]:
        """
        Метод получает список условий шаблона класса номеров

        Parameters:
        template_id (int): идентификатор шаблона
        name (str): наименование условия
        is_active (bool): признак активности нового условия
        test_MSISDN (int): тестовый номер условия
        macro_region_ids (list[int]): идентификаторы макрорегионов
        phone_number_class_condition_ids (list[int]): идентификаторы условий шаблонов классов номеров

        Returns:
        list[dict]: список объектов с информацией об условиях шаблона разметки классов номеров
        """
        payload = {"macroRegionIds": self.macro_region_ids}
        if name:
            payload["name"] = name
        if is_active is not None:
            payload["isActive"] = is_active
        if test_MSISDN:
            payload["testMSISDN"] = test_MSISDN
        if phone_number_class_condition_ids:
            payload["phoneNumberClassConditionIds"] = phone_number_class_condition_ids
        get_info = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/{template_id}/conditions/search",
            data=payload,
        )
        self.check_response_status(get_info, 200, "Не удалось получить список условий шаблона класса номеров")
        return get_info.json()["items"]

    @allure.step("API: Удаление условия шаблона класса номеров")
    def remove_rule_templates(self, template_id: int, condition_ids: list[int]) -> APIResponse:
        """
        Метод удаляет условие шаблона класса номеров

        Parameters:
        template_id (int): идентификатор шаблона класса номеров
        condition_ids list[int]: идентификатор условия шаблона класса номеров

        Returns:
        APIResponse: объект ответа API с массивом конфликтов, возникших при удалении условия
        """
        payload = {"macroRegionId": self.macro_region_id}
        if condition_ids:
            payload["phoneNumberClassConditionIds"] = condition_ids
        remove_rule = self.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/{template_id}/conditions/deleteBulk",
            data=payload,
        )
        self.check_response_status(remove_rule, 200, "Не удалось удалить условие шаблона класса номеров")
        return remove_rule

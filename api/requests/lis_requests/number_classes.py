import allure
from playwright.sync_api import APIRequestContext, APIResponse

from common.helpers.env_helper import BASE_URL_LIS


class NumberClassesRequests:
    """
    Класс для управления классами номеров, шаблонами классов номеров и условиями шаблонов с помощью api запросов
    """
    def __init__(self, api_request_auth_context: APIRequestContext):
        self.api_request_auth_context = api_request_auth_context

    @allure.step("Добавление нового элемента в справочник 'Классы номеров'")
    def add_number_class(self, name: str, macro_region_id: int = 1, service_provider_id: int = None,
                         active: bool = None) -> int:
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
        payload = {
            "name": name,
            "macroRegionId": macro_region_id
        }
        if service_provider_id:
            payload["serviceProviderId"] = service_provider_id
        if active:
            payload["active"] = active
        add_class = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/ps/v1/logicalResources/private/numberClasses", data=payload)
        assert add_class.status == 201, (f"Не удалось добавить класс номеров, ошибка: {add_class.status} "
                                         f"{add_class.json().get('userMessage', add_class.text())}")
        return add_class.json()['numberClassId']

    @allure.step("Получение списка классов номеров")
    def get_list_number_class(self, name: str = None, ids: list[int] = None, macro_region_ids: list[int] = (0, 1),
                              active: bool = None) -> list[dict]:
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
        payload = {"macroRegionIds": macro_region_ids}
        if name:
            payload["name"] = name
        if ids:
            payload["ids"] = ids
        if active:
            payload["numberClassIds"] = active
        get_info = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/dictionaries/logicalResources/numberClasses/search", data=payload)
        assert get_info.status == 200, (f"Не удалось получить список классов номеров, ошибка: {get_info.status} "
                                        f"{get_info.json().get('userMessage', get_info.text())}")
        return get_info.json()['items']

    @allure.step("Удаление элемента справочника 'Классы номеров'")
    def remove_number_class(self, number_class_id: int):
        """
        Метод удаляет элемент справочника 'Классы номеров'

        Parameters:
        number_class_id (int): идентификатор класса номера
        """
        params = {"macroRegionId": 1}
        remove_class = self.api_request_auth_context.delete(
            url=f"{BASE_URL_LIS}/ps/v1/logicalResources/private/numberClasses/{number_class_id}", params=params)
        assert remove_class.status == 204, (f"Не удалось удалить класс номеров, ошибка: {remove_class.status} "
                                            f"{remove_class.json().get('userMessage', remove_class.text())}")

    @allure.step("Добавление шаблона разметки классов номеров")
    def add_number_class_template(self, name: str, number_class_id: int, priority: int, is_default: bool = False,
                                  macro_region_id: int = 1) -> int:
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
            "macroRegionId": macro_region_id
        }
        add_template = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates", data=payload)
        assert add_template.status == 201, (f"Не удалось добавить шаблон разметки классов номеров, ошибка: "
                                            f"{add_template.status} "
                                            f"{add_template.json().get('userMessage', add_template.text())}")
        return add_template.json()['phoneNumberClassTemplateId']

    @allure.step("Получение списка шаблонов разметки классов номеров")
    def get_list_number_class_template(self, name: str = None, number_class_id: int = None, priority: int = None,
                                       is_default: bool = None, macro_region_ids: list[int] = 1,
                                       phone_number_class_template_ids: list[int] = None) -> list[dict]:
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
        payload = {"macroRegionIds": macro_region_ids}
        if name:
            payload["name"] = name
        if number_class_id:
            payload["numberClassId"] = number_class_id
        if priority:
            payload["priority"] = priority
        if is_default:
            payload["isDefault"] = is_default
        if phone_number_class_template_ids:
            payload["phoneNumberClassTemplateIds"] = phone_number_class_template_ids
        get_info = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/search", data=payload)
        assert get_info.status == 200, (f"Не удалось получить список шаблонов разметки классов номеров , ошибка: "
                                        f"{get_info.status} {get_info.json().get('userMessage', get_info.text())}")
        return get_info.json()['items']

    @allure.step("Удаление шаблона классов номеров")
    def remove_number_class_template(self, template_ids: list[int]) -> APIResponse:
        """
        Метод удаляет шаблон разметки классов номеров

        Parameters:
        template_ids list[int]: идентификатор шаблона разметки классов номеров

        Returns:
        APIResponse: объект ответа API с массивом конфликтов, возникших при удалении шаблона
        """
        payload = {"macroRegionId": 1}
        if template_ids:
            payload["phoneNumberClassTemplateIds"] = template_ids
        remove_template = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/deleteBulk", data=payload)
        assert remove_template.status == 200, (f"Не удалось удалить шаблон разметки классов номеров, ошибка: "
                                               f"{remove_template.status} "
                                               f"{remove_template.json().get('userMessage', remove_template.text())}")
        return remove_template

    @allure.step("Добавление условия в шаблон для разметки класса номера")
    def add_template_rule(self, template_id: int, name: str, condition: str, is_active: bool = True,
                          test_MSISDN: int = None, macro_region_id: int = 1) -> int:
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
            "macroRegionId": macro_region_id
        }
        if test_MSISDN:
            payload["testMSISDN"] = test_MSISDN
        add_rule = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/{template_id}/conditions",
            data=payload)
        assert add_rule.status == 201, (f"Не удалось добавить условие шаблона класса номеров, ошибка: "
                                        f"{add_rule.status} {add_rule.json().get('userMessage', add_rule.text())}")
        return add_rule.json()['phoneNumberClassConditionId']

    @allure.step("Получение списка условий шаблона класса номеров")
    def get_list_rule_templates(self, template_id: int, name: str = None, is_active: bool = None,
                                test_MSISDN: int = None, macro_region_ids: list[int] = 1,
                                phone_number_class_condition_ids: list[int] = None) -> list[dict]:
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
        payload = {"macroRegionIds": macro_region_ids}
        if name:
            payload["name"] = name
        if is_active:
            payload["isActive"] = is_active
        if test_MSISDN:
            payload["testMSISDN"] = test_MSISDN
        if phone_number_class_condition_ids:
            payload["phoneNumberClassConditionIds"] = phone_number_class_condition_ids
        get_info = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/{template_id}/conditions/search",
            data=payload)
        assert get_info.status == 200, (f"Не удалось получить список условий шаблона класса номеров, ошибка: "
                                        f"{get_info.status} {get_info.json().get('userMessage', get_info.text())}")
        return get_info.json()['items']

    @allure.step("Удаление условия шаблона класса номеров")
    def remove_rule_templates(self, template_id: int, condition_ids: list[int]) -> APIResponse:
        """
        Метод удаляет условие шаблона класса номеров

        Parameters:
        template_id (int): идентификатор шаблона класса номеров
        condition_ids list[int]: идентификатор условия шаблона класса номеров

        Returns:
        APIResponse: объект ответа API с массивом конфликтов, возникших при удалении условия
        """
        payload = {"macroRegionId": 1}
        if condition_ids:
            payload["phoneNumberClassConditionIds"] = condition_ids
        remove_rule = self.api_request_auth_context.post(
            url=f"{BASE_URL_LIS}/OAPI/v1/lis/logicalResources/phoneNumberClassTemplates/{template_id}/conditions/deleteBulk",
            data=payload)
        assert remove_rule.status == 200, (f"Не удалось удалить условие шаблона класса номеров, ошибка: "
                                           f"{remove_rule.status} "
                                           f"{remove_rule.json().get('userMessage', remove_rule.text())}")
        return remove_rule

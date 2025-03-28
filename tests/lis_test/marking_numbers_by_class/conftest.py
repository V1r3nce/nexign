import pytest
from playwright.sync_api import APIRequestContext

from api.requests.lis_requests.number_classes import NumberClassesRequests
from api.requests.lis_requests.phone_numbers import PhoneNumbersRequests
from common.helpers.data_generator import generate_random_number


@pytest.fixture
def add_and_remove_class(api_request_auth_context: APIRequestContext) -> dict:
    """Фикстура для создания и удаления класса номеров"""
    number_classes_api = NumberClassesRequests(api_request_auth_context)
    class_name = "Скидочный" + str(generate_random_number(3))
    class_id = number_classes_api.add_number_class(name=class_name)
    yield class_name, class_id
    if number_classes_api.get_list_number_class(ids=[class_id]):
        number_classes_api.remove_number_class(class_id)


@pytest.fixture
def add_and_remove_template(add_and_remove_class: dict, api_request_auth_context: APIRequestContext) -> dict:
    """Фикстура для создания и удаления шаблона разметки классов номеров"""
    number_classes_api = NumberClassesRequests(api_request_auth_context)
    class_name, class_id = add_and_remove_class
    template_name = class_name + "_DEF"
    template_id = number_classes_api.add_number_class_template(
        name=template_name, number_class_id=class_id, priority=50, is_default=True
    )
    yield class_name, template_name, template_id
    if number_classes_api.get_list_number_class_template(phone_number_class_template_ids=[template_id]):
        number_classes_api.remove_number_class_template([template_id])


@pytest.fixture
def add_and_remove_rule(add_and_remove_template: dict, api_request_auth_context: APIRequestContext) -> dict:
    """Фикстура для создания и удаления условия шаблона класса номеров"""
    number_classes_api = NumberClassesRequests(api_request_auth_context)
    class_name, template_name, template_id = add_and_remove_template
    rule_name = "AABCDEFGHI" + str(generate_random_number(3))
    rule_id = number_classes_api.add_template_rule(
        template_id=template_id, name=rule_name, condition=":1 = :2", test_MSISDN=9912346745
    )
    yield class_name, template_name, rule_name
    if number_classes_api.get_list_rule_templates(template_id=template_id, phone_number_class_condition_ids=[rule_id]):
        number_classes_api.remove_rule_templates(template_id=template_id, condition_ids=[rule_id])


@pytest.fixture
def remove_number_class(api_request_auth_context: APIRequestContext) -> str:
    """Фикстура для удаления класса, созданного в тесте"""
    number_classes_api = NumberClassesRequests(api_request_auth_context)
    class_name = "Скидочный" + str(generate_random_number(3))
    yield class_name
    classes = number_classes_api.get_list_number_class(name=class_name)
    if classes:
        class_id = classes[0]["numberClassId"]
        number_classes_api.remove_number_class(class_id)


@pytest.fixture
def add_class_and_remove_template(add_and_remove_class: dict, api_request_auth_context: APIRequestContext) -> dict:
    """Фикстура для удаления шаблона разметки классов номеров, созданного в тесте"""
    number_classes_api = NumberClassesRequests(api_request_auth_context)
    class_name, class_id = add_and_remove_class
    template_name = class_name + "_DEF"
    yield class_name, template_name
    templates = number_classes_api.get_list_number_class_template(name=template_name)
    if templates:
        template_id = templates[0]["phoneNumberClassTemplateId"]
        number_classes_api.remove_number_class_template([template_id])


@pytest.fixture
def add_template_and_remove_rule(add_and_remove_template: dict, api_request_auth_context: APIRequestContext) -> dict:
    """Фикстура для удаления условия шаблона класса номеров, созданного в тесте"""
    number_classes_api = NumberClassesRequests(api_request_auth_context)
    _, template_name, template_id = add_and_remove_template
    rule_name = "AABCDEFGHI" + str(generate_random_number(3))
    yield template_name, rule_name
    rules = number_classes_api.get_list_rule_templates(template_id=template_id, name=rule_name)
    if rules:
        rule_id = rules[0]["phoneNumberClassConditionId"]
        number_classes_api.remove_rule_templates(template_id=template_id, condition_ids=[rule_id])


@pytest.fixture
def lock_phone_number(api_request_auth_context: APIRequestContext) -> None:
    """Фикстура устанавливает блокировку для случайного номера телефона, если в системе нет заблокированных номеров"""
    phone_number_api = PhoneNumbersRequests(api_request_auth_context)
    reserved_numbers = phone_number_api.get_phone_numbers(is_reserved=True).json()["items"]
    if not reserved_numbers:
        number_id = phone_number_api.get_phone_numbers(state_id=[2, 4], status_id=[1], is_reserved=False).json()[
            "items"
        ][0]["phoneNumberId"]
        phone_number_api.lock_phone_numbers([number_id])

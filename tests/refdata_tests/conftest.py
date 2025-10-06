from typing import Callable

import pytest
from playwright.sync_api import APIRequestContext, Page

from api.rfd_requests.references_requests import ReferenceRequests
from common.helpers.env_helper import BASE_URL_RFD, UserData
from pages.locators.rfd_locators.home_element_rfd import HomeElementsRfd
from pages.locators.rfd_locators.login_page_rfd import LoginFormRfd


@pytest.fixture(scope="function")
def stand_login_rfd(page: Page) -> Page:
    page.goto(f"{BASE_URL_RFD}/ps/refdata/")
    login_page = LoginFormRfd(page)
    home_page = HomeElementsRfd(page)
    login_page.LOGIN.fill(UserData.login)
    login_page.PASSWORD.click()
    login_page.PASSWORD.type(UserData.password)
    login_page.SUBMIT.click()
    home_page.REFDATA_LOGO.wait_to_be_visible(timeout=6000)
    yield home_page.page


@pytest.fixture
def remove_reference_test_elements(api_request_context: APIRequestContext) -> Callable[[str, str, str, str], None]:
    """
    Фикстура для регистрации тестовых элементов справочника, которые будут удалены после завершения теста.
    Используется для автоматического восстановления имён элементов справочника после теста.

    Возвращает:
        Callable: Функцию register_elements_for_store , которую можно использовать для регистрации элементов.

    Использование:
        Добавьте вызов фикстуры в тест и используйте её для регистрации элементов, которые нужно вернуть после теста.
    """
    items_to_remove = []

    def register_elements_for_store(reference_name: str, item_code: str, ru_name: str, en_name: str):
        """
        Регистрирует элемент справочника, который будет восстановлен после теста.
        :param reference_name: Название справочника
        :param item_code: Код элемента справочника
        :param ru_name: Новое русское имя элемента
        :param en_name: Новое английское имя элемента
        """
        items_to_remove.append((reference_name, item_code, ru_name, en_name))

    yield register_elements_for_store

    reference_api = ReferenceRequests(api_request_context)
    for reference_name, item_code, ru_name, en_name in items_to_remove:
        reference_api.update_reference_item_name(reference_name, item_code, ru_name, en_name)

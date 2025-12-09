import re

import allure
import pytest

from pages.base_page import BasePage
from pages.locators.nbss.home_page_elements import HomePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Навигация и проверка разделов")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestInquiriesNavigation:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.home_page = HomePage()

    @allure.title("Отображение всех полей поиска на титульной оболочке")
    @allure.id(681617)
    def test_navigate_to_inquiries_and_check_search_fields(self):
        with allure.step("Проверка нахождения на главной странице"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible(timeout=10000)

        with allure.step("Открытие бургер-меню и переход в раздел 'Заявки'"):
            self.home_page.BURGER_MENU.select_by_value("Заявки")

        with allure.step("Проверка успешного перехода в раздел 'Заявки'"):
            self.base_page.expect_title(re.compile(".*Nexign UI.*"))

        with allure.step("Проверка отображения поля 'Абонент' на титульной строке"):
            self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible(timeout=10000)
            test_subscriber = "79001234567"
            self.home_page.HEADER_SUBSCRIBER.fill(test_subscriber)

        with allure.step("Проверка отображения поля 'Лицевой счет' на титульной строке"):
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible()
            test_account = "12345678"
            self.home_page.HEADER_ACCOUNT_NUM.fill(test_account)

        with allure.step("Проверка отображения кнопки 'Найти' (лупа)"):
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_visible()
            self.home_page.HEADER_SEARCH_BTN.wait_to_be_enabled()

    @allure.title("Отображение поля Абонент на титульной оболочке")
    @allure.id(681683)
    def test_check_subscriber_field_on_title_bar(self):
        with allure.step("Проверка нахождения на главной странице"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible(timeout=10000)

        with allure.step("Открытие бургер-меню и переход в раздел 'Заявки'"):
            self.home_page.BURGER_MENU.select_by_value("Заявки")

        with allure.step("Проверка успешного перехода в раздел 'Заявки'"):
            self.base_page.expect_title(re.compile(".*Nexign UI.*"))

        with allure.step("Проверка отображения поля 'Абонент' на титульной оболочке"):
            self.home_page.HEADER_SUBSCRIBER.wait_to_be_visible(timeout=10000)

        with allure.step("Проверка возможности ввода в поле 'Абонент'"):
            test_subscriber = "79001234567"
            self.home_page.HEADER_SUBSCRIBER.fill(test_subscriber)

        with allure.step("Проверка, что поле 'Абонент' активно"):
            self.home_page.HEADER_SUBSCRIBER.wait_to_be_enabled()

    @allure.title("Отображение поля Лицевой счет на титульной оболочке")
    @allure.id(681682)
    def test_check_account_number_field_on_title_bar(self):
        with allure.step("Проверка нахождения на главной странице"):
            self.home_page.CUSTOMER_NAME.wait_to_be_visible(timeout=10000)

        with allure.step("Открытие бургер-меню и переход в раздел 'Заявки'"):
            self.home_page.BURGER_MENU.select_by_value("Заявки")

        with allure.step("Проверка успешного перехода в раздел 'Заявки'"):
            self.base_page.expect_title(re.compile(".*Nexign UI.*"))

        with allure.step("Проверка отображения поля 'Лицевой счет' на титульной оболочке"):
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_visible(timeout=10000)

        with allure.step("Проверка возможности ввода в поле 'Лицевой счет'"):
            test_account = "12345678"
            self.home_page.HEADER_ACCOUNT_NUM.fill(test_account)

        with allure.step("Проверка, что поле 'Лицевой счет' активно"):
            self.home_page.HEADER_ACCOUNT_NUM.wait_to_be_enabled()

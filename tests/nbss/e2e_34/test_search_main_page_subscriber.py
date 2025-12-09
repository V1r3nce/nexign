import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.helpers.data_generator import generate_random_number
from models.user import IndividualClient
from pages.locators.nbss.client.client_search import ClientSearch
from pages.locators.nbss.home_page_elements import HomePage
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchMainPageSubscriber:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePage()
        self.client_search = ClientSearch()
        self.client_profile = ClientProfilePage()
        self.client_request_api = ClientInquiriesRequests()

    @allure.title("Валидация поля 'Абонент' — корректный формат")
    @allure.id(517432)
    @allure.description(
        "Проверить, что при вводе значения до 15 символов поиск выполняется корректно по полному совпадению номера/логина абонента"
    )
    def test_subscriber_field_validation_positive(self, create_individual_user: IndividualClient) -> None:
        with allure.step("Создание абонента"):
            inquiry = self.client_request_api.product_sale(create_individual_user)

        self.client_profile.search_from_main_page(subscriber=inquiry.product.phone_number)

        with allure.step("Проверка результатов поиска"):
            self.client_search.FOUNDED_FIO.wait_to_be_visible(timeout=15000)
            found_count = self.client_search.FOUNDED_FIO.elements_len()
            assert found_count > 0, "Список найденных клиентов пуст"
            self.client_search.FOUNDED_FIO[0].click()

        with allure.step("Проверка абонента в профиле клиента"):
            self.client_profile.locators.CLIENT_FIO_BTN.wait_to_be_visible()
            self.client_profile.locators.PRODUCTS_TAB.click()
            self.client_profile.locators.SUBSCRIBER.wait_to_have_text(inquiry.product.phone_number)

    @allure.title("Валидация поля 'Абонент'— некорректное заполнение поля")
    @allure.id(517438)
    @allure.description("Проверить, что при вводе некорректного значения происходит переход на страницу 'Поиск'")
    def test_subscriber_field_validation_wrong_num(self) -> None:
        wrong_subscriber = f"{generate_random_number(15)}%$&"

        self.client_profile.search_from_main_page(subscriber=wrong_subscriber)

        with allure.step("Проверка, что результаты поиска не найдены"):
            self.client_search.FOUNDED_FIO.wait_not_to_be_visible()

        with allure.step("Проверка, что некорректное значение сохранено в поле"):
            self.client_search.SUBSCRIPTION_ID.to_have_value(wrong_subscriber)

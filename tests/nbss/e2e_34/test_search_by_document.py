import allure
import pytest

from models.client import IndividualClient
from pages.nbss.home_page import HomePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchByDocument:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.home_page = HomePage()

    @allure.title("Поиск по серии и номеру документа")
    @allure.id(680915)
    def test_search_individual_by_document(self, create_individual_user: IndividualClient) -> None:
        client = create_individual_user

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.home_page.go_to_search_and_clear_filters()

        with allure.step(f"Поиск клиента по документу: серия '{client.document_serial}', номер '{client.document_num}'"):
            self.home_page.search_client(document_series=client.document_serial, document_number=client.document_num)

        with allure.step("Проверка, что клиент найден"):
            self.home_page.verify_client_found(client)

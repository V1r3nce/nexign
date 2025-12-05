import allure
import pytest

from models.user import OrganizationClient
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchByInnKpp:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()

    @allure.title("Поиск по ИНН")
    @allure.id(680972)
    def test_search_organization_by_inn(self, create_organization: OrganizationClient) -> None:
        client = create_organization

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Поиск клиента по ИНН '{client.inn}'"):
            self.client_profile_page.search_client(inn=client.inn)

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(client)
            self.client_profile_page.client_search_page.FOUNDED_CUSTOMER_STATUS[0].to_contain_text("Действующий")

    @allure.title("Поиск по ИНН и КПП")
    @allure.id(680974)
    def test_search_organization_by_inn_and_kpp(self, create_organization: OrganizationClient) -> None:
        client = create_organization

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Ввод ИНН '{client.inn}'"):
            self.client_profile_page.client_search_page.INN_INPUT.fill(client.inn)

        with allure.step(f"Ввод КПП '{client.kpp}'"):
            self.client_profile_page.client_search_page.KPP.fill(client.kpp)

        with allure.step("Запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(client)

    @allure.title("Поиск по КПП")
    @allure.id(680973)
    def test_search_organization_by_kpp(self, create_organization: OrganizationClient) -> None:
        client = create_organization

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Ввод наименования клиента '{client.customer_name}'"):
            self.client_profile_page.client_search_page.CUSTOMER_NAME_INPUT.fill(client.customer_name)

        with allure.step(f"Ввод КПП '{client.kpp}'"):
            self.client_profile_page.client_search_page.KPP.fill(client.kpp)

        with allure.step("Запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(client)

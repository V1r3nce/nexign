import allure
import pytest

from models.context import test_context
from models.user import OrganizationClient
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchByAccount:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_ui_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()

    @allure.title("Поиск по номеру лицевого счета")
    @allure.id(680913)
    def test_search_client_by_account_number(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        agreement = test_context.client.get_agreement()
        account = agreement.accounts[0]

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Поиск клиента по номеру лицевого счета '{account.number}'"):
            self.client_profile_page.search_client(account_number=str(account.number))

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(test_context.client)

    @allure.title("Поиск по номеру лицевого счета с указанием статуса")
    @allure.id(681497)
    def test_search_client_by_account_with_status(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        agreement = test_context.client.get_agreement()
        account = agreement.accounts[0]

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Ввод номера лицевого счета '{account.number}'"):
            self.client_profile_page.client_search_page.ACCOUNT_NUM.fill(str(account.number))

        with allure.step("Выбор неправильного статуса 'Закрыт'"):
            self.client_profile_page.client_search_page.ACCOUNT_STATUSES.select_by_value("Закрыт", check=False)

        with allure.step("Запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка, что клиент НЕ найден"):
            self.client_profile_page.client_search_page.FOUNDED_CLIENTS.not_to_be_visible(timeout=5000)

        with allure.step("Очистка статуса"):
            self.client_profile_page.client_search_page.ACCOUNT_STATUSES.clear_select()

        with allure.step("Выбор статуса 'Действующий'"):
            self.client_profile_page.client_search_page.ACCOUNT_STATUSES.select_by_value("Действующий", check=False)

        with allure.step("Повторный запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(test_context.client)

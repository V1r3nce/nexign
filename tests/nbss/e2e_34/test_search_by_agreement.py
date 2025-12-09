import allure
import pytest

from common.helpers.time_helpers import delay
from models.context import test_context
from models.user import OrganizationClient
from pages.nbss.client.client_profile_page import ClientProfilePage


@pytest.mark.regress
@pytest.mark.nbss_portal
@allure.epic("E2E_34 Поиск клиента/абонента")
@allure.suite("E2E_34 Поиск клиента/абонента")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=674672853", name="Поиск клиента/абонента")
class TestSearchByAgreement:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.client_profile_page = ClientProfilePage()

    @allure.title("Поиск по номеру договора")
    @allure.id(680919)
    def test_search_organization_by_agreement_number(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        agreement = test_context.client.get_agreement()

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Поиск клиента по номеру договора '{agreement.number}'"):
            self.client_profile_page.search_client(agreement_number=agreement.number)

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(test_context.client)

    @allure.title("Поиск по номеру договора с указанием статуса")
    @allure.id(681000)
    def test_search_organization_by_agreement_with_status(
        self, create_organization_with_agreement_and_account: OrganizationClient
    ) -> None:
        delay(1, "Клиент перешел в статус действующий")
        agreement = test_context.client.get_agreement()

        with allure.step("Переход на страницу расширенного поиска и очистка фильтров"):
            self.client_profile_page.go_to_search_and_clear_filters()

        with allure.step(f"Ввод номера договора '{agreement.number}'"):
            self.client_profile_page.client_search_page.CONTRACT_NUM.fill(agreement.number)

        with allure.step("Выбор неправильного статуса 'Закрыт'"):
            self.client_profile_page.client_search_page.CONTRACT_STATUS.select_by_value("Закрыт", check=False)

        with allure.step("Запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка, что клиент НЕ найден"):
            self.client_profile_page.client_search_page.FOUNDED_CLIENTS.not_to_be_visible(timeout=5000)

        with allure.step("Очистка статуса"):
            self.client_profile_page.client_search_page.CONTRACT_STATUS.clear_select()

        with allure.step("Выбор статуса 'Оформлен'"):
            self.client_profile_page.client_search_page.CONTRACT_STATUS.select_by_value("Оформлен", check=False)

        with allure.step("Повторный запуск поиска"):
            self.client_profile_page.client_search_page.SEARCH_BTN.click()

        with allure.step("Проверка результатов поиска"):
            self.client_profile_page._verify_client_found(test_context.client)

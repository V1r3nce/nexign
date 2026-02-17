import allure
import pytest

from common.helpers.data_generator import generate_random_number
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient
from models.context import test_context
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.client_groups_search_page import ClientGroupsSearchPage


@allure.epic("E2E_64 Создание и управление клиентом и его иерархиями")
@allure.suite("E2E_64 Создание и управление клиентом и его иерархиями")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestManageClientGroups:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login) -> None:
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.client_groups_search_page = ClientGroupsSearchPage()

        self.client_group_name = f"Группа клиентов {generate_random_number(10)}"
        self.client_group_type = "Холдинг"
        self.client_group_comment = "Комментарий"
        self.client_role = "Дочерняя компания"

    @allure.title("Создание группы клиентов")
    @allure.id(757399)
    def test_add_client_group(self) -> None:
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Поиск группы клиентов")

        self.client_groups_search_page.create_client_group(
            self.client_group_name, self.client_group_type, self.client_group_comment
        )
        self.client_groups_search_page.check_client_group(
            self.client_group_name, self.client_group_type, self.client_group_comment
        )

    @allure.title("Редактирование группы клиентов")
    @allure.id(757465)
    def test_edit_client_group(self) -> None:
        client_group_name_updated = self.client_group_name + " updated"
        client_group_comment_updated = self.client_group_comment + " updated"

        self.client_profile_page.locators.BURGER_MENU.select_by_value("Поиск группы клиентов")

        self.client_groups_search_page.create_client_group(
            self.client_group_name, self.client_group_type, self.client_group_comment
        )
        self.client_groups_search_page.edit_client_group(client_group_name_updated, client_group_comment_updated)
        self.client_groups_search_page.check_client_group(
            client_group_name_updated, self.client_group_type, client_group_comment_updated
        )

    @allure.title("Добавление клиентов в группы")
    @allure.id(757571)
    def test_add_clients_to_groups(self, create_organization: OrganizationClient) -> None:
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Поиск группы клиентов")
        self.client_groups_search_page.create_client_group(
            self.client_group_name, self.client_group_type, self.client_group_comment
        )

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

        self.client_profile_page.click_tab("Группы клиентов")
        self.client_profile_page.add_client_to_client_group(self.client_group_name, self.client_role)

        self.client_profile_page.locators.CLIENT_GROUP_LIST[0].wait_to_have_text(self.client_group_name)

    @allure.title("Удаление клиента из группы")
    @allure.id(757605)
    def test_delete_client_from_group(self, create_organization: OrganizationClient) -> None:
        self.client_profile_page.locators.BURGER_MENU.select_by_value("Поиск группы клиентов")
        self.client_groups_search_page.create_client_group(
            self.client_group_name, self.client_group_type, self.client_group_comment
        )

        self.base_page.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible(timeout=15000)

        self.client_profile_page.click_tab("Группы клиентов")
        self.client_profile_page.add_client_to_client_group(self.client_group_name, self.client_role)

        self.client_profile_page.locators.CLIENT_GROUP_LIST.click(0)
        self.client_profile_page.locators.DELETE_CLIENT_FROM_GROUP_BTN.click()
        self.client_profile_page.locators.MODAL_SECOND_BTN.click()

        self.client_profile_page.locators.CLIENT_GROUP_LIST.wait_to_have_count(0)

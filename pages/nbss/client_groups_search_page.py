import allure

from pages.base_page import BasePage
from pages.locators.nbss.client_group_search_elements import ClientGroupsSearchElements


class ClientGroupsSearchPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientGroupsSearchElements()

    @allure.step("Создать группу клиентов с именем {1}, типом {2}, комментарием {3}")
    def create_client_group(self, client_group_name: str, client_group_type: str, client_group_comment: str) -> None:
        self.locators.ADD_BTN.wait_to_be_visible(timeout=15000)
        self.locators.ADD_BTN.click()
        self.locators.NAME_INPUT.wait_to_be_visible(timeout=15000)
        self.locators.NAME_INPUT.fill(client_group_name)
        self.locators.TYPE_SELECT.select_by_value(client_group_type)
        self.locators.COMMENT_INPUT.fill(client_group_comment)
        self.locators.CREATE_BTN.click()

    @allure.step("Отредактировать группу клиентов: Наименование {1}, Комментарий {2}")
    def edit_client_group(self, client_group_name: str, client_group_comment: str) -> None:
        self.locators.EDIT_BTN.wait_to_be_visible(timeout=15000)
        self.locators.EDIT_BTN.click()
        self.locators.EDIT_NAME_INPUT.wait_to_be_visible()
        self.locators.EDIT_NAME_INPUT.fill(client_group_name)
        self.locators.EDIT_COMMENT_INPUT.fill(client_group_comment)
        self.locators.CREATE_BTN.click()

    @allure.step("Проверить значения группы клиентов. Наименование {1}, Тип {2}, Комментарий {3}")
    def check_client_group(self, client_group_name: str, client_group_type: str, client_group_comment: str) -> None:
        self.locators.GROUP_NAME.wait_to_have_text("Группа клиентов: " + client_group_name)
        self.locators.GROUP_TYPE.wait_to_have_text(client_group_type)
        self.locators.COMMENT.to_have_value(client_group_comment)

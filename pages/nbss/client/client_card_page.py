import allure

from common.helpers.env_helper import BASE_URL
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import ClientProfileElements


class ClientCardPage(BasePage):
    """Страница /customers/{client_id}/customer 'Клиент' в карточке клиента."""

    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProfileElements()

    @allure.step("Открыть вкладку 'Клиент' по адресу карточки клиента")
    def open_client_card(self, client_id: int) -> None:
        """Открыть вкладку 'Клиент' карточки клиента по прямому адресу.

        :param client_id: id клиента
        """
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{client_id}/customer")

    @allure.step("Открыть вкладку 'Клиент'")
    def open_client_tab(self) -> None:
        """Открыть вкладку 'Клиент' и дождаться загрузки её атрибутов."""
        self.locators.CLIENT_TAB.click()
        self.locators.FIO.wait_to_be_visible(timeout=15000)

    @allure.step("Проверить атрибуты клиента на вкладке 'Клиент'")
    def check_client_attributes(
        self,
        inn: str | None = None,
        surname: str | None = None,
        document_num: str | None = None,
    ) -> None:
        """Сверить атрибуты клиента на уже открытой вкладке 'Клиент'.

        :param inn: ожидаемый ИНН; None — не проверять
        :param surname: ожидаемая фамилия; None — не проверять
        :param document_num: ожидаемый номер документа; None — не проверять
        """
        if inn is not None:
            self.locators.INN.to_have_value(inn)
        if surname is not None:
            self.locators.FIO.to_contain_value(surname)
        if document_num is not None:
            self.locators.DOCUMENT_SERIAL_AND_NUM.to_contain_value(document_num)

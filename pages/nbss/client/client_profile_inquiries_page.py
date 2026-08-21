import allure

from common.helpers.env_helper import BASE_URL
from pages.base_page import BasePage
from pages.locators.nbss.client.client_profile import ClientProfileElements


class ClientProfileInquiriesPage(BasePage):
    """Страница /customers/{client_id}/inquiries 'Заявки' в карточке клиента."""

    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProfileElements()

    @allure.step("Открыть последнюю заявку клиента")
    def open_last_client_inquiry(self, client_id: int) -> None:
        """Открыть список заявок клиента, дождаться их появления и перейти в последнюю заявку.

        :param client_id: id клиента
        """
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{client_id}/inquiries")
        self.locators.REQUEST_NUMBER.wait_to_be_visible(timeout=15000)
        self.locators.REQUEST_NUMBER[-1].click()

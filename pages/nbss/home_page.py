import allure

from models.client import IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.client.client_search import ClientSearchElements
from pages.locators.nbss.home_page_elements import HomePageElements


class HomePage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.locators = HomePageElements()
        self.client_search_page = ClientSearchElements()

    def _navigate_to_client_search(self) -> None:
        self.locators.HEADER_SEARCH_BTN.click()

    def go_to_search_and_clear_filters(self) -> None:
        self._navigate_to_client_search()
        self._clear_all_filters()

    @allure.step("Поиск с главной страницы")
    def search_from_main_page(
        self,
        customer_name: str = None,
        inn: str = None,
        account_number: str | int = None,
        subscriber: str = None,
        clear_and_research: bool = True,
    ) -> None:
        """
        Выполняет поиск с главной страницы, заполняет соответствующие поля,
        нажимает поиск, ждет загрузки страницы поиска.
        Если clear_and_research=True, очищает фильтры и повторно выполняет поиск.
        """
        with allure.step("Проверка отображения полей на главной странице"):
            self.locators.HEADER_SEARCH_BTN.wait_to_be_visible()

        search_values = []
        with allure.step("Заполнение полей поиска на главной странице"):
            if customer_name:
                self.locators.CUSTOMER_NAME.wait_to_be_visible()
                self.locators.CUSTOMER_NAME.fill(customer_name)
                search_values.append(f"Клиент: '{customer_name}'")
            if inn:
                self.locators.INN.wait_to_be_visible()
                self.locators.INN.fill(inn)
                search_values.append(f"ИНН: '{inn}'")
            if account_number:
                self.locators.HEADER_ACCOUNT_NUM.wait_to_be_visible()
                self.locators.HEADER_ACCOUNT_NUM.fill(str(account_number))
                search_values.append(f"Лицевой счет: '{account_number}'")
            if subscriber:
                self.locators.HEADER_SUBSCRIBER.wait_to_be_visible()
                self.locators.HEADER_SUBSCRIBER.fill(subscriber)
                search_values.append(f"Абонент: '{subscriber}'")

        with allure.step(f"Выполнение поиска с главной страницы ({', '.join(search_values)})"):
            self.locators.HEADER_SEARCH_BTN.click()

        with allure.step("Проверка перехода на форму расширенного поиска"):
            self.client_search_page.TITLE.wait_to_have_text("Поиск клиента", timeout=10000)
            self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()

        if clear_and_research:
            with allure.step("Очистка предзаполненных фильтров и выполнение поиска"):
                self._clear_all_filters()
                self.client_search_page.SEARCH_BTN.click()

    def _clear_all_filters(self) -> None:
        self.client_search_page.TITLE.wait_to_be_visible()
        self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_visible()
        self.client_search_page.CUSTOMER_STATUSES.clear_select()
        self.client_search_page.ACCOUNT_STATUSES.clear_select()
        self.client_search_page.CONTRACT_STATUS.clear_select()

    @allure.step("Поиск клиента")
    def search_client(
        self,
        customer_name: str = None,
        inn: str = None,
        kpp: str = None,
        account_number: str = None,
        agreement_number: str = None,
        document_series: str = None,
        document_number: str = None,
        customer_status: str = None,
        account_status: str = None,
        contract_status: str = None,
    ) -> None:
        self._clear_all_filters()
        if customer_name:
            self.client_search_page.CUSTOMER_NAME_INPUT.fill(customer_name)
        if inn:
            self.client_search_page.INN_INPUT.fill(inn)
        if account_number:
            self.client_search_page.ACCOUNT_NUM.fill(account_number)
        if agreement_number:
            self.client_search_page.CONTRACT_NUM.fill(agreement_number)
        if document_series:
            self.client_search_page.ID_DOCUMENT_SERIAL.fill(document_series)
        if document_number:
            self.client_search_page.ID_DOCUMENT_NUM.fill(document_number)
        if customer_status:
            self.client_search_page.CUSTOMER_STATUSES.select_by_value(customer_status, check=False)
        if account_status:
            self.client_search_page.ACCOUNT_STATUSES.select_by_value(account_status, check=False)
        if contract_status:
            self.client_search_page.CONTRACT_STATUS.select_by_value(contract_status, check=False)
        if kpp:
            self.client_search_page.KPP_INPUT.fill(kpp)

        self.client_search_page.SEARCH_BTN.click()

    @allure.step("Проверка, что клиент не найден")
    def verify_client_not_found(self) -> None:
        self.client_search_page.FOUNDED_CLIENTS.not_to_be_visible(timeout=5000)

    def verify_client_found(self, client: IndividualClient | OrganizationClient) -> None:
        if isinstance(client, IndividualClient):
            client_name = f"{client.sur_name} {client.first_name}"
            with allure.step(f"Проверка найденного клиента: {client_name}"):
                self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible(timeout=15000)
                self.client_search_page.FOUNDED_FIO[0].to_contain_text(client.sur_name)
                self.client_search_page.FOUNDED_FIO[0].to_contain_text(client.first_name)
                self.client_search_page.FOUNDED_CUSTOMER_TYPE[0].wait_to_have_text(client.type)
        else:
            with allure.step(f"Проверка найденного клиента: {client.customer_name}"):
                self.client_search_page.FOUNDED_CLIENTS.wait_to_be_visible(timeout=15000)
                self.client_search_page.FOUNDED_FIO[0].to_contain_text(client.customer_name)
                self.client_search_page.FOUNDED_CUSTOMER_TYPE[0].wait_to_have_text(client.type)

    @allure.step("Проверка, для заполнения доступны все необходимые параметры поиска")
    def verify_input_parametrs(self) -> None:
        self.client_search_page.RESET_BTN.wait_to_be_enabled()
        self.client_search_page.CUSTOMER_NAME_INPUT.wait_to_be_enabled()
        self.client_search_page.CUSTOMER_STATUSES.wait_to_be_enabled()
        self.client_search_page.ACCOUNT_STATUSES.wait_to_be_enabled()
        self.client_search_page.ACCOUNT_NUM.wait_to_be_enabled()
        self.client_search_page.ID_DOCUMENT_SERIAL.wait_to_be_enabled()
        self.client_search_page.ID_DOCUMENT_NUM.wait_to_be_enabled()
        self.client_search_page.INN_INPUT.wait_to_be_enabled()
        self.client_search_page.KPP_INPUT.wait_to_be_enabled()
        self.client_search_page.CONTRACT_STATUS.wait_to_be_enabled()
        self.client_search_page.SUBSCRIPTION_ID.wait_to_be_enabled()
        self.client_search_page.NUM_LINES_INPUT.wait_to_be_enabled()
        self.client_search_page.SERIAL_NUM_EQUIPMENT.wait_to_be_enabled()

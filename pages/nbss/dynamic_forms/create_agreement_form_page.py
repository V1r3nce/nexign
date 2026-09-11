import allure

from models.client import EntrepreneurClient, IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ContractCreate


class CreateAgreementFormPage(BasePage):
    """Форма 'Создание договора' — открывается из карточки клиента и из заявки на продажу."""

    def __init__(self) -> None:
        super().__init__()

        self.locators = ContractCreate()

    @allure.step("Заполнить обязательные поля формы создания договора и нажать 'Создать'")
    def fill_and_save(
        self,
        client: OrganizationClient | IndividualClient | EntrepreneurClient,
        signing_date: str | None = None,
        with_client_bank_details: bool = True,
    ) -> None:
        """Заполнить уже открытую форму создания договора и сохранить её.

        :param client: клиент, чьи реквизиты и ФИО представителя оператора подставляются
        :param signing_date: ожидаемая предзаполненная дата подписания; None — не проверять
        :param with_client_bank_details: заполнять ли банковские реквизиты клиента
        """
        if signing_date is not None:
            self.locators.CONTRACT_SIGN_DATE.wait_to_be_visible(timeout=15000)
            self.locators.CONTRACT_SIGN_DATE.to_have_value(signing_date)
        self.locators.OPERATOR_FIO.select_by_value(client.operator_name)
        self.locators.OPERATOR_BANK_DATA.select_by_value(client.operator_bank_details)
        if with_client_bank_details:
            self.locators.USE_EXISTING_BANK_CHECKBOX.click()
            self.locators.CLIENT_BANK_CURRENT_ACCOUNT.fill(client.bank_account)
            self.locators.CLIENT_BANK.select_by_value(client.bank_name)
        self.locators.SAVE_BTN.click()

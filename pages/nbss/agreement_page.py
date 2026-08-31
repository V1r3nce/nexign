from pathlib import Path

import allure

from common.helpers.download_helper import CheckFile
from models.context import test_context
from pages.base_page import BasePage
from pages.locators.nbss.agreement_form import AgreementFormElements
from pages.locators.nbss.client.client_profile import ClientProfileElements
from pages.locators.nbss.dynamic_form_elements import DynamicForms


class AgreementPage(BasePage):
    """Страница /customer-hierarchy-management/agreements/{agreementId}/agreement"""

    def __init__(self) -> None:
        super().__init__()
        self.locators = AgreementFormElements()
        self.client_profile = ClientProfileElements()
        self.dynamic_form = DynamicForms()

    @allure.step("Заполнить данные при подписании договора")
    def fill_sign_agreement_form(
        self, signing_date: str, client_representative_name: str | None, file_path: list[Path]
    ) -> None:
        self.locators.SIGNING_DATE.fill(signing_date)
        self.locators.CLIENT_REPRESENTATIVE_NAME.select_by_value(client_representative_name)
        self.locators.OPERATOR_REPRESENTATIVE_NAME.select_by_value("Иванов Иван Иванович", timeout_sec=10)
        self.locators.ATTACH_DOCUMENT_FIELD.upload_files(file_path)

    @staticmethod
    def create_agreement_text_file(file_name: str) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        with open(file_path, "w") as file:
            file.write("Тестовый договор")
        file_check.is_exist()
        return file_path

    @allure.step("Открыть вкладку 'Документы' и проверить, что создано {expected_count} документа(ов)")
    def open_documents_tab_and_check_count(self, expected_count: int = 2) -> None:
        self.locators.TAB_DOCUMENT.wait_to_be_visible()
        self.locators.TAB_DOCUMENT.click()
        self.locators.DOCUMENTS_TABLE_CELLS.wait_to_have_count(expected_count, timeout=10000)

    @allure.step("Заполнить данные при создании договора")
    def fill_data_create_agreement(self) -> None:
        if test_context.client is None:
            raise ValueError("В test_context не задан клиент")
        if test_context.client.type != "b2c":
            self.dynamic_form.CLIENT_BANK_DETAILS_CHBX.click()
            self.dynamic_form.CLIENT_BANK_CURRENT_ACCOUNT.fill(test_context.client.bank_account)
            self.dynamic_form.CLIENT_BANK.select_by_value(test_context.client.bank_name)
        self.dynamic_form.OPERATOR_BANK_DETAILS.select_by_value(test_context.client.operator_bank_details)
        self.dynamic_form.OPERATOR_AGENT_FIO.select_by_value("Иванов Иван Иванович")

    @allure.step("Подписать договор: загрузить документ и нажать 'Подписать'")
    def sign_agreement(
        self,
        signing_date: str,
        client_representative_name: str,
        file_name: str,
        downloaded_files: list,
    ) -> None:
        """Нажимает 'Подписать договор', заполняет форму подписания и подписывает договор.

        :param signing_date: дата подписания
        :param client_representative_name: ФИО представителя клиента (связанное лицо)
        :param file_name: имя создаваемого файла договора
        :param downloaded_files: список файлов для удаления после теста
        """
        self.client_profile.SIGN_AGREEMENT_BTN.click()
        self.locators.TITLE.wait_to_be_visible(timeout=15000)
        file_path = self.create_agreement_text_file(file_name)
        self.fill_sign_agreement_form(signing_date, client_representative_name, [file_path])
        downloaded_files.append(file_path)
        self.locators.SIGN_ACCEPT_BTN.click()
        self.locators.TITLE.not_to_be_visible(timeout=15000)

from pathlib import Path

import allure

from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
from pages.locators.nbss.agreement_form import AgreementFormElements


class AgreementPage(BasePage):
    """Страница /customer-hierarchy-management/agreements/{agreementId}/agreement"""

    def __init__(self) -> None:
        super().__init__()
        self.locators = AgreementFormElements()

    @allure.step("Заполнить данные при подписании договора")
    def fill_sign_agreement_form(
        self, signing_date: str, client_representative_name: str | None, file_path: list[Path]
    ) -> None:
        self.locators.SIGNING_DATE.fill(signing_date)
        self.locators.CLIENT_REPRESENTATIVE_NAME.select_by_value(client_representative_name)
        self.locators.OPERATOR_REPRESENTATIVE_NAME.select_by_value("Иванович Иван Иванов")
        self.locators.ATTACH_DOCUMENT_FIELD.upload_files(file_path)

    @staticmethod
    def create_agreement_text_file(file_name: str) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        with open(file_path, "w") as file:
            file.write("Тестовый договор")
        file_check.is_exist()
        return file_path

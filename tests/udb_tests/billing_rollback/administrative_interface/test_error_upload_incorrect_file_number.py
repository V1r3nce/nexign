import allure
import pytest
from playwright.sync_api import Page

from pages.udb_pages.billing_tasks_page import BillingTasksPage


@pytest.mark.usefixtures("stand_login_udb")
class TestErrorUploadIncorrectFileNumber:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.billing_tasks_page = BillingTasksPage(page)

    @allure.suite("E2E_85 Откат биллинга")
    @allure.title("Ошибка при загрузке файла с несуществующим номером ЛС")
    @allure.id(578871)
    @allure.description(
        'Появление сообщения об ошибке при попытке загрузить файл с несуществующим номером ЛС на форме "Задание на откат биллинга"'
    )
    @allure.link(url="jira.nexign.com/browse/TUDS-2569", name="TUDS-2569")
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=555189386", name="Откат биллинга по клиенту")
    @pytest.mark.regress
    def test_error_upload_incorrect_file_number(self, page: Page, base_url: str, remove_file_from_download_folder: list):
        with allure.step(
            'Перейти в форму "Биллинговые задания", нажать кнопку "Новое задание", выбрать из выпадающего списка "Задание на откат"'
        ):
            self.billing_tasks_page.locators.TABLE_ROW.wait_to_be_visible()
            self.billing_tasks_page.locators.NEW_TASK_BTN.wait_to_be_visible()

            self.billing_tasks_page.locators.NEW_TASK_BTN.click()
            self.billing_tasks_page.locators.ROLLBACK_TASK_OPTION.click()
            self.billing_tasks_page.locators.ROLLBACK_FORM_TITLE.wait_to_be_visible()

        with allure.step(
            'Выбрать "Выбор профилей" "Из файла", выбрать вручную подготовленный файл и дождаться окончания загрузки файла'
        ):
            self.billing_tasks_page.locators.FROM_FILE_BTN.click()

            file_name = "account_file_csv"
            account_id = 000000
            file_path = self.billing_tasks_page.create_csv_file_with_accoind_id(file_name, account_id)

            remove_file_from_download_folder.append(file_path)

            with self.billing_tasks_page.page.expect_file_chooser() as fc_info:
                self.billing_tasks_page.locators.FILE_UPLOAD_BTN.click()
            file_chooser = fc_info.value
            file_chooser.set_files(file_path)

            self.billing_tasks_page.locators.ERROR_BODY.wait_to_be_visible()
            self.billing_tasks_page.locators.ERROR_BODY.to_contain_text("Возникла пользовательская ошибка")

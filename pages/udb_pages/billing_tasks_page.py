from pathlib import Path

import allure
import pandas as pd
from playwright.sync_api import Page

from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
from pages.locators.udb_locators.billing_tasks import BillingTasks


class BillingTasksPage(BasePage):
    """Страница /tasks Биллинговые задания"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = BillingTasks(page)

    @allure.step("Создать файл для создания задания на откат биллинга")
    def create_csv_file_with_account_id(self, file_name: str, account_id: int | str | None = None) -> str | Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        df = pd.DataFrame([[account_id]]) if account_id is not None else pd.DataFrame()
        df.to_csv(file_path, sep=";", index=False, header=False)
        file_check.is_exist()
        return file_path

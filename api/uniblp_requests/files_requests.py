import allure

from api.base_requests import BaseRequests
from api.exceptions import UniblpFileProcessingTimeoutError
from common.helpers.checker import wait_that
from common.helpers.env_helper import BASE_URL_UNIBLP


class FilesUniblpRequests(BaseRequests):
    @allure.step("API: Получение списка файлов")
    def get_files_list(self, limit: int = 100) -> dict:
        response = self.post(f"{BASE_URL_UNIBLP}/API/files/search?limit={limit}")
        self.check_response_status(response, 200, "Не удалось получить список файлов")
        return response.json()

    @allure.step("API: Получение статуса последнего файла")
    def get_last_file_status(self) -> dict | None:
        files_list = self.get_files_list()
        items = files_list.get("items", [])

        if not items:
            return None

        last_file = items[0]

        return last_file.get("fileStatusName")

    @allure.step("API: Ожидание обработки файла")
    def wait_for_file_processed(self, timeout: int = 120, sleep_seconds: int = 5) -> None:
        wait_that(
            lambda: self.get_last_file_status() == "Обработан",
            timeout=timeout,
            sleep_seconds=sleep_seconds,
            exception=UniblpFileProcessingTimeoutError,
            message=f"Файл не перешёл в статус 'Обработан' за {timeout} секунд",
        )

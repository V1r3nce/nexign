import allure

from pages.base_page import BasePage
from pages.locators.uniblp_locators.home_elements_uniblp import HomeUniblpElements
from pages.uniblp_pages.files_page import FilesUniblpPage


class HomeUniblpPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = HomeUniblpElements()
        self.files_page = FilesUniblpPage()

    @allure.step("Открытие формы 'Файлы'")
    def open_files_tab(self) -> None:
        self.locators.FILES.wait_to_be_enabled()
        self.locators.FILES.click()
        self.files_page.locators.FILES_HEADER.wait_to_be_visible()
        self.files_page.locators.FILES_HEADER.to_contain_text("Файлы")

import allure
import pytest
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number
from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from pages.refdata_pages.home_page_rfd import HomePageRfd


@allure.epic("E2E_110 Централизированное управление НСИ")
@allure.suite("Интеграция")
@pytest.mark.usefixtures("stand_login_rfd")
class TestCentralizedManagementNSI:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.home_page_rfd = HomePageRfd(page)

    @allure.title("Экспорт справочника")
    @allure.id(611224)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=683897194",
        name="КР [NBSS] Правила работы со справочниками (Стандартное)",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=776513158", name="Реестр справочников REFDATA")
    @pytest.mark.regress
    def test_export_directory(self, remove_file_from_download_folder: list):
        self.home_page_rfd.locators.SEARCH_CODE_FLD.type_and_press_enter("accountType")
        self.home_page_rfd.locators.DIRECTORY[0].click()

        with self.home_page_rfd.page.expect_download(timeout=2000) as download_info:
            self.home_page_rfd.locators.EXPORT_BNT.click()
        download = download_info.value
        file_name = download.suggested_filename
        self.file_check = CheckFile(file_name)
        download.save_as(self.file_check.path)
        remove_file_from_download_folder.append(file_name)
        self.file_check.is_exist()
        self.file_check.check_file_type(expect_type=".json")

    @allure.title("Импорт справочника")
    @allure.id(611223)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=683897194",
        name="КР [NBSS] Правила работы со справочниками (Стандартное)",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=776513158", name="Реестр справочников REFDATA")
    @pytest.mark.regress
    def test_import_directory(self, remove_file_from_download_folder: list):
        name_directory = "accountTypeExample" + str(generate_random_number(10))
        file_path = self.home_page_rfd.create_json_file_to_upload_directory(
            file_name="accountType.json", code_name_directory=name_directory
        )
        with self.home_page_rfd.page.expect_file_chooser() as fc_info:
            self.home_page_rfd.locators.IMPORT_BNT.click()
            self.home_page_rfd.locators.CHOSE_IMPORT_FILE_BTN.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

        self.home_page_rfd.locators.SUCCESS_IMPORT_BTN.wait_to_be_enabled()
        self.home_page_rfd.locators.SUCCESS_IMPORT_BTN.click(force=True)
        self.home_page_rfd.locators.SUCCESS_IMPORT_INFO.wait_to_be_visible()
        self.home_page_rfd.locators.SUCCESS_OK_BNT.click()

        remove_file_from_download_folder.append(file_path)

        self.home_page_rfd.locators.SEARCH_CODE_FLD.type_and_press_enter(name_directory)

        self.home_page_rfd.locators.DIRECTORY[0].wait_to_have_text(name_directory)
        self.home_page_rfd.locators.DIRECTORY[0].click()
        self.home_page_rfd.locators.DIRECTORY_INFORMATION.wait_to_be_visible()

        self.home_page_rfd.locators.ELEMENTS_BNT.click()
        self.home_page_rfd.locators.PUBLISH_BTN.wait_to_be_enabled()
        delay(0.2, reason="Нельзя убрать это ожидание, кнопка удаления должна прогрузиться")
        self.home_page_rfd.locators.PUBLISH_All_BTN.click()

        self.home_page_rfd.locators.NEXT_BNT_RFD.click()

    @allure.title("Ошибка удаления опубликованного элемента справочника")
    @allure.id(619337)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=683897194",
        name="КР [NBSS] Правила работы со справочниками (Стандартное)",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=776513158", name="Реестр справочников REFDATA")
    @pytest.mark.regress
    def test_error_delete_published_directory(self):
        self.home_page_rfd.locators.SEARCH_CODE_FLD.type_and_press_enter("accountType")
        delay(
            0.5,
            reason="Не успевает подтягивать данные о справчонике, завязаться на какой-либо UI-элемент нет возможности",
        )
        self.home_page_rfd.locators.DIRECTORY[0].click()
        self.home_page_rfd.locators.DIRECTORY_INFORMATION.wait_to_be_visible()
        self.home_page_rfd.locators.ELEMENTS_BNT.click()

        self.home_page_rfd.locators.ADD_ELEMENT_DIRECTORY_BTN.click()

        self.home_page_rfd.create_directory_element(type="account")
        self.home_page_rfd.locators.SAVE_OK_BTN[0].click()
        code = self.home_page_rfd.locators.COUNT_CURRENT_ELEMENT.text
        self.home_page_rfd.locators.CODE_ELEMENT_CURRENCIES_FLD.type_and_press_enter(code.strip("[]"))
        self.home_page_rfd.locators.DIRECTORY.wait_elements_visible(element_index=-1, timeout=4000)

        self.home_page_rfd.locators.DIRECTORY.to_contain_text(-1, code.strip("[]"))
        self.home_page_rfd.locators.DIRECTORY.wait_elements_visible(element_index=-1, timeout=4000)
        self.home_page_rfd.locators.DIRECTORY[-1].click()

        self.home_page_rfd.locators.PUBLISH_BTN.element_not_contain_disabled_attribute()
        self.home_page_rfd.locators.PUBLISH_BTN.click()
        self.home_page_rfd.locators.SAVE_OK_BTN.wait_elements_visible(element_index=2, timeout=2000)
        self.home_page_rfd.locators.SAVE_OK_BTN[2].click()

        self.home_page_rfd.locators.DIRECTORY.to_contain_text(-1, code.strip("[]"))
        self.home_page_rfd.locators.DIRECTORY.wait_elements_visible(element_index=-1, timeout=8000)

        self.home_page_rfd.locators.DIRECTORY[-1].click()

        delay(0.2, reason="Нельзя убрать это ожидание, кнопка удаления должна прогрузиться")
        self.home_page_rfd.locators.DELETE_ELEMENT_BTN.click()
        self.home_page_rfd.locators.CONFIRM_DELETE_ELEMENT_BTN.wait_to_be_enabled()
        self.home_page_rfd.locators.CONFIRM_DELETE_ELEMENT_BTN.click()

        self.home_page_rfd.locators.CONFIG_MESSAGE.wait_to_be_visible()

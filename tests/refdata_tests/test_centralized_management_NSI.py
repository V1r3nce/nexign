from typing import Callable

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from common.helpers.data_generator import generate_random_number
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL
from common.helpers.time_helpers import delay
from models.user import OrganizationClient
from pages.locators.dynamic_form_elements import CreateOrganization, IndividualCustomerCreate
from pages.personal_account_page import PersonalAccountPage
from pages.refdata_pages.home_page_rfd import HomePageRfd


@allure.epic("E2E_110 Централизированное управление НСИ")
@allure.suite("E2E_110 Централизированное управление НСИ")
@pytest.mark.usefixtures("stand_login_rfd")
class TestCentralizedManagementNSI:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, organization_user_data: OrganizationClient) -> None:
        self.home_page_rfd = HomePageRfd(page)
        self.personal_account_page = PersonalAccountPage(page, organization_user_data)
        self.individual_customer_create_form = IndividualCustomerCreate(page)
        self.organization_create_form = CreateOrganization(page)

    @allure.title("Изменение наименования типа сегмента")
    @allure.id(618747)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=683897194",
        name="КР [NBSS] Правила работы со справочниками (Стандартное)",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=776513158", name="Реестр справочников REFDATA")
    @pytest.mark.regress
    def test_change_name_segment_type(
        self,
        page: Page,
        api_request_auth_context: APIRequestContext,
        remove_reference_test_elements: Callable[[str, str, str, str], None],
    ) -> None:
        reference_name = "segmentTypes"
        item_code = "1"
        ru_name = "Работа с долгом"
        en_name = "Debt management"
        segment_value = "test"

        remove_reference_test_elements(reference_name, item_code, ru_name, en_name)

        self.home_page_rfd.locators.SEARCH_CODE_FLD.type_and_press_enter(reference_name)
        delay(
            0.5,
            reason="Не успевает подтягивать данные о справочнике, завязаться на какой-либо UI-элемент нет возможности",
        )
        self.home_page_rfd.locators.DIRECTORY[0].wait_to_have_text(reference_name)
        self.home_page_rfd.locators.DIRECTORY[0].click()
        self.home_page_rfd.locators.DIRECTORY_INFORMATION.wait_to_be_visible()

        self.home_page_rfd.locators.ELEMENTS_BNT.click()
        self.home_page_rfd.locators.ELEMENTS_PANEL.wait_to_be_visible()

        delay(0.1, reason="Не успевает выбрать элемент, методы ожидания не помогают")
        self.home_page_rfd.locators.DIRECTORY[1].click()
        self.home_page_rfd.locators.EDIT_ELEMENT_BTN.element_not_contain_disabled_attribute(timeout=0.5)
        self.home_page_rfd.locators.EDIT_ELEMENT_BTN.click()
        self.home_page_rfd.edit_directory_element(test_value=segment_value)

        page.goto(f"{BASE_URL}")

        self.personal_account_page.create_customer_with_type("organization")
        self.organization_create_form.SAVE_BTN.click()

        self.personal_account_page.locators.CLIENT_TAB.click()
        self.personal_account_page.locators.SEGMENTS_TAB.click()

        self.personal_account_page.locators.SEGMENTS_REFRESH_BTN.wait_to_be_visible()
        self.personal_account_page.locators.SEGMENTS_REFRESH_BTN.click()
        self.personal_account_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text(segment_value)

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
        account_value: str = "account" + str(generate_random_number(3))

        self.home_page_rfd.create_directory_element(element_type=account_value)
        self.home_page_rfd.locators.SAVE_OK_BTN[0].click()
        delay(0.2, reason="Нужно подождать, пока обновится поле количества элементов у справочника")
        code = self.home_page_rfd.locators.COUNT_CURRENT_ELEMENT.text
        self.home_page_rfd.locators.CODE_ELEMENT_CURRENCIES_FLD.type_and_press_enter(code.strip("[]"))
        self.home_page_rfd.locators.DIRECTORY.wait_elements_visible(element_index=-1, timeout=4000)

        self.home_page_rfd.locators.DIRECTORY.to_contain_text(-1, code.strip("[]"))
        self.home_page_rfd.locators.DIRECTORY.wait_elements_visible(element_index=-1, timeout=4000)
        self.home_page_rfd.locators.DIRECTORY[-1].click()

        self.home_page_rfd.locators.PUBLISH_BTN.element_not_contain_disabled_attribute(3)
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

    @allure.title("Создание справочника")
    @allure.id(611221)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=683897194",
        name="КР [NBSS] Правила работы со справочниками (Стандартное)",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=776513158", name="Реестр справочников REFDATA")
    @pytest.mark.regress
    def test_create_directory(self):
        code_directory = "test" + str(generate_random_number(10))
        self.home_page_rfd.locators.ADD_BNT.click()
        self.home_page_rfd.create_directory(type=code_directory)
        self.home_page_rfd.locators.SEARCH_CODE_FLD.type_and_press_enter(code_directory)
        self.home_page_rfd.locators.DIRECTORY[0].click()
        self.home_page_rfd.locators.DIRECTORY_INFORMATION.wait_to_be_visible()

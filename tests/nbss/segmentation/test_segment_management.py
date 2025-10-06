import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.nbss.segmentation_requests import SegmentationRequests
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.time_helpers import delay
from models.user import IndividualClient, OrganizationClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import EditSegmentsForm
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_17 Сегментация")
@allure.suite("E2E_17 Сегментация")
@allure.link(url="jira.nexign.com/browse/TUDS-2339", name="TUDS-2339")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=742590762",
    name="CLM-471158 ГФС: ФАЗА_1 Сегментация сущностей",
)
@pytest.mark.regress
class TestSegmentManagement:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_context: APIRequestContext,
        create_organization: OrganizationClient,
        individual_user_data: IndividualClient,
    ) -> None:
        self.base_page = BasePage(nexign_ui_stand_login)
        self.client_profile_page = ClientProfilePage(nexign_ui_stand_login)
        self.current_date = get_current_datetime_string(is_full_format=False)
        self.edit_segments_form = EditSegmentsForm(nexign_ui_stand_login)
        self.segmentation_request_api = SegmentationRequests(api_request_context)
        self.personal_account_page = PersonalAccountPage(nexign_ui_stand_login, individual_user_data)
        self.client_id = create_organization.user_id

    @allure.title("01 Автоматическое определение сегмента при создании клиента")
    @allure.description("Автоматическое определение сегмента при создании клиента")
    @allure.id(587531)
    def test_auto_segment_user_create(self, base_url: str) -> None:
        with allure.step("Перейти в контекст созданного клиента"):
            self.personal_account_page.create_customer_with_type("individual")
            self.personal_account_page.dynamic_form.SAVE_BTN.click()
            self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Открыть пользовательскую ЭФ Сегменты в контексте клиента"):
            self.client_profile_page.locators.CLIENT_TAB.click()
            self.client_profile_page.locators.SEGMENTS_TAB.click()
            self.client_profile_page.locators.SEGMENTS_REFRESH_BTN.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Автоматически")

    @allure.title("Управление сегментом клиента (ручное)")
    @allure.description("Управление сегментом клиента (ручное)")
    @allure.id(587533)
    def test_manual_segment_management(self, base_url: str) -> None:
        with allure.step("Перейти в контекст созданного клиента"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_id}/overview")
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Открыть пользовательскую ЭФ Сегменты в контексте клиента"):
            self.client_profile_page.locators.CLIENT_TAB.click()
            self.client_profile_page.locators.SEGMENTS_TAB.click()
            self.client_profile_page.locators.SEGMENTS_REFRESH_BTN.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Автоматически")

        with allure.step("Перейти к форме Управление сегментами"):
            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.click()
            self.edit_segments_form.TITLE.to_contain_text("Управление сегментами")

        with allure.step("Отредактировать необходимые поля"):
            self.edit_segments_form.SEARCH_SEGMENTS_VALUE_FLD.select_by_value("B2B VIP")
            self.edit_segments_form.MANAGEMENT_TYPE_RADIO_BTN.select_by_value("Ручное назначение")
            self.edit_segments_form.SAVE_SEGMENT_BTN.click()
            delay(0.5, reason="Ожидание загрузки таблицы и сообщения")
            self.client_profile_page.locators.INFO_MESSAGE.wait_to_have_text(
                "Измененные сегменты больше не будут назначаться автоматически"
            )
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_have_text("B2B VIP")
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Вручную")

    @allure.title("Автоматическая пересегментация по сущности клиент")
    @allure.description("Автоматическая пересегментация по сущности клиент")
    @allure.id(587535)
    def test_auto_segment_management(self, base_url: str) -> None:
        with allure.step("Подготовить тестовые данные"):
            self.personal_account_page.create_customer_with_type("individual")
            self.personal_account_page.dynamic_form.SAVE_BTN.click()
            self.personal_account_page.locators.INFO_MESSAGE.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
            manual_client_id = self.personal_account_page.get_customer_id_from_url()
            self.client_profile_page.locators.CLIENT_TAB.click()
            self.client_profile_page.locators.SEGMENTS_TAB.click()
            self.client_profile_page.locators.SEGMENTS_REFRESH_BTN.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Автоматически")

            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.click()
            self.edit_segments_form.TITLE.to_contain_text("Управление сегментами")
            self.edit_segments_form.SEARCH_SEGMENTS_VALUE_FLD.select_by_value("B2C VIP")
            self.edit_segments_form.MANAGEMENT_TYPE_RADIO_BTN.select_by_value("Ручное назначение")
            self.edit_segments_form.SAVE_SEGMENT_BTN.click()
            delay(0.5, reason="Ожидание загрузки таблицы и сообщения")
            self.client_profile_page.locators.INFO_MESSAGE.wait_to_have_text(
                "Измененные сегменты больше не будут назначаться автоматически"
            )
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_have_text("B2C VIP")
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Вручную")

            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{self.client_id}/overview")
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile_page.locators.CLIENT_TAB.click()
            self.client_profile_page.locators.SEGMENTS_TAB.click()
            self.client_profile_page.locators.SEGMENTS_REFRESH_BTN.wait_to_be_visible(timeout=10000)
            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_be_visible()
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Автоматически")

            self.client_profile_page.locators.SEGMENTS_MANAGEMENT_BTN.click()
            self.edit_segments_form.TITLE.to_contain_text("Управление сегментами")
            self.edit_segments_form.SEARCH_SEGMENTS_VALUE_FLD.select_by_value("B2B VIP")
            self.edit_segments_form.SAVE_SEGMENT_BTN.click()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_have_text("B2B VIP")
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Вручную")
            clients_list = [str(manual_client_id), str(self.client_id)]
            self.segmentation_request_api.auto_segmentation(entity_type_code="customer", entity_ids=clients_list)

        with allure.step("Работа с клиентом с 'Тип управления значениями сегментов' - Автоматическое"):
            self.client_profile_page.locators.SEGMENTS_REFRESH_BTN.click()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_have_text("B2B обычный")
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Автоматически")

        with allure.step("Работа с клиентом с 'Тип управления значениями сегментов' - Ручное"):
            self.base_page.open(f"{base_url}customer-hierarchy-management/customers/{manual_client_id}/overview")
            self.client_profile_page.locators.CLIENT_FIO.wait_to_be_visible()
            self.client_profile_page.locators.CLIENT_TAB.click()
            self.client_profile_page.locators.SEGMENTS_TAB.click()
            self.client_profile_page.locators.TABLE_SEGMENT_TYPE[0].wait_to_have_text("Работа с долгом")
            self.client_profile_page.locators.TABLE_SEGMENT_VALUE[0].wait_to_have_text("B2C VIP")
            self.client_profile_page.locators.TABLE_SEGMENT_DATE[0].to_contain_text(self.current_date)
            self.client_profile_page.locators.TABLE_SEGMENT_ASSIGNED[0].wait_to_have_text("Вручную")

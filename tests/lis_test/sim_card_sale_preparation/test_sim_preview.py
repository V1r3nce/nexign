import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.data_generator import get_shifted_datetime_string
from common.helpers.download_helper import CheckFile
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.lis_pages.sim_card_page import SimCardsPage
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
@pytest.mark.regress
@pytest.mark.lis
@pytest.mark.nbss_portal
class TestSimCardsPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis: Page) -> None:
        self.base_page = BasePage(stand_login_lis)
        self.home_page_lis = HomeElementsLis(stand_login_lis)
        self.sim_cards_page = SimCardsPage(stand_login_lis)

    @allure.title("Просмотр списка SIM-карт")
    @allure.id(578445)
    @allure.description("Просмотр списка SIM-карт")
    def test_sim_card_preview(self, api_request_context: APIRequestContext) -> None:
        sim_requests = SimCardsRequests(api_request_context)
        sims = sim_requests.get_sim_card_list()
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.REFRESH_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.REFRESH_BTN.click()

        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(3)
        self.sim_cards_page.sim_cards_elements.TABLE_LINE[0].to_have_class(class_name=re.compile(r"js-selected"))
        self.sim_cards_page.sim_cards_elements.TABLE_LINE[3].to_have_class(class_name=re.compile(r"js-selected"))
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_cards_page.sim_cards_elements.NUMBERS_COUNTER.to_contain_text("Всего*")
        self.sim_cards_page.sim_cards_elements.NUMBERS_COUNTER.to_contain_text(str(sims.json()["listInfo"]["count"]))
        self.sim_cards_page.sim_cards_elements.REFRESH_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.wait_to_be_visible()

    @allure.title("Просмотр списка SIM-карт (Выгрузка в файл)")
    @allure.id(578468)
    @allure.description("Просмотр списка SIM-карт (Выгрузка в файл)")
    @pytest.mark.skip(reason="https://jira.nexign.com/browse/TUDS-5439")
    def test_sim_card_preview_download_file(
        self, api_request_context: APIRequestContext, remove_file_from_download_folder: list
    ) -> None:
        sim_requests = SimCardsRequests(api_request_context)
        sims = sim_requests.get_sim_card_list()
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.REFRESH_BTN.click()
        self.sim_cards_page.sim_cards_elements.CHECK_ALL_BTN.click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.DOWNLOAD_BTN.hover()
        self.sim_cards_page.sim_cards_elements.DOWNLOAD_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL[0].wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[0].to_contain_text("Подтверждение операции")
        with self.sim_cards_page.page.expect_download(timeout=20000) as download_info:
            self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[0].click()
        download = download_info.value
        file_name = download.suggested_filename
        self.file_check = CheckFile(file_name)
        download.save_as(self.file_check.path)
        remove_file_from_download_folder.append(file_name)
        self.file_check.check_excel_file_group_of_fields_contains([[0, 0], [0, 1], [0, 2]], ["IMSI", "ICC", "MSISDN"])
        self.file_check.check_excel_file_contain_filled_rows(sims.json()["listInfo"]["count"] + 1)

    @allure.title("Просмотр списка SIM-карт (Изменение срока действия SIM-карты)")
    @allure.id(580313)
    @allure.description("Просмотр списка SIM-карт (Изменение срока действия SIM-карты)")
    def test_sim_card_preview_change_expiration_date(self) -> None:
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.BLOCKING_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.NOT_BLOCKED_OPTION.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.EDIT_EXPIRATION_DATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Изменение срока действия")
        new_date = get_shifted_datetime_string("+500d", is_full_format=False)
        self.sim_cards_page.sim_cards_elements.CONFIRM_CHANGE_EXPIRATION_DATE_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.MODAL_SECOND_BTN[-1].wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.MODAL_EXPIRATION_DATE_INPUT.type(new_date)
        self.sim_cards_page.sim_cards_elements.CONFIRM_CHANGE_EXPIRATION_DATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.EXPIRATIONS_DATES.to_contain_text(0, new_date)

    @allure.title("Просмотр списка SIM-карт (История SIM-карты)")
    @allure.id(578868)
    @allure.description("Просмотр списка SIM-карт (История SIM-карты)")
    def test_sim_card_history(self, api_request_context: APIRequestContext) -> None:
        sim_requests = SimCardsRequests(api_request_context)
        sims = sim_requests.get_sim_card_list(state_id=[10])
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS.wait_to_have_count(19)
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS[16].click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.HISTORY_BTN.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text(f"История по IMSI {sims_data[0].imsi}")
        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.REFRESH_MODAL_TABLE_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN[0].to_contain_text("LIS")
        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN[1].to_contain_text("Greenfield")
        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN[2].to_contain_text("Операций")

        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN[0].element_have_css_color("background", "dark_green")
        self.sim_cards_page.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS[0].wait_to_have_text(
            re.compile(r"Занят|Свободен|Недоступен")
        )
        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN[2].click()
        self.sim_cards_page.sim_cards_elements.HISTORY_TYPE_BTN[2].element_have_css_color("background", "dark_green")
        self.sim_cards_page.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS.wait_to_be_visible()
        delay(0.5, reason="Ожидание для обновления строки")
        self.sim_cards_page.sim_cards_elements.TABLE_FIRST_COLUMN_ELEMENTS[0].wait_to_have_text(re.compile(r"\d{1,5}"))

    @allure.title("Просмотр списка SIM-карт (История SIM-карты, Несколько карт)")
    @allure.id(578872)
    @allure.description("Просмотр списка SIM-карт (История SIM-карты, Несколько карт)")
    def test_sim_cards_history_btn(self) -> None:
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.REFRESH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(1)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.HISTORY_BTN.check_attribute_by_value("disabled", "disabled")
        self.sim_cards_page.sim_cards_elements.HISTORY_BTN.click()
        delay(1, reason="Чтобы наверняка убедиться, что окно истории не открылась")
        self.sim_cards_page.sim_cards_elements.MODAL.wait_not_to_be_visible()

    @allure.title("Просмотр списка SIM-карт (Передача SIM-карт дилеру)")
    @allure.id(584968)
    @allure.description("Просмотр списка SIM-карт (Передача SIM-карт дилеру)")
    def test_sim_cards_send_to_seller(self) -> None:
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_OPTION_FREE.click()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS.wait_to_have_count(19)
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS[9].click()
        self.sim_cards_page.sim_cards_elements.BLOCKING_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.NOT_BLOCKED_OPTION.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()

        self.sim_cards_page.sim_cards_elements.NUMBERS_STATUSES.to_contain_text(0, "Свободен")
        new_seller = "Торговая точка 1"
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.SEND_TO_SELLER_BTN.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Передача SIM-карт дилеру")
        self.sim_cards_page.sim_cards_elements.MODAL_OPEN_SELLER_LIST.click()
        self.sim_cards_page.choose_new_seller_name(new_seller)
        self.sim_cards_page.sim_cards_elements.MODAL_CANCEL_BTN.to_contain_text("Отменить")
        self.sim_cards_page.sim_cards_elements.MODAL_SEND_BTN.to_contain_text("Передать")
        self.sim_cards_page.sim_cards_elements.MODAL_SEND_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            ' Операция "Передача SIM-карт дилеру" будет выполнена для выбранных записей (1). Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.SELLER_FIELDS.to_contain_text(0, new_seller)

    @allure.title("Просмотр списка SIM-карт (Связывание SIM-карт с коммутатором)")
    @allure.id(584261)
    @allure.description("Просмотр списка SIM-карт (Связывание SIM-карт с коммутатором)")
    def test_sim_cards_change_commutator(self) -> None:
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")

        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_OPTION_FREE.click()
        self.sim_cards_page.sim_cards_elements.BLOCKING_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.NOT_BLOCKED_OPTION.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        new_commutator = self.sim_cards_page.get_new_commutator_name_for_first_line()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.CHOOSE_COMMUTATOR_BTN.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Выбор оборудования:")
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAME_SEARCH.fill(new_commutator)
        self.sim_cards_page.page.keyboard.press("Enter")
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE.wait_to_have_count(2)
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            ' Операция "Задать коммутатор" будет выполнена для выбранных записей (1). Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.NUMBERS_COMMUTATOR[0].wait_to_have_text(new_commutator)

    @allure.title("Просмотр списка SIM-карт (Фильтрация списка)")
    @allure.id(578447)
    @allure.description("Просмотр списка SIM-карт (Фильтрация списка)")
    def test_sim_cards_filters(self, api_request_context: APIRequestContext) -> None:
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()

        self.sim_cards_page.check_search_elements()

        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_OPTIONS.to_have_text_list(
            ["По диапазону", "По количеству", "Точное значение", "Из файла"]
        )
        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.ICC_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.ICC_FILTER_OPTIONS.to_have_text_list(
            ["По диапазону", "По количеству", "Точное значение", "Из файла"]
        )
        self.sim_cards_page.sim_cards_elements.ICC_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.MSISDN_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.MSISDN_FILTER_OPTIONS.to_have_text_list(
            ["По диапазону", "По количеству", "Точное значение", "Из файла"]
        )

        self.sim_cards_page.sim_cards_elements.STATUS_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_OPTION_FREE.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        sim_requests = SimCardsRequests(api_request_context)
        sims = sim_requests.get_sim_card_list(status_id=[1])
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_cards_page.sim_cards_elements.HIDE_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.not_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)

        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.CHOSEN_STATUSES[0].wait_to_have_text("Свободен")

        self.sim_cards_page.sim_cards_elements.CLEAR_FILTER_BTN.click()
        sims_2 = sim_requests.get_sim_card_list()
        sims_data_2 = sim_requests.get_sim_cards_data(sims_2)
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data_2[0].imsi)

    @allure.title("Просмотр списка SIM-карт (Шаблон поиска)")
    @allure.id(578611)
    @allure.description("Просмотр списка SIM-карт (Шаблон поиска)")
    def test_sim_cards_templates(
        self, api_request_context: APIRequestContext, remove_sim_card_search_templates: None
    ) -> None:
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()

        self.sim_cards_page.sim_cards_elements.STATUS_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_OPTION_FREE.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()
        sim_requests = SimCardsRequests(api_request_context)
        sims = sim_requests.get_sim_card_list(status_id=[1])
        sims_data = sim_requests.get_sim_cards_data(sims)
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATUSES[0].wait_to_have_text("Свободен")

        self.sim_cards_page.sim_cards_elements.SAVE_SEARCH_TEMPLATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.NEW_TEMPLATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.NEW_TEMPLATE_NAME_INPUT.fill("Статус Свободен")
        self.sim_cards_page.sim_cards_elements.TEMPLATE_SAVE_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.TEMPLATE_CANCEL_BTN.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.TEMPLATE_SAVE_BTN.click()
        self.sim_cards_page.sim_cards_elements.CLEAR_FILTER_BTN.click()
        sims_without_filters = sim_requests.get_sim_card_list()
        sims_data_without_filters = sim_requests.get_sim_cards_data(sims_without_filters)
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data_without_filters[0].imsi)

        self.sim_cards_page.sim_cards_elements.CHOOSE_SEARCH_TEMPLATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.TEMPLATE_OPTIONS.to_contain_text(0, "Статус Свободен")
        self.sim_cards_page.sim_cards_elements.TEMPLATE_OPTIONS[0].click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data[0].imsi)
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATUSES[0].wait_to_have_text("Свободен")

        self.sim_cards_page.sim_cards_elements.REMOVE_TEMPLATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[0].to_contain_text(
            "Вы действительно хотите удалить шаблон?"
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.CHOOSE_SEARCH_TEMPLATE_BTN.click()
        self.sim_cards_page.sim_cards_elements.TEMPLATE_OPTIONS.wait_not_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(sims_data_without_filters[0].imsi)

    @allure.title("Просмотр списка SIM-карт (Изменение атрибутов)")
    @allure.id(580324)
    @allure.description("Просмотр списка SIM-карт (Изменение атрибутов)")
    def test_sim_card_preview_change_attribute(self) -> None:
        self.home_page_lis.SIM_CARD_BTN.wait_to_be_visible()
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATUS_OPTION_FREE.click()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS.wait_to_have_count(19)
        self.sim_cards_page.sim_cards_elements.STATE_FILTER_OPTIONS[15].click()
        self.sim_cards_page.sim_cards_elements.BLOCKING_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.NOT_BLOCKED_OPTION.click()
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.wait_to_be_visible()

        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES.click(0)
        sim_imsi = self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].text
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.EDIT_ATTRIBUTE_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Редактирование атрибутов SIM-карт")
        self.sim_cards_page.sim_cards_elements.MODAL_CHOOSE_BRAND_BTN.click(click_count=2)
        self.sim_cards_page.sim_cards_elements.BRAND_OPTION_NEXIGN.click(click_count=2)
        self.sim_cards_page.sim_cards_elements.MODAL_CHOOSE_MARKET_SEGMENT_BTN.click(click_count=2)
        self.sim_cards_page.sim_cards_elements.MARKET_SEGMENT_OPTION_B2X.click(click_count=2)
        self.sim_cards_page.sim_cards_elements.MODAL_CHANGE_ATTRIBUTE_SAVE_BTN.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE.wait_to_have_count(4)
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].wait_to_have_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()

        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_BTN.click()
        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_OPTIONS[2].wait_to_have_text("Точное значение")
        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_OPTIONS[2].click()
        self.sim_cards_page.sim_cards_elements.IMSI_FILTER_INPUT.fill(sim_imsi)
        self.sim_cards_page.sim_cards_elements.FILTER_SEARCH_BTN.click()
        self.sim_cards_page.sim_cards_elements.TABLE_LINE.wait_elements_visible(0)
        self.sim_cards_page.sim_cards_elements.BRAND_FIELDS.to_contain_text(0, "Nexign")
        self.sim_cards_page.sim_cards_elements.MARKET_SEGMENT_FIELDS.to_contain_text(0, "B2X")

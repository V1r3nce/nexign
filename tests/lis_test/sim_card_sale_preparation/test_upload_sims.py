import re

import allure
import pytest

from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.data_generator import (
    generate_random_number,
    get_datetime_from_full_time_string,
    get_shifted_datetime_string,
)
from common.helpers.time_helpers import delay
from models.context import test_context
from pages.lis_pages.sim_card_page import SimCardsPage
from pages.locators.lis_locators.home_elements_lis import HomeLisElements


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
@pytest.mark.regress
@pytest.mark.lis
@pytest.mark.nbss_portal
class TestSimCardsPreview:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis) -> None:
        self.sim_requests = SimCardsRequests()
        self.home_page_lis = HomeLisElements()
        self.sim_cards_page = SimCardsPage()

    @allure.title("Загрузка SIM-карт")
    @allure.id(583562)
    @allure.description("Загрузка SIM-карт")
    def test_sim_cards_upload(self, remove_file_from_download_folder: list) -> None:
        sims = self.sim_requests.get_sim_card_list(sim_sort="-IMSI")
        sims_data = self.sim_requests.get_sim_cards_data(sims)
        last_sims_imsi, last_sims_icc = (int(sims_data[0].imsi), int(sims_data[0].icc))
        self.home_page_lis.SIM_CARD_BTN.click()

        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].element_have_css_color("color", "dark_grey")

        self.sim_cards_page.sim_cards_elements.UPLOAD_CARDS_BTN.click()
        file_name = "load_sim_f_583562.txt"
        file_path = self.sim_cards_page.create_txt_file_to_upload_sim(
            file_name,
            [str(last_sims_imsi + 1), str(last_sims_imsi + 2)],
            [str(last_sims_icc + 1), str(last_sims_icc + 2)],
        )
        remove_file_from_download_folder.append(file_path)
        with test_context.page.expect_file_chooser() as fc_info:
            self.sim_cards_page.sim_cards_elements.UPLOAD_SIMS_INPUT.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_CHOOSE_BTN.click()
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.sim_cards_page.press_keyboard_button("Enter")
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        self.sim_cards_page.sim_cards_elements.TYPE_CHOOSE_BTN.click()
        self.sim_cards_page.sim_cards_elements.TYPE_NAMES_ADD_SIM_MODAL.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.TYPE_NAMES_ADD_SIM_MODAL[0].click(click_count=2)
        self.sim_cards_page.sim_cards_elements.TEMPLATE_INPUT_ADD_SIM_MODAL.to_contain_text(
            "Шаблон для макрорегиона NEXIGN"
        )
        new_date = get_shifted_datetime_string("+500d", is_full_format=False)
        self.sim_cards_page.sim_cards_elements.EXPIRATION_DATE_INPUT_ADD_SIM_MODAL.clear_input()
        delay(1, "Ожидание для корректного ввода даты")
        self.sim_cards_page.sim_cards_elements.EXPIRATION_DATE_INPUT_ADD_SIM_MODAL.type(new_date, delay=300)
        self.sim_cards_page.sim_cards_elements.ADD_BUTTON_ADD_SIM_MODAL.to_contain_text("Добавить")
        self.sim_cards_page.sim_cards_elements.CANCEL_BTN_ADD_SIM_MODAL.to_contain_text("Отменить")
        self.sim_cards_page.sim_cards_elements.ADD_BUTTON_ADD_SIM_MODAL.click()

        self.sim_cards_page.sim_cards_elements.OK_BTN.click()

        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS[0].wait_to_have_text(str(last_sims_imsi + 2))
        self.sim_cards_page.sim_cards_elements.ICC_NUMBERS_UPLOAD_SIMS[0].wait_to_have_text(str(last_sims_icc + 2))

    @allure.title("Ввод SIM-карт в эксплуатацию")
    @allure.id(583588)
    @allure.description("Ввод SIM-карт в эксплуатацию")
    @pytest.mark.smoke
    def test_sim_cards_start_usage(self, remove_file_from_download_folder: list) -> None:
        sims_data = self.sim_requests.get_sim_cards_data(self.sim_requests.get_sim_card_list(sim_sort="-IMSI"))
        new_sim_imsi, new_sim_icc = (int(sims_data[0].imsi) + 2, int(sims_data[0].icc) + 2)
        file_name = f"load_sim_f{generate_random_number(2)}.txt"
        new_sims_file_path = self.sim_cards_page.create_txt_file_to_upload_sim(
            file_name, [str(new_sim_imsi - 1), str(new_sim_imsi)], [str(new_sim_icc - 1), str(new_sim_icc)]
        )
        self.sim_requests.upload_sims_by_api(new_sims_file_path)
        remove_file_from_download_folder.append(new_sims_file_path)
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS[0].to_contain_text(str(new_sim_imsi))

        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES_UPLOAD_SIMS.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.START_USAGE_BTN.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            ' Операция "В эксплуатацию" будет выполнена для выбранных записей (1). Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS[0].not_to_contain_text(str(new_sim_imsi))

        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[0].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        self.sim_cards_page.sim_cards_elements.STATE_DATE_CHANGE_HEADER.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS[0].wait_to_have_text(
            re.compile(str(new_sim_imsi)), timeout=7500
        )
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATUSES[0].wait_to_have_text("Свободен")
        self.sim_cards_page.sim_cards_elements.NUMBERS_STATES[0].wait_to_have_text("Получена")

    @allure.title("Изменение оборудования")
    @allure.id(585216)
    @allure.description("Изменение оборудования")
    def test_sim_cards_change_equipment(self) -> None:
        uploaded_sims = self.sim_requests.get_downloaded_sims(sim_sort="-IMSI")
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].element_have_css_color("color", "dark_grey")

        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS[0].wait_to_have_text(
            uploaded_sims.json()["items"][0]["IMSI"]
        )
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES_UPLOAD_SIMS.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.CHANGE_COMMUTATOR_BTN.click()
        new_commutator = self.sim_cards_page.get_new_commutator_name_for_first_line_into_upload_sim(
            uploaded_sims.json()["items"][0]["equipment"]["name"]
        )
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAME_SEARCH.fill(new_commutator)
        self.sim_cards_page.press_keyboard_button("Enter")
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_TYPE_NAMES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.COMMUTATOR_SUBMIT_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            ' Операция "Задать коммутатор" будет выполнена для выбранных записей (1). Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.COMMUTATORS_UPLOAD_SIMS.to_contain_text(0, new_commutator)

    @allure.title("Изменение проект")
    @allure.id(585205)
    @allure.description("Изменение проект")
    def test_sim_cards_change_project(self, change_first_uploaded_sim_project_to_common: None) -> None:
        uploaded_sims = self.sim_requests.get_downloaded_sims(sim_sort="-IMSI")
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS.to_contain_text(
            0, uploaded_sims.json()["items"][0]["IMSI"]
        )
        self.sim_cards_page.sim_cards_elements.PROJECTS_UPLOAD_SIMS.to_contain_text(0, "Общий проект")

        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES_UPLOAD_SIMS.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.PROJECT_CHANGE_BTN.click()
        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Изменение проекта IMSI")
        self.sim_cards_page.sim_cards_elements.MODAL_DROP_DOWN_BTN.click()
        self.sim_cards_page.sim_cards_elements.PROJECT_OPTIONS_CHANGE_PROJECT_MODAL.to_have_text_list(
            ["Динамическая SIM-карта", "Общий проект", "Подменные IMSI динамических SIM-карт"]
        )
        self.sim_cards_page.sim_cards_elements.MODAL_DROP_DOWN_BTN.click()
        self.sim_cards_page.sim_cards_elements.CHECKBOX_NULL_PROJECT_MODAL.click()
        self.sim_cards_page.sim_cards_elements.SAVE_BUTTON_PROJECT_MODAL.to_contain_text("Сохранить")
        self.sim_cards_page.sim_cards_elements.CANCEL_BTN_PROJECT_MODAL.to_contain_text("Отменить")
        self.sim_cards_page.sim_cards_elements.SAVE_BUTTON_PROJECT_MODAL.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            'Значение поля "Проект" будет сброшено для всех выбранных записей. Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            ' Операция "Изменить проект" будет выполнена для выбранных записей (1). Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()

        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS.to_contain_text(
            0, uploaded_sims.json()["items"][0]["IMSI"]
        )
        self.sim_cards_page.sim_cards_elements.PROJECTS_UPLOAD_SIMS[0].to_contain_text(" ")
        self.sim_cards_page.sim_cards_elements.PROJECTS_UPLOAD_SIMS[0].not_to_contain_text("Общий проект")

    @allure.title("Изменение срока действия")
    @allure.id(585201)
    @allure.description("Изменение срока действия")
    def test_sim_cards_change_expiration_date(self) -> None:
        uploaded_sims = self.sim_requests.get_downloaded_sims(sim_sort="-IMSI")
        self.home_page_lis.SIM_CARD_BTN.click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS.wait_to_have_count(3)
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].click()
        self.sim_cards_page.sim_cards_elements.PAGE_TABS[1].element_have_css_color("color", "dark_grey")
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS.wait_to_be_visible()
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        delay(1, "Время на прямую сортировку списка")
        self.sim_cards_page.sim_cards_elements.IMSI_HEADER_UPLOAD_SIMS.click()
        self.sim_cards_page.sim_cards_elements.IMSI_NUMBERS_UPLOAD_SIMS.to_contain_text(
            0, uploaded_sims.json()["items"][0]["IMSI"]
        )
        old_datetime = get_datetime_from_full_time_string(uploaded_sims.json()["items"][0]["expirationDate"])
        self.sim_cards_page.sim_cards_elements.EXPIRATIONS_DATE_UPLOAD_SIMS.to_contain_text(
            0, old_datetime.strftime("%d.%m.%Y")
        )

        short_new_date = get_shifted_datetime_string("+3d", False, old_datetime)
        self.sim_cards_page.sim_cards_elements.LINE_CHECKBOXES_UPLOAD_SIMS.click(0)
        delay(0.3, reason="Кнопка не активна доли секунды, даже в случае enabled")
        self.sim_cards_page.sim_cards_elements.PERIOD_CHANGE_BTN.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Изменение срока действия")
        self.sim_cards_page.sim_cards_elements.NEW_DATE_INPUT_MODAL.type(short_new_date)
        self.sim_cards_page.sim_cards_elements.SAVE_BTN_DATE_MODAL.to_contain_text("Сохранить")
        self.sim_cards_page.sim_cards_elements.CANCEL_BTN_DATE_MODAL.to_contain_text("Отменить")
        self.sim_cards_page.sim_cards_elements.SAVE_BTN_DATE_MODAL.click()

        self.sim_cards_page.sim_cards_elements.MODAL_TITLE[-1].to_contain_text("Подтверждение операции")
        self.sim_cards_page.sim_cards_elements.MODAL_BODY_TEXT[-1].to_contain_text(
            ' Операция "Изменить срок действия" будет выполнена для выбранных записей (1). Выполнить операцию?'
        )
        self.sim_cards_page.sim_cards_elements.MODAL_FIRST_BTN[-1].click()

        self.sim_cards_page.sim_cards_elements.EXPIRATIONS_DATE_UPLOAD_SIMS.to_contain_text(0, short_new_date)

import re

import allure
import pytest

from api.exceptions import UpdateStatusException
from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.lis_locators.create_sim_card_elements import CreateSimCardElementsLis
from pages.locators.lis_locators.home_elements_lis import HomeElementsLis


@allure.epic("E2E_09 Подготовка SIM-карт к продаже")
@allure.suite("E2E_09 Подготовка SIM-карт к продаже")
@pytest.mark.lis
class TestCreateImsiRange:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_lis) -> None:
        self.base_page = BasePage()
        self.home_page_lis = HomeElementsLis()
        self.create_sim_card = CreateSimCardElementsLis()

    @allure.title("Формирование диапазонов IMSI (Успешное добавление, новые значения, количество)")
    @allure.id(579060)
    @allure.description("Формирование диапазонов IMSI (Успешное добавление, новые значения, количество)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_imsi_range_by_quantity(self, add_first_imsi_pool: None) -> None:
        imsi_requests = SimCardsRequests()
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("1")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.START_RANGE_INPUT.fill(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.ADD_RANGE_BTN.to_contain_text("Добавить")
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.to_contain_text("Отменить")
        self.create_sim_card.ADD_RANGE_BTN.click()
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.not_to_be_visible()

        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.create_sim_card.PROJECT_FIELDS[0].wait_to_have_text("Общий проект")
        self.create_sim_card.STATUS_FIELDS_SM[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 1))

    @allure.title("Формирование диапазонов IMSI (Успешное добавление, новые значения, диапазон)")
    @allure.id(579083)
    @allure.description("Формирование диапазонов IMSI (Успешное добавление, новые значения, диапазон)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_imsi_range_by_range(self) -> None:
        imsi_requests = SimCardsRequests()
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_RANGE_BTN.click()
        self.create_sim_card.BY_RANGE_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))

        self.create_sim_card.START_RANGE_INPUT.fill(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.fill(str(int(imsi_data[0].imsi_end) + 2))
        self.create_sim_card.QUANTITY_INPUT.to_have_value("2")
        self.create_sim_card.ADD_RANGE_BTN.to_contain_text("Добавить")
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.to_contain_text("Отменить")
        self.create_sim_card.ADD_RANGE_BTN.click()
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.not_to_be_visible()

        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.create_sim_card.PROJECT_FIELDS[0].wait_to_have_text("Общий проект")
        self.create_sim_card.STATUS_FIELDS_SM[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_end) + 2))

    @allure.title("Формирование диапазонов IMSI (Неуспешное добавление, частично повторные значения)")
    @allure.id(579082)
    @allure.description("Формирование диапазонов IMSI (Неуспешное добавление, частично повторные значения)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_imsi_range_wrong_number_partly(self) -> None:
        imsi_requests = SimCardsRequests()
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))

        self.create_sim_card.START_RANGE_INPUT.fill(imsi_data[0].imsi_end)
        self.create_sim_card.QUANTITY_INPUT.fill("2")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("2")
        self.create_sim_card.ADD_RANGE_BTN.click()

        self.create_sim_card.MODAL_TITLE.wait_to_have_count(3)
        self.create_sim_card.MODAL_TITLE[2].wait_to_have_text("Информация")
        self.create_sim_card.MODAL_BODY_TEXT[1].wait_to_have_text(
            f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - "
            f"{int(imsi_data[0].imsi_end) + 1} уже используется в"
            f" существующих блоках IMSI или SIM-картах в макрорегионе: 999"
        )
        self.create_sim_card.OK_BTN.click()

        self.create_sim_card.MODAL_TITLE[1].wait_to_have_text("Ошибка")
        self.create_sim_card.MODAL_BODY_TEXT[0].wait_to_have_text(
            f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - {int(imsi_data[0].imsi_end) + 1} уже используется в существующих"
            f" блоках IMSI или SIM-картах в макрорегионе: 1"
        )

    @allure.title("Формирование диапазонов IMSI (Неуспешное добавление, повторные значения)")
    @allure.id(579081)
    @allure.description("Формирование диапазонов IMSI (Неуспешное добавление, повторные значения)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_imsi_range_wrong_number(self) -> None:
        imsi_requests = SimCardsRequests()
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")

        self.create_sim_card.ADD_BLOCK_BTN.to_contain_text("Добавить блок")
        self.create_sim_card.REFRESH_BTN.wait_to_be_visible()
        self.create_sim_card.ADD_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Добавление блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))
        self.create_sim_card.END_RANGE_INPUT.to_have_value(str(int(imsi_data[0].imsi_end) + 1))

        self.create_sim_card.START_RANGE_INPUT.fill(imsi_data[0].imsi_end)
        self.create_sim_card.QUANTITY_INPUT.fill("1")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("1")
        self.create_sim_card.ADD_RANGE_BTN.click()

        self.create_sim_card.MODAL_TITLE.wait_to_have_count(3)
        self.create_sim_card.MODAL_TITLE[2].wait_to_have_text("Информация")
        self.create_sim_card.MODAL_BODY_TEXT[1].wait_to_have_text(
            f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - "
            f"{imsi_data[0].imsi_end} уже используется в существ"
            f"ующих блоках IMSI или SIM-картах в макрорегионе: 999"
        )
        self.create_sim_card.OK_BTN.click()

        self.create_sim_card.MODAL_TITLE[1].wait_to_have_text("Ошибка")
        self.create_sim_card.MODAL_BODY_TEXT[0].wait_to_have_text(
            f"Часть IMSI из диапазона {imsi_data[0].imsi_end} - {imsi_data[0].imsi_end} уже используется в существующих"
            f" блоках IMSI или SIM-картах в макрорегионе: 999"
        )

    @allure.title("Формирование диапазонов IMSI (Изменение статуса)")
    @allure.id(580280)
    @allure.description("Формирование диапазонов IMSI (Изменение статуса)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_imsi_range_change_status(self) -> None:
        imsi_requests = SimCardsRequests()
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")
        imsis = imsi_requests.get_imsi_pools(imsi_sort="-imsiEnd", active="Y")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.STATUS_FILTER_FIELD.click()
        self.create_sim_card.STATUS_FILTER_OPTIONS[0].click()
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        self.create_sim_card.START_RANGE_FIELDS.to_contain_text(0, imsi_data[0].imsi_start)
        self.create_sim_card.STATUS_FIELDS_SM[0].wait_to_have_text("Активный")

        self.create_sim_card.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.CHANGE_STATUS_BTN.click()
        self.create_sim_card.STATUS_FILTER_FIELD.click()
        self.create_sim_card.STATUS_FILTER_OPTIONS[1].click()
        self.create_sim_card.STATUS_FIELDS_SM[0].wait_to_have_text("Неактивный")
        self.create_sim_card.START_RANGE_FIELDS.to_contain_text(0, imsi_data[0].imsi_start)

        self.create_sim_card.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.CHANGE_STATUS_BTN.click()
        self.create_sim_card.STATUS_FILTER_FIELD.click()
        self.create_sim_card.STATUS_FILTER_OPTIONS[0].click()
        self.create_sim_card.STATUS_FIELDS_SM[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS.to_contain_text(0, imsi_data[0].imsi_start)

    @allure.title("Формирование диапазонов IMSI (Редактирование параметров)")
    @allure.id(580277)
    @allure.description("Формирование диапазонов IMSI (Редактирование параметров)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_edit_imsi_range(self) -> None:
        imsi_requests = SimCardsRequests()
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[2].click()
        self.create_sim_card.PAGE_TABS[2].element_have_css_color("color", "dark_grey")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на прямую сортировку списка")
        self.create_sim_card.START_RANGE_HEADER.click()
        delay(1, "Время на обратную сортировку списка")
        self.create_sim_card.LINE_CHECKBOXES[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.EDIT_BLOCK_BTN.click()

        imsis = imsi_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = imsi_requests.get_imsi_pool_data(imsis)
        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Редактирование блока")
        self.create_sim_card.PROJECT_VALUE.wait_to_have_text("Общий проект")
        self.create_sim_card.BY_QUANTITY_BTN.element_have_css_color("background", "dark_green")
        self.create_sim_card.START_RANGE_INPUT.to_have_value(imsi_data[0].imsi_start)
        self.create_sim_card.END_RANGE_INPUT.to_have_value(imsi_data[0].imsi_end)

        self.create_sim_card.QUANTITY_INPUT.fill("3")
        self.create_sim_card.QUANTITY_INPUT.to_have_value("3")
        self.create_sim_card.ADD_RANGE_BTN.click()
        self.create_sim_card.CANCEL_ADD_RANGE_BTN.not_to_be_visible()

        self.create_sim_card.PROJECT_FIELDS[0].wait_to_have_text("Общий проект")
        self.create_sim_card.STATUS_FIELDS_SM[0].wait_to_have_text("Активный")
        self.create_sim_card.START_RANGE_FIELDS[0].wait_to_have_text(imsi_data[0].imsi_start)
        self.create_sim_card.END_RANGE_FIELDS[0].wait_to_have_text(str(int(imsi_data[0].imsi_start) + 2))

    @allure.title("Создание заказов на изготовление SIM-карт без резервирования MSISDN")
    @allure.id(582966)
    @allure.description("Создание заказов на изготовление SIM-карт без резервирования MSISDN")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_sim_order_without_imsi_reservation(self) -> None:
        imsi_requests = SimCardsRequests()
        imsi_available = imsi_requests.get_available_for_reservation_imsis(2)
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[0].element_have_css_color("color", "dark_grey")

        self.create_sim_card.CREATE_BTN.click()
        self.create_sim_card.WITHOUT_RESERVATION_IMSI_BTN.click()

        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.fill("2")
        self.create_sim_card.PROJECT_OPEN_BTN.click()
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM.wait_to_have_count(3)
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM[1].click()
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.to_have_value(imsi_available.json()["IMSIRange"]["startIMSI"])
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.to_have_value(imsi_available.json()["IMSIRange"]["endIMSI"])
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.CANCEL_BTN.wait_to_be_visible()
        self.create_sim_card.NEXT_BTN.wait_to_be_visible()
        self.create_sim_card.NEXT_BTN.click()

        self.create_sim_card.MODAL_BODY_INPUT.fill("Autotest")
        self.create_sim_card.FORM_BTN.click()

        self.create_sim_card.OPERATIONS_TYPES.to_contain_text(0, "Изготовление SIM-карт без MSISDN")
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: imsi_requests.get_sims_creation().json()["items"][0]["state"]["name"] == "Задание выполнено",
            timeout=18,
            sleep_seconds=0.5,
            exception=UpdateStatusException,
            message="Статус не обновился в указанное время",
        )
        self.create_sim_card.REFRESH_BTN_CREATE_SIM.click()
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.create_sim_card.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.create_sim_card.PROCES_END_FIELDS.to_contain_text(0, today_date)

    @allure.title("Создание заказов на изготовление SIM-карт без резервирования MSISDN (количество больше чем IMSI)")
    @allure.id(583030)
    @allure.description(
        "Создание заказов на изготовление SIM-карт без резервирования MSISDN (количество больше чем IMSI)"
    )
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_sim_order_without_imsi_reservation_too_much(self) -> None:
        imsi_requests = SimCardsRequests()
        high_count_imsi = 1000
        imsi_available = imsi_requests.get_available_for_reservation_imsis(high_count_imsi)
        assert imsi_available is None, f"Существует указанное завышенное количество доступных imsi {high_count_imsi}"
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[0].element_have_css_color("color", "dark_grey")

        self.create_sim_card.CREATE_BTN.click()
        self.create_sim_card.WITHOUT_RESERVATION_IMSI_BTN.click()

        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.wait_to_be_enabled()
        self.create_sim_card.PROJECT_OPEN_BTN.click()
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM.wait_to_have_count(3)
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM[1].click()
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.CANCEL_BTN.wait_to_be_visible()
        self.create_sim_card.NEXT_BTN.wait_to_be_visible()

        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.fill("1000")

        self.create_sim_card.MODAL_TITLE.wait_to_have_count(3)
        self.create_sim_card.MODAL_TITLE[-1].wait_to_have_text("Информация")
        (
            self.create_sim_card.MODAL_BODY_TEXT[-1].wait_to_have_text(
                re.compile(r"Impossible to allocate range IMSI. Requested: 1000, available: {1,3}")
            )
        )

    @allure.title("Создание заказов на изготовление SIM-карт с резервирования MSISDN")
    @allure.id(582976)
    @allure.description("Создание заказов на изготовление SIM-карт с резервирования MSISDN")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_sim_order_imsi_with_msisdn_reservation(self) -> None:
        sim_requests = SimCardsRequests()
        phone_numbers = PhoneNumbersRequests()
        imsis = sim_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = sim_requests.get_imsi_pool_data(imsis)
        sim_requests.add_imsi_pools(str(int(imsi_data[0].imsi_end) + 1), str(int(imsi_data[0].imsi_end) + 2))
        phones = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
        def_data = phone_numbers.get_numbers_data(phones)
        new_number = str(int(def_data[0].MSISDN) + 1)
        new_number_2 = str(int(def_data[0].MSISDN) + 2)
        phone_numbers.add_phone_numbers(new_number, "2")
        delay(0.5, reason="Время для корректного выполнения запросов")
        phones_2 = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
        def_data_2 = phone_numbers.get_numbers_data(phones_2)
        phone_numbers.set_phone_numbers_in_use([def_data_2[0].phone_number_id, def_data_2[1].phone_number_id])

        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[0].element_have_css_color("color", "dark_grey")

        self.create_sim_card.CREATE_BTN.click()
        self.create_sim_card.WITH_IMSI_RESERVATION_BTN.click()

        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.wait_to_be_enabled()
        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.fill("2")
        self.create_sim_card.PROJECT_OPEN_BTN.click()
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM.wait_to_have_count(3)
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM[1].to_contain_text("Общий проект")
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM[1].click()
        self.create_sim_card.CHOOSE_COMMUTATOR_BTN.click()
        self.create_sim_card.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.base_page.press_keyboard_button("Enter")
        self.create_sim_card.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.create_sim_card.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        imsi_available = sim_requests.get_available_for_reservation_imsis(2)
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.to_have_value(imsi_available.json()["IMSIRange"]["startIMSI"])
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.to_have_value(imsi_available.json()["IMSIRange"]["endIMSI"])
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.NUMBER_TYPE_FIELD.click()
        self.create_sim_card.NUMBER_TYPE_OPTIONS[3].to_contain_text("Федеральная")
        self.create_sim_card.NUMBER_TYPE_OPTIONS[3].click()
        self.create_sim_card.USE_GOAL_FIELD.to_contain_text("Общий пул")
        self.create_sim_card.TAKE_FREE_AFTER_INPUT.fill("0")
        self.create_sim_card.TAKE_RESERVED_ONLY_CHECKBOX.not_to_have_class(re.compile("n-check-checkbox_checked"))
        self.create_sim_card.TEMPLATE_INPUT.to_have_value("")
        self.create_sim_card.START_MSISDN_INPUT.fill(new_number)
        self.create_sim_card.END_MSISDN_INPUT.fill(new_number_2)
        self.create_sim_card.CANCEL_BTN.wait_to_be_visible()
        self.create_sim_card.NEXT_BTN.click()

        assert self.create_sim_card.NUMBER_TYPE_CLASSES.elements_len() >= 4, "Не отражаются классы номеров"
        self.create_sim_card.NEXT_BTN.click()

        self.create_sim_card.MODAL_BODY_INPUT.fill("Autotest")
        self.create_sim_card.FORM_BTN.click()

        self.create_sim_card.OPERATIONS_TYPES.to_contain_text(0, "Изготовление SIM-карт с MSISDN")
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_creation().json()["items"][0]["state"]["name"] == "Задание выполнено",
            timeout=18,
            sleep_seconds=0.5,
            exception=UpdateStatusException,
            message="Статус не обновился в указанное время",
        )
        self.create_sim_card.REFRESH_BTN_CREATE_SIM.click()
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.create_sim_card.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.create_sim_card.PROCES_END_FIELDS.to_contain_text(0, today_date)

    @allure.title("Создание заказов на изготовление SIM-карт с резервирования MSISDN (Зарезервированы)")
    @allure.id(583142)
    @allure.description("Создание заказов на изготовление SIM-карт с резервирования MSISDN (Зарезервированы)")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_create_sim_order_imsi_with_msisdn_and_reserved_nums(self) -> None:
        sim_requests = SimCardsRequests()
        phone_numbers = PhoneNumbersRequests()
        imsis = sim_requests.get_imsi_pools(imsi_sort="-imsiEnd")
        imsi_data = sim_requests.get_imsi_pool_data(imsis)
        sim_requests.add_imsi_pools(str(int(imsi_data[0].imsi_end) + 1), str(int(imsi_data[0].imsi_end) + 2))
        phones = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
        def_data = phone_numbers.get_numbers_data(phones)
        new_number = str(int(def_data[0].MSISDN) + 1)
        new_number_2 = str(int(def_data[0].MSISDN) + 2)
        phone_numbers.add_phone_numbers(new_number, "2")
        delay(0.5, reason="Время для корректного выполнения запросов")
        phones_2 = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
        def_data_2 = phone_numbers.get_numbers_data(phones_2)
        phone_numbers.set_phone_numbers_in_use([def_data_2[0].phone_number_id, def_data_2[1].phone_number_id])
        delay(0.5, reason="Время для корректного выполнения запросов")
        phone_numbers.set_phone_numbers_reserved([def_data_2[0].phone_number_id, def_data_2[1].phone_number_id])

        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[0].element_have_css_color("color", "dark_grey")

        self.create_sim_card.CREATE_BTN.click()
        self.create_sim_card.WITH_IMSI_RESERVATION_BTN.click()

        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.wait_to_be_enabled()
        self.create_sim_card.QUANTITY_INPUT_CREATE_SIM.fill("2")
        self.create_sim_card.PROJECT_OPEN_BTN.click()
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM.wait_to_have_count(3)
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM[1].to_contain_text("Общий проект")
        self.create_sim_card.PROJECT_OPTIONS_CREATE_SIM[1].click()
        self.create_sim_card.CHOOSE_COMMUTATOR_BTN.click()
        self.create_sim_card.COMMUTATOR_TYPE_NAME_SEARCH.fill("Коммутатор_DEF")
        self.base_page.press_keyboard_button("Enter")
        self.create_sim_card.COMMUTATOR_TYPE_NAMES.wait_to_have_count(1)
        self.create_sim_card.COMMUTATOR_TYPE_NAMES[0].click(click_count=2)
        imsi_available = sim_requests.get_available_for_reservation_imsis(2)
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.to_have_value(imsi_available.json()["IMSIRange"]["startIMSI"])
        self.create_sim_card.START_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.to_have_value(imsi_available.json()["IMSIRange"]["endIMSI"])
        self.create_sim_card.END_RANGE_INPUT_CREATE_SIM.check_attribute_by_value("disabled", "disabled")
        self.create_sim_card.NUMBER_TYPE_FIELD.click()
        self.create_sim_card.NUMBER_TYPE_OPTIONS[3].to_contain_text("Федеральная")
        self.create_sim_card.NUMBER_TYPE_OPTIONS[3].click()
        self.create_sim_card.USE_GOAL_FIELD.to_contain_text("Общий пул")
        self.create_sim_card.TAKE_FREE_AFTER_INPUT.fill("0")
        self.create_sim_card.TAKE_RESERVED_ONLY_CHECKBOX.click()
        self.create_sim_card.TAKE_RESERVED_ONLY_CHECKBOX.to_have_class(re.compile("n-check-checkbox_checked"))
        self.create_sim_card.TEMPLATE_INPUT.to_have_value("")
        self.create_sim_card.START_MSISDN_INPUT.fill(new_number)
        self.create_sim_card.END_MSISDN_INPUT.fill(new_number_2)
        self.create_sim_card.CANCEL_BTN.wait_to_be_visible()
        self.create_sim_card.NEXT_BTN.click()

        assert self.create_sim_card.NUMBER_TYPE_CLASSES.elements_len() >= 4, "Не отражаются классы номеров"
        self.create_sim_card.NEXT_BTN.click()

        self.create_sim_card.MODAL_BODY_INPUT.fill("Autotest")
        self.create_sim_card.FORM_BTN.click()

        self.create_sim_card.OPERATIONS_TYPES.to_contain_text(0, "Изготовление SIM-карт с MSISDN")
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание создано")
        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_creation().json()["items"][0]["state"]["name"] == "Задание выполнено",
            timeout=18,
            sleep_seconds=0.5,
            exception=UpdateStatusException,
            message="Статус не обновился в указанное время",
        )
        self.create_sim_card.REFRESH_BTN_CREATE_SIM.click()
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание выполнено")
        today_date = get_current_datetime_string(is_full_format=False)
        self.create_sim_card.PROCES_START_FIELDS.to_contain_text(0, today_date)
        self.create_sim_card.PROCES_END_FIELDS.to_contain_text(0, today_date)

    @allure.title("Аннулирование заказов на изготовление SIM-карт")
    @allure.id(583143)
    @allure.description("Аннулирование заказов на изготовление SIM-карт")
    @allure.tag("can_auth", "success")
    @pytest.mark.regress
    def test_cancel_sim_order(self) -> None:
        self.home_page_lis.SIM_CARD_CREATE_BTN.click()
        sim_requests = SimCardsRequests()
        sim_requests.get_sims_creation()
        sim_requests.check_response_content("items[0].state.name", "==", "Задание выполнено")
        self.create_sim_card.PAGE_TABS.wait_to_have_count(3)
        self.create_sim_card.PAGE_TABS[0].wait_to_have_text("Изготовление SIM-карт")
        self.create_sim_card.PAGE_TABS[0].element_have_css_color("color", "dark_grey")

        self.create_sim_card.PROCES_START_FIELDS[0].click()
        delay(0.3, reason="Кнопка не активна доли секунды при enabled статусе")
        self.create_sim_card.CANCEL_TASK_BTN.click()

        self.create_sim_card.MODAL_TITLE[0].wait_to_have_text("Вы уверены?")
        self.create_sim_card.MODAL_BODY_TEXT[0].wait_to_have_text('Выполнить операцию "Аннулирование заказа"?')
        self.create_sim_card.MODAL_FIRST_BTN[0].click()

        delay(1, reason="Время для обработки задания")
        wait_that(
            lambda: sim_requests.get_sims_creation().json()["items"][0]["state"]["name"]
            == "Задание отменено пользователем",
            timeout=18,
            sleep_seconds=0.5,
            exception=UpdateStatusException,
            message="Статус не обновился в указанное время",
        )
        self.create_sim_card.REFRESH_BTN_CREATE_SIM.click()
        self.create_sim_card.STATUS_FIELDS.to_contain_text(0, "Задание отменено пользователем")

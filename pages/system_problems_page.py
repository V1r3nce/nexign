import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.locators.system_problems import SystemProblems
from pages.locators.dynamic_form_elements import CreateSystemProblem, TransferProcessing, FilterSettings, EditSystemProblem, SelectingReasonType
from pages.ui_elements import Element, ElementsList
from common.helpers.data_generator import get_shifted_datetime_string
from datetime import datetime
from common.helpers.time_helpers import delay
from common.helpers.string_helper import remove_parantheses

class SystemProblemsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = SystemProblems(page)
        self.add_system_problem = CreateSystemProblem(page)
        self.transfer_processing = TransferProcessing(page)
        self.filter_settings = FilterSettings(page)
        self.edit_system_problems = EditSystemProblem(page)
        self.selecting_reason_type = SelectingReasonType(page)

    @allure.step("Выбрать элемент c названием {name}")
    def choose_option_with_name(self, elements_list: ElementsList, name: str):
        elements_list.wait_to_be_visible()
        for item in range(elements_list.elements_len()):
            if elements_list.inner_html(element_index=item) == name:
                elements_list.click(element_index=item)

    @allure.step("Обработка шага {step_name}")
    def processing_step_ordinary(self, step_name: str):
        queue_option = "Обработка проблем (очередь по умолчанию)"

        self.locators.PROCESSING_DEFAULT_BTN.click(0)
        self.locators.PROCESSING_OPTION.click(-1)

        self.transfer_processing.TRANSFER_FORM.wait_to_be_visible()
        self.transfer_processing.TRANSFER_STEP_FIELD.select_by_value(step_name)
        self.transfer_processing.QUEUE_FIELD.select_by_value(queue_option)
        self.transfer_processing.HAND_OVER_BTN.click(-1)

    @allure.step("Обработка шага {step_name}")
    def processing_step_complex(self, step_name: str):
        queue_option = "Обработка проблем (очередь по умолчанию)"
        cover_note_text = "Нужно подключить интернет"

        if step_name == "Решение":
            self.locators.PROCESSING_DEFAULT_BTN.click(-1)
        else:
            self.locators.PROCESSING_DEFAULT_BTN.click(0)
        self.locators.PROCESSING_OPTION.click(-1)

        self.transfer_processing.TRANSFER_FORM.wait_to_be_visible()
        self.transfer_processing.TRANSFER_STEP_FIELD.select_by_value(step_name)
        self.transfer_processing.QUEUE_FIELD.select_by_value(queue_option)

        self.transfer_processing.PROCESS_UNTIL.fill(get_shifted_datetime_string("+1m"))
        self.transfer_processing.COVER_NOTE_FIELD.fill(cover_note_text)
        self.transfer_processing.HAND_OVER_BTN.click(-1)

    @allure.step("Проверка чекбоксов по наименованиям причин")
    def click_checkbox_by_title(self, title_list: ElementsList, checkbox_list: ElementsList, expected_title: str):
        for item in range(title_list.elements_len()):
            if title_list.inner_html(element_index=item) == expected_title:
                checkbox_list.click(element_index=item)

    def filter_type_check(self, click_value: str):
        titles_list = self.filter_settings.CHECKBOX_TITLE_LIST
        checkbox_list = self.filter_settings.CHECKBOX_LIST
        self.click_checkbox_by_title(titles_list, checkbox_list, click_value)
                
    def check_problem_names_list(self, expected_name: str):
        name_list: ElementsList = self.locators.PROBLEM_NAMES_LIST
        for name in name_list:
            name.to_contain_text(expected_name)

    @staticmethod
    def check_date(locator: Element, expected_date: datetime | str | None = None, is_full_format: bool = True):
        if locator.text == "Не регламентировано":
            return

        if expected_date is None:
            expected_date = datetime.now()
        elif isinstance(expected_date, str):
            """Провекрка строки на формат: если больше 16 символов - то формат полный"""
            if len(expected_date) > 16:
                expected_date = datetime.strptime(expected_date, "%d.%m.%Y %H:%M:%S")
            else:
                expected_date = datetime.strptime(expected_date, "%d.%m.%Y")

        if len(locator.text) > 16:
            ui_date = datetime.strptime(locator.text,"%d.%m.%Y %H:%M:%S")
        else:
            ui_date = datetime.strptime(locator.text,"%d.%m.%Y")

        difference = abs((expected_date - ui_date).total_seconds())

        minute = 60
        day = 86500
        if is_full_format:
            assert difference < minute, f"Разница между ожидаемым и полученным значением даты, ожидается: {expected_date.strftime("%d.%m.%Y %H:%M:%S")}, получено: {ui_date.strftime("%d.%m.%Y %H:%M:%S")}"
        else:
            assert difference < day, f"Разница между ожидаемым и полученным значением даты, ожидается: {expected_date.strftime("%d.%m.%Y")}, получено: {ui_date.strftime("%d.%m.%Y %H:%M:%S")}"

    def check_after_creating_problem(
        self,
        problem_type: str = "—",
        reason_type: str = "—",
        influence_potential: str = "—",
        experts: str = "Нет",
        operator_description: str = "—",
        tech_description: str = "—",
        inform_client: str = "—",
        client_type: str = "—",
        solution_planned_duration: str = "—",
        problematic_service: str = "—",
        adjustment_required: str ="Нет",
        attempts_num: str = "—",
        charges_amount: str = "—",
        service_name: str = "—",
        client_contact_again: str = "Нет",
        problem_occurrence_date: str | None = None,
        problem_region: str = "—",
        process_before_date: str = "Не регламентировано",
        creation_date: datetime | None = None,
        planned_end_date: str = "Не регламентировано",
        origin_date: str | None = None,
        priority: str | None = None,
        registered: str = "Иванов Иван Иванович",
        fact_end_date: str = "Не регламентировано",
        ):

        creation_date = creation_date or datetime.now()
        origin_date = origin_date or datetime.now()

        delay(2, reason="Список системных проблем обновляется")
        self.locators.REVIEW_PROBLEM_TYPE.to_contain_text(remove_parantheses(problem_type))
        self.locators.REVIEW_REASON_TYPE.to_contain_text(reason_type)
        self.locators.REVIEW_INFLUENCE_POTENTIAL.to_contain_text(influence_potential)
        self.locators.REVIEW_EXPERTS.to_contain_text(experts)
        self.locators.REVIEW_OPERATOR_DESCRIPTION.to_contain_text(operator_description)
        self.locators.REVIEW_TECH_DESCRIPTION.to_contain_text(tech_description)
        self.locators.REVIEW_NOTIFY_CLIENT.to_contain_text(inform_client)

        if "Технические проблемы" in self.locators.REVIEW_PROBLEM_TYPE.text:
            self.locators.REVIEW_CLIENT_TYPE.to_contain_text(client_type)
            self.locators.REVIEW_SOLUTION_PLANNED_DURATION.to_contain_text(solution_planned_duration)

        if "Тестовый тип проблем" in self.locators.REVIEW_PROBLEM_TYPE.text:
            self.locators.REVIEW_PROBLEMATIC_SERVICE.to_contain_text(problematic_service)
            self.locators.REVIEW_ADJUSTMENT_REQUIRED.to_contain_text(adjustment_required)
            self.locators.REVIEW_ATTEMPTS_NUM.to_contain_text(attempts_num)
            self.locators.REVIEW_CHARGES_AMOUNT.to_contain_text(charges_amount)
            self.locators.REVIEW_SERVICE_NAME.to_contain_text(service_name)
            self.locators.REVIEW_CLIENT_CONTACT_AGAIN.to_contain_text(client_contact_again)
            self.check_date(self.locators.REVIEW_PROBLEM_OCCURANCE_DATE, problem_occurrence_date, is_full_format=False)

        if "Другое" in self.locators.REVIEW_PROBLEM_TYPE.text:
            self.locators.REVIEW_SOLUTION_PLANNED_DURATION.to_contain_text(solution_planned_duration)
            self.locators.REVIEW_CLIENT_TYPE.to_contain_text(client_type)

        if "Покрытие\Связь" in self.locators.REVIEW_PROBLEM_TYPE.text:
            self.locators.REVIEW_SOLUTION_PLANNED_DURATION.to_contain_text(solution_planned_duration)
            self.locators.REVIEW_PROBLEM_REGION.to_contain_text(problem_region)
        
        self.check_date(self.locators.REVIEW_PROCESS_BEFORE, process_before_date)
        self.check_date(self.locators.REVIEW_CREATION_DATE, creation_date)
        self.check_date(self.locators.REVIEW_PLANNED_END_DATE, planned_end_date)
        self.check_date(self.locators.REVIEW_ORIGIN_DATE, origin_date)
        self.locators.REVIEW_PRIORITY.to_contain_text(priority)
        self.locators.REVIEW_REGISTERED.to_contain_text(registered)
        self.check_date(self.locators.REVIEW_FACT_END_DATE, fact_end_date)

    def check_after_problem_step(
        self,
        step_num: int,
        planned_end_date: datetime | str = "Не регламентировано",
        queue_option: str = "Обработка проблем (очередь по умолчанию)",
        processing_report_text : str = "—"
    ):
        all_step_names = ["Регистрация", "Решение", "Ожидание остаточных откликов на проблему", "Выполнение действий"]
        expected_steps = all_step_names[:step_num]
        
        for i, step_name in enumerate(expected_steps):
            self.locators.HISTORY_STEP_NAME_LIST.to_contain_text(element_index=i, text=step_name)

        if step_num != 1 and processing_report_text == "—":
            self.check_date(self.locators.HISTORY_END_DATE)

        self.locators.HISTORY_STEP_NAME_LIST.click(-1)

        if processing_report_text == "Проблема решена":
            self.check_date(self.locators.HISTORY_END_DATE)

        try:
            datetime.strptime(self.locators.HISTORY_STEP_CREATION_DATE.text,"%d.%m.%Y %H:%M:%S")
        except ValueError:
            raise AssertionError(f"Указан неверный формат времени создания шага: {self.locators.HISTORY_STEP_CREATION_DATE.text}. ожидался '%d.%m.%Y %H:%M:%S'")
        
        time_string = self.locators.HISTORY_DURATION.text
        parts = time_string.split()
        assert len(parts) == 6, f"Количество элементов строки '{time_string}' неверно. Ожидаемое количество: 6"
        assert int(parts[0]) >= 0 and int(parts[2]) >= 0 and int(parts[4]) >= 0, f"Невозможно преобразовать части строки в числа: {time_string}"
        assert parts[1] == "ч", f"Ошибка в еденице измерения времени для часов: {time_string}"
        assert parts[3] == "мин", f"Ошибка в еденице измерения времени для минут: {time_string}"
        assert parts[5] == "сек", f"Ошибка в еденице измерения времени для секунд: {time_string}"
        
        self.locators.HISTORY_STEP_NAME.to_contain_text(expected_steps[-1])
        self.check_date(self.locators.HISTORY_PLANNED_END_DATE, planned_end_date)
        self.locators.HISTORY_QUEUE.to_contain_text(queue_option)

        all_events_on_step = ["Регистрация", "Передача на обработку", "Возобновление обработки", "Закрытие"]
        step_events_name = self.locators.HISTORY_STEP_EVENTS

        self.locators.PROCESSING_REPORT.to_contain_text(processing_report_text)

        for i in range(step_events_name.elements_len()):
            assert step_events_name.inner_html(i) in all_events_on_step, f"Наименование события на шаге некорректно: {step_events_name.inner_html(i)}"
        



            
import pytest
import allure
from playwright.sync_api import Page

from pages.system_problems_page import SystemProblemsPage
from common.helpers.data_generator import generate_random_number, get_current_datetime_string, get_shifted_datetime_string, get_exact_day_of_current_month
from common.helpers.time_helpers import delay

@pytest.mark.usefixtures("nexign_ui_stand_login")
class TestSystemProblems:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.system_problems_page = SystemProblemsPage(page)

    @allure.suite("E2E_90 Системные проблемы")
    @allure.title("Создание системной проблемы с заполнением обязательных полей, перевод в обработку, закрытие системной проблемы")
    @allure.id(529957)
    def test_add_sp_required_fields(self, page: Page, base_url: str):
        problem_name = "Название-системной-проблемы " + str(generate_random_number(4))
        priority_name = "Высокий"
        problem_type_name = "(CF_TYPE_3) Технические проблемы"
        reason_type_name = "Авария"
        influence_potential_name = "Вся абонентская база"
        deadline_name = "Сутки"

        step_solution_name = "Решение"
        step_residual_responses_name = "Ожидание остаточных откликов на проблему"
        step_performing_actions_name = "Выполнение действий"

        modal_text = "Проблема решена"

        with allure.step('Открыть форму "Системные проблемы"'):
            page.goto(f"{base_url}common-faults-list/all")

        with allure.step('Нажать кнопку "Добавить", заполнить обязательные поля и нажать "Создать"'):
            self.system_problems_page.locators.ADD_PROBLEM_BTN.click()
            self.system_problems_page.add_system_problem.PROBLEM_NAME.fill(problem_name)
            delay(5, reason="UI может не успеть настроить базовый язык")
            self.system_problems_page.add_system_problem.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.choose_option_with_name(self.system_problems_page.selecting_reason_type.PROBLEM_TYPE_LIST, problem_type_name)
            self.system_problems_page.selecting_reason_type.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.add_system_problem.REASON_TYPE.select_by_value(reason_type_name)
            self.system_problems_page.add_system_problem.PRIORITY.select_by_value(priority_name)
            self.system_problems_page.add_system_problem.POTENTIAL.select_by_value(influence_potential_name)
            self.system_problems_page.add_system_problem.DEADLINE.select_by_value(deadline_name)
            self.system_problems_page.add_system_problem.CLEAR_OCCURANCE_DATE.click(0)
            self.system_problems_page.add_system_problem.CLEAR_END_DATE.click(0)
            self.system_problems_page.add_system_problem.INFORM_CLIENT_FIELD.clear_input()
            self.system_problems_page.add_system_problem.CREATE_PROBLEM_BTN.click(0)

        self.system_problems_page.check_after_creating_problem(
            problem_type=problem_type_name,
            influence_potential=influence_potential_name,
            solution_planned_duration=deadline_name,
            reason_type=reason_type_name,
            priority=priority_name
        )

        self.system_problems_page.locators.PROCESSING_HISTORY_TAB.click()
        self.system_problems_page.check_after_problem_step(step_num=1)

        with allure.step('Заполнить поля формы Передача на обработку для шага {step_solution_name}'):
            self.system_problems_page.processing_step_ordinary(step_solution_name)
            self.system_problems_page.check_after_problem_step(step_num=2)
        with allure.step('Заполнить поля формы Передача на обработку для шага {step_residual_responses_name}'):
            self.system_problems_page.processing_step_ordinary(step_residual_responses_name)
            self.system_problems_page.check_after_problem_step(step_num=3)
        with allure.step('Заполнить поля формы Передача на обработку для шага {step_performing_actions_name}'):
            self.system_problems_page.processing_step_ordinary(step_performing_actions_name)
            self.system_problems_page.check_after_problem_step(step_num=4)

        with allure.step('На карточке системной проблемы нажать кнопку Закрыть проблему'):   
            self.system_problems_page.locators.PROBLEM_CLOSE_DEFAULT_BTN.click()
            self.system_problems_page.locators.MODAL_FIELD.fill(modal_text)
            self.system_problems_page.locators.MODAL_CLOSE_PROBLEM_BTN.click()
            self.system_problems_page.check_after_problem_step(step_num=4, processing_report_text=modal_text)
    
    @allure.suite("E2E_90 Системные проблемы")
    @allure.title("Создание системной проблемы с заполнением всех полей, перевод в обработку, закрытие системной проблемы")
    @allure.id(540284)
    def test_add_sp_all_fields(self, page: Page, base_url: str):
        problem_name = "Тест-кейс " + str(generate_random_number(4))
        priority_name = "Низкий"
        problem_type_name = "(CF_TYPE_1) Тестовый тип проблем"
        reason_type_name = "Плановые работы"
        influence_potential_name = "Не определено"
        service_name = "Интернет"
        attempts_num = "5"
        amount_of_charges = "100 руб. 00 коп."
        inform_client_text = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос."
        technical_description_text = "Не подключен тариф"
        operator_description_text = "Не работает интернет"

        step_solution_name = "Решение"
        step_residual_responses_name = "Ожидание остаточных откликов на проблему"
        step_performing_actions_name = "Выполнение действий"
        
        modal_text = "Проблема решена"

        with allure.step('Открыть форму "Системные проблемы"'):
            page.goto(f"{base_url}common-faults-list/all")

        with allure.step('Нажать кнопку "Добавить", заполнить обязательные поля и нажать "Создать"'):
            self.system_problems_page.locators.ADD_PROBLEM_BTN.click()
            self.system_problems_page.add_system_problem.PROBLEM_NAME.fill(problem_name)
            delay(5, reason="UI может не успеть настроить базовый язык")
            self.system_problems_page.add_system_problem.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.choose_option_with_name(self.system_problems_page.selecting_reason_type.PROBLEM_TYPE_LIST, problem_type_name)
            self.system_problems_page.selecting_reason_type.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.add_system_problem.REASON_TYPE.select_by_value(reason_type_name)
            self.system_problems_page.add_system_problem.PRIORITY.select_by_value(priority_name)
            self.system_problems_page.add_system_problem.POTENTIAL.select_by_value(influence_potential_name)
            self.system_problems_page.add_system_problem.CLEAR_OCCURANCE_DATE.click(0)
            self.system_problems_page.add_system_problem.CLEAR_END_DATE.click(0)
            origin_date = get_current_datetime_string()
            planned_end_date = get_shifted_datetime_string("+1d", False)
            problem_occurance_date = get_current_datetime_string(False)
            self.system_problems_page.add_system_problem.OCCURANCE_DATE.fill(origin_date)
            self.system_problems_page.add_system_problem.PLANNED_END_DATE.fill(planned_end_date)
            is_experts = "Да"
            self.system_problems_page.add_system_problem.EXPERTS_CHECKBOX.click()
            self.system_problems_page.add_system_problem.PROBLEM_SERVICE_FIELD.fill(service_name)
            self.system_problems_page.add_system_problem.CLIENT_CONTACTS_AGAIN_RADIO_BTNS.click(0)
            self.system_problems_page.add_system_problem.PROBLEM_OCCURANCE_DATE.fill(problem_occurance_date)

            self.system_problems_page.add_system_problem.PROBLEMATIC_SERVICE_FIELD.select_by_value(service_name)
            self.system_problems_page.add_system_problem.ATTEMPTS_NUM_FIELD.fill(attempts_num)
            self.system_problems_page.add_system_problem.ADJUSTMENT_REQUIRED_RADIO_BTNS.click(0)
            self.system_problems_page.add_system_problem.AMOUNT_OF_CHARGES_FIELD.fill(amount_of_charges)

            self.system_problems_page.add_system_problem.INFORM_CLIENT_FIELD.fill(inform_client_text)
            self.system_problems_page.add_system_problem.TECHNICAL_DESCRIPTION_FIELD.fill(technical_description_text)
            self.system_problems_page.add_system_problem.OPERATOR_DESCRIPTION_FIELD.fill(operator_description_text)
            self.system_problems_page.add_system_problem.CREATE_PROBLEM_BTN.click(0)

        self.system_problems_page.check_after_creating_problem(
            problem_type=problem_type_name,
            influence_potential=influence_potential_name,
            operator_description=operator_description_text,
            inform_client=inform_client_text,
            reason_type=reason_type_name,
            experts=is_experts,
            tech_description=technical_description_text,
            problematic_service=service_name,
            adjustment_required="Да",
            attempts_num=attempts_num,
            charges_amount=amount_of_charges,
            service_name=service_name,
            problem_occurance_date=problem_occurance_date,
            client_contact_again="Да",
            process_before_date=planned_end_date,
            planned_end_date=planned_end_date,
            origin_date=origin_date,
            priority=priority_name,
        )
        self.system_problems_page.locators.PROCESSING_HISTORY_TAB.click()
        self.system_problems_page.check_after_problem_step(step_num=1, planned_end_date=planned_end_date)

        with allure.step('Заполнить поля формы Передача на обработку для шага {step_solution_name}'):
            self.system_problems_page.processing_step_complex(step_solution_name)
            self.system_problems_page.check_after_problem_step(step_num=2, planned_end_date=get_shifted_datetime_string("+1m", True))
        with allure.step('Заполнить поля формы Передача на обработку для шага {step_residual_responses_name}'):
            self.system_problems_page.processing_step_complex(step_residual_responses_name)
            self.system_problems_page.check_after_problem_step(step_num=3, planned_end_date=get_shifted_datetime_string("+1m", True))
        with allure.step('Заполнить поля формы Передача на обработку для шага {step_performing_actions_name}'):
            self.system_problems_page.processing_step_complex(step_performing_actions_name)
            self.system_problems_page.check_after_problem_step(step_num=4, planned_end_date=get_shifted_datetime_string("+1m", True))

        with allure.step('На карточке системной проблемы нажать кнопку Закрыть проблему'):
            self.system_problems_page.locators.PROBLEM_CLOSE_DEFAULT_BTN.click()
            self.system_problems_page.locators.MODAL_FIELD.fill(modal_text)
            self.system_problems_page.locators.MODAL_CLOSE_PROBLEM_BTN.click()
            self.system_problems_page.check_after_problem_step(step_num=4, planned_end_date=get_shifted_datetime_string("+1m", True), processing_report_text=modal_text)

    @allure.suite("E2E_90 Системные проблемы")    
    @allure.title("Проверка фильтров системных проблем")
    @allure.id(540285)
    def test_add_sp_and_checking_filters(self, page: Page, base_url: str):
        problem_name = "Тест-кейс-фильтры " + str(generate_random_number(4))
        priority_name = "Средний"
        problem_type_name = "(CF_TYPE_4) Другое"
        reason_type_name = "Другое"
        influence_potential_name = "от 100 и более"
        client_type = "Юридическое лицо"
        deadline_name = "Более суток"
        inform_client_text = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос."
        
        problems_status = "Активные"
        active_background_color = "green"
        filter_reason_type = "(CF_TYPE_4) Другое"
        filter_another_reason_type = "(CF_TYPE_2) Покрытие\Связь"

        filter_problem_type = "Другое"
        filter_another_problem_type = "Плановые работы"

        filter_priority = "Средний"
        filter_another_priority = "Высокий"

        filter_registered_name = "Иванов Иван Иванович"
        filter_another_registered_name = "Петров Петр Петрович" 

        filter_step = "(REGISTRATION) Регистрация"
        filter_another_step = "(SOLUTION) Решение"

        with allure.step('Открыть форму "Системные проблемы"'):
            page.goto(f"{base_url}common-faults-list/all")

        with allure.step('Нажать кнопку "Добавить", заполнить обязательные поля и нажать "Создать"'):
            self.system_problems_page.locators.ADD_PROBLEM_BTN.click()
            self.system_problems_page.add_system_problem.PROBLEM_NAME.fill(problem_name)
            delay(5, reason="UI может не успеть настроить базовый язык")
            self.system_problems_page.add_system_problem.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.choose_option_with_name(self.system_problems_page.selecting_reason_type.PROBLEM_TYPE_LIST, problem_type_name)
            self.system_problems_page.selecting_reason_type.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.add_system_problem.REASON_TYPE.select_by_value(reason_type_name)
            self.system_problems_page.add_system_problem.PRIORITY.select_by_value(priority_name)
            self.system_problems_page.add_system_problem.POTENTIAL.select_by_value(influence_potential_name)
            origin_date = get_current_datetime_string()
            planned_end_date = get_shifted_datetime_string("+1d", False)
            self.system_problems_page.add_system_problem.OCCURANCE_DATE.fill(origin_date)
            self.system_problems_page.add_system_problem.PLANNED_END_DATE.fill(planned_end_date)
            is_experts = "Да"
            self.system_problems_page.add_system_problem.EXPERTS_CHECKBOX.click()
            self.system_problems_page.add_system_problem.CLIENT_TYPE_FIELD.select_by_value(client_type)
            self.system_problems_page.add_system_problem.DEADLINE.select_by_value(deadline_name)
            self.system_problems_page.add_system_problem.INFORM_CLIENT_FIELD.fill(inform_client_text)
            self.system_problems_page.add_system_problem.CREATE_PROBLEM_BTN.click(0)

            self.system_problems_page.check_after_creating_problem(
                problem_type=problem_type_name,
                influence_potential=influence_potential_name,
                reason_type=reason_type_name,
                experts=is_experts,
                inform_client=inform_client_text,
                client_type=client_type,
                solution_planned_duration=deadline_name,
                process_before_date=planned_end_date,
                planned_end_date=planned_end_date,
                origin_date=origin_date,
                priority=priority_name,
            )

        with allure.step('Ввести номер системной проблемы в фильтр Номер СП'):
            problem_number = self.system_problems_page.locators.PROBLEM_NUMBER.text
            self.system_problems_page.locators.FILTER_PROBLEM_NUMBER_FIELD.fill(problem_number)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.to_contain_text_in_any(problem_name)
            assert self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.wait_to_have_count(1)
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.to_contain_text_in_any(problem_name)

        with allure.step('Ввести название системной проблемы "{problem_name}" в фильтр Наименование СП'):
            self.system_problems_page.locators.FILTER_PROBLEM_NAME_FIELD.fill(problem_name)
            assert self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.wait_to_have_count(1)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.to_contain_text_in_any(problem_name)
        
        self.system_problems_page.locators.PROBLEM_CLEAR_BTN.click(0)
        self.system_problems_page.locators.PROBLEM_CLEAR_BTN.click(1)

        with allure.step('Переключить фильтр системных проблем (Все|Активные) в положение Активные'):
            self.system_problems_page.choose_option_with_name(self.system_problems_page.locators.PROBLEM_LIST_FILTER_SWITCHES, problems_status)
            delay(3, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_STATUS_COLOR_LIST.to_have_css_color("background-color", expected_color=active_background_color)

        with allure.step('Открыть расширенный фильтр СП'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()

        with allure.step('В расширенном фильтре указать несколько номеров СП и применить'):
            num_filter_text = ",".join(map(str, [int(problem_number) - 2, int(problem_number) - 1, int(problem_number)]))
            self.system_problems_page.filter_settings.PROBLEM_NUM_FIELD.fill(num_filter_text)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-1)
            delay(2, reason="Список системных проблем обновляется")
            assert self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.elements_len() != 0 , "Системные проблемы не обнаружены"
            self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.to_contain_text_in_any(problem_number)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре наименование СП и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-2)

            self.system_problems_page.filter_settings.PROBLEM_NAME_FIELD.fill(problem_name)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-1)
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.wait_to_be_visible()
            self.system_problems_page.check_problem_names_list(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре Тип причины - {filter_reason_type} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-2)

            self.system_problems_page.filter_settings.PROBLEM_REASON_FIELD.click()
            titles_list = self.system_problems_page.filter_settings.TREE_TITLE_LIST
            checkbox_list = self.system_problems_page.filter_settings.REASON_CHECKBOX_LIST
            self.system_problems_page.click_checkbox_by_title(titles_list, checkbox_list, filter_reason_type)
            self.system_problems_page.filter_settings.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            problem_number = self.system_problems_page.locators.PROBLEM_NUMBER.text
            self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.to_contain_text(0, problem_number)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре Тип причины - {filter_another_reason_type} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)
                
            self.system_problems_page.filter_settings.PROBLEM_REASON_FIELD.click()
            titles_list = self.system_problems_page.filter_settings.TREE_TITLE_LIST
            checkbox_list = self.system_problems_page.filter_settings.REASON_CHECKBOX_LIST
            self.system_problems_page.filter_settings.CANCEL_CHOICE.click()
            self.system_problems_page.click_checkbox_by_title(titles_list, checkbox_list, filter_another_reason_type)
            self.system_problems_page.filter_settings.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            if self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.elements_len() != 0 :
                self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.not_to_contain_text(0, problem_number)
            
        with allure.step('Сбросить фильтр, указать в расширенном фильтре Тип проблемы - {filter_problem_type} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)
  
            self.system_problems_page.filter_settings.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.filter_type_check(filter_problem_type)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)

            delay(3, reason="Список системных проблем обновляется")
            assert self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.elements_len() != 0, f"Отсутствует заведенная проблема, номер проблемы: {problem_number}"
            self.system_problems_page.locators.PROBLEM_NUMBERS_LIST.to_contain_text(0, problem_number)
            
        with allure.step('Сбросить фильтр, указать в расширенном фильтре Тип проблемы - {filter_another_problem_type} и применить'): 
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)

            self.system_problems_page.filter_settings.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.filter_type_check(filter_another_problem_type)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.not_to_contain_text_in_any(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре Приоритет - {filter_priority} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)

            self.system_problems_page.filter_settings.PRIORITY_FIELD.click()  
            self.system_problems_page.filter_type_check(filter_priority)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            delay(2, reason="Список системных проблем обновляется")
            assert self.system_problems_page.locators.PROBLEM_NAMES_LIST.elements_len() != 0, f"Отсутствует заведенная проблема, номер проблемы: {problem_name}"
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.to_contain_text_in_any(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре Приоритет - {filter_another_priority} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)

            self.system_problems_page.filter_settings.PRIORITY_FIELD.click()  
            self.system_problems_page.filter_type_check(filter_another_priority)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.not_to_contain_text_in_any(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре пользователя Кто зарегистрировал - {filter_registered_name} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)
                
            self.system_problems_page.filter_settings.REGISTERED_FIELD.click()  
            self.system_problems_page.filter_type_check(filter_registered_name)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.to_contain_text_in_any(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре пользователя Кто зарегистрировал - {filter_another_registered_name} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)
                
            self.system_problems_page.filter_settings.REGISTERED_FIELD.click()  
            self.system_problems_page.filter_type_check(filter_another_registered_name)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-2)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.not_to_contain_text_in_any(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре Шаг - {filter_step} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-3)

            self.system_problems_page.filter_settings.PROBLEM_TOPIC_FIELD.click()
            try:
                self.system_problems_page.filter_settings.PLUS_SQUARE.click()
            except:
                pass
            titles_list = self.system_problems_page.filter_settings.TREE_TITLE_LIST
            checkbox_list = self.system_problems_page.filter_settings.REASON_CHECKBOX_LIST
            self.system_problems_page.click_checkbox_by_title(titles_list, checkbox_list, filter_step)
            self.system_problems_page.filter_settings.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-3)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.to_contain_text_in_any(problem_name)

        with allure.step('Сбросить фильтр, указать в расширенном фильтре Шаг - {filter_another_step} и применить'):
            self.system_problems_page.locators.PROBLEM_FILTER_SETTINGS_BTN.click()
            self.system_problems_page.filter_settings.RESET_BTN.click(-4)
                
            self.system_problems_page.filter_settings.PROBLEM_TOPIC_FIELD.click()
            titles_list = self.system_problems_page.filter_settings.TREE_TITLE_LIST
            checkbox_list = self.system_problems_page.filter_settings.REASON_CHECKBOX_LIST
            self.system_problems_page.filter_settings.CANCEL_CHOICE.click()
            self.system_problems_page.click_checkbox_by_title(titles_list, checkbox_list, filter_another_step)
            self.system_problems_page.filter_settings.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.filter_settings.APPLY_BTN.click(-3)
            delay(2, reason="Список системных проблем обновляется")
            self.system_problems_page.locators.PROBLEM_NAMES_LIST.not_to_contain_text_in_any(problem_name)

    @allure.suite("E2E_90 Системные проблемы")    
    @allure.title("Проверка редактирования системных проблем")
    @allure.id(540286)
    def test_add_sp_and_editing(self, page: Page, base_url: str):
        problem_name = "Тест редактирование " + str(generate_random_number(4))
        problem_type_name = "(CF_TYPE_2) Покрытие\Связь"
        reason_type_name = "Авария"
        priority_name = "Средний"
        influence_potential_name = "от 1000 и более"
        deadline_name = "Более суток"
        problem_region = "Магаданская область" 
        inform_client_text = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос."
        description_text = "Авария"
        text_to_operator = "Авария на подстанции"

        edited_problem_name = "Тест редактирование" + str(generate_random_number(4)) + " (отредактировано)"
        edited_problem_type_name = "(CF_TYPE_4) Другое"
        edited_reason_type_name = "Другое"
        edited_priority_name = "Низкий"
        edited_influence_potential_name = "Не определено"
        edited_inform_client_text = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос. (отредактировано)"
        edited_description_text = "Авария"
        edited_text_to_operator = "Авария на подстанции"

        with allure.step('Открыть форму "Системные проблемы"'):
            page.goto(f"{base_url}common-faults-list/all")
        with allure.step('Нажать кнопку "Добавить", заполнить обязательные поля и нажать "Создать"'):
            self.system_problems_page.locators.ADD_PROBLEM_BTN.click()
            self.system_problems_page.add_system_problem.PROBLEM_NAME.fill(problem_name)
            delay(5, reason="UI может не успеть настроить базовый язык")        
            self.system_problems_page.add_system_problem.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.choose_option_with_name(self.system_problems_page.selecting_reason_type.PROBLEM_TYPE_LIST, problem_type_name)
            self.system_problems_page.selecting_reason_type.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.add_system_problem.REASON_TYPE.select_by_value(reason_type_name)
            self.system_problems_page.add_system_problem.PRIORITY.select_by_value(priority_name)
            self.system_problems_page.add_system_problem.POTENTIAL.select_by_value(influence_potential_name)
            self.system_problems_page.add_system_problem.CLEAR_OCCURANCE_DATE.click(0)
            self.system_problems_page.add_system_problem.CLEAR_END_DATE.click(0)
            origin_date = get_current_datetime_string()
            planned_end_date = get_shifted_datetime_string("+1d", False)
                
            self.system_problems_page.add_system_problem.OCCURANCE_DATE.fill(origin_date)
            self.system_problems_page.add_system_problem.PLANNED_END_DATE.fill(planned_end_date)
            is_experts = "Да"
            self.system_problems_page.add_system_problem.EXPERTS_CHECKBOX.click()
            self.system_problems_page.add_system_problem.DEADLINE.select_by_value(deadline_name)
            self.system_problems_page.add_system_problem.PROBLEM_REGION.select_by_value(problem_region)
            self.system_problems_page.add_system_problem.INFORM_CLIENT_FIELD.fill(inform_client_text)
            self.system_problems_page.add_system_problem.TECHNICAL_DESCRIPTION_FIELD.fill(description_text)
            self.system_problems_page.add_system_problem.OPERATOR_DESCRIPTION_FIELD.fill(text_to_operator)
            self.system_problems_page.add_system_problem.CREATE_PROBLEM_BTN.click(0)

            self.system_problems_page.check_after_creating_problem(
                problem_type=problem_type_name,
                influence_potential=influence_potential_name,
                reason_type=reason_type_name,
                experts=is_experts,
                operator_description=text_to_operator,
                tech_description=description_text,
                inform_client=inform_client_text,
                solution_planned_duration=deadline_name,
                problem_region=problem_region,
                process_before_date=planned_end_date,
                planned_end_date=planned_end_date,
                origin_date=origin_date,
                priority=priority_name,
            )

        with allure.step('На карточке системной проблемы нажать кнопку Редактировать'):
            self.system_problems_page.locators.EDIT_PROBLEM_BTN.click()

        with allure.step('Отредактировать все поля доступные для редактирования и сохранить изменения'):
            self.system_problems_page.edit_system_problems.PROBLEM_NAME.fill(edited_problem_name)
            self.system_problems_page.edit_system_problems.PROBLEM_TYPE_FIELD.click()
            self.system_problems_page.choose_option_with_name(self.system_problems_page.edit_system_problems.PROBLEM_TYPE_OPTIONS, edited_problem_type_name)
            self.system_problems_page.edit_system_problems.PRIMARY_ACCEPT_BTNS.click(-1)
            self.system_problems_page.edit_system_problems.REASON_TYPE_FIELD.select_by_value(edited_reason_type_name)
            self.system_problems_page.edit_system_problems.PRIORITY_FIELD.select_by_value(edited_priority_name)
            self.system_problems_page.edit_system_problems.INFLUENCE_POTENTIAL_FIELD.select_by_value(edited_influence_potential_name)
            self.system_problems_page.edit_system_problems.CLEAR_OCCURANCE_DATE.click(0)
            self.system_problems_page.edit_system_problems.CLEAR_END_DATE.click(0)
            edited_origin_date = get_exact_day_of_current_month("first")
            edited_planned_end_date = get_exact_day_of_current_month("last", False)
            self.system_problems_page.edit_system_problems.OCCURANCE_DATE.fill(edited_origin_date)
            self.system_problems_page.edit_system_problems.PLANNED_END_DATE.fill(edited_planned_end_date)
            is_experts = "Нет"
            self.system_problems_page.edit_system_problems.EXPERTS_CHECKBOX.click()
            self.system_problems_page.edit_system_problems.INFORM_CLIENT_FIELD.fill(edited_inform_client_text)
            self.system_problems_page.edit_system_problems.TECHNICAL_DESCRIPTION_FIELD.fill(edited_description_text)
            self.system_problems_page.edit_system_problems.OPERATOR_DESCRIPTION_FIELD.fill(edited_text_to_operator)
            self.system_problems_page.edit_system_problems.SAVE_PROBLEM_BTN.click(0)

            self.system_problems_page.check_after_creating_problem(
                problem_type=edited_problem_type_name,
                influence_potential=edited_influence_potential_name,
                reason_type=edited_reason_type_name,
                experts=is_experts,
                operator_description=edited_text_to_operator,
                tech_description=edited_description_text,
                inform_client=edited_inform_client_text,
                solution_planned_duration=deadline_name,
                process_before_date=planned_end_date,
                planned_end_date=edited_planned_end_date,
                origin_date=edited_origin_date,
                priority=edited_priority_name,
            )


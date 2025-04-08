from dataclasses import dataclass

from common.helpers.data_generator import generate_random_number


@dataclass
class SystemProblem:
    problem_name: str = "Тест-кейс " + str(generate_random_number(4))
    priority_name: str = "Низкий"
    problem_type_name: str = "(CF_TYPE_1) Тестовый тип проблем"
    reason_type_name: str = "Плановые работы"
    influence_potential_name: str = "Не определено"
    service_name: str = "Интернет"
    attempts_num: str = "5"
    amount_of_charges: str = "100 руб. 00 коп."
    inform_client_text: str = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос."
    technical_description_text: str = "Не подключен тариф"
    operator_description_text: str = "Не работает интернет"

    step_solution_name: str = "Решение"
    step_residual_responses_name: str = "Ожидание остаточных откликов на проблему"
    step_performing_actions_name: str = "Выполнение действий"

    modal_text: str = "Проблема решена"


@dataclass
class NecessarilySystemProblem:
    problem_name: str = "Название-системной-проблемы " + str(generate_random_number(4))
    priority_name: str = "Высокий"
    problem_type_name: str = "(CF_TYPE_3) Технические проблемы"
    reason_type_name: str = "Авария"
    influence_potential_name: str = "Вся абонентская база"
    deadline_name: str = "Сутки"

    step_solution_name: str = "Решение"
    step_residual_responses_name: str = "Ожидание остаточных откликов на проблему"
    step_performing_actions_name: str = "Выполнение действий"

    modal_text: str = "Проблема решена"


@dataclass
class FiletredProblem:
    problem_name: str = "Тест-кейс-фильтры " + str(generate_random_number(4))
    priority_name: str = "Средний"
    problem_type_name: str = "(CF_TYPE_4) Другое"
    reason_type_name: str = "Другое"
    influence_potential_name: str = "от 100 и более"
    client_type: str = "Юридическое лицо"
    deadline_name: str = "Более суток"
    inform_client_text: str = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос."

    problems_status: str = "Активные"
    active_background_color: str = "green"
    filter_reason_type: str = "(CF_TYPE_4) Другое"
    filter_another_reason_type: str = r"(CF_TYPE_2) Покрытие\Связь"

    filter_problem_type: str = "Другое"
    filter_another_problem_type: str = "Плановые работы"

    filter_priority: str = "Средний"
    filter_another_priority: str = "Высокий"

    filter_registered_name: str = "Иванов Иван Иванович"
    filter_another_registered_name: str = "Петров Петр Петрович"

    filter_step: str = "(REGISTRATION) Регистрация"
    filter_another_step: str = "(SOLUTION) Решение"


@dataclass
class EditingProblem:
    problem_name: str = "Тест редактирование " + str(generate_random_number(4))
    problem_type_name: str = r"(CF_TYPE_2) Покрытие\Связь"
    reason_type_name: str = "Авария"
    priority_name: str = "Средний"
    influence_potential_name: str = "от 1000 и более"
    deadline_name: str = "Более суток"
    problem_region: str = "Магаданская область"
    inform_client_text: str = "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос."
    description_text: str = "Авария"
    text_to_operator: str = "Авария на подстанции"

    edited_problem_name: str = "Тест редактирование" + str(generate_random_number(4)) + " (отредактировано)"
    edited_problem_type_name: str = "(CF_TYPE_4) Другое"
    edited_reason_type_name: str = "Другое"
    edited_priority_name: str = "Низкий"
    edited_influence_potential_name: str = "Не определено"
    edited_inform_client_text: str = (
        "Спасибо, что сообщили. Примите наши извинения. Мы уже решаем Ваш вопрос. (отредактировано)"
    )
    edited_description_text: str = "Авария"
    edited_text_to_operator: str = "Авария на подстанции"

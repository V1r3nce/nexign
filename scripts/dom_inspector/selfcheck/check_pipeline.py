"""Самопроверка пакета ``scripts.dom_inspector``: приёмочный сценарий заказчика плюс регрессии.

Запуск из корня репозитория::

    .venv/Scripts/python.exe -m scripts.dom_inspector.selfcheck.check_pipeline

Проверяется три вещи:

* приёмочный сценарий на синтетической мини-фикстуре: локатор ``chm-ChmAgreementsList-tlb-1-create``
  подписан «Кнопка 'Добавить' договор», в DOM это кнопка «Создать», встречается дважды,
  один экземпляр скрыт через ``clip-path: inset(100%)``. Ожидаем ``UNIQUE_VISIBLE``,
  ``text_mismatch=True`` и первым кандидатом настоящую кнопку «Добавить».
  Фикстура нужна потому, что в живом репозитории этот локатор уже поправлен руками;
* разбор дампа: маркеры кейсов, границы снимков, классификация пометок;
* подкоманда ``inspect``: поиск по атрибутам (class, type, href, data-*), отличие истинного нуля
  от ложного и совпадение машинного вывода ``--json`` с человеческим;
* фильтр покрытия: класс-владелец вместо файла, якорный ``#id`` и раздел про страницы вне дампа;
* пошаговый режим на мини-проекте: разбор тела теста на шаги (позднее связывание ``self``,
  отсечение мёртвой ветки по литеральному аргументу, локальный конструктор в теле теста
  и фикстура, названная не ``setup``) и сшивка шагов со снимками дампа;
* код возврата пошагового режима: неоднозначный локатор роняет прогон так же, как ненайденный,
  а пустой дамп не выдаётся за «проблем нет»;
* защита от сдвига разметки: снимок, съехавший на шаг, распознаётся даже когда на нём
  находится один паразитный локатор (шапка страницы есть на любом экране);
* регрессия по репозиторию: число собранных локаторов и единственный битый селектор.

Скрипт ничего не пишет в репозиторий: временные файлы создаются в каталоге ОС и удаляются.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_ROOT_PATH))

from scripts.dom_inspector.cli import (  # noqa: E402
    build_parser,
    render_report,
    report_to_dict,
    run_inspect,
    section_of,
    steps_exit_code,
)
from scripts.dom_inspector.dump_parser import parse_dump_with_warnings  # noqa: E402
from scripts.dom_inspector.locator_checker import check_dump, collapse_ws_outside_quotes  # noqa: E402
from scripts.dom_inspector.locator_collector import (  # noqa: E402
    EXPECTED_LOCATOR_COUNT,
    SYNTHESIZED_WRAPPERS,
    classify_selector,
    collect_locator_index,
    collect_locators,
)
from scripts.dom_inspector.models import InspectionOptions, MatchStatus, NoteStatus, SelectorKind  # noqa: E402
from scripts.dom_inspector.step_collector import collect_tests  # noqa: E402
from scripts.dom_inspector.step_matcher import build_report, match_tests  # noqa: E402
from scripts.dom_inspector.step_matcher import render_report as render_steps_report  # noqa: E402

#: Эталонный локатор из практики: подписан «Добавить», а в DOM это «Создать» в двух экземплярах.
REFERENCE_SELECTOR = "[data-testid=chm-ChmAgreementsList-tlb-1-create]"

#: Локатор, который человек нашёл руками как правильную замену.
REFERENCE_REPLACEMENT = "[data-testid=chm-ChmAgreementCreation-btn-agreements-buttons-addButtonTitle]"

#: Мини-снимок DOM: настоящая кнопка «Добавить», видимая «Создать» и её скрытый дубль.
FIXTURE_HTML = (
    '<body><div id="app" class="platform-root">'
    '<button data-testid="chm-ChmAgreementCreation-btn-agreements-buttons-addButtonTitle" '
    'type="button" class="ant-btn ant-btn-primary"><span>Добавить</span></button>'
    '<button data-testid="chm-ChmAgreementsList-tlb-1-create" type="button" class="ant-btn">'
    "<span>Создать</span></button>"
    '<div style="clip-path: inset(100%); position: fixed; opacity: 0; z-index: -200">'
    '<button data-testid="chm-ChmAgreementsList-tlb-1-create" type="button" class="ant-btn">'
    "<span>Создать</span></button></div>"
    '<div class="ant-modal-content"><div class="ant-modal-title">Найден дубликат</div></div>'
    "</div></body>"
)

#: Синтетический дамп: маркер кейса, снимок, пометка автора и кейс со ссылкой на баг.
FIXTURE_DUMP = "\n".join(
    [
        "case 29:",
        FIXTURE_HTML,
        "Все есть",
        "case31:",
        "тут баг, так что скипни по причине https://jira.nexign.com/browse/RMBSS-18239",
        "",
    ]
)

#: Фикстура локаторов: тот самый неверно подписанный локатор плюс заведомо отсутствующий.
FIXTURE_LOCATORS = '''"""Фикстура локаторов для самопроверки dom_inspector."""

from pages.ui_elements import Element, ElementsList


class AgreementsFixtureElements:
    """Локаторы мини-фикстуры."""

    def __init__(self) -> None:
        """Объявляет локаторы фикстуры."""
        self.ADD_AGREEMENT_BTN = Element("[data-testid=chm-ChmAgreementsList-tlb-1-create]", "Кнопка 'Добавить' договор")
        self.MODAL_TITLE = Element("[class*=modal-title]", "Заголовок модального окна")
        self.MISSING_BTN = Element("[data-testid=totally-absent-button]", "Кнопка 'Которой нет'")
        self.ROWS = ElementsList("button", "Кнопки страницы")
'''

#: Мини-снимок для проверки фильтра покрытия: страница с якорным id и тремя опознаваемыми кнопками.
COVERAGE_HTML = (
    '<body><div id="anchor-page" class="page">'
    '<button data-testid="cov-one" type="button"><span>Один</span></button>'
    '<button data-testid="cov-two" type="button"><span>Два</span></button>'
    '<button data-testid="cov-three" type="button"><span>Три</span></button>'
    "</div></body>"
)

#: Дамп для проверки фильтра покрытия.
COVERAGE_DUMP = "\n".join(["case 1:", COVERAGE_HTML, ""])

#: Класс-владелец, чья страница в дампе есть: три локатора находятся, четвёртый сломан.
COVERAGE_PRESENT_LOCATORS = '''"""Фикстура: страница, которая в дампе есть."""

from pages.ui_elements import Element


class CoveredPageElements:
    """Локаторы присутствующей страницы."""

    def __init__(self) -> None:
        """Объявляет локаторы присутствующей страницы."""
        self.ONE = Element("[data-testid=cov-one]", "Кнопка 'Один'")
        self.TWO = Element("[data-testid=cov-two]", "Кнопка 'Два'")
        self.THREE = Element("[data-testid=cov-three]", "Кнопка 'Три'")
        self.BROKEN = Element("#anchor-page span[class*='spin-dot']", "Лоадер страницы")
'''

#: Класс-владелец, чьей страницы в дампе нет вовсе: покрытие нулевое.
COVERAGE_ABSENT_LOCATORS = '''"""Фикстура: страница, которой в дампе нет."""

from pages.ui_elements import Element


class AbsentPageElements:
    """Локаторы отсутствующей страницы."""

    def __init__(self) -> None:
        """Объявляет локаторы отсутствующей страницы."""
        self.A = Element("[data-testid=absent-a]", "Кнопка A")
        self.B = Element("[data-testid=absent-b]", "Кнопка B")
        self.C = Element("[data-testid=absent-c]", "Кнопка C")
'''

#: Класс с низким покрытием: 1 из 6 локаторов найден, но у одного из сломанных есть якорь страницы.
COVERAGE_ANCHOR_LOCATORS = '''"""Фикстура: низкое покрытие плюс якорный id в селекторе."""

from pages.ui_elements import Element


class AnchorProbeElements:
    """Локаторы с низким покрытием класса."""

    def __init__(self) -> None:
        """Объявляет локаторы с низким покрытием класса."""
        self.FOUND = Element("[data-testid=cov-one]", "Кнопка 'Один'")
        self.NO_ANCHOR_1 = Element("[data-testid=nope-1]", "Нет якоря 1")
        self.NO_ANCHOR_2 = Element("[data-testid=nope-2]", "Нет якоря 2")
        self.NO_ANCHOR_3 = Element("[data-testid=nope-3]", "Нет якоря 3")
        self.NO_ANCHOR_4 = Element("[data-testid=nope-4]", "Нет якоря 4")
        self.ANCHORED = Element("#anchor-page .spin-dot", "Лоадер по якорю страницы")
'''


#: Локаторы мини-фикстуры пошагового режима. Форма ФЛ переопределяет ``NEXT_BTN`` базовой формы,
#: а метод ``go_next`` объявлен в базе — на этой паре проверяется позднее связывание ``self``.
STEP_FIXTURE_LOCATORS = '''"""Фикстура локаторов для самопроверки пошагового режима."""

from pages.ui_elements import Element


class BaseFixtureForm:
    """Базовая форма: её метод go_next наследуют конкретные формы."""

    def __init__(self) -> None:
        """Объявляет локаторы базовой формы."""
        self.NEXT_BTN = Element("[data-testid=base-next]", "Кнопка 'Далее' базовой формы")
        self.SAVE_BTN = Element("[data-testid=form-save]", "Кнопка 'Сохранить'")

    def go_next(self) -> None:
        """Нажимает 'Далее': метод объявлен в базе, а вызывается на наследнике."""
        self.NEXT_BTN.click()


class IndividualFixtureForm(BaseFixtureForm):
    """Форма ФЛ: переопределяет 'Далее' собственным id."""

    def __init__(self) -> None:
        """Объявляет локаторы формы ФЛ."""
        super().__init__()
        self.NEXT_BTN = Element("#individual-next", "Кнопка 'Далее' формы ФЛ")
        self.BANK_ACCOUNT = Element("[data-testid=form-bank-account]", "Расчётный счёт клиента")
        self.RESULT_TITLE = Element("[data-testid=fixture-result-title]", "Заголовок результата")


class ShiftFixtureForm:
    """Форма для проверки сдвига: шапка есть на каждом экране, поля — только на своём."""

    def __init__(self) -> None:
        """Объявляет локаторы формы."""
        self.HEADER = Element("[data-testid=fixture-header]", "Шапка, видимая на всех экранах")
        self.INN = Element("#fixture-inn", "ИНН")
        self.KPP = Element("#fixture-kpp", "КПП")
        self.NAME = Element("#fixture-name", "Наименование")
        self.SUBMIT = Element("#fixture-submit", "Кнопка 'Отправить'")
        self.RESULT = Element("#fixture-result", "Результат")
'''

#: Пейдж мини-фикстуры: банковский локатор лежит в ветке ``if with_bank``, которую тест гасит литералом.
STEP_FIXTURE_PAGE = '''"""Фикстура пейджа для самопроверки пошагового режима."""

from pages.locators.steps_fixture import IndividualFixtureForm, ShiftFixtureForm


class FixtureFormPage:
    """Пейдж мини-фикстуры."""

    def __init__(self) -> None:
        """Заводит форму мини-фикстуры."""
        self.form = IndividualFixtureForm()

    def fill_form(self, with_bank: bool = True) -> None:
        """Заполняет форму; банковский блок трогается только при with_bank."""
        if with_bank:
            self.form.BANK_ACCOUNT.fill("40702810")
        self.form.SAVE_BTN.click()

    def check_result(self) -> None:
        """Проверяет заголовок результата."""
        self.form.RESULT_TITLE.wait_to_be_visible()


class ShiftFixturePage:
    """Пейдж для проверки сдвига разметки."""

    def __init__(self) -> None:
        """Заводит форму."""
        self.form = ShiftFixtureForm()

    def fill_attributes(self) -> None:
        """Заполняет пять полей формы."""
        self.form.HEADER.wait_to_be_visible()
        self.form.INN.fill("7701234567")
        self.form.KPP.fill("770101001")
        self.form.NAME.fill("ООО Ромашка")
        self.form.SUBMIT.click()
'''

#: Тест мини-фикстуры: три шага, номер кейса 15 в заголовке allure, вызов через цепочку self.page.form.
STEP_FIXTURE_TEST = '''"""Фикстура теста для самопроверки пошагового режима."""

import allure
import pytest

from pages.steps_fixture_page import FixtureFormPage


class TestStepsFixture:
    """Мини-тест из трёх шагов."""

    @pytest.fixture(autouse=True)
    def setup(self, stand_login) -> None:
        """Заводит пейдж-объекты теста."""
        self.form_page = FixtureFormPage()

    @allure.id(777001)
    @allure.title("15. Мини-сценарий самопроверки пошагового режима")
    def test_fixture_steps_flow(self) -> None:
        """Проходит форму и проверяет результат."""
        with allure.step("Нажать 'Далее' в форме"):
            self.form_page.form.go_next()

        with allure.step("Заполнить форму без банковских реквизитов"):
            self.form_page.fill_form(with_bank=False)

        with allure.step("Проверить заголовок результата"):
            self.form_page.check_result()
'''

#: Снимок первого шага: переопределённая кнопка 'Далее' формы ФЛ, базовой кнопки в DOM нет.
STEP_SNAPSHOT_ONE = (
    '<body><div id="app"><button id="individual-next" type="button"><span>Далее</span></button></div></body>'
)

#: Снимок второго шага: только 'Сохранить'; банковского поля нет, и его не должно быть в наборе шага.
STEP_SNAPSHOT_TWO = (
    '<body><div id="app"><button data-testid="form-save" type="button"><span>Сохранить</span></button></div></body>'
)

#: Снимок третьего шага: заголовка результата нет — на этом шаге отчёт обязан показать проблему.
STEP_SNAPSHOT_THREE = '<body><div id="app"><div class="ant-result-title">Готово</div></div></body>'

#: Пошаговый дамп с явной разметкой шагов.
STEP_FIXTURE_DUMP = "\n".join(
    [
        "case 15:",
        "шаг 1",
        STEP_SNAPSHOT_ONE,
        "шаг 2",
        STEP_SNAPSHOT_TWO,
        "шаг 3",
        STEP_SNAPSHOT_THREE,
        "",
    ]
)

#: Тот же дамп без номеров шагов: раскладка по порядку и честная пометка об этом в шапке.
STEP_FIXTURE_DUMP_PLAIN = "\n".join(["case 15:", STEP_SNAPSHOT_ONE, STEP_SNAPSHOT_TWO, STEP_SNAPSHOT_THREE, ""])


#: Снимок второго шага с двумя кнопками 'Сохранить': именно так выглядит регресс селектора,
#: из-за которого Playwright падает по strict mode. Ненайденных локаторов в таком дампе нет вообще.
STEP_SNAPSHOT_TWO_TWICE = (
    '<body><div id="app"><button data-testid="form-save" type="button"><span>Сохранить</span></button>'
    '<button data-testid="form-save" type="button"><span>Сохранить</span></button></div></body>'
)

#: Дамп только на первые два шага: единственная проблема — неоднозначный SAVE_BTN.
STEP_FIXTURE_DUMP_AMBIGUOUS = "\n".join(["case 15:", "шаг 1", STEP_SNAPSHOT_ONE, "шаг 2", STEP_SNAPSHOT_TWO_TWICE, ""])

#: Тест-фикстура сдвига: фикстура названа не 'setup', во втором шаге форма создаётся прямо в тесте.
STEP_SHIFT_TEST = '''"""Фикстура теста для проверки сдвига разметки и разбора без фикстуры 'setup'."""

import allure
import pytest

from pages.locators.steps_fixture import ShiftFixtureForm
from pages.steps_fixture_page import ShiftFixturePage


class TestStepsShiftFixture:
    """Мини-тест из двух шагов."""

    @pytest.fixture(autouse=True)
    def prepare(self, stand_login) -> None:
        """Раздача пейдж-объектов лежит НЕ в методе с именем setup."""
        self.attributes_page = ShiftFixturePage()

    @allure.id(777002)
    @allure.title("16. Мини-сценарий сдвига разметки")
    def test_fixture_shift_flow(self) -> None:
        """Заполняет форму и проверяет результат."""
        with allure.step("Заполнить атрибуты"):
            self.attributes_page.fill_attributes()

        with allure.step("Проверить результат"):
            form = ShiftFixtureForm()
            form.RESULT.wait_to_be_visible()


class TestStepsNoFixture:
    """Тест-класс, где пейдж-объекты не раздаются вообще."""

    @allure.id(777003)
    @allure.title("17. Мини-сценарий без setup-фикстуры")
    def test_fixture_without_setup(self) -> None:
        """Обращается к пейдж-объекту, которого никто не завёл."""
        with allure.step("Заполнить атрибуты"):
            self.attributes_page.fill_attributes()
'''

#: Экран атрибутов: шапка и все пять полей формы.
SHIFT_SNAPSHOT_FORM = (
    '<body><div id="app"><div data-testid="fixture-header">Клиент</div>'
    '<input id="fixture-inn"><input id="fixture-kpp"><input id="fixture-name">'
    '<button id="fixture-submit"><span>Отправить</span></button></div></body>'
)

#: Экран результата: та же шапка и больше ничего из формы.
SHIFT_SNAPSHOT_RESULT = (
    '<body><div id="app"><div data-testid="fixture-header">Клиент</div>'
    '<div id="fixture-result">Готово</div></div></body>'
)

#: Дамп со сдвигом разметки на шаг: экран результата подписан первым шагом, экран формы — вторым.
#: На чужом снимке у шага 1 находится ровно один локатор — шапка; из-за неё старая защита молчала.
STEP_FIXTURE_DUMP_SHIFT = "\n".join(["case 16:", "шаг 1", SHIFT_SNAPSHOT_RESULT, "шаг 2", SHIFT_SNAPSHOT_FORM, ""])


def _fail(failures: list[str], condition: bool, message: str) -> None:
    """Регистрирует проваленную проверку.

    :param failures: Накопитель сообщений об ошибках.
    :param condition: Проверяемое условие.
    :param message: Что именно ожидалось.
    :return: Ничего.
    """
    if condition:
        print(f"  ok   {message}")
    else:
        print(f"  FAIL {message}")
        failures.append(message)


def check_reference_case(failures: list[str], workdir: Path) -> None:
    """Приёмочный сценарий заказчика на синтетической мини-фикстуре.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Приёмочный сценарий (мини-фикстура):")
    dump_path = workdir / "fixture_dump"
    dump_path.write_text(FIXTURE_DUMP, encoding="utf-8")
    locators_root = workdir / "fixture_locators"
    locators_root.mkdir()
    (locators_root / "__init__.py").write_text("", encoding="utf-8")
    (locators_root / "agreements_fixture.py").write_text(FIXTURE_LOCATORS, encoding="utf-8")
    options = InspectionOptions(
        dump_path=dump_path,
        locators_root=locators_root,
        ui_elements_path=PROJECT_ROOT_PATH / "pages" / "ui_elements.py",
        project_root=workdir,
        fail_on_problems=True,
    )
    report = check_dump(options)
    by_attr = {check.locator.attr: check for check in report.checks}
    _fail(failures, len(report.checks) == 4, f"собрано 4 локатора фикстуры (получено {len(report.checks)})")
    reference = by_attr.get("ADD_AGREEMENT_BTN")
    if reference is None:
        failures.append("локатор ADD_AGREEMENT_BTN не собран")
        print("  FAIL локатор ADD_AGREEMENT_BTN не собран")
        return
    _fail(failures, reference.locator.selector == REFERENCE_SELECTOR, "селектор эталонного локатора разобран как есть")
    _fail(
        failures,
        reference.status is MatchStatus.UNIQUE_VISIBLE,
        f"статус эталонного локатора unique_visible (получен {reference.status})",
    )
    _fail(
        failures,
        reference.max_matches_in_snapshot == 2,
        f"совпадений в снимке 2 (получено {reference.max_matches_in_snapshot})",
    )
    _fail(failures, reference.text_mismatch, "расхождение описания и текста поймано")
    _fail(failures, reference.expected_text == "Добавить", f"из описания взято 'Добавить' ({reference.expected_text})")
    _fail(failures, reference.observed_texts == ["Создать"], f"в DOM найдено 'Создать' ({reference.observed_texts})")
    candidates = [candidate.selector for candidate in reference.candidates]
    _fail(
        failures,
        bool(candidates) and candidates[0] == REFERENCE_REPLACEMENT,
        f"первый кандидат — настоящая кнопка «Добавить» ({candidates[:1]})",
    )
    hidden = [element for result in reference.results for element in result.elements if not element.rendered]
    _fail(
        failures,
        any(element.hidden_reason == "css:clip-path-inset-100" for element in hidden),
        "дубль опознан как скрытый через clip-path: inset(100%)",
    )
    _fail(
        failures,
        all(element.pw_visible for result in reference.results for element in result.elements),
        "скрытый дубль всё равно считается для strict mode (pw_visible=True)",
    )
    missing = by_attr["MISSING_BTN"]
    _fail(failures, missing.status is MatchStatus.NOT_FOUND, f"отсутствующий локатор — not_found ({missing.status})")
    _fail(failures, section_of(reference) == "text_mismatch", "эталон попадает в раздел про расхождение текста")
    _fail(failures, section_of(missing) == "not_found", "отсутствующий локатор попадает в раздел сломанных")
    _fail(failures, report.exit_code == 1, "код возврата 1 при найденных проблемах")
    args = build_parser().parse_args(["check", str(dump_path)])
    text = render_report(report, args)
    _fail(failures, "СЛОМАННЫЕ ЛОКАТОРЫ" in text, "в текстовом отчёте есть раздел сломанных локаторов")
    _fail(failures, REFERENCE_REPLACEMENT in text, "в текстовом отчёте напечатан кандидат на замену")
    payload = report_to_dict(report, args)
    _fail(failures, payload["problems_total"] >= 2, "машинный отчёт содержит найденные проблемы")


def check_dump_parsing(failures: list[str], workdir: Path) -> None:
    """Регрессия разбора дампа на синтетическом файле.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Разбор дампа:")
    dump_path = workdir / "fixture_dump"
    document, warnings = parse_dump_with_warnings(dump_path)
    _fail(failures, len(document.snapshots) == 1, f"снимков 1 (получено {len(document.snapshots)})")
    _fail(failures, len(document.blocks) == 2, f"кейсов 2 (получено {len(document.blocks)})")
    _fail(failures, document.blocks[0].case_no == 29, "первый маркер разобран как case 29")
    _fail(failures, document.blocks[1].case_no == 31, "слитный маркер case31 разобран")
    _fail(failures, document.blocks[0].status is NoteStatus.DONE, "пометка «Все есть» даёт статус done")
    _fail(failures, document.blocks[1].status is NoteStatus.SKIP, "ссылка на Jira даёт статус skip")
    _fail(
        failures,
        document.blocks[1].notes[0].jira_key == "RMBSS-18239",
        "ключ задачи Jira извлечён из ссылки",
    )
    _fail(failures, not warnings, f"предупреждений нет (получено {warnings})")
    _fail(failures, not document.snapshots[0].truncated, "снимок не помечен усечённым")


def check_inspect_search(failures: list[str], workdir: Path) -> None:
    """Регрессия подкоманды ``inspect``: поиск по атрибутам, честный ноль и фильтрация JSON.

    Закрывает три претензии приёмки: поиск не видел class/type/href/data-*; вывод не показывал
    атрибуты вообще; ``--json`` игнорировал ``--search`` и ``--limit``.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Подкоманда inspect:")
    dump_path = workdir / "fixture_dump"
    parser = build_parser()

    def run(*extra: str) -> str:
        """Прогоняет ``inspect`` и возвращает захваченный stdout.

        :param extra: Дополнительные ключи командной строки.
        :return: Текст вывода.
        """
        args = parser.parse_args(["inspect", str(dump_path), *extra])
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run_inspect(args)
        return buffer.getvalue()

    by_class = run("--search", "ant-modal-content")
    _fail(failures, "[атрибут]" in by_class, "поиск находит элемент по значению class")
    _fail(failures, "class='ant-modal-content'" in by_class, "в выводе показано, в каком атрибуте совпало")
    by_type = run("--search", "ant-btn")
    _fail(failures, "совпадений по 'ant-btn': 3" in by_type, f"по class найдены все три кнопки:\n{by_type}")
    verbose = run("--search", "addButtonTitle", "-v")
    _fail(failures, "type='button'" in verbose, "с ключом -v печатаются атрибуты элемента")
    true_zero = run("--search", "совершенно-отсутствующая-строка")
    _fail(failures, "настоящий ноль" in true_zero, "истинный ноль назван истинным")
    false_zero = run("--search", "z-index")
    _fail(failures, "ложный ноль" in false_zero, f"ложный ноль отличён от истинного:\n{false_zero}")
    _fail(failures, "grep -o -F" in false_zero, "при ложном нуле выдана подсказка про grep")

    json_path = workdir / "inspect.json"
    args = parser.parse_args(["inspect", str(dump_path), "--search", "ant-btn", "--json", str(json_path)])
    with contextlib.redirect_stdout(io.StringIO()):
        run_inspect(args)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    elements = [element for entry in payload for element in entry["elements"]]
    _fail(failures, len(elements) == 3, f"--json отдаёт ровно отфильтрованные элементы (получено {len(elements)})")
    _fail(failures, all("attrs" in element for element in elements), "в JSON у элемента есть словарь attrs")
    _fail(
        failures,
        any(element["attrs"].get("type") == "button" for element in elements),
        "атрибут type виден в машинном выводе",
    )
    limited = workdir / "inspect_limited.json"
    args = parser.parse_args(["inspect", str(dump_path), "--search", "ant-btn", "--limit", "1", "--json", str(limited)])
    with contextlib.redirect_stdout(io.StringIO()):
        run_inspect(args)
    limited_payload = json.loads(limited.read_text(encoding="utf-8"))
    limited_elements = [element for entry in limited_payload for element in entry["elements"]]
    _fail(failures, len(limited_elements) == 1, f"--json учитывает --limit (получено {len(limited_elements)})")


def check_coverage_filter(failures: list[str], workdir: Path) -> None:
    """Регрессия фильтра покрытия: класс-владелец, якорный id и раздел про пропущенные страницы.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Фильтр покрытия:")
    dump_path = workdir / "coverage_dump"
    dump_path.write_text(COVERAGE_DUMP, encoding="utf-8")
    locators_root = workdir / "coverage_locators"
    locators_root.mkdir()
    (locators_root / "__init__.py").write_text("", encoding="utf-8")
    (locators_root / "covered_page.py").write_text(COVERAGE_PRESENT_LOCATORS, encoding="utf-8")
    (locators_root / "absent_page.py").write_text(COVERAGE_ABSENT_LOCATORS, encoding="utf-8")
    (locators_root / "anchor_page.py").write_text(COVERAGE_ANCHOR_LOCATORS, encoding="utf-8")
    options = InspectionOptions(
        dump_path=dump_path,
        locators_root=locators_root,
        ui_elements_path=PROJECT_ROOT_PATH / "pages" / "ui_elements.py",
        project_root=workdir,
    )
    report = check_dump(options)
    by_origin = {f"{check.locator.class_name}.{check.locator.attr}": check for check in report.checks}
    broken = by_origin["CoveredPageElements.BROKEN"]
    _fail(
        failures,
        broken.status is MatchStatus.NOT_FOUND,
        f"сломанный локатор присутствующей страницы — not_found (получен {broken.status})",
    )
    anchored = by_origin["AnchorProbeElements.ANCHORED"]
    _fail(
        failures,
        anchored.status is MatchStatus.NOT_FOUND,
        f"якорный id перевешивает низкое покрытие класса (получен {anchored.status})",
    )
    _fail(failures, anchored.owner_anchor_found, "якорь селектора отмечен в результате проверки")
    no_anchor = by_origin["AnchorProbeElements.NO_ANCHOR_1"]
    _fail(
        failures,
        no_anchor.status is MatchStatus.PAGE_NOT_IN_DUMP,
        f"локатор без якоря при низком покрытии остаётся отфильтрованным (получен {no_anchor.status})",
    )
    absent = by_origin["AbsentPageElements.A"]
    _fail(
        failures,
        absent.status is MatchStatus.PAGE_NOT_IN_DUMP,
        f"страница, которой нет в дампе, отфильтрована (получен {absent.status})",
    )
    _fail(
        failures,
        any("--coverage 0" in warning for warning in report.warnings),
        "в предупреждениях сказано про --coverage 0",
    )
    args = build_parser().parse_args(["check", str(dump_path), "--limit", "0"])
    text = render_report(report, args)
    _fail(failures, "СТРАНИЦЫ, КОТОРЫХ НЕТ В ДАМПЕ" in text, "в отчёте есть раздел про страницы вне дампа")
    _fail(failures, "absent_page.py" in text, "отфильтрованный файл назван по имени")
    _fail(failures, "AbsentPageElements" in text, "отфильтрованный класс назван по имени")
    payload = report_to_dict(report, args)
    _fail(failures, "pages_not_in_dump" in payload, "в JSON есть ключ pages_not_in_dump")
    absent_entry = next(
        (entry for entry in payload["pages_not_in_dump"] if entry["file"].endswith("absent_page.py")), None
    )
    _fail(
        failures,
        absent_entry is not None and absent_entry["skipped"] == 3 and absent_entry["found"] == 0,
        f"в JSON у отсутствующей страницы пропущено 3, найдено 0 (получено {absent_entry})",
    )
    _fail(
        failures,
        payload["pages_not_in_dump_total"] == 7,
        f"всего отфильтровано 7 локаторов (получено {payload['pages_not_in_dump_total']})",
    )


def _build_step_fixture(workdir: Path) -> tuple[Path, Path]:
    """Раскладывает мини-проект пошагового режима: пейджи, локаторы и тест.

    :param workdir: Временный каталог самопроверки.
    :return: Пара «корень мини-проекта, файл теста».
    """
    root = workdir / "step_fixture"
    (root / "pages" / "locators").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "pages" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pages" / "locators" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pages" / "locators" / "steps_fixture.py").write_text(STEP_FIXTURE_LOCATORS, encoding="utf-8")
    (root / "pages" / "steps_fixture_page.py").write_text(STEP_FIXTURE_PAGE, encoding="utf-8")
    test_path = root / "tests" / "test_steps_fixture.py"
    test_path.write_text(STEP_FIXTURE_TEST, encoding="utf-8")
    (root / "tests" / "test_steps_shift.py").write_text(STEP_SHIFT_TEST, encoding="utf-8")
    return root, test_path


def check_step_mode(failures: list[str], workdir: Path) -> None:
    """Пошаговый режим на мини-фикстуре: разбор тела теста и сшивка шагов со снимками.

    Проверяется то, на чём разбор врёт молча: позднее связывание ``self`` (метод объявлен
    в базовой форме, а вызывается на наследнике с переопределённым селектором) и отсечение
    мёртвой ветки по литеральному аргументу. Дальше эти же шаги сшиваются со снимками:
    зелёные шаги остаются одной строкой, а шаг с отсутствующим в DOM локатором разворачивается.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :return: Ничего.
    """
    print("Пошаговый режим (мини-фикстура):")
    root, test_path = _build_step_fixture(workdir)
    locators = collect_locator_index(root / "pages" / "locators", PROJECT_ROOT_PATH / "pages" / "ui_elements.py", root)
    tests = collect_tests(test_path, locators, root, pages_root=root / "pages")
    _fail(failures, len(tests) == 1, f"в мини-фикстуре разобран 1 тест (получено {len(tests)})")
    if not tests:
        return
    test = tests[0]
    _fail(
        failures,
        test.case_no == 15 and test.allure_id == "777001",
        f"номер кейса взят из заголовка, allure.id прочитан (получено case={test.case_no}, id={test.allure_id})",
    )
    _fail(failures, len(test.steps) == 3, f"шагов разобрано 3 (получено {len(test.steps)})")
    per_step = {step.number: [use.record for use in step.uses] for step in test.steps}
    first = per_step.get(1, [])
    _fail(
        failures,
        [record.attr for record in first] == ["NEXT_BTN"],
        f"на шаге 1 ровно один локатор NEXT_BTN (получено {[record.attr for record in first]})",
    )
    _fail(
        failures,
        bool(first) and first[0].selector == "#individual-next",
        "позднее связывание: метод базовой формы отдал переопределённый селектор наследника "
        f"(получено {first[0].selector if first else '—'})",
    )
    second = [record.attr for record in per_step.get(2, [])]
    _fail(
        failures,
        second == ["SAVE_BTN"],
        f"мёртвая ветка with_bank=False отсечена, BANK_ACCOUNT в шаг 2 не попал (получено {second})",
    )
    _fail(failures, len(match_tests(list(tests), "15")) == 1, "тест отбирается по номеру кейса из --test")

    dump_path = workdir / "step_fixture_dump"
    dump_path.write_text(STEP_FIXTURE_DUMP, encoding="utf-8")
    document, _ = parse_dump_with_warnings(dump_path)
    report = build_report(test, document, root)
    _fail(failures, report.explicit_numbering, "номера шагов взяты из разметки дампа, а не угаданы")
    _fail(
        failures,
        report.problem_steps == [3] and report.has_broken,
        f"проблема только на шаге 3, где заголовка результата в DOM нет (получено {report.problem_steps})",
    )
    text = render_steps_report(report)
    _fail(
        failures,
        "RESULT_TITLE" in text and "не найден" in text,
        "в отчёте развёрнут именно ненайденный локатор шага 3",
    )
    _fail(
        failures,
        "NEXT_BTN" not in text and "SAVE_BTN" not in text,
        "зелёные шаги свёрнуты в одну строку: найденные локаторы в отчёт не печатаются",
    )
    _fail(
        failures,
        "BANK_ACCOUNT" not in text,
        "локатор отсечённой ветки в отчёт не попал",
    )

    plain_path = workdir / "step_fixture_dump_plain"
    plain_path.write_text(STEP_FIXTURE_DUMP_PLAIN, encoding="utf-8")
    plain_document, _ = parse_dump_with_warnings(plain_path)
    plain_report = build_report(test, plain_document, root)
    _fail(
        failures,
        not plain_report.explicit_numbering
        and any("разложено по порядку" in warning for warning in plain_report.warnings),
        f"дамп без номеров шагов разложен по порядку и помечен как угаданный (получено {plain_report.warnings})",
    )
    check_step_exit_codes(failures, workdir, test, root)
    check_step_shift(failures, workdir, root)


def check_step_exit_codes(failures: list[str], workdir: Path, test: object, root: Path) -> None:
    """Код возврата пошагового режима: неоднозначность роняет так же, как ненайденный локатор.

    Регресс, ради которого проверка и написана: селектор стал находить два элемента (Playwright
    падает по strict mode), отчёт красный — а код возврата был нулевой, и CI пропускал поломку.
    Второй кейс — дамп не того файла: ноль снимков нельзя выдавать за «проблем нет».

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :param test: Разобранный тест мини-фикстуры.
    :param root: Корень мини-проекта.
    :return: Ничего.
    """
    dump_path = workdir / "step_fixture_dump_ambiguous"
    dump_path.write_text(STEP_FIXTURE_DUMP_AMBIGUOUS, encoding="utf-8")
    document, _ = parse_dump_with_warnings(dump_path)
    report = build_report(test, document, root)
    text = render_steps_report(report)
    _fail(
        failures,
        not report.has_broken and report.problem_steps == [2] and "найдено 2, ожидался 1" in text,
        f"дубль локатора в снимке шага 2 попал в отчёт (получено {report.problem_steps}, broken={report.has_broken})",
    )
    _fail(
        failures,
        steps_exit_code(report) == 1,
        f"неоднозначный локатор роняет код возврата так же, как ненайденный (получено {steps_exit_code(report)})",
    )
    _fail(failures, steps_exit_code(report, no_fail=True) == 0, "ключ --no-fail гасит и неоднозначность")

    empty_path = workdir / "step_fixture_dump_empty"
    empty_path.write_text("", encoding="utf-8")
    empty_document, _ = parse_dump_with_warnings(empty_path)
    empty_report = build_report(test, empty_document, root)
    empty_text = render_steps_report(empty_report)
    _fail(
        failures,
        empty_report.nothing_checked and "сверять нечего" in empty_text and "проблем нет" not in empty_text,
        f"пустой дамп не выдаётся за успех (получено {empty_text.splitlines()[2] if empty_text else empty_text})",
    )
    _fail(
        failures,
        steps_exit_code(empty_report) == 2 and steps_exit_code(empty_report, no_fail=True) == 2,
        f"на пустом дампе код возврата 2, и --no-fail его не гасит (получено {steps_exit_code(empty_report)})",
    )


def check_step_shift(failures: list[str], workdir: Path, root: Path) -> None:
    """Сдвиг разметки на шаг при одном паразитном совпадении и разбор без фикстуры 'setup'.

    Шапка формы находится на любом экране, поэтому у шага со съехавшим снимком находится ровно
    один локатор из пяти. Раньше этого хватало, чтобы отключить и свёртку, и подсказку о сдвиге:
    отчёт печатал четыре ложных «не найден» и ни слова о том, что снимок чужой.

    :param failures: Накопитель сообщений об ошибках.
    :param workdir: Временный каталог для фикстур.
    :param root: Корень мини-проекта.
    :return: Ничего.
    """
    locators = collect_locator_index(root / "pages" / "locators", PROJECT_ROOT_PATH / "pages" / "ui_elements.py", root)
    tests = collect_tests(root / "tests" / "test_steps_shift.py", locators, root, pages_root=root / "pages")
    by_name = {item.name: item for item in tests}
    shift_test = by_name.get("test_fixture_shift_flow")
    _fail(failures, shift_test is not None, "тест со сдвигом разобран")
    if shift_test is None:
        return
    per_step = {step.number: [use.record.attr for use in step.uses] for step in shift_test.steps}
    _fail(
        failures,
        per_step.get(1) == ["HEADER", "INN", "KPP", "NAME", "SUBMIT"],
        f"фикстура найдена по @pytest.fixture(autouse=True), а не по имени setup (получено {per_step.get(1)})",
    )
    _fail(
        failures,
        per_step.get(2) == ["RESULT"],
        f"локальный конструктор в теле теста разрешён (получено {per_step.get(2)})",
    )
    no_setup = by_name.get("test_fixture_without_setup")
    gaps = [gap.reason for step in no_setup.steps for gap in step.gaps] if no_setup is not None else []
    _fail(
        failures,
        any("нет setup-фикстуры" in gap for gap in gaps),
        f"класс без setup-фикстуры теряет пейдж-объект НЕ молча (получено {gaps})",
    )

    dump_path = workdir / "step_fixture_dump_shift"
    dump_path.write_text(STEP_FIXTURE_DUMP_SHIFT, encoding="utf-8")
    document, _ = parse_dump_with_warnings(dump_path)
    report = build_report(shift_test, document, root)
    first = report.outcomes[0]
    _fail(
        failures,
        first.found == 1 and bool(first.shift_hint),
        f"сдвиг замечен, хотя одно совпадение на шаге всё-таки есть (получено найдено={first.found}, "
        f"подсказка={first.shift_hint!r})",
    )
    text = render_steps_report(report)
    _fail(
        failures,
        "#fixture-inn" not in text and "снимок чужой" in text,
        "локаторы шага с чужим снимком свёрнуты в строку, а не покрашены красным поштучно",
    )


def check_repository(failures: list[str]) -> None:
    """Регрессия по реальному репозиторию: сбор локаторов и классификация селекторов.

    :param failures: Накопитель сообщений об ошибках.
    :return: Ничего.
    """
    print("Репозиторий:")
    records, _ = collect_locators(
        PROJECT_ROOT_PATH / "pages" / "locators",
        PROJECT_ROOT_PATH / "pages" / "ui_elements.py",
        PROJECT_ROOT_PATH,
    )
    _fail(
        failures,
        len(records) == EXPECTED_LOCATOR_COUNT,
        f"собрано {EXPECTED_LOCATOR_COUNT} локаторов (получено {len(records)})",
    )
    _fail(failures, all(record.selector for record in records), "пустых селекторов нет")
    synthesized = [record for record in records if record.wrapper in SYNTHESIZED_WRAPPERS]
    _fail(failures, len(synthesized) == 40, f"локаторов с синтезом id 40 (получено {len(synthesized)})")
    _fail(
        failures,
        all(record.selector.startswith(("[id$=", "[class*=dropdown-trigger]")) for record in synthesized),
        "у SelectWithId/DropdownWithId селектор собран по шаблону, а не взят сырым id",
    )
    _fail(
        failures,
        classify_selector("div.foo") is SelectorKind.CSS,
        "CSS не принимается за XPath (lxml компилирует 'div.foo' как валидный XPath)",
    )
    _fail(failures, classify_selector("//button[1]") is SelectorKind.XPATH, "XPath распознан по префиксу")
    _fail(failures, collapse_ws_outside_quotes("div  > p") == "div > p", "пробелы схлопнуты (иначе падает soupsieve)")
    _fail(
        failures,
        collapse_ws_outside_quotes("[title='а  б']") == "[title='а  б']",
        "пробелы внутри кавычек сохранены",
    )


def main() -> None:
    """Точка входа самопроверки.

    :return: Ничего.
    :raises SystemExit: Кодом 1, если хотя бы одна проверка провалилась.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    failures: list[str] = []
    workdir = Path(tempfile.mkdtemp(prefix="dom_inspector_selfcheck_"))
    try:
        check_reference_case(failures, workdir)
        check_dump_parsing(failures, workdir)
        check_inspect_search(failures, workdir)
        check_coverage_filter(failures, workdir)
        check_step_mode(failures, workdir)
        check_repository(failures)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    print("")
    if failures:
        print(f"ПРОВАЛЕНО ПРОВЕРОК: {len(failures)}")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    print("Все проверки пройдены.")


if __name__ == "__main__":
    main()

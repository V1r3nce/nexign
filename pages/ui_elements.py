import re
import time
from pathlib import Path
from typing import Any, Iterator

import allure
from playwright.sync_api import Locator, expect

from common.exceptions import IncorrectNumberOfFields
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.time_helpers import delay
from models.context import test_context
from pages.exceptions import ElementIsNotDraggable


class Element:
    def __init__(self, path: str, locator_name: str, locator: Locator = None):
        self.page = test_context.page
        self.path = path
        self.locator_name = locator_name
        self.locator = locator

    def __str__(self) -> str:
        return self.locator_name

    def __repr__(self) -> str:
        return self.locator_name

    @allure.step("Нажать на '{0}'")
    def click(self, *args: Any, **kwargs: Any) -> None:
        locator = self.locator or self.page.locator(self.path)
        locator.is_visible()
        locator.click(*args, **kwargs)

    @allure.step("Двойной клик на '{0}'")
    def dblclick(self, *args: Any, **kwargs: Any) -> None:
        locator = self.locator or self.page.locator(self.path)
        locator.is_visible()
        locator.dblclick(*args, **kwargs)

    @property
    def text(self) -> str | None:
        el = self.locator or self.page.locator(self.path)
        return el.text_content() or el.get_attribute("value")

    @property
    def inner_text(self) -> str | None:
        return (self.locator or self.page.locator(self.path)).inner_text()

    @allure.step("Ввести в поле '{0}' текст '{1}'")
    def fill(self, text: Any) -> None:
        (self.locator or self.page.locator(self.path)).fill(str(text))

    @allure.step("Ввести в поле '{0}' текст '{1}' посимвольный ввод текста")
    def type(self, text: str, *args: Any, **kwargs: Any) -> None:
        """Посимвольный ввод, используется в случаях если нужно повторить поведение пользователя
        и ввести строку по буквам"""
        (self.locator or self.page.locator(self.path)).type(text, *args, **kwargs)

    @allure.step("Ввести в поле '{0}' текст '{1}' и прожать Enter")
    def type_and_press_enter(self, text: str) -> None:
        el = self.locator or self.page.locator(self.path)
        el.type(text)
        delay(0.5, reason="в некоторых формах без этого не работает")
        el.press("Enter")

    @allure.step("Стереть текст, в поле '{0}'")
    def clear_input(self) -> None:
        (self.locator or self.page.locator(self.path)).fill("")

    @allure.step("Загрузить в элемент '{0}' файлы '{1}'")
    def upload_files(self, files: list[str | Path]) -> None:
        (self.locator or self.page.locator(self.path)).set_input_files(files)

    @allure.step("Ожидание визуального присутствия '{0}'")
    def wait_to_be_visible(self, *args: Any, timeout: int = 10000, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).to_be_visible(*args, timeout=timeout, **kwargs)

    @allure.step("Поле '{0}' содержит текст '{text}'")
    def to_contain_text(
        self, text: Any, clear_phone: bool = False, separated: bool = False, timeout_sec: int = 0
    ) -> None:
        """Проверка, что поле содержит текст.
        :param text: (str | re.Pattern): текст или регулярное выражение для проверки
        :param clear_phone: (bool): приводить ли текст к номеру телефона
        :param separated: (bool): убирать ли разделители
        :param timeout_sec: (int): время ожидания
        """
        element_text = self.text
        if clear_phone:
            element_text = re.sub(r"[^\d+]", "", self.text)
        if separated:
            element_text = element_text.replace(" ", "").replace("\u2009", "").replace("\xa0", "")
        if element_text:
            if isinstance(text, re.Pattern):
                condition = lambda: bool(text.search(self.text)) or bool(text.search(element_text))
            else:
                condition = lambda: str(text) in self.text or str(text) in element_text
            wait_that(
                condition,
                timeout=timeout_sec,
                sleep_seconds=1,
                exception=AssertionError,
                message=lambda: (
                    f"Поле '{self}' не содержит текст '{text.pattern if isinstance(text, re.Pattern) else text}'.\nТекущий текст '{self.text}'"
                ),
            )
        else:
            raise AssertionError(f"Поле '{self}' пустое.")

    @allure.step("Поле '{0}' содержит свойство value '{text}'")
    def to_have_value(self, text: str, timeout: int = 5000) -> None:
        expect(self.locator or self.page.locator(self.path)).to_have_value(value=text, timeout=timeout)

    @allure.step("Поле '{0}' имеет свойство value '{text}'")
    def to_contain_value(self, text: str, timeout: int = 5000, separated: bool = False) -> None:
        if separated:
            pattern = re.compile(r"^" + r"\s*".join(map(re.escape, text)) + r"$")
        else:
            pattern = re.compile(text)
        expect(self.locator or self.page.locator(self.path)).to_have_value(value=pattern, timeout=timeout)

    @allure.step("Проверить, что элемент '{0}' активен")
    def to_be_enabled(self, *args: Any, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).to_be_enabled(*args, **kwargs)

    @allure.step("Проверить, что элемент '{0}' не активен")
    def not_to_be_enabled(self, *args: Any, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).not_to_be_enabled(*args, **kwargs)

    @allure.step("Проверить, что элемент '{0}' неактивен (содержит disable)")
    def to_be_disabled(self, *args: Any, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).to_be_disabled(*args, **kwargs)

    @allure.step("Проверить, что элемент '{0}' отсутствует")
    def not_to_be_visible(self, *args: Any, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).not_to_be_visible(*args, **kwargs)

    @allure.step("Проверить, что элемент '{0}' остаётся невидимым в течение {invisible_time} мс")
    def not_to_be_visible_for(self, invisible_time: int = 5000) -> None:
        """Проверить, что элемент не становится видимым на всём протяжении таймаута.

        Проходит, если элемент ни разу не стал видимым за `timeout` мс; падает,
        если элемент виден изначально или появляется в течение таймаута.
        """
        try:
            expect(self.locator or self.page.locator(self.path)).to_be_visible(timeout=invisible_time)
        except AssertionError:
            return
        raise AssertionError(f"Элемент '{self}' стал видимым в течение {invisible_time} мс, ожидалось его отсутствие")

    @allure.step("Прокрутить до элемента '{0}'")
    def scroll_into_view_if_needed(self) -> None:
        (self.locator or self.page.locator(self.path)).scroll_into_view_if_needed()

    @allure.step("Прокрутить элемент '{0}' на {scroll}")
    def scroll_scrollable_platform(self, scroll: int) -> None:
        (self.locator or self.page.locator(self.path)).evaluate(f"e => e.scrollTop += {scroll}")

    @allure.step("Текст в поле '{0}' равен тексту '{1}'")
    def wait_to_have_text(self, *args: Any, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).to_have_text(*args, **kwargs)

    @allure.step("Поле '{0}' не содержит текст '{text}'")
    def not_to_contain_text(self, text: str, timeout: int = 5000) -> None:
        expect(self.locator or self.page.locator(self.path)).not_to_contain_text(expected=text, timeout=timeout)

    @allure.step("Получить html для блока элемента '{0}'")
    def inner_html(self) -> str:
        return (self.locator or self.page.locator(self.path)).inner_html()

    @allure.step("Атрибут '{attribute}' элемента '{0}' содержит значение '{value}'")
    def check_attribute_by_value(self, attribute: str, value: str | re.Pattern[str]) -> None:
        expect(self.locator or self.page.locator(self.path)).to_have_attribute(attribute, value)

    @allure.step("Атрибут '{attribute}' элемента '{0}' содержит значение '{value}'")
    def has_attribute_value(self, attribute: str, value: str) -> bool:
        return (self.locator or self.page.locator(self.path)).get_attribute(attribute) == value

    @allure.step("Атрибут '{attribute}' элемента '{0}' не содержит значение '{value}'")
    def check_attribute_not_contain_value(self, attribute: str, value: str) -> None:
        expect(self.locator or self.page.locator(self.path)).not_to_have_attribute(attribute, value)

    @allure.step("Проверить, что элемент '{0}' не содержит атрибут 'disabled'")
    def element_not_contain_disabled_attribute(self, timeout: int = 0) -> None:
        delay(timeout, reason="Нужен чтобы дать время элементу стать активным")
        assert (self.locator or self.page.locator(self.path)).evaluate('element => !element.hasAttribute("disabled")'), (
            f'Элемент "{self.locator_name}" не активен'
        )

    @allure.step("Ожидание наличия класса '{class_name}' в элементе '{0}'")
    def to_have_class(self, class_name: str | re.Pattern[str]) -> None:
        expect(self.locator or self.page.locator(self.path)).to_have_class(class_name)

    @allure.step("Ожидание отсутствия класса '{class_name}' в элементе '{0}'")
    def not_to_have_class(self, class_name: str | re.Pattern[str]) -> None:
        expect(self.locator or self.page.locator(self.path)).not_to_have_class(class_name)

    @allure.step("Ожидание css атрибута '{attribute}' элемента '{0}' равного '{value}'")
    def to_have_css(self, attribute: str, value: str) -> None:
        expect(self.locator or self.page.locator(self.path)).to_have_css(attribute, value)

    @allure.step("Сравнение цвета свойства {css_property} с ожидаемым {expected_color} для элемента {0}")
    def element_have_css_color(self, css_property: str, expected_color: str) -> None:
        """
        Проверка цвета у элемента: принимает строковое наименование цвета
        и сравнивает со своим словарем цветовых значений, затем проверяет цвет у элемента.

        :param css_property - свойство, у которого проверяется значение цвета (н.п. background-color)
        :param expected_color - название ожидаемого значения цвета (н.п. "green")
        """
        color_map = {
            "green": r"0, 173, 33",
            "dark_green": r"69, 166, 0",
            "grey": r"160, 173, 180",
            "dark_grey": r"39, 45, 52",
            "dark_grey_lis_button": r"86, 90, 102",
            "red": r"211, 76, 76",
            "dark_red": r"203, 0, 0",
            "blue_button": r"80, 128, 231",
            "deep_blue": r"37, 97, 225",
            "yellow": r"255, 152, 0",
            "moon_white": r"255, 255, 255",
            "olive": r"175, 180, 43",
        }

        if expected_color in color_map:
            expected_color = color_map.get(expected_color)
        else:
            raise ValueError(
                f"Цвет '{expected_color}' отсутствует в словаре допустимых цветов: {list(color_map.keys())}"
            )
        expect(self.locator or self.page.locator(self.path)).to_have_css(css_property, re.compile(expected_color))

    @allure.step("Ожидание доступности '{0}'")
    def wait_to_be_enabled(self, *args: Any, **kwargs: Any) -> None:
        expect(self.locator or self.page.locator(self.path)).to_be_enabled(*args, **kwargs)

    @allure.step("Навести курсор на '{0}'")
    def hover(self) -> None:
        (self.locator or self.page.locator(self.path)).hover()

    @allure.step("Получить значение свойства '{css_property}' элемента '{0}'")
    def get_css_property(self, css_property: str) -> str:
        return (self.locator or self.page.locator(self.path)).evaluate(
            f"element => getComputedStyle(element).getPropertyValue('{css_property}')"
        )

    @allure.step("Проверка, что есть псевдоэлемент ::after")
    def has_after(self) -> bool:
        return (self.locator or self.page.locator(self.path)).evaluate(
            "(el) => {return window.getComputedStyle(el, '::after').content !== 'none';}"
        )

    @allure.step("Получение значения атрибута {attribute_name} локатора элемента")
    def get_attribute(self, attribute_name: str) -> str | None:
        return (self.locator or self.page.locator(self.path)).get_attribute(attribute_name)

    @allure.step("Перемещение элемента '{0}' к элементу '{destination}")
    def drag_to(self, destination: "Element", **kwargs: Any) -> None:
        try:
            self.locator.drag_to(destination.locator, **kwargs)
        except AttributeError:
            raise ElementIsNotDraggable

    @allure.step("Проверка отображения элемента")
    def is_visible(self) -> bool:
        return (self.locator or self.page.locator(self.path)).is_visible()


class ElementsList(Element):
    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name)

    def __getitem__(self, key: int | slice) -> Element | list[Element]:
        wait_that(
            lambda: self.page.locator(self.path).count() > key,
            message=f"Не найдено элемента {self.locator_name} с индексом {key}",
            exception=AssertionError,
        )
        return [Element(self.path, self.locator_name, locator=el.first) for el in self.page.locator(self.path).all()][
            key
        ]

    def __iter__(self) -> Iterator[Element]:
        for el in self.page.locator(self.path).all():
            yield Element(self.path, self.locator_name, locator=el.first)

    @allure.step("Клик по первому элементу списка с текстом '{text}'")
    def click_by_text(self, text: str, timeout: int = 5000) -> None:
        self.page.locator(self.path).filter(has_text=text).first.click(timeout=timeout)

    @allure.step("Поле '{0}' с индексом '{element_index}' содержит текст '{text}'")
    def to_contain_text(self, element_index: int, text: str, timeout: int = 5000) -> None:
        expect(self.page.locator(self.path).nth(element_index)).to_contain_text(expected=text, timeout=timeout)

    @allure.step("Нажать элемент '{0}' с индексом {element_index}'")
    def click(self, element_index: int) -> None:
        self.page.locator(self.path).nth(element_index).click()

    @property
    def text_list(self) -> list[str]:
        return [self[index].text.strip() for index in range(self.elements_len())]

    @allure.step("Прокрутить до элемента '{0}' с индексом {element_index}'")
    def scroll_into_view_if_needed(self, element_index: int) -> None:
        self.page.locator(self.path).nth(element_index).scroll_into_view_if_needed()

    @allure.step("Дождаться визуального наличия элемента для '{0}' с индексом {element_index}'")
    def wait_elements_visible(self, element_index: int, timeout: int = 5000) -> None:
        expect(self.page.locator(self.path).nth(element_index)).to_be_visible(timeout=timeout)

    @allure.step("Получить количество элементов для '{0}'")
    def elements_len(self) -> int:
        return self.page.locator(self.path).count()

    @allure.step("Дождаться наличия элементов в количестве {amount} или более")
    def wait_to_have_count_or_greater(self, amount: int, timeout: int = 10000) -> None:
        wait_that(
            lambda: self.elements_len() >= amount,
            exception=IncorrectNumberOfFields,
            message=f"Количество элементов меньше чем {amount}",
            timeout=int(timeout / 100),
            sleep_seconds=2,
        )

    @allure.step("Поле '{0}' с индексом {element_index} не содержит текст '{text}'")
    def not_to_contain_text(self, element_index: int, text: str, timeout: int = 5000) -> None:
        expect(self.page.locator(self.path).nth(element_index)).not_to_contain_text(expected=text, timeout=timeout)

    @allure.step("Получить html блока для '{0}'")
    def inner_html(self, element_index: int) -> str:
        return self.page.locator(self.path).nth(element_index).inner_html()

    @allure.step("Ожидание наличия класса '{class_name}' в элементе '{0}' с индексом {element_index}")
    def wait_to_have_class(self, element_index: int, class_name: str) -> None:
        expect(self.page.locator(self.path).nth(element_index)).to_have_class(class_name)

    @allure.step("Ожидание наличия списка '{text_lst}' в элементах '{0}'")
    def to_have_text_list(self, text_lst: list) -> None:
        elements = [Element(self.path, self.locator_name, locator=el) for el in self.page.locator(self.path).all()]
        text_in_elements = [element.text for element in elements]
        assert text_lst == text_in_elements, (
            f"Некорректный список в элементах, ожидаемый список '{text_lst}', фактический '{text_in_elements}'"
        )

    @allure.step("Ожидание появления текста '{text}' в одном из элементов списка '{0}'")
    def wait_for_text_in_all(self, text: str | list[str], timeout: int = 5000) -> None:
        expect(self.page.locator(self.path)).to_contain_text(expected=text, timeout=timeout)

    @allure.step("Ожидание отсутствия текста '{text}' во всех элементах списка '{0}'")
    def wait_for_not_contain_text_in_all(self, text: str, timeout: int = 5000) -> None:
        expect(self.page.locator(self.path)).not_to_contain_text(expected=text, timeout=timeout)

    @allure.step("Проверка, что в списке элементов '{0}' есть текст '{expected_text}'")
    def to_contain_text_in_any(
        self,
        expected_text: str,
        timeout: int = 5,
        case_sensitive: bool = True,
    ) -> None:
        """
        Проверка наличия текста среди элементов списка: метод ожидает до `timeout` сек,
        что хотя бы один элемент, соответствующий локатору `self.path`, содержит `expected_text`.
        Поддерживает чувствительность к регистру (по умолчанию включена).
        Если по истечении тайм-аута текст не найден — выбрасывает AssertionError
        с описанием текущего состояния элементов.

        :param expected_text: Текст, который должен присутствовать хотя бы в одном элементе.
        :param timeout: Время ожидания (сек).
        :param case_sensitive: Если True — сравнение с учётом регистра, иначе — без.
        """
        has_text = expected_text if case_sensitive else re.compile(re.escape(expected_text), re.IGNORECASE)

        base = self.page.locator(self.path)

        wait_that(
            lambda: any(el.filter(has_text=has_text).is_visible() for el in base.all()),
            exception=AssertionError,
            message=lambda: (
                f"Текст '{expected_text}' не найден среди элементов '{self.path}'. "
                f"Текущий текст в элементах: {base.all_text_contents()}"
            ),
            timeout=timeout,
        )

    @allure.step("Проверка, что в списке элементов '{0}' нет текста '{expected_text}'")
    def not_to_contain_text_in_any(self, expected_text: str, timeout: int = 5000) -> None:
        """
        Ждет появления списка. Если список появился, проверяет, что в нем нет текста
        """
        locator = self.page.locator(self.path)

        if locator.count() == 0 or not locator.first.is_visible(timeout=timeout):
            return

        elements = locator.all()

        for element in elements:
            if expected_text in element.text_content():
                raise AssertionError(f"Обнаружен нежелательный текст: '{expected_text}'")

    @allure.step("Проверка, что в каждом элементе списка '{0}' есть текст '{expected_text}'")
    def to_contain_text_in_all(self, expected_text: str) -> None:
        elements = self.page.locator(self.path).all()

        assert_that(
            lambda: all(expected_text in el.text_content() for el in elements),
            message=f"Не во всех элементах содержится текст '{expected_text}'",
        )

    @allure.step("Сравнение цвета свойства {css_property} с ожидаемым {expected_color}")
    def to_have_css_color(self, css_property: str, expected_color: str) -> None:
        """
        Проверка цвета у свойств всех элементов списка: принимает строковое наименование цвета
        и сравнивает со своим словарем цветовых значений, затем проходяится по списку, сравнивая со словарным значением цвета.

        :param css_property - свойство, у которого проверяется значение цвета (н.п. background-color)
        :param expected_color - название ожидаемого значения цвета (н.п. "green")
        """
        COLOR_MAP = {"green": "rgb(0, 173, 33)", "grey": "rgb(160, 173, 180)"}

        if expected_color in COLOR_MAP:
            expected_color = COLOR_MAP.get(expected_color)
        else:
            raise ValueError(
                f"Цвет '{expected_color}' отсутствует в словаре допустимых цветов: {list(COLOR_MAP.keys())}"
            )

        for element in self.page.locator(self.path).all():
            expect(element).to_have_css(css_property, expected_color)

    @allure.step("Ожидание количества элементов '{0}' должно быть '{1}'")
    def wait_to_have_count(self, count: int, *args: Any, **kwargs: Any) -> None:
        expect(self.page.locator(self.path)).to_have_count(count, *args, **kwargs)

    @allure.step("Ожидание визуального отсутствия всех '{0}'")
    def wait_not_to_be_visible(self, *args: Any, **kwargs: Any) -> None:
        for el in self.page.locator(self.path).all():
            expect(el).not_to_be_visible(*args, **kwargs)

    @allure.step("Ожидание css атрибута '{2}' элемента '{0}' равного '{3}'")
    def wait_to_have_css(self, element_index: int, attribute: str, value: str) -> None:
        expect(self.page.locator(self.path).nth(element_index)).to_have_css(attribute, value)

    @allure.step("Ожидание визуального присутствия всех '{0}'")
    def wait_to_be_visible(self, *args: Any, **kwargs: Any) -> None:
        elements = self.page.locator(self.path)
        expect(elements.first).to_be_visible(*args, **kwargs)
        for el in elements.all():
            expect(el).to_be_visible(*args, **kwargs)

    @allure.step("Получить элемент с текстом")
    def get_element_by_text(self, text: str) -> Element:
        for element in self.page.locator(self.path).all():
            if text in element.text_content():
                return Element(self.path, self.locator_name, locator=element)
        raise AssertionError("Не найдено ни одного элемента с ожидаемым текстом")


class BaseSelect(Element):
    """Базовый класс для элементов с выпадающим списком
    Унаследовавшись от него, нужно заполнить в конструкторе параметры ниже
    """

    def __init__(
        self,
        path: str,
        root_path: str,
        selected_text_path: str,
        option_items_path: str,
        locator_name: str,
        item_text_relative_path: str = "",
    ):
        """
        :param path: путь
        :param root_path: указывается путь к базовому полю селектора
        :param selected_text_path: указывается путь к локатору, содержащему текст после выбора элемента
        :param option_items_path: указывается путь к пункту выпадающего меню при нажатии на базовое поле
        :param locator_name: описание базового поля
        :param item_text_relative_path: указывается дополнительный относительный путь к тексту внутри пункта выпадающего меню. Например, div > span
        """
        super().__init__(path, locator_name)
        self.root_path = root_path
        self.selected_text_path = selected_text_path
        self.option_items_path = option_items_path
        self.item_text_relative_path = item_text_relative_path
        self.options_dict: dict[str, Locator] = {}

    def open_dropdown(self) -> None:
        self.root.click()

    @property
    def root(self) -> Locator:
        return self.page.locator(self.root_path).filter(has=self.page.locator(self.path)).last

    @property
    def text(self) -> str | None:
        selected_text = self.root.locator(self.selected_text_path)
        return selected_text.text_content() or selected_text.get_attribute("value")

    @property
    def options(self) -> dict:
        up_root = self.root.locator("..")
        for item in up_root.locator(self.option_items_path).all():
            self.options_dict[item.locator(self.item_text_relative_path).text_content()] = item
        return self.options_dict

    def find_by_value(self, value: str) -> Locator | None:
        element = None
        if value in self.options.keys():
            element = self.options[value]
        return element

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str) -> None:
        self.options_dict = {}
        self.open_dropdown()
        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ выпадающем списке отсутствует значение '{value}'."
            f"\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.click()

        wait_that(
            lambda: self.text == value,
            timeout=5,
            sleep_seconds=0.1,
            exception=AssertionError,
            message=f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}",
        )

    @allure.step("Текст в поле '{0}' равен тексту '{1}'")
    def wait_to_have_text(self, expected_text: str) -> None:
        wait_that(
            lambda: self.text == expected_text,
            timeout=5,
            sleep_seconds=0.1,
            exception=AssertionError,
            message=lambda: f"Ожидался текст: {expected_text}\nТекущий текст: {self.text}",
        )

    @allure.step("Выбрать значение c индексом {idx}")
    def select_by_index(self, idx: int) -> None:
        self.open_dropdown()

        def _options_loaded() -> bool:
            self.options_dict = {}
            keys = list(self.options.keys())
            if not keys:
                return False
            return not any((k or "").strip() in ("...", "…") for k in keys)

        wait_that(
            _options_loaded,
            message="Выпадающий список не подгрузился или пуст",
            timeout=10,
            exception=TimeoutError,
        )

        option_list = list(self.options.values())
        check_that(
            lambda: len(option_list) > idx,
            IndexError,
            f"Переданный индекс {idx} не найден в списке элемента {self}",
        )
        option_list[idx].click()


class Select(BaseSelect):
    """Элементы с выпадающим списком."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(
            path,
            root_path="//div[contains(@class, '-select-selector')]",
            selected_text_path="//span[contains(@class, '-select-selection-item') and not(contains(@class, '-select-selection-item-'))]",
            option_items_path="//div[contains(@class, '-select-item-option') and contains(@class, '-item ')]",
            item_text_relative_path="div > span",
            locator_name=locator_name,
        )

    @property
    def clear_button(self) -> Locator:
        return self.root.locator("//span[contains(@class, '-select-clear')]")

    @allure.step("Очистить выбранное значение в поле '{0}'")
    def clear_select(self) -> None:
        if self.clear_button.is_visible(timeout=2000):
            self.clear_button.click()

    @allure.step(
        "Проверить что значение с наименованием {1} отображается в списке доступных значений выпадающего списка"
    )
    def check_option_in_values(self, option_name: str) -> None:
        self.open_dropdown()
        wait_that(
            lambda: len(self.options.values()) > 0,
            message="Выпадающий список отсутствует",
            timeout=5,
            exception=TimeoutError,
        )

        option_list = list(self.options.keys())
        assert_that(
            lambda: option_name in option_list,
            "Значение {option_name} отсутствует в списке доступных значений выпадающего списка",
        )
        self.open_dropdown()


class SelectWithId(BaseSelect):
    def __init__(self, id: str, locator_name: str, additional_restriction: str = ""):
        super().__init__(
            f"[id$={id}]{additional_restriction}",
            root_path="[class*=select-selector]",
            selected_text_path="[class*=selection-item]",
            option_items_path=f"[class*=select-dropdown]:has([id*={id}]) [class*=virtual-list-holder-inner] > [class*=option]",
            item_text_relative_path="[class*=option-content]",
            locator_name=locator_name,
        )

    @property
    def options(self) -> dict:
        for item in self.page.locator(self.option_items_path).all():
            self.options_dict[item.locator(self.item_text_relative_path).text_content()] = item
        return self.options_dict


class SelectDifferentRoot(Select):
    """Элементы с выпадающим списком."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(
            path,
            locator_name=locator_name,
        )

    @property
    def root(self) -> Locator:
        return self.page.locator(self.path)


class SelectDifferentItemTextPath(SelectDifferentRoot):
    """Элементы с неразрывными пробелами в выпадающем списке"""

    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name=locator_name)
        self.item_text_relative_path = "div div div"

    @allure.step("Выбрать значение c текстом '{entity_type} {value}' у поля '{0}'")
    def select_by_value(self, entity_type: str, value: str) -> None:
        self.options_dict = {}
        self.open_dropdown()
        value_for_search = entity_type + "\xa0" + value
        value_for_check = entity_type + " " + value
        wait_that(
            lambda: self.find_by_value(value_for_search) is not None,
            message=f"\nВ выпадающем списке отсутствует значение '{value}'."
            f"\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(value_for_search)
        element.click()

        assert self.text == entity_type + " " + value, (
            f"Не удалось выбрать значение '{value_for_check}'\nТекущее значение: {self.text}"
        )


class Autocomplete(BaseSelect):
    """Элементы с автокомплитным выбором. Сначала вводится текст в поле, затем выбирается значение из выпадающего списка."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(
            path,
            root_path="//div[contains(@class, '-form-item ')]",
            selected_text_path="//span[contains(@class, '-select-selection-item')]",
            option_items_path="//div[contains(@class, '-select-item-option') and contains(@class, '-item ')]",
            item_text_relative_path="div > span",
            locator_name=locator_name,
        )

    @property
    def text(self) -> str | None:
        el = self.page.locator(self.path)
        if el.text_content() or el.get_attribute("value"):
            return el.text_content() or el.get_attribute("value")
        selected_text = self.root.locator(self.selected_text_path)
        return selected_text.text_content() or selected_text.get_attribute("value")

    @allure.step("Выбрать значение c текстом '{value}' у поля с автокомплитом '{0}'")
    def select_by_value(self, value: str, include_last_symbol: bool = False) -> None:
        self.options_dict = {}
        self.open_dropdown()

        self.page.locator(self.path).fill(
            value[:-1] if not include_last_symbol else value
        )  # вводим текст, без последнего символа

        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.click()

        assert self.text == value, f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"

    @allure.step(
        "Ввести значение '{input_value}', выбрать значение '{select_value}', проверить что выбрано '{field_value}'"
    )
    def select_address_by_value(self, input_value: str, select_value: str, field_value: str) -> None:
        self.options_dict = {}
        self.open_dropdown()

        self.page.locator(self.path).fill(input_value)

        wait_that(
            lambda: self.find_by_value(select_value) is not None,
            message=f"\nВ выпадающем списке отсутствует значение '{select_value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(select_value)
        element.click()

        assert self.text == field_value, f"Не удалось выбрать значение '{select_value}'\nТекущее значение: {self.text}"

    @allure.step("Проверить, что значение {1} отсутствует в автокомплите '{0}'")
    def check_option_not_in_values(self, option_name: str) -> None:
        self.options_dict = {}
        self.open_dropdown()
        self.page.locator(self.path).fill(option_name)
        option_list = list(self.options.keys())
        assert_that(
            lambda: option_name not in option_list,
            f"Значение '{option_name}' присутствует в списке, хотя не должно.\nОтображаемые значения: {option_list}",
        )
        self.open_dropdown()


class DatePicker(Element):
    """Элементы с полем выбора даты."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name=locator_name)
        self.clear_calendar_path = path + "//span[contains(@class, 'picker-clear')]"
        self.calendar_date_field_path = path + "//input[@placeholder]"

    @allure.step("Выбрать дату '{text} у поля '{0}'")
    def fill(self, text: str, *args: Any, **kwargs: Any) -> None:
        el = self.page.locator(self.path)
        el.click()
        el.fill(text)
        self.page.keyboard.press("Enter")

        assert self.text == text, f"Не удалось ввести дату '{text}'\nТекущее значение: {self.text}"

    @allure.step("Заполнение периода дат в поле '{0}'. Начальная дата {1}, конечная дата {2}")
    def fill_calendar_dates_period(self, start_date: str, end_date: str) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        if self.page.locator(self.clear_calendar_path).is_visible(timeout=0):
            with allure.step("Очистить поля ввода дат"):
                self.page.locator(self.clear_calendar_path).click()
        with allure.step(f"Открыть календарь и указать начальную {start_date} и конечную {end_date} даты"):
            self.page.locator(self.calendar_date_field_path).nth(0).click()
            self.page.locator(self.calendar_date_field_path).nth(0).fill(start_date)
            self.page.keyboard.press("Tab")
            self.page.locator(self.calendar_date_field_path).nth(1).fill(end_date)
            self.page.keyboard.press("Enter")


class MultySelect(SelectDifferentRoot):
    """Элементы с полем выбора нескольких значений."""

    def __init__(self, path: str, locator_name: str) -> None:
        super().__init__(path, locator_name)
        self.selected_options_path = "//*[contains(@class, '-select-selection-overflow-item')]/span"

    @property
    def selected_options(self) -> dict:
        self.options_dict = {}
        for item in self.root.locator(self.selected_options_path).all():
            self.options_dict[item.text_content()] = item
        return self.options_dict

    @property
    def text_list(self) -> list:
        return [item_text for item_text in self.selected_options.keys()]

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str, check: bool = True, without_dropdown: bool = False) -> None:
        self.options_dict = {}
        if not without_dropdown:
            self.open_dropdown()
        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ поле мультиселекта отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.click()
        if not without_dropdown:
            self.open_dropdown()
        if check:
            assert_that(
                lambda: value in self.text_list,
                f"Не удалось выбрать значение '{value}'\nСписок выбранных значений: {self.text_list}",
            )

    @allure.step("Выбрать все значения списка")
    def choose_all_options(self) -> None:
        """
        Метод проставляет чекбоксы для всех значений списка
        """
        all_options = self.options.keys()
        checked_options = self.text_list
        for option in all_options:
            if option not in checked_options:
                self.select_by_value(option, without_dropdown=True)
        assert len(self.options.keys()) == len(self.text_list), (
            f"Ожидалось что будут выбраны все значения списка, выбраны: {self.text_list}"
        )


class GrafanaVariableSelect(Element):
    """Комбобокс переменных (react-select): контейнер div с input внутри, опции по role='option'."""

    @property
    def _root(self) -> Locator:
        return self.locator or self.page.locator(self.path)

    @allure.step("Ввести в поле '{0}' текст '{text}'")
    def fill(self, text: str) -> None:
        self._root.click()
        self._root.locator("input").fill(str(text))

    @allure.step("Выбрать значение '{value}' у поля '{0}'")
    def select_by_value(self, value: str) -> None:
        self._root.click()
        self._root.locator("input").fill(value)
        option = self.page.get_by_role("option", name=value)
        wait_that(
            lambda: option.is_visible(),
            message=f"Опция '{value}' не появилась в выпадающем списке",
            timeout=10,
            exception=TimeoutError,
        )
        option.click()
        self._close_dropdown()

    def _close_dropdown(self) -> None:
        """Закрывает выпадающий список: Escape или клик по контейнеру фильтра."""
        self.page.keyboard.press("Escape")
        delay(0.2, reason="дать меню время закрыться")
        listbox = self.page.get_by_role("listbox")
        if listbox.is_visible(timeout=500):
            self._root.click()


class Dropdown(BaseSelect):
    """Элементы с выпадающим списком."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(
            path=path,
            root_path=path,
            selected_text_path="span",
            option_items_path="[class*=dropdown-placement][class*=dropdown-button]:not([class*=hidden]) [class*=menu-item][role=menuitem]",
            locator_name=locator_name,
            item_text_relative_path="[class*=menu-title-content]",
        )

    @property
    def root(self) -> Locator:
        return self.page.locator(self.root_path).last

    @property
    def options(self) -> dict:
        for item in self.page.locator(self.option_items_path).all():
            self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str) -> None:
        self.options_dict = {}
        self.open_dropdown()
        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ выпадающем списке отсутствует значение '{value}'."
            f"\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.click()


class DropdownWithId(BaseSelect):
    """Элементы с выпадающим списком."""

    def __init__(self, id: str, locator_name: str):
        super().__init__(
            path=f"[class*=dropdown-trigger][id*={id}]",
            root_path="[class*=dropdown-button-wrapper]",
            selected_text_path="span",
            option_items_path=f"[class*=dropdown-menu-item][id*={id}][role=menuitem]",
            item_text_relative_path="[class*=menu-title-content]",
            locator_name=locator_name,
        )

    @property
    def options(self) -> dict:
        for item in self.page.locator(self.option_items_path).all():
            self.options_dict[item.locator(self.item_text_relative_path).text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str) -> None:
        self.options_dict = {}
        self.open_dropdown()
        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ выпадающем списке отсутствует значение '{value}'."
            f"\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.click()


class RadioOrCheckboxBlock(Select):
    """Блок элементов с радио кнопками или чекбоксами."""

    def __init__(
        self,
        path: str,
        locator_name: str,
        options_elements_path: str | None = None,
        checked_value_path: str | None = None,
    ):
        super().__init__(path, locator_name)
        if options_elements_path is None:
            self.options_elements_path = "[class*=radio-wrapper], [class*=radio-button-wrapper], [class*=checkbox-wrapper], li.ui-select-dropdown-menu__item"
        if checked_value_path is None:
            self.checked_value_path = "[class*=radio-wrapper-checked], [class*=radio-button-wrapper-checked], [class*=checkbox-wrapper-checked], li[aria-selected='true']"

    @property
    def options_elements(self) -> list:
        return self.page.locator(self.path).locator(self.options_elements_path).all()

    @property
    def checked_value(self) -> str | None:
        el = self.page.locator(self.path).locator(self.checked_value_path)
        if el.is_visible():
            return el.text_content()
        return None

    @property
    def options(self) -> dict:
        options_locator = self.page.locator(self.path).locator(self.options_elements_path).first
        try:
            expect(options_locator).to_be_visible(timeout=10000)
        except AssertionError:
            return {}

        self.options_dict = {}
        for item in self.options_elements:
            self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str, contains: bool = False) -> None:
        """
        Выбрать значение по тексту.

        Args:
            value: Текст для поиска
            contains: Если True, ищет элемент, содержащий value. Если False, ищет точное совпадение.
        """
        if contains:
            found_key = None
            for key in self.options.keys():
                if value in key:
                    found_key = key
                    break
            if found_key is None:
                raise AssertionError(
                    f"\nОтсутствует радио кнопка/чекбокс с текстом, содержащим '{value}'.\nОтображаемые значения: {list(self.options.keys())}"
                )
            element = self.options[found_key]
            element.click()
        else:
            if self.checked_value != value:
                wait_that(
                    lambda: self.find_by_value(value) is not None,
                    message=f"\nОтсутствует радио кнопка/чекбокс с текстом '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
                    timeout=5,
                    exception=AssertionError,
                )
                element = self.find_by_value(value)
                element.click()

                assert self.checked_value == value, (
                    f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"
                )

    @allure.step("Ожидание наличия класса '{class_name}' у каждого элемента '{0}'")
    def all_elements_to_have_class(self, class_name: str | re.Pattern[str]) -> None:
        for item in self.options_elements:
            expect(item).to_have_class(class_name)

    @allure.step("Ожидание отсутствия класса '{class_name}' у каждого элемента '{0}'")
    def all_elements_not_to_have_class(self, class_name: str | re.Pattern[str]) -> None:
        for item in self.options_elements:
            expect(item).not_to_have_class(class_name)


class CheckboxBlock(MultySelect):
    """Блок элементов с чекбоксами."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name)
        self.option_items_path = "[class*=-checkbox-wrapper]"
        self.item_text_relative_path = "//span[2]"
        self.selected_options_path = "[class*=-checkbox-wrapper-checked]"

    @property
    def options_elements(self) -> list:
        return self.page.locator(self.path).locator(self.option_items_path).all()


class SelectLIS(SelectDifferentRoot):
    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name)
        self.selected_text_path = "span"
        self.option_items_path = (
            "//div[@ps-list-drop-internal][not(contains(@style, 'display'))] //ps-list-item[not(@is-not-item)]"
        )

    @property
    def text(self) -> str | None:
        selected_text = self.root.locator(self.selected_text_path)
        return selected_text.text_content().strip() or selected_text.get_attribute("value").strip()

    @property
    def options(self) -> dict | None:
        items = self.page.locator(self.option_items_path).all()
        for item in items:
            if item.is_visible():
                self.options_dict[item.text_content().strip()] = item
        return self.options_dict


class SelectUniblp(SelectDifferentRoot):
    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name)
        self.selected_text_path = "span"
        self.option_items_path = (
            "div.ps-list-drop[ps-list-drop-internal]:visible ps-list-item:not(.ps-list-drop-option_no_data)"
        )

    @property
    def text(self) -> str | None:
        selected_text = self.root.locator(self.selected_text_path)
        if selected_text.count() > 0:
            return selected_text.first.text_content().strip()
        return None

    @property
    def options(self) -> dict | None:
        dropdown_list = self.page.locator("div.ps-list-drop[ps-list-drop-internal]:visible")
        if dropdown_list.count() == 0:
            return {}

        items = dropdown_list.locator("ps-list-item:not(.ps-list-drop-option_no_data)").all()
        for item in items:
            if item.is_visible():
                text = item.text_content().strip()
                if text and text != "нет данных":
                    self.options_dict[text] = item
        return self.options_dict


class BurgerMenu(SelectDifferentRoot):
    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name)
        self.need_click_tree_switcher = False
        self.option_items_path = "[role=tree] div[role=treeitem]"
        self.tree_switcher_path = "[data-icon=KeyboardArrowDown]"

    @property
    def options(self) -> dict:
        for item in self.page.locator(self.option_items_path).all():
            if item.text_content():
                self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' в бургер меню")
    def select_by_value(self, value: str) -> None:
        """Выбирает значение из бургер меню. Если в значении есть " > " то будет последовательный выбор значений.
        Поддерживается только одно вложение."""
        value_list = value.strip().split(">")
        self.open_dropdown()
        self.need_click_tree_switcher = True if ">" in value else False
        for value in value_list:
            value = value.strip()
            self.options_dict = {}
            wait_that(
                lambda: self.find_by_value(value) is not None,
                message=f"\nВ бургер меню отсутствует значение '{value}'."
                f"\nОтображаемые значения: {list(self.options.keys())}",
                timeout=5,
                exception=TimeoutError,
            )
            element = self.find_by_value(value)
            element.locator(self.tree_switcher_path if self.need_click_tree_switcher else "a").click()
            self.need_click_tree_switcher = False


class DynamicField(Element):
    """Класс для работы с доп атрибутами при создании клиента"""

    def __init__(self, path: str, field_name: str, sub_field_path: str, locator_name: str):
        """
        :param path: указывается путь до базового поля. он же div, которые содержит div'ы для каждого динамического доп. атрибута
        :param field_name: содержится в class div'а для каждого динамического доп. атрибута
        :param sub_field_path: относительный путь, до локатора который нужно вернуть в случае подходящего атрибута
        :param locator_name: описание базового поля
        """
        super().__init__(path, locator_name)
        self.field_name = field_name
        self.sub_field_path = sub_field_path
        self.options_dict: dict[str, Locator] = {}

    @property
    def root(self) -> Locator:
        return self.page.locator(self.path)

    @property
    def options(self) -> dict:
        for item in self.root.locator(self.field_name).all():
            self.options_dict[item.text_content()] = item.locator(self.sub_field_path)
        return self.options_dict

    def find_field_by_value(self, value: str) -> Locator | None:
        field = None
        for key, val in self.options.items():
            if value in key:
                return val
        return field

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str) -> Locator | None:
        self.options_dict = {}
        wait_that(
            lambda: self.find_field_by_value(value) is not None,
            message=f"\nВ списке отсутствует поле '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout=5,
            exception=TimeoutError,
        )
        locator = self.find_field_by_value(value)
        locator.click()
        return locator

    @allure.step("Получить поле с текстом '{value}' у поля '{0}'")
    def get_element_by_value(self, value: str) -> Element:
        found_field = self.find_field_by_value(value)
        assert_that(lambda: found_field is not None, f"Поле с текстом {value} не найдено")
        return Element("", f"Выбранный элемент по значению {value}", locator=found_field)

    @allure.step("Найти поле c текстом '{value}' у элемента '{0}' и проверить его доступность")
    def find_and_enable_check(self, value: str, enable: bool, *args: Any, **kwargs: Any) -> None:
        if enable:
            expect(self.find_field_by_value(value)).to_be_enabled(*args, **kwargs)
        else:
            expect(self.find_field_by_value(value)).not_to_be_enabled(*args, **kwargs)

    @allure.step("Найти поле c текстом '{value}' у элемента '{0}' и проверить его обязательность")
    def find_and_required_check(self, value: str, required: bool) -> None:
        self.locator = self.find_field_by_value(value)
        if required:
            self.check_attribute_by_value("aria-required", "true")
        else:
            self.check_attribute_not_contain_value("aria-required", "true")

    @allure.step("Найти поле c текстом '{value}' у элемента '{0}' и получить текст подсказки")
    def get_hint_text(self, value: str, timeout: int = 10000) -> str | Any | None:
        field = self.find_field_by_value(value)
        hint = field.locator(
            "xpath=ancestor::div[contains(@class,'form-item-row')][1]"
            "//div[contains(@class,'form-item-explain') and contains(@id,'_help')]//div[1]"
        )
        expect(hint).to_be_visible(timeout=timeout)
        return hint.text_content()

    @allure.step("Найти поле c текстом '{value}' у элемента '{0}' и проверить текст подсказки")
    def check_hint_contain_text(self, value: str, hint_text: str) -> None:
        assert_that(
            lambda: self.get_hint_text(value) == hint_text,
            "Нужный текст подсказки не отобразился",
        )


class VirtualSelect(SelectDifferentRoot):
    """Класс для выбора из выпадающего меню, которое появляется поверх(virtual list). Т.е не появляется под корневым div после клика"""

    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name=locator_name)

    @property
    def options(self) -> dict:
        for item in self.page.locator(self.option_items_path).all():
            self.options_dict[item.text_content()] = item
        return self.options_dict


class VirtualTable(SelectDifferentRoot):
    """Класс с работы с таблицей, в которой содержаться значения. Похоже на обычный селект."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name=locator_name)
        self.options_dict: dict[str, Locator] = {}

    @property
    def options(self) -> dict[str, Locator]:
        for item in self.page.locator(self.path).locator("[class*=table-row]").all():
            self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str, timeout: int = 10) -> None:
        self.options_dict = {}
        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ таблице отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout=timeout,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.click()


class VirtualTableCheckbox(SelectDifferentRoot):
    """Класс с работы с таблицей, в которой содержаться значения. Выбор происходит по чек-боксам."""

    def __init__(self, path: str, locator_name: str):
        super().__init__(path, locator_name=locator_name)
        self.options_dict: dict[str, Locator] = {}

    @property
    def options(self) -> dict[str, Locator]:
        for item in self.page.locator(self.path).locator("[class*=table-row]").all():
            self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str, timeout: int = 10) -> None:
        self.options_dict = {}
        wait_that(
            lambda: self.find_by_value(value) is not None,
            message=f"\nВ таблице отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout=timeout,
            exception=TimeoutError,
        )
        element = self.find_by_value(value)
        element.locator("input[type=checkbox]").click()


class ScrollableList(Element):
    """Список с виртуальным скроллом: невидимые элементы отсутствуют в DOM,
    стандартный scroll_into_view_if_needed для них не работает.
    Компонент сам прокручивает контейнер пока нужный элемент не появится.
    """

    def __init__(
        self,
        path: str,
        item_path: str,
        locator_name: str,
        scroll_step: int = 200,
    ):
        """
        :param path: путь к скроллящемуся контейнеру списка
        :param item_path: путь к элементам с текстом внутри списка (относительный к контейнеру)
        :param locator_name: описание для allure-отчёта
        :param scroll_step: шаг скролла в пикселях за итерацию
        """
        super().__init__(path, locator_name)
        self.item_path = item_path
        self.scroll_step = scroll_step

    def _item_by_text(self, value: str) -> Locator:
        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
        return self.page.locator(self.path).locator(f"{self.item_path}:text-is('{escaped}')").first

    @allure.step("Выбрать в списке '{0}' элемент с текстом '{value}'")
    def select_by_value(self, value: str, timeout: int = 15, verify_selection: bool = True) -> None:
        """
        Прокручивает список и кликает по строке с заданным текстом. Начинает прокручивать с текущей позиции до конца,
        если элемент не найден - переходит в верх списка и прокручивает вниз (элемент может быть выше текущей позиции).

        :param value: текст строки для поиска
        :param timeout: верхняя граница ожидания для обоих проходов
        :param verify_selection: если True - после клика вызывает ``_verify_selection``
        :raises AssertionError: элемент не найден за два прохода либо ``timeout`` исчерпан
        """
        item = self._item_by_text(value)
        container = self.page.locator(self.path)
        per_check_timeout_ms = 300
        deadline = time.time() + timeout

        def _click_and_verify() -> None:
            item.click()
            if verify_selection:
                self._verify_selection(value)

        def _scroll_until_visible_or_bottom() -> bool:
            """
            Прокручивает контейнер вниз от текущей позиции, пока элемент не станет виден
            или не будет достигнут конец списка.
            """
            while time.time() < deadline:
                try:
                    expect(item).to_be_visible(timeout=per_check_timeout_ms)
                    return True
                except AssertionError:
                    pass

                before, after = container.evaluate(
                    f"el => {{const b = el.scrollTop; el.scrollTop += {self.scroll_step}; return [b, el.scrollTop]; }}"
                )

                if abs(after - before) < 1:
                    return False

            raise AssertionError(
                f"В списке '{self.locator_name}' не удалось выбрать значение '{value}' за {timeout} сек "
                "(таймаут исчерпан до завершения поиска)."
            )

        if _scroll_until_visible_or_bottom():
            _click_and_verify()
            return

        container.evaluate("el => el.scrollTop = 0")
        if _scroll_until_visible_or_bottom():
            _click_and_verify()
            return

        raise AssertionError(f"В списке '{self.locator_name}' не найдено значение '{value}' (достигнут конец списка).")

    @allure.step("Проверить, что в списке '{0}' выделена строка с текстом '{value}'")
    def _verify_selection(self, value: str, timeout: int = 5) -> None:
        """Проверяет, что после клика в списке выделена ровно одна строка
        и её текст совпадает с переданным значением.

        Выделение определяется по computed-style: у выбранной строки фон
        отличается от остальных (визуально серая на фоне белых). Для каждого
        пункта списка берётся background-color ближайшего предка с непрозрачным
        фоном; пункты группируются по цвету, и выделенной считается группа
        с наименьшим числом элементов (обычно одна строка).

        :param value: ожидаемый текст выделенной строки
        :param timeout: время ожидания применения визуального выделения (сек)
        :raises AssertionError: если выделена не одна строка, её текст
            не совпадает с `value`, либо у всех строк одинаковый фон
        """
        list_items = self.page.locator(self.path).locator(self.item_path)

        # Для каждого пункта поднимаемся по DOM до ближайшего предка с
        # непрозрачным background-color и возвращаем найденный фон + текст.
        js_collect_row_state = """
            items => items.map(item => {
                let node = item;
                let background = '';
                while (node) {
                    const color = getComputedStyle(node).backgroundColor;
                    if (color && color !== 'rgba(0, 0, 0, 0)' && color !== 'transparent') {
                        background = color;
                        break;
                    }
                    node = node.parentElement;
                }
                return { text: (item.textContent || '').trim(), background };
            })
        """

        def _is_expected_row_highlighted() -> bool:
            rows_state = list_items.evaluate_all(js_collect_row_state)
            rows_by_background: dict[str, list[str]] = {}
            for row in rows_state:
                rows_by_background.setdefault(row["background"], []).append(row["text"])

            if len(rows_by_background) < 2:
                return False

            highlighted_background = min(rows_by_background, key=lambda bg: len(rows_by_background[bg]))
            highlighted_row_texts = rows_by_background[highlighted_background]

            return len(highlighted_row_texts) == 1 and highlighted_row_texts[0] == value

        wait_that(
            _is_expected_row_highlighted,
            exception=AssertionError,
            message=(
                f"После выбора в списке '{self.locator_name}' не найдена ровно одна "
                f"выделенная строка с текстом '{value}'"
            ),
            timeout=timeout,
            sleep_seconds=0.3,
        )

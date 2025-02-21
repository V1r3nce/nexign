import re
from pathlib import Path

import allure
from playwright.sync_api import Page, expect, Locator
from waiting import wait


class Element:
    def __init__(self, path: str, locator_name: str, page: Page, locator: Locator=None):
        self.page = page
        self.path = path
        self.locator_name = locator_name
        self.locator = locator

    def __str__(self):
        return self.locator_name

    def __repr__(self):
        return self.locator_name

    @allure.step("Нажать на '{0}'")
    def click(self, *args, **kwargs):
        if self.locator:
            self.locator.click(*args, **kwargs)
        else:
            self.page.locator(self.path).click(*args, **kwargs)

    @property
    def text(self):
        if self.locator:
            return self.locator.text_content() or self.locator.get_attribute('value')
        else:
            el = self.page.locator(self.path)
            return el.text_content() or el.get_attribute('value')

    @allure.step("Ввести в поле '{0}' текст '{1}'")
    def fill(self, text: str):
        el = self.locator or self.page.locator(self.path)
        el.fill(text)

    @allure.step("Стереть текст, в поле '{0}'")
    def clear_input(self):
        el = self.locator or self.page.locator(self.path)
        el.fill("")

    @allure.step("Загрузить в элемент '{0}' файлы '{1}'")
    def upload_files(self, files: [str, Path]):
        (self.locator or self.page.locator(self.path)).set_input_files(files)

    @allure.step("Ожидание визуального присутствия '{0}'")
    def wait_to_be_visible(self, *args, **kwargs):
        expect(self.locator or self.page.locator(self.path)).to_be_visible(*args, **kwargs)

    @allure.step("Поле '{0}' содержит текст '{text}'")
    def to_contain_text(self, text: str, clear_phone=False):
        """Проверка, что поле содержит текст.
        Parameters:
            text: (str): текст для проверки.
            clear_phone: (bool): приводить ли текст к номеру телефона.
        """
        element_text = self.text
        if clear_phone:
            element_text = re.sub(r"[^\d+]", "", self.text)
        if element_text:
            assert text in element_text, f"Поле '{self}' не содержит текст '{text}'.\nТекущий текст '{self.text}'"
        else:
            raise AssertionError(f"Поле '{self}' пустое.")

    @allure.step("Поле '{0}' содержит свойство value '{text}'")
    def to_have_value(self, text: str, timeout: int = 5000):
        expect(self.locator or self.page.locator(self.path)).to_have_value(value=text, timeout=timeout)

    @allure.step("Проверить, что элемент '{0}' активен")
    def to_be_enabled(self, *args, **kwargs):
        expect(self.locator or self.page.locator(self.path)).to_be_enabled(*args, **kwargs)

    @allure.step("Проверить, что элемент '{0}' не активен")
    def not_to_be_enabled(self, *args, **kwargs):
        expect(self.locator or self.page.locator(self.path)).not_to_be_enabled(*args, **kwargs)

    @allure.step("Проверить, что элемент '{0}' отсутствует")
    def not_to_be_visible(self, *args, **kwargs):
        expect(self.locator or self.page.locator(self.path)).not_to_be_visible(*args, **kwargs)

    @allure.step("Прокрутить до элемента '{0}'")
    def scroll_into_view_if_needed(self):
        if self.locator:
            self.locator.scroll_into_view_if_needed()
        else:
            self.page.locator(self.path).scroll_into_view_if_needed()

    @allure.step("Поле '{0}' содержит текст '{1}' с ожиданием")
    def wait_to_have_text(self, *args, **kwargs):
        expect(self.locator or self.page.locator(self.path)).to_have_text(*args, **kwargs)

    @allure.step("Поле '{0}' не содержит текст '{text}'")
    def not_to_contain_text(self, text: str, timeout: int = 5000):
        expect(self.locator or self.page.locator(self.path)).not_to_contain_text(expected=text, timeout=timeout)

    @allure.step("Получить html для блока элемента '{0}'")
    def inner_html(self):
        if self.locator:
            return self.locator.inner_html()
        else:
            el = self.page.locator(self.path)
            return el.inner_html()

    @allure.step("Атрибут '{attribute}' элемента '{0}' содержит значение '{value}'")
    def check_attribute_by_value(self, attribute: str, value: str):
        expect(self.locator or self.page.locator(self.path)).to_have_attribute(attribute, value)

    @allure.step("Проверить, что элемент '{0}' не содержит атрибут 'disabled'")
    def element_not_contain_disabled_attribute(self):
        return (self.locator or self.page.locator(self.path)).evaluate('element => !element.hasAttribute("disabled")')

    @allure.step("Ожидание наличия класса '{class_name}' в элементе '{0}'")
    def to_have_class(self, class_name: str):
        expect(self.locator or self.page.locator(self.path)).to_have_class(class_name)

    @allure.step("Ожидание css атрибута '{attribute}' элемента '{0}' равного '{value}'")
    def to_have_css(self, attribute: str, value: str):
        expect(self.locator or self.page.locator(self.path)).to_have_css(attribute, value)

    @allure.step("Сравнение цвета свойства {css_property} с ожидаемым {expected_color} для элемента {0}")
    def element_have_css_color(self, css_property: str, expected_color: str):
        """
        Проверка цвета у элемента: принимает строковое наименование цвета
        и сравнивает со своим словарем цветовых значений, затем проверяет цвет у элемента.

        :param css_property - свойство, у которого проверяется значение цвета (н.п. background-color)
        :param expected_color - название ожидаемого значения цвета (н.п. "green")
        """
        color_map = {
            "green": r"rgb\(0, 173, 33\)",
            "dark_green": r"rgb\(69, 166, 0\)",
            "grey": r"rgb\(160, 173, 180\)",
            "dark_grey": r"rgb\(39, 45, 52\)",
            "dark_red": r"rgb\(203, 0, 0\)",
        }

        if expected_color in color_map:
            expected_color = color_map.get(expected_color)
        else:
            raise ValueError(
                f"Цвет '{expected_color}' отсутствует в словаре допустимых цветов: {list(color_map.keys())}")
        expect(self.locator or self.page.locator(self.path)).to_have_css(css_property, re.compile(expected_color))

    @allure.step("Ожидание доступности '{0}'")
    def wait_to_be_enabled(self, *args, **kwargs):
        expect(self.locator or self.page.locator(self.path)).to_be_enabled(*args, **kwargs)

    @allure.step("Навести курсор на '{0}'")
    def hover(self):
        self.locator or self.page.locator(self.path).hover()


class ElementsList(Element):
    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)

    def __getitem__(self, key):
        return [Element(self.path, self.locator_name, self.page, locator=el.first) for el in self.page.locator(self.path).all()][key]

    @allure.step("Поле '{0}' с индексом '{element_index}' содержит текст '{text}'")
    def to_contain_text(self, element_index: int, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).to_contain_text(expected=text, timeout=timeout)

    @allure.step("Нажать элемент '{0}' с индексом {element_index}'")
    def click(self, element_index: int):
        self.page.locator(self.path).nth(element_index).click()

    @allure.step("Прокрутить до элемента '{0}' с индексом {element_index}'")
    def scroll_into_view_if_needed(self, element_index: int):
        self.page.locator(self.path).nth(element_index).scroll_into_view_if_needed()

    @allure.step("Дождаться визуального наличия элемента для '{0}' с индексом {element_index}'")
    def wait_elements_visible(self, element_index: int, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).to_be_visible(timeout=timeout)

    @allure.step("Получить количество элементов для '{0}'")
    def elements_len(self):
        return self.page.locator(self.path).count()

    @allure.step("Поле '{0}' с индексом {element_index} не содержит текст '{text}'")
    def not_to_contain_text(self, element_index: int, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).not_to_contain_text(expected=text, timeout=timeout)

    @allure.step("Получить html блока для '{0}'")
    def inner_html(self, element_index: int):
        return self.page.locator(self.path).nth(element_index).inner_html()

    @allure.step("Ожидание наличия класса '{class_name}' в элементе '{0}' с индексом {element_index}")
    def wait_to_have_class(self, element_index: int, class_name: str):
        expect(self.page.locator(self.path).nth(element_index)).to_have_class(class_name)

    @allure.step("Ожидание появления текста '{text}' в одном из элементов списка '{0}'")
    def wait_for_text_in_all(self, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path)).to_contain_text(expected=text, timeout=timeout)

    @allure.step("Проверка, что в списке элементов '{0}' есть текст '{expected_text}'")
    def to_contain_text_in_any(self, expected_text: str, timeout: int = 5000):
        elements = self.page.locator(self.path).all()

        for element in elements:
            if expected_text in element.text_content():
                return

        raise ValueError(f"В списке элементов нет текста {expected_text}")

    @allure.step("Проверка, что в списке элементов '{0}' нет текста '{expected_text}'")
    def not_to_contain_text_in_any(self, expected_text: str, timeout: int = 5000):
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

    @allure.step("Сравнение цвета свойства {css_property} с ожидаемым {expected_color}")
    def to_have_css_color(self, css_property: str, expected_color: str):
        """
        Проверка цвета у свойств всех элементов списка: принимает строковое наименование цвета
        и сравнивает со своим словарем цветовых значений, затем проходяится по списку, сравнивая со словарным значением цвета.

        :param css_property - свойство, у которого проверяется значение цвета (н.п. background-color)
        :param expected_color - название ожидаемого значения цвета (н.п. "green")
        """
        COLOR_MAP = {
            "green": "rgb(0, 173, 33)",
            "grey": "rgb(160, 173, 180)"
        }
        
        if expected_color in COLOR_MAP:
            expected_color = COLOR_MAP.get(expected_color)
        else:
            raise ValueError(f"Цвет '{expected_color}' отсутствует в словаре допустимых цветов: {list(COLOR_MAP.keys())}")

        for element in self.page.locator(self.path).all():
            expect(element).to_have_css(css_property, expected_color)

    @allure.step("Ожидание количества элементов '{0}' должно быть '{1}'")
    def wait_to_have_count(self, count: int, *args, **kwargs):
        expect(self.page.locator(self.path)).to_have_count(count, *args, **kwargs)

    @allure.step("Ожидание визуального отсутствия всех '{0}'")
    def wait_not_to_be_visible(self, *args, **kwargs):
        [expect(el).not_to_be_visible(*args, **kwargs) for el in self.page.locator(self.path).all()]

    @allure.step("Ожидание css атрибута '{2}' элемента '{0}' равного '{3}'")
    def wait_to_have_css(self, element_index: int, attribute: str, value: str):
        expect(self.page.locator(self.path).nth(element_index)).to_have_css(attribute, value)

    @allure.step("Ожидание визуального присутствия всех '{0}'")
    def wait_to_be_visible(self, *args, **kwargs):
        [expect(el).to_be_visible(*args, **kwargs) for el in self.page.locator(self.path).all()]


class Select(Element):
    """Элементы с выпадающим списком."""

    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)
        self.options_dict = {}

    def open_dropdown(self):
        self.field.click()

    @property
    def field(self):
        return self.page.locator(".ant-select").filter(has=self.page.locator(self.path)).last

    @property
    def text(self):
        selected_text = self.field.locator(".ant-select-selection-item")
        return selected_text.text_content() or selected_text.get_attribute('value')

    @property
    def options(self):
        for item in self.field.locator(".ant-select-item-option").all():
            self.options_dict[item.locator("div > span").text_content()] = item
        return self.options_dict

    def find_by_value(self, value: str):
        element = None
        if value in self.options.keys():
            element = self.options[value]
        return element

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str):
        self.options_dict = {}
        self.open_dropdown()
        wait(lambda: self.find_by_value(value) is not None, waiting_for=f"\nВ выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}", timeout_seconds=5)
        element = self.find_by_value(value)
        element.click()

        assert self.text == value, f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"


class DropDownMenu(Select):
    """Элементы с выпадающим списком."""
    @property
    def field(self):
        return self.page.locator(self.path)

    @property
    def options(self):
        for item in self.field.locator("li[role=menuitem]").all():
            self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str):
        self.options_dict = {}
        wait(
            lambda: self.find_by_value(value) is not None,
            waiting_for=f"\nВ выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}",
            timeout_seconds=5
        )
        element = self.find_by_value(value)
        element.click()


class Autocomplete(Select):
    """Элементы с автокомплитным выбором. Сначала вводится текст в поле, затем выбирается значение из выпадающего списка."""

    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)

    @property
    def field(self):
        return self.page.locator(".ant-form-item").filter(has=self.page.locator(self.path))

    @property
    def text(self):
        el = self.page.locator(self.path)
        if el.text_content() or el.get_attribute('value'):
            return el.text_content() or el.get_attribute('value')
        selected_text = self.field.locator(".ant-select-selection-item")
        return selected_text.text_content() or selected_text.get_attribute('value')

    @allure.step("Выбрать значение c текстом '{value}' у поля с автокомплитом '{0}'")
    def select_by_value(self, value: str):
        self.options_dict = {}
        self.open_dropdown()

        self.page.locator(self.path).fill(value[:-1])  # вводим текст, без последнего символа
        wait(lambda: self.find_by_value(value) is not None, waiting_for=f"\nВ выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}", timeout_seconds=5)
        element = self.find_by_value(value)
        element.click()

        assert self.text == value, f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"


class DatePicker(Element):
    """Элементы с полем выбора даты."""

    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)

    def fill(self, text: str, *args, **kwargs):
        el = self.page.locator(self.path)
        el.click()
        el.fill(text)
        self.page.keyboard.press("Enter")

        assert self.text == text, f"Не удалось ввести дату '{text}'\nТекущее значение: {el.text_content()}"


class MultySelect(Select):
    """Элементы с полем выбора нескольких значений."""

    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)
        self.options_dict = {}

    @property
    def field(self):
        return self.page.locator(self.path)

    @property
    def selected_options(self):
        if not self.options_dict:
            for item in self.field.locator(".ant-select-selection-overflow-item > span").all():
                self.options_dict[item.text_content()] = item
        return self.options_dict

    def find_by_value(self, value: str):
        element = None
        if value in self.options.keys():
            element = self.options[value]
        return element

    @property
    def text_list(self):
        return [item_text for item_text in self.selected_options.keys()]

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str):
        self.options_dict = {}
        self.open_dropdown()
        wait(lambda: self.find_by_value(value) is not None, waiting_for=f"\nВ поле мультиселекта отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}", timeout_seconds=5)
        element = self.find_by_value(value)
        element.click()
        self.open_dropdown()

        assert value in self.text_list, f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"


class Dropdown(Select):
    """Элементы с выпадающим списком."""

    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)

    @property
    def field(self):
        return self.page.locator(self.path)

    @property
    def options(self):
        if not self.options_dict:
            for item in self.page.locator(".ant-dropdown-menu-item").all():
                self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str):
        self.options_dict = {}
        self.open_dropdown()
        element = self.find_by_value(value)
        assert element, f"В выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}"
        element.click()

class RadioOrCheckbox(Select):
    """Элементы с радио кнопками или чекбоксом."""
    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)
        self.options_dict = {}

    @property
    def checked_value(self) -> str | None:
        el = self.page.locator(self.path).locator(".ant-radio-wrapper-checked,.ant-checkbox-wrapper-checked")
        if el.is_visible():
            return el.text_content()
        return None

    @property
    def options(self):
        if not self.options_dict:
            for item in self.page.locator(self.path).locator(".ant-radio-wrapper,.ant-checkbox-wrapper").all():
                self.options_dict[item.text_content()] = item
        return self.options_dict

    @allure.step("Выбрать значение c текстом '{value}' у поля '{0}'")
    def select_by_value(self, value: str):
        if self.checked_value != value:
            self.options_dict = {}
            wait(lambda: self.find_by_value(value) is not None, waiting_for=f"\nОтсутствует радио кнопка/чекбокс с текстом '{value}'.\nОтображаемые значения: {list(self.options.keys())}", timeout_seconds=5)
            element = self.find_by_value(value)
            element.click()

            assert self.checked_value == value, f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"
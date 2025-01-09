import re
import time

import allure
from playwright.sync_api import Page, expect, Locator


class Element:
    def __init__(self, path: str, locator_name: str, page: Page, locator:Locator=None):
        self.page = page
        self.path = path
        self.locator_name = locator_name
        self.locator = locator

    def __str__(self):
        return self.locator_name

    def __repr__(self):
        return self.locator_name

    @allure.step("Нажать на '{0}'")
    def click(self):
        if self.locator:
            self.locator.click()
        else:
            self.page.locator(self.path).click()

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
        assert text in element_text, f"Поле '{self}' не содержит текст '{text}'.\nТекущий текст '{self.text}'"

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

    def select_option(self, value, *args, **kwargs):
        if self.locator:
            self.locator.select_option(value, *args, **kwargs)
        else:
            self.page.locator(self.path).select_option(value, *args, **kwargs)

    # todo рудимент. после простановки data аттрибутов элементам - удалить и заменить на методы Select/Autocomplete классов
    @allure.step("Нажать на '{0}' и выбрать значение")
    def click_and_choose(self, order_value: int):
        self.page.locator(self.path).click()
        for _ in range(order_value):
            self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")

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

    @allure.step("Количество элементов '{0}' должно быть '{count}'")
    def to_have_count(self, count: int):
        expect(self.page.locator(self.path)).to_have_count(count)

    @allure.step("Поле '{0}' с индексом {element_index} не содержит текст '{text}'")
    def not_to_contain_text(self, element_index: int, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).not_to_contain_text(expected=text, timeout=timeout)

    @allure.step("Получить html блока для '{0}'")
    def inner_html(self, element_index: int):
        return self.page.locator(self.path).nth(element_index).inner_html()


class Select(Element):
    """Элементы с выпадающим списком."""

    def __init__(self, path: str, locator_name: str, page: Page):
        super().__init__(path, locator_name, page)
        self.options_dict = {}

    def open_dropdown(self):
        self.field.click()

    @property
    def field(self):
        return self.page.locator(".ant-select").filter(has=self.page.locator(self.path))

    @property
    def text(self):
        selected_text = self.field.locator(".ant-select-selection-item")
        return selected_text.text_content() or selected_text.get_attribute('value')

    @property
    def options(self):
        if not self.options_dict:
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
        time.sleep(.2)  # некоторые элементы могут не отображаться сразу
        element = self.find_by_value(value)
        assert element, f"В выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}"
        element.click()

        assert self.text == value, f"Не удалось выбрать значение '{value}'\nТекущее значение: {self.text}"


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
        time.sleep(1)  # некоторые элементы могут не отображаться сразу
        assert value in self.options.keys(), f"В выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}"

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
        time.sleep(.2)  # некоторые элементы могут не отображаться сразу
        element = self.find_by_value(value)
        assert element, f"В выпадающем списке отсутствует значение '{value}'.\nОтображаемые значения: {list(self.options.keys())}"
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

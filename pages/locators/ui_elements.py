import allure
from playwright.sync_api import Page, expect


class Element:
    def __init__(self, path: str, locator_name: str, page: Page):
        self.page = page
        self.path = path
        self.locator_name = locator_name

    def __str__(self):
        return self.locator_name

    def __repr__(self):
        return self.locator_name

    @allure.step("Нажать на '{0}'")
    def click(self):
        self.page.locator(self.path).click()

    @allure.step("Ввести в поле '{0}' текст '{1}'")
    def fill(self, text: str):
        self.page.locator(self.path).fill(text)

    @allure.step("Ожидание визуального присутствия '{0}'")
    def wait_to_be_visible(self):
        expect(self.page.locator(self.path)).to_be_visible()

    @allure.step("Поле '{0}' содержит текст '{1}'")
    def to_contain_text(self, text: str):
        expect(self.page.locator(self.path)).to_contain_text(text)

    @allure.step("Получить текст для '{0}'")
    def text_content(self):
        return self.page.locator(self.path).text_content()

    @allure.step("Поле '{0}' содержит свойство value '{text}'")
    def to_have_value(self, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path)).to_have_value(value=text, timeout=timeout)

    @allure.step("Проверить, что элемент '{0}' активен")
    def to_be_enabled(self):
        expect(self.page.locator(self.path)).to_be_enabled()

    @allure.step("Проверить, что элемент '{0}' не активен")
    def not_to_be_enabled(self):
        expect(self.page.locator(self.path)).not_to_be_enabled()

    @allure.step("Проверить, что элемент '{0}' отсутствует")
    def not_to_be_visible(self):
        expect(self.page.locator(self.path)).not_to_be_visible()

    @allure.step("Прокрутить до элемента '{0}'")
    def scroll_into_view_if_needed(self):
        self.page.locator(self.path).scroll_into_view_if_needed()


class ElementsList:
    def __init__(self, path: str, locator_name: str, page: Page):
        self.page = page
        self.path = path
        self.locator_name = locator_name

    def __str__(self):
        return self.locator_name

    def __repr__(self):
        return self.locator_name

    @allure.step("Поле '{0}' с индексом {element_index} содержит текст '{text}'")
    def to_contain_text(self, element_index: int, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).to_contain_text(expected=text, timeout=timeout)

    @allure.step("Получить текст для '{0}' с индексом {element_index}'")
    def get_text(self, element_index: int):
        return self.page.locator(self.path).nth(element_index).text_content()

    @allure.step("Нажать элемент '{0}' с индексом {element_index}'")
    def click(self, element_index: int):
        self.page.locator(self.path).nth(element_index).click()

    @allure.step("Прокрутить до элемента '{0}' с индексом {element_index}'")
    def scroll_into_view_if_needed(self, element_index: int):
        self.page.locator(self.path).nth(element_index).scroll_into_view_if_needed()

    @allure.step("Дождаться визуального наличия элементов для '{0}' с индексом {element_index}'")
    def wait_elements_visible(self, element_index: int, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).to_be_visible(timeout=timeout)

    @allure.step("Дождаться визуального отсутствия элементов для '{0}' с индексом {element_index}'")
    def not_to_be_visible(self, element_index: int, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).not_to_be_visible(timeout=timeout)

    @allure.step("Получить количество элементов для '{0}'")
    def elements_len(self):
        return self.page.locator(self.path).count()

    @allure.step("Поле '{0}' с индексом {element_index} не содержит текст '{text}'")
    def not_to_contain_text(self, element_index: int, text: str, timeout: int = 5000):
        expect(self.page.locator(self.path).nth(element_index)).not_to_contain_text(expected=text, timeout=timeout)

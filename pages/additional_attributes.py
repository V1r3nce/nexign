import allure
from playwright.sync_api import Page

from common.helpers.checker import assert_that
from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.additional_attributes import AdditionalAttributes
from pages.ui_elements import ElementsList


class AdditionalAttributesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.attribute_locator = AdditionalAttributes(page)

    def fill_name(self, name: str) -> None:
        self.attribute_locator.NAMES.wait_to_be_visible()
        delay(0.5)
        self.attribute_locator.NAMES[0].type(name)
        self.attribute_locator.NAMES[1].type(name)
        self.attribute_locator.CODE.type(name)

    def check_if_elements_sorted(self, elements_list: ElementsList) -> None:
        prev = elements_list[0].text
        for code in elements_list:
            assert_that(lambda: prev <= code.text, "Сортировка по коду атрибута не сработала")
            prev = code.text

    def clear_names_edit_sidebar(self) -> None:
        self.attribute_locator.NAMES.wait_to_be_visible()
        delay(0.5)
        for i in range(2):
            self.attribute_locator.EDIT_CLEAR_NAMES[i].click()
            delay(0.5)

    def delete_attribute(self, name: str, base_url: str) -> None:
        self.attribute_locator.base_page.open(f"{base_url}additional-attributes/attributes")
        self.attribute_locator.ENTITY_SEARCH.wait_to_be_visible(timeout=10000)
        self.attribute_locator.ENTITY_SEARCH.type(name)
        self.attribute_locator.ENTITY_CODE.wait_to_have_count(1)
        self.attribute_locator.ENTITY_CODE[0].click()
        self.attribute_locator.DELETE_BUTTON.click()
        self.attribute_locator.DELETE_MESSAGE_BUTTON.click()
        self.attribute_locator.ADD_BUTTON.wait_to_be_visible()
        self.attribute_locator.ENTITY_SEARCH_CLEAR.click()

    @allure.step("Добавление атрибута")
    def add_attribute(self, name: str, entity: str, variant: str = "default") -> None:
        self.attribute_locator.ADD_BUTTON.click()
        self.attribute_locator.NAMES.wait_to_be_visible()
        self.fill_name(name)
        if variant == "mandatory_1":
            self.attribute_locator.MIN_CARDINALITY.fill("0")
            self.attribute_locator.MAX_CARDINALITY.fill("2")
        elif variant == "mandatory_2":
            self.attribute_locator.MIN_CARDINALITY.fill("1")
            self.attribute_locator.MAX_CARDINALITY.fill("2")
        else:
            if variant not in ["uneditable", "editable"]:
                self.attribute_locator.MAX_CARDINALITY.fill("100")
        if variant == "template":
            self.attribute_locator.CHECKBOXES[0].click()
        else:
            self.attribute_locator.ENTITY.select_by_value(entity)
        if variant == "template":
            self.attribute_locator.TYPE.select_by_value("DICTIONARY")
            self.attribute_locator.GET_DICT_METHOD.select_by_value("Вызов метода получения справочника")
            self.attribute_locator.GET_DICT_STR.type("openapi/v1/customerManagement/dictionaries/languages")
            self.attribute_locator.GET_DICT_STR_METHOD.select_by_value("GET")
            self.attribute_locator.RESPONSE_ID_ATTRIBUTE.type("languageId")
            self.attribute_locator.RESPONSE_NAME_ATTRIBUTE.type("name")
        elif variant == "uneditable":
            self.attribute_locator.TYPE.select_by_value("BOOLEAN")
            self.attribute_locator.CHECKBOXES[2].click()
        elif variant == "editable":
            self.attribute_locator.TYPE.select_by_value("BOOLEAN")
        else:
            self.attribute_locator.TYPE.select_by_value("INTEGER")
            self.attribute_locator.UI_TYPE.select_by_value("numberField")
        if variant == "hint":
            self.attribute_locator.HINT_TEXT.type(f"hint_{name}")
        self.attribute_locator.APPLY_BUTTON.click()

    @allure.step("Проверка, что атрибут добавился")
    def check_attribute_added(self, name: str) -> None:
        self.attribute_locator.ENTITY_SEARCH.wait_to_be_visible()
        self.attribute_locator.ENTITY_SEARCH.type(name)
        self.attribute_locator.ENTITY_CODE.wait_to_have_count(1)
        self.attribute_locator.ENTITY_SEARCH_CLEAR.wait_to_be_visible()
        self.attribute_locator.ENTITY_SEARCH_CLEAR.click()

    @allure.step("Выбор атрибута")
    def choose_attribute(self, name: str) -> None:
        self.attribute_locator.ENTITY_SEARCH.wait_to_be_visible()
        self.attribute_locator.ENTITY_SEARCH.type(name)
        self.attribute_locator.ENTITY_CODE.wait_to_have_count(1)
        self.attribute_locator.ENTITY_CODE[0].click()

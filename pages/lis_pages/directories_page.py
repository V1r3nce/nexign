import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.lis_locators.directories_elements import DirectoriesElementsLis


class DirectoriesPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = DirectoriesElementsLis(page)

    @allure.step("Проверка справочника 'Классы номеров'")
    def check_dictionary_number_classes(self):
        self.locators.TABLE_LINE.wait_elements_visible(0)
        assert self.locators.TABLE_LINE.elements_len() >= 6, "Не отображаются элементы справочника 'Классы номеров'"
        self.locators.TABLE_COLUMN_NAMES[0].wait_to_have_text("Элемент справочника")
        self.locators.TABLE_COLUMN_NAMES[1].wait_to_have_text("Активный")

    @allure.step("Проверка формы 'Добавление элемента справочника'")
    def check_add_dictionary_element(self):
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].wait_to_have_text("Добавление элемента справочника")
        self.locators.ADD_NAME_INPUT_TITLE.check_attribute_by_value("on-required-label", "")
        self.locators.ADD_NAME_INPUT.element_not_contain_disabled_attribute()
        self.locators.ADD_ACTIVE_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.ADD_FEDERAL_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.ADD_ELEMENT_BTN.wait_to_have_text("Добавить")
        self.locators.CANCEL_ADD_ELEMENT_BTN.wait_to_have_text("Отменить")

    @allure.step("Проверка формы 'Редактирование элемента справочника'")
    def check_edit_dictionary_element(self):
        self.locators.MODAL.wait_elements_visible(0)
        self.locators.MODAL_TITLE[0].wait_to_have_text("Редактирование элемента справочника")
        self.locators.EDIT_NAME_INPUT.element_not_contain_disabled_attribute()
        self.locators.EDIT_ACTIVE_CHECKBOX.element_not_contain_disabled_attribute()
        self.locators.SAVE_EDIT_ELEMENT_BTN.wait_to_have_text("Сохранить")
        self.locators.CANCEL_EDIT_ELEMENT_BTN.wait_to_have_text("Отменить")

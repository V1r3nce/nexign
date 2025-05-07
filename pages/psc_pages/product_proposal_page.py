import allure
from playwright.sync_api import Page

from common.helpers.time_helpers import delay
from pages.base_page import BasePage
from pages.locators.psc_locators.pp_elements_psc import CreatePriceFormElements, ProductProposalDetailsElements


class ProductProposalPagePsc(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = ProductProposalDetailsElements(page)
        self.create_price_form = CreatePriceFormElements(page)

    @allure.step("Выбрать опцию {option}")
    def choose_option(self, option: str) -> str | None:
        self.locators.OPTIONS.wait_to_be_visible(timeout=10000)
        delay(0.7)
        for item in self.locators.OPTIONS:
            if item.text == option:
                item.click()
                return option
        raise AssertionError(f"Не найдена опция {option}")

    @allure.step("Добавить характеристику {name}")
    def add_characteristic(self, name: str) -> None:
        self.locators.ADD_BTN.click()
        self.locators.SEARCH_INPUT.fill(name)
        delay(0.7)
        for item in self.locators.CHARACTERISTICS_OPTIONS:
            if f" {name} " in item.text:
                item.click()
                break

    @allure.step("Добавить мета характеристику '{meta_name}' и ее значение '{meta_value}'")
    def add_meta_characteristic_and_value(self, meta_name: str, meta_value: str) -> str | None:
        self.locators.META_ADD_BTN.click()
        self.locators.SEARCH_INPUT.fill(meta_name)
        delay(0.7)
        for item in self.locators.CHARACTERISTICS_OPTIONS:
            if f" {meta_name} " == item.text:
                item.click(force=True)
                break
        self.locators.META_CHARACTERISTIC_DROPDOWN_BTN[-1].click()
        self.choose_option(meta_value)
        return meta_value

    @allure.step("Добавить мета характеристику {meta_name}")
    def add_meta_characteristic(self, meta_name: str) -> str | None:
        self.locators.META_ADD_BTN.click()
        self.locators.SEARCH_INPUT.fill(meta_name)
        delay(0.7)
        for item in self.locators.CHARACTERISTICS_OPTIONS:
            if f" {meta_name} " == item.text:
                item.click(force=True)
            return meta_name
        raise AssertionError(f"Не найдена опция {meta_name}")

    @allure.step("Добавить характеристику {name}")
    def add_form_characteristic(self, name: str) -> None:
        self.create_price_form.ADD_CHARACTERISTIC_BTN.click()
        self.create_price_form.SEARCH_INPUT.fill(name)
        delay(0.7)
        for item in self.locators.CHARACTERISTICS_OPTIONS:
            if f" {name} " in item.text:
                item.click()
                break

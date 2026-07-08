import allure

from pages.base_page import BasePage
from pages.locators.nbss.finances.discount_charges_setting import DiscountChargesSettingElements


class DiscountChargesSettingPage(BasePage):
    """Страница настройки шаблонов 'Скидки/доначисления' (Биллинг > Скидки/доначисления)"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = DiscountChargesSettingElements()

    @allure.step("Открыть страницу 'Скидки/доначисления' через боковое меню")
    def open_discount_charges_setting_page(self) -> None:
        self.open_home_page()
        self.base_elements.BURGER_MENU.select_by_value("Биллинг > Скидки/доначисления")
        self.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")

    @allure.step("Создать шаблон биллинговой скидки '{discount_scheme_name_ru}'")
    def create_discount_template(
        self,
        discount_scheme_name_ru: str,
        discount_scheme_name_en: str,
        start_date: str,
        end_date: str,
        discount_priority: str = "5",
        discount_size: str = "10",
        threshold_size: str = "100",
    ) -> None:
        self.locators.ADD_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.ADD_BTN.click()
        self.fill_discount_data(
            discount_scheme_name_ru=discount_scheme_name_ru,
            discount_scheme_name_en=discount_scheme_name_en,
            start_date=start_date,
            end_date=end_date,
        )
        self.locators.ADD_ACTION_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.ADD_ACTION_BTN.click()
        self.fill_discount_action(
            discount_priority=discount_priority, discount_size=discount_size, threshold_size=threshold_size
        )

    @allure.step("Заполнить параметры шаблона биллинговой скидки")
    def fill_discount_data(
        self, discount_scheme_name_ru: str, discount_scheme_name_en: str, start_date: str, end_date: str
    ) -> None:
        self.locators.DISCOUNT_NAME[0].fill(discount_scheme_name_ru)
        self.locators.DISCOUNT_NAME[1].fill(discount_scheme_name_en)
        self.locators.DATE[0].fill(start_date)
        self.page.keyboard.press("Tab")
        self.locators.DATE[1].fill(end_date)
        self.page.keyboard.press("Tab")

    @allure.step("Заполнить параметры действия шаблона биллинговой скидки")
    def fill_discount_action(
        self,
        discount_priority: str = "5",
        discount_size: str = "10",
        threshold_size: str = "100",
    ) -> None:
        self.locators.ACTION.select_by_value("Скидка при превышении порога потребления")
        self.page.keyboard.press("Enter")
        self.locators.ACTION_PRIORITY.fill(discount_priority)
        self.locators.DISCOUNT.fill(discount_size)
        self.locators.THRESHOLD.fill(threshold_size)
        self.locators.UPDATE_BTN.click()
        self.locators.SAVE_BTN.click()

    @allure.step("Найти шаблон '{template_name}' в таблице и выбрать его")
    def find_and_select_template(self, template_name: str) -> None:
        self.refresh_page(wait="networkidle")
        self.locators.ROW_DISCOUNT.wait_to_be_visible(timeout=20000)
        self.locators.NAME_FIND_TABLE.fill(template_name)
        self.locators.ROW_DISCOUNT.wait_to_have_count(1)
        self.locators.ROW_DISCOUNT[0].click()

    @allure.step("Отредактировать размер скидки в действии выбранного шаблона")
    def edit_discount_action_size(self, discount_size: str) -> None:
        self.locators.DISCOUNT_EDIT_BTN[0].wait_to_be_enabled(timeout=15000)
        self.locators.DISCOUNT_EDIT_BTN[0].click()
        self.locators.NAME_ACTION_DISCOUNT.wait_to_be_visible(timeout=20000)
        self.locators.NAME_ACTION_DISCOUNT[0].click()
        self.locators.DISCOUNT_EDIT_BTN[1].wait_to_be_enabled(timeout=15000)
        self.locators.DISCOUNT_EDIT_BTN[1].click()
        self.locators.SIZE_DISCOUNT.wait_to_be_visible(timeout=20000)
        self.locators.SIZE_DISCOUNT.fill(discount_size)
        self.locators.UPDATE_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.UPDATE_BTN.click()
        self.locators.SAVE_BTN.wait_to_be_visible(timeout=20000)
        self.locators.SAVE_BTN.click()

    @allure.step("Удалить выбранный шаблон биллинговой скидки")
    def delete_selected_template(self) -> None:
        self.locators.DISCOUNT_DELETE_BTN[0].wait_to_be_enabled(timeout=20000)
        self.locators.DISCOUNT_DELETE_BTN[0].click()
        self.locators.ACCEPT_DISCOUNT_DELETE_BTN.wait_to_be_enabled(timeout=20000)
        self.locators.ACCEPT_DISCOUNT_DELETE_BTN.click()

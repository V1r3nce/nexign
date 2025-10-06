import allure
import pytest
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.nbss.home_page_elements import HomePage


@pytest.mark.nbss_portal_mock
class TestPortalStartPageDashboard:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_mock_login, base_url) -> None:
        self.base_page = BasePage(page)
        self.home_page = HomePage(page)
        self.base_url = base_url

    @allure.title("Проверка наличия виджетов, проверка их работы")
    def test_widgets(self):
        with allure.step("Проверка наличия виджетов на странице"):
            self.home_page.WIDGET_LABEL.to_contain_text_in_any("Заявки в обработке")
            self.home_page.WIDGET_LABEL.to_contain_text_in_any("Заявки в очередях")
            self.home_page.WIDGET_LABEL.to_contain_text_in_any("Быстрые действия")
            self.home_page.LAST_INQUIRY_BTN.wait_to_be_visible()
        with allure.step("Проверка работы виджетов"):
            for widget_name, widget in zip(self.home_page.WIDGET_LABEL, self.home_page.WIDGETS):  # type: ignore
                with allure.step(f"Нажатие на виджет '{widget_name.text}'"):
                    widget.click()
                self.base_page.open(self.base_url)
                self.home_page.USER_DROPDOWN_BTN.wait_to_be_visible(timeout=15000)

    @allure.title("Проверка возможности перемещения виджетов")
    def test_widgets_drag(self):
        self.home_page.WIDGET_DRAG_INDICATOR[1].drag_to(self.home_page.WIDGETS[2])
        self.home_page.WIDGET_DRAG_INDICATOR[2].drag_to(self.home_page.WIDGETS[0])

    @allure.title("Проверка возможности изменения размеров виджетов")
    def test_widgets_resize(self):
        self.home_page.WIDGETS[1].hover()
        self.home_page.WIDGET_RESIZE_HANDLE[1].drag_to(self.home_page.WIDGETS[2], force=True)

    @allure.step("Проверка возможности удалить и добавить виджет")
    def test_widgets_delete_add(self):
        with allure.step("Удаление виджета"):
            self.home_page.WIDGET_MORE_BTN[2].click()
            self.home_page.WIDGET_DELETE_BTN[0].click()
            self.home_page.MODAL_SECOND_BTN.click()
        with allure.step("Добавление виджета"):
            self.home_page.SETTINGS_BTN.click()
            self.home_page.WIDGET_DRAG_INDICATOR[3].drag_to(self.home_page.WIDGETS[1])
            self.home_page.WIDGETS.wait_to_have_count(4)

    @allure.title("Проверка обновления данных в виджетах")
    def test_widgets_refresh(self):
        self.home_page.WIDGET_TEXT[0].wait_to_be_visible()
        self.home_page.WIDGET_REFRESH_BTN[0].click()
        self.home_page.WIDGET_TEXT[0].wait_to_be_visible()

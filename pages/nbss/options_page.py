import allure

from pages.base_page import BasePage
from pages.locators.nbss.options.points_of_sale import FormAddUserPointsOfSale, PointsOfSale


class OptionsPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.points_of_sale_page = PointsOfSale()
        self.form_add_point = FormAddUserPointsOfSale()

    @allure.step("Удалить все точки продажи у пользователя")
    def clear_points_of_sale(self) -> None:
        for i in range(self.points_of_sale_page.LIST_POINTS_SALE_USER.elements_len() - 1, -1, -1):
            self.points_of_sale_page.LIST_POINTS_SALE_USER[i].click()
            self.points_of_sale_page.DELETE_BTN.click()
            self.points_of_sale_page.ACCEPT_BTN.wait_to_be_visible(timeout=15000)
            self.points_of_sale_page.ACCEPT_BTN.click()
        self.points_of_sale_page.REFRESH_BTN.click()

    @allure.step("Перейти в Настройки > Точки продажи")
    def open_points_of_sale_from_menu(self) -> None:
        self.points_of_sale_page.BURGER_MENU.wait_to_be_visible(timeout=15000)
        self.points_of_sale_page.BURGER_MENU.select_by_value("Настройки > Точки продаж")

    @allure.step("Открыть вкладку 'Пользователи' точек продаж и добавить выбранные точки пользователю")
    def open_user_points_tab_and_add_points(
        self,
        point_indices: int = 0,
    ) -> None:
        """
        Открывает страницу заявок клиента, переходит в Настройки > Точки продаж,
        вкладку «Пользователи», выбирает первого пользователя, открывает форму добавления
        и отмечает в форме точки продаж по переданным индексам, затем подтверждает.

        :param user_id: ID пользователя/клиента (например, test_context.client.user_id).
        :param point_indices: Индексы точек в списке формы для выбора. По умолчанию — одна точка.
        """

        self.open_points_of_sale_from_menu()
        self.points_of_sale_page.TAB.wait_to_be_visible(timeout=15000)
        self.points_of_sale_page.TAB[1].click()
        self.points_of_sale_page.USER_LIST.wait_to_be_visible(timeout=60000)
        self.points_of_sale_page.USER_LIST[0].click()
        self.points_of_sale_page.ADD_BTN.wait_to_be_enabled()
        self.points_of_sale_page.ADD_BTN.click()
        self.form_add_point.POINTS_SALE.wait_to_be_visible(timeout=15000)

        self.form_add_point.POINTS_SALE[point_indices].click()
        self.form_add_point.INNER_ACCEPT_BTN.click()

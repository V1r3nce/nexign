import allure
from playwright.sync_api import Page

from common.helpers.string_helper import add_separators
from pages.base_page import BasePage
from pages.locators.consumption import Consumption


class ConsumptionPage(BasePage):
    """Страница /consuming/subscribers Потребление"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = Consumption(page)

    @allure.step("Проверка отображаемой информации об объёме")
    def check_volume(
        self,
        volume_index: int = 0,
        name: str | None = None,
        volume_remaining: int | None = None,
        volume_issued: int | None = None,
        product: str | None = None,
        start_period: str | None = None,
        end_period: str | None = None,
        check_more_info: bool = False,
        status: str | None = None,
        volume_used: int | None = None,
        valid_from: str | None = None,
        expiration_date: str | None = None,
        used_up_on: str | None = None,
        volume_type: str | None = None,
        renewal_date: str | None = None,
    ) -> None:
        if volume_remaining:
            volume_remaining = add_separators(volume_remaining, "\xa0")
        if volume_issued:
            volume_issued = add_separators(volume_issued, "\xa0")

        self.locators.VOLUME.wait_elements_visible(volume_index)
        if name:
            self.locators.VOLUME_NAME[volume_index].wait_to_have_text(name)
        if product:
            self.locators.VOLUME_PRODUCT[volume_index].wait_to_have_text(product)
        if volume_remaining and volume_issued:
            self.locators.VOLUME_REMAINING[volume_index].wait_to_have_text(f"{volume_remaining} из {volume_issued}")
        if start_period and end_period:
            self.locators.VOLUME_ACTIVE_PERIOD[volume_index].wait_to_have_text(
                f"Действует с {start_period} по {end_period}"
            )

        if check_more_info:
            self.locators.VOLUME.click(volume_index)
            if name:
                self.locators.TITLE_VOLUME_NAME.wait_to_have_text(name)
            if status:
                self.locators.VOLUME_PROPERTY[0].wait_to_have_text("Статус объема" + status)
            if volume_issued:
                self.locators.VOLUME_PROPERTY[1].wait_to_have_text("Выданный объем" + volume_issued)
            if volume_used:
                volume_used = add_separators(volume_used, "\xa0")
                self.locators.VOLUME_PROPERTY[2].wait_to_have_text("Потребленный объем" + volume_used)
            if volume_remaining:
                self.locators.VOLUME_PROPERTY[3].wait_to_have_text("Оставшийся объем" + volume_remaining)
            if valid_from:
                self.locators.VOLUME_PROPERTY[4].wait_to_have_text("Дата начала действия объема" + valid_from)
            if expiration_date:
                self.locators.VOLUME_PROPERTY[5].wait_to_have_text("Дата окончания действия объема" + expiration_date)
            if used_up_on:
                self.locators.VOLUME_PROPERTY[6].wait_to_have_text("Дата исчерпания объема" + used_up_on)
            if volume_type:
                self.locators.VOLUME_PROPERTY[7].wait_to_have_text("Тип объема" + volume_type)
            if renewal_date:
                self.locators.VOLUME_PROPERTY[8].wait_to_have_text("Дата возобновления" + renewal_date)
            if product:
                self.locators.VOLUME_PROPERTY[9].wait_to_have_text("Продукт" + f"Тарифный план «{product}»")

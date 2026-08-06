from datetime import datetime
from typing import Literal

import allure

from common.helpers.checker import assert_that
from common.helpers.data_generator import calculate_refund_amount
from common.helpers.string_helper import add_separators, balance_parse, get_price_and_currency
from common.helpers.time_helpers import get_datetime_from_string
from models.product import MainProduct
from pages.base_page import BasePage
from pages.locators.nbss.finances.consumptionelements import ConsumptionElements


class ConsumptionPage(BasePage):
    """Страница /consuming/subscribers Потребление"""

    def __init__(self) -> None:
        super().__init__()

        self.locators = ConsumptionElements()

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

    @allure.step("Проверка начисления со скидкой на сумму {expected_amount}")
    def check_accrual_amount(self, expected_amount: float, index: int = 0, tolerance: float = 0.01) -> None:
        """
        Проверяет, что в списке начислений есть запись с указанной суммой (по умолчанию первая).
        """
        self.locators.ACCRUAL_LIST.wait_to_be_visible(timeout=10000)
        self.locators.ACCRUAL_SUMS[index].wait_to_be_visible(timeout=10000)
        sum = self.locators.ACCRUAL_SUMS[index].text
        actual_amount, _ = get_price_and_currency(sum)

        assert_that(
            lambda: abs(actual_amount - expected_amount) <= tolerance,
            f"Ожидалось: {expected_amount:.2f}, найдено: {actual_amount:.2f} (текст: '{sum}')",
        )

    @allure.step("Открыть вкладку Начисления")
    def open_accrual_list(self) -> None:
        self.locators.CHARGES_TAB.wait_to_be_visible(timeout=15000)
        self.locators.CHARGES_TAB.click()
        self.locators.ACCRUALS_TITLE_LIST.wait_to_be_visible(timeout=25000)

    @allure.step("Найти дату перерасчета АП")
    def get_accrual_info(self, product: MainProduct, refund_action: str = "") -> tuple[datetime, float]:
        """
        Метод для получения начисления
        :param product: продукт у которого был перерасчет АП
        :param refund_action: строка с типом пересчета или его отсутствии. Возможные варианты '' - полное списание АП, 'disconnect' - отключение пп, 'discount' - скидка на АП, 'extra' - увеличение стоимости АП
        :return: дату начисления в формате datetime, сумму начисления
        """
        self.locators.ACCRUAL_LIST.wait_to_be_visible(timeout=10000)
        refund_date = None
        refund_amount = None
        if refund_action in ["discount", "disconnect"]:
            match_func = lambda s: s[0] == "-"
        elif refund_action == "extra":
            match_func = lambda s: balance_parse(s) < product.subscription_fee
        else:
            match_func = lambda s: (balance_parse(s) - product.subscription_fee) < 0.01
        for i in range(self.locators.ACCRUAL_DATES.elements_len()):
            accrual_amount = self.locators.ACCRUAL_SUMS[i].text
            product_name = self.locators.ACCRUAL_PRODUCT_NAMES[i].text
            if accrual_amount and match_func(accrual_amount) and product_name == product.product_name:
                refund_date = self.locators.ACCRUAL_DATES[i].text
                refund_amount = self.locators.ACCRUAL_SUMS[i].text
                break
        assert_that(
            lambda: refund_amount is not None and refund_date is not None, "Начисление с нужными параметрами не найдено"
        )
        return get_datetime_from_string(refund_date, is_full_format=True), balance_parse(refund_amount)

    @allure.step("Проверить сумму пересчета АП")
    def check_refund_amount(self, product: MainProduct, action: str = "disconnect") -> None:
        """
        Метод для проверки начисление после пересчета АП
        :param product: продукт у которого был перерасчет АП
        :param action: строка с типом пересчета. Возможные варианты 'disconnect' - отключение пп, 'discount' - скидка на АП, 'extra' - увеличение стоимости АП
        """
        refund_date, refund_amount = self.get_accrual_info(product=product, refund_action=action)
        subscription_date, subs_amount = self.get_accrual_info(product=product)
        assert_that(
            lambda: (
                (
                    refund_amount
                    + calculate_refund_amount(
                        refund_date=refund_date,
                        subscription_date=subscription_date,
                        original_amount=product.subscription_fee,
                    )
                    - subs_amount
                )
                < 0.02
            ),
            "Сумма пересчета не совпадает с ожидаемой",
        )

    @allure.step("Кликнуть по абоненту с индексом {subscriber_index}")
    def click_subscriber(self, subscriber_index: int = 0) -> None:
        self.locators.SUBSCRIBER_NUM[subscriber_index].wait_to_be_visible()
        self.locators.SUBSCRIBER_NUM[subscriber_index].click()

    @allure.step("Выбрать режим отображения - {mode}")
    def select_view_mode(self, mode: Literal["Абоненты", "Лицевые счета", "Без абонента"]) -> None:
        self.locators.SUBSCRIBER_VIEW_MODE.wait_to_be_visible()
        self.locators.SUBSCRIBER_VIEW_MODE.select_by_value(mode)
        self.locators.LOAD_SPINS.wait_not_to_be_visible()

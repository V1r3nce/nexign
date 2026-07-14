import allure

from common.helpers.checker import assert_that, wait_that
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import extract_volumes
from common.helpers.time_helpers import delay
from models.product import MainProduct
from pages.base_page import BasePage
from pages.locators.nbss.client.client_product_profile import ClientProductProfileElements
from pages.locators.nbss.dynamic_form_elements import ProductInfoForm


class ClientProductProfilePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProductProfileElements()
        self.product_info_form = ProductInfoForm()

    @allure.step("Открыть продуктовый профиль клиента, дождаться загрузки страницы")
    def open_products_page(self, user_id: int, product_list: list[MainProduct], is_activated: bool = True) -> None:
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{user_id}/products")
        self.locators.PRODUCT_NAME.wait_to_be_visible(timeout=10000)
        self.check_all_products(products=product_list, is_activated=is_activated)

    @allure.step("Проверить что все продукты и абоненты отображаются и активированы")
    def check_all_products(self, products: list[MainProduct], is_activated: bool = True) -> None:
        products_count = len(products)
        self.expand_all_products()
        self.locators.PRODUCTS.wait_to_have_count(products_count, timeout=15000)
        for i in range(products_count):
            subscriber = self.locators.SUBSCRIBER[i].text
            name = self.locators.PRODUCT_NAME[i].text
            for product in products:
                if subscriber == product.phone_number or subscriber == product.internet_number:
                    assert_that(
                        lambda: name == product.product_name,
                        f"У абонента {subscriber} название продукта {name} не совпадает с {product.product_name}",
                    )
                    break
        if is_activated:
            self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")

    @allure.step("Развернуть все продукты клиента")
    def expand_all_products(self) -> None:
        """
        Раскрывает все свернутые продукты клиента на странице продуктов.

        Метод проходит по всем продуктам и раскрывает те, которые свернуты (aria-expanded="false").
        Ждет появления каждого раскрытого продукта перед переходом к следующему.
        Может раскрыться несколько продуктов одновременно от одного клика.
        """
        self.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=15000)
        self.locators.PRODUCTS_HEADER_LIST.wait_to_be_visible()
        for i in range(self.locators.PRODUCTS_LIST.elements_len()):
            header = self.locators.PRODUCTS_HEADER_LIST[i]

            if header.locator.is_visible(timeout=1000):
                aria_expanded = header.get_attribute("aria-expanded")
                if aria_expanded == "false":
                    header.scroll_into_view_if_needed()
                    delay(0.3, "Ожидание прокрутки к элементу")

                    current_opened = self.locators.PRODUCTS.elements_len()
                    header.click(force=True)

                    wait_that(
                        lambda: self.locators.PRODUCTS.elements_len() > current_opened,
                        timeout=15,
                        sleep_seconds=0.5,
                        exception=AssertionError,
                        message=f"Количество открытых продуктов не увеличилось после клика на продукт {i}",
                    )

    @allure.step("Кликнуть на первый продукт")
    def click_first_product(self, subscriber: str, product_name: str, product_active: bool = True) -> None:
        self.locators.PRODUCTS_LIST.wait_elements_visible(0)
        self.locators.SUBSCRIBER[0].wait_to_have_text(subscriber)
        if product_active:
            self.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.locators.PRODUCT_NAME.wait_elements_visible(0)
        self.locators.PRODUCT_NAME[0].wait_to_have_text(product_name)
        self.locators.PRODUCT_NAME[0].click(force=True)
        self.product_info_form.PRODUCT_NAME.wait_to_be_visible()

    @allure.step("Проверить что объемы соответствуют ожидаемым: {expected_volumes} из {expected_max_volumes}")
    def check_product_volumes(self, expected_volumes: list[int], expected_max_volumes: list[int]) -> None:
        self.locators.PRODUCT_LIMIT_VALUES.wait_to_have_count(len(expected_volumes))

        minutes_volume_product_profile = self.locators.PRODUCT_LIMIT_VALUES[0].text
        internet_volume_product_profile = self.locators.PRODUCT_LIMIT_VALUES[1].text
        sms_volume_product_profile = self.locators.PRODUCT_LIMIT_VALUES[2].text

        product_volumes = [minutes_volume_product_profile, internet_volume_product_profile, sms_volume_product_profile]
        self.check_volumes(product_volumes, expected_volumes, expected_max_volumes)

    @allure.step("Проверить что объемы соответствуют ожидаемым: {expected_volumes} из {expected_max_volumes}")
    def check_product_volumes_in_sidebar(self, expected_volumes: list[int], expected_max_volumes: list[int]) -> None:
        self.product_info_form.PRODUCT_VOLUMES.wait_to_have_count(len(expected_volumes))

        minutes_volume_product_profile_sidebar = self.product_info_form.PRODUCT_VOLUMES[0].text
        internet_volume_product_profile_sidebar = self.product_info_form.PRODUCT_VOLUMES[1].text
        sms_volume_product_profile_sidebar = self.product_info_form.PRODUCT_VOLUMES[2].text

        product_volumes = [
            minutes_volume_product_profile_sidebar,
            internet_volume_product_profile_sidebar,
            sms_volume_product_profile_sidebar,
        ]
        self.check_volumes(product_volumes, expected_volumes, expected_max_volumes)

    @allure.step("Сравнение объемов")
    def check_volumes(self, volumes: list[str], expected_volumes: list[int], expected_max_volumes: list[int]) -> None:
        for i in range(len(expected_volumes)):
            volume, max_volume = extract_volumes(volumes[i])
            assert_that(
                lambda: volume == expected_volumes[i],
                f"Объем отличется от ожидаемого: Фактический объем - {volume}, Ожидаемый объем - {expected_volumes[i]}",
            )
            assert_that(
                lambda: max_volume == expected_max_volumes[i],
                f"Максимальный объем отличется от ожидаемого: Фактический максимальный объем - {max_volume}, Ожидаемый максимальный объем - {expected_max_volumes[i]}",
            )

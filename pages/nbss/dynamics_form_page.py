import allure

from common.helpers.string_helper import check_price_with_tax
from pages.base_page import BasePage
from pages.locators.nbss.client.client_product_profile import ClientProductProfileElements
from pages.locators.nbss.dynamic_form_elements import ProductInfoForm
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements


class DynamicsFormPage(BasePage):
    """Динамические формы: сайдбар с детальной информацией о продукте и его вкладки."""

    def __init__(self) -> None:
        super().__init__()
        self.product_info_form = ProductInfoForm()
        self.product_offer_form = SelectProductOffersFormElements()
        self.client_product_profile_locators = ClientProductProfileElements()

    @allure.step("Открыть вкладку 'Цены' сайдбара продукта и раскрыть все блоки с ценами")
    def open_price_tab(self) -> None:
        self.product_info_form.PRICE_TAB.wait_to_be_visible(timeout=10000)
        self.product_info_form.PRICE_TAB.click()
        self.product_info_form.PRICES_DROPDOWN_BTN.wait_elements_visible(0, timeout=10000)
        for dropdown_index in range(self.product_info_form.PRICES_DROPDOWN_BTN.elements_len()):
            self.product_info_form.PRICES_DROPDOWN_BTN[dropdown_index].click()

    @allure.step("Проверить отображение налога на вкладке 'Цены'")
    def check_taxes_on_price_tab(self, price_index: int = 0) -> None:
        """Проверить, что на вкладке 'Цены' отображаются 'Цена без налога', 'Сумма налога' и 'Цена с налогом'.

        :param price_index: порядковый номер цены на вкладке
        """
        self.product_info_form.PRICE_WITHOUT_TAX.wait_elements_visible(price_index, timeout=10000)
        self.product_info_form.PRICE_TAX.wait_elements_visible(price_index, timeout=10000)
        self.product_info_form.PRICE_WITH_TAX.wait_elements_visible(price_index, timeout=10000)
        check_price_with_tax(
            self.product_info_form.PRICE_WITHOUT_TAX[price_index],
            self.product_info_form.PRICE_TAX[price_index],
            self.product_info_form.PRICE_WITH_TAX[price_index],
        )

    @allure.step("Проверить отображение налога в детальной информации о продукте '{product_offer_name}'")
    def check_product_details_taxes(self, product_offer_name: str, product_index: int = 0) -> None:
        """Открыть детальную информацию о найденном ПП, проверить налоги на вкладке 'Цены' и закрыть её.

        :param product_offer_name: название продуктового предложения
        :param product_index: порядковый номер карточки продукта в результатах поиска
        """
        self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([product_offer_name], timeout=10000)
        self.product_offer_form.PRODUCT_CARD_DETAILS.wait_elements_visible(product_index, timeout=10000)
        self.product_offer_form.PRODUCT_CARD_DETAILS[product_index].wait_to_be_enabled(timeout=10000)
        self.product_offer_form.PRODUCT_CARD_DETAILS[product_index].click()
        self.product_info_form.PRODUCT_NAME.wait_to_have_text(product_offer_name, timeout=10000)

        self.open_price_tab()
        self.check_taxes_on_price_tab()

        self.product_info_form.CROSS_BTN.click()
        self.product_info_form.PRODUCT_NAME.not_to_be_visible(timeout=10000)

    @allure.step("Проверить отображение налога на вкладке 'Цены' сайдбара продукта")
    def check_taxes_on_product_sidebar(self, product_index: int = 0) -> None:
        """Открыть сайдбар продукта в продуктовом профиле и проверить налоги на вкладке 'Цены'.

        :param product_index: порядковый номер продукта в продуктовом профиле
        """
        self.client_product_profile_locators.PRODUCT_NAME.wait_elements_visible(product_index, timeout=10000)
        self.client_product_profile_locators.PRODUCT_NAME[product_index].click()
        self.product_info_form.PRODUCT_NAME.wait_to_be_visible(timeout=10000)
        self.open_price_tab()
        self.check_taxes_on_price_tab()

    @allure.step("Проверить отображение налога на вкладке 'Цены' сайдбара опции")
    def check_taxes_on_option_sidebar(self, option_index: int = 0) -> None:
        """Раскрыть опции продукта, открыть сайдбар опции и проверить налоги на вкладке 'Цены'.

        :param option_index: порядковый номер опции у продукта
        """
        self.client_product_profile_locators.OPEN_OPTIONS_BTN.wait_elements_visible(option_index, timeout=10000)
        self.client_product_profile_locators.OPEN_OPTIONS_BTN[option_index].click(force=True)
        self.client_product_profile_locators.OPTION_NAME.wait_elements_visible(option_index, timeout=10000)
        self.client_product_profile_locators.OPTION_NAME[option_index].click()
        self.product_info_form.PRODUCT_NAME.wait_to_be_visible(timeout=10000)
        self.open_price_tab()
        self.check_taxes_on_price_tab()

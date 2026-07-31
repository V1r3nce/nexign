from datetime import date, timedelta

import allure

from common.enums.inquiry import InquiryDocumentFormationMode
from common.exceptions import IncorrectActivationDateException
from common.helpers.checker import assert_that, check_that, wait_that
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import check_price, extract_volumes, get_price_and_currency
from common.helpers.time_helpers import delay
from models.client import IndividualClient
from models.product import AdditionalProduct, MainProduct
from pages.base_page import BasePage
from pages.locators.nbss.client.client_product_profile import ClientProductProfileElements
from pages.locators.nbss.client.client_profile import ClientProfileEndUser
from pages.locators.nbss.client.edit_product_activation_date_form import EditProductActivationDateForm
from pages.locators.nbss.dynamic_form_elements import (
    AddOptionsForm,
    ChangeMainProductForm,
    CreateSalesAndServiceManagement,
    ProductInfoForm,
)
from pages.locators.nbss.inquiries_elements import InquiriesElements
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements


class ClientProductProfilePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = ClientProductProfileElements()
        self.product_info_form = ProductInfoForm()
        self.add_options_form = AddOptionsForm()
        self.end_user_form = ClientProfileEndUser()
        self.change_product_form = ChangeMainProductForm()
        self.select_product_offers_form = SelectProductOffersFormElements()
        self.create_request_form = CreateSalesAndServiceManagement()
        self.inquiries_form = InquiriesElements()
        self.edit_product_activation_date_form = EditProductActivationDateForm()

    @allure.step("Открыть продуктовый профиль клиента, дождаться загрузки страницы")
    def open_products_page(self, user_id: int) -> None:
        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{user_id}/products")
        self.locators.SUBSCRIBER_EXPAND_BUTTON.wait_to_be_visible(timeout=15000)
        self.locators.SUBSCRIBER_EXPAND_BUTTON[0].click()
        self.locators.PRODUCT_NAME.wait_to_be_visible(timeout=10000)

    @allure.step("Проверить что все продукты и абоненты отображаются и активированы")
    def check_all_products(self, products: list[MainProduct], is_activated: bool = True) -> None:
        self.expand_all_products()
        self.locators.PRODUCTS.wait_to_have_count(len(products), timeout=15000)

        products_count = len(products)
        subscribers_count = self.locators.SUBSCRIBER.elements_len()

        for i in range(subscribers_count):
            subscriber = self.locators.SUBSCRIBER[i].text
            name = self.locators.PRODUCT_NAME[i].text
            for product in products:
                if subscriber == product.phone_number or subscriber == product.internet_number:
                    assert_that(
                        lambda: name == product.product_name,
                        f"У абонента {subscriber} название продукта {name} не совпадает с {product.product_name}",
                    )
                    if is_activated:
                        self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")
                    break

        for i in range(subscribers_count, products_count):
            name = self.locators.PRODUCT_NAME[i].text
            assert_that(
                lambda: any(name == p.product_name for p in products), f"В списке продуктов отсутствует продукт {name}"
            )
            if is_activated:
                self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")

    @allure.step("Кликнуть на первый продукт")
    def click_first_product(self, subscriber: str, product_name: str, product_active: bool = True) -> None:
        self.locators.PRODUCTS_LIST.wait_elements_visible(0)
        self.locators.SUBSCRIBER[0].wait_to_have_text(subscriber)
        if product_active:
            self.locators.PRODUCT_LIMIT.wait_to_be_visible()
        self.locators.PRODUCT_NAME.wait_elements_visible(0)
        self.locators.PRODUCT_NAME[0].wait_to_have_text(product_name)
        self.locators.PRODUCT_NAME[0].click()
        self.product_info_form.PRODUCT_NAME.wait_to_be_visible()

    @allure.step("Получить количество лимитов опций {index} продукта")
    def get_option_limit_count(self, index: int) -> int:
        return len(
            self.page.locator(self.locators.PRODUCTS.path).nth(index).locator(self.locators.OPTION_LIMIT_ICON.path).all()
        )

    @allure.step("Добавить дополнительное продуктовое предложение {product_name} через опции")
    def add_adoption_product(self, product_name: str) -> None:
        """Добавление дополнительного продуктового предложения
        :param product_name: Название дополнительного продукта"""

        with allure.step('Нажать "..." -> "Добавить опцию".'):
            self.locators.PRODUCTS_UPDATE_BTN.click()
            self.locators.PRODUCTS_OPTIONS_OPEN_BTN[0].click()
            self.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            if not self.page.locator(self.locators.PRODUCTS_OPTIONS_ADD_BTN.path).is_visible():
                self.press_keyboard_button("Escape")
                self.locators.SUBSCRIBERS_DETAILS_OPEN_BTN[0].click()
                self.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            self.locators.PRODUCTS_OPTIONS_ADD_BTN.wait_to_be_visible()
            self.locators.PRODUCTS_OPTIONS_ADD_BTN.click()

        with allure.step(f"Выбрать дополнительный продукт {product_name}"):
            self.add_options_form.SEARCH_OPTIONS_FLD.fill(product_name)
            self.add_options_form.SEARCH_BTN.click()
            self.add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
            self.add_options_form.CHOSE_OPTION_BTN[0].click()
            self.add_options_form.INNER_ACCEPT_BTN.click()

    @allure.step("Сменить ПП с формированием договора")
    def change_product_offer_with_contract(
        self,
        auto_contract: bool = True,
        product_number: int = 1,
        product_name: str | None = None,
        future_date: str | None = None,
    ) -> str:
        """
        :param auto_contract: автоматическое / ручное согласование договора
        :param product_number: номер продукта в списке (1-й, 2-й, 3-й и т.д.)
        :param product_name: название ПП. Если указано - в первую очередь будет искать по нему
        :param future_date: Отложенная активация: дата "ДД.ММ.ГГГГ чч:мм" для смены будущей датой (или None)
        :return: имя выбранного продукта
        """
        self.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)
        self.locators.PRODUCTS_UPDATE_BTN.click()
        tech_product_index = product_number - 1

        with allure.step("Инициировать смену продукта"):
            self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")
            self.locators.SUBSCRIBERS_DETAILS_OPEN_BTN[0].wait_to_be_enabled()
            self.locators.SUBSCRIBERS_DETAILS_OPEN_BTN[0].click()
            self.locators.LOAD_SPINS.not_to_be_visible(timeout=8000)
            self.locators.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN.click()

        with allure.step(f"Выбрать продукт №{product_number} для замены"):
            self.change_product_form.SEARCH_BTN.wait_to_be_enabled()
            self.select_product_offers_form.PRODUCT_CARD_NAME.wait_to_be_visible(timeout=15000)

            chose_product_buttons = self.change_product_form.CHOSE_PRODUCT_BTN
            text_products = self.select_product_offers_form.PRODUCT_CARD_NAME
            target_product = None

            if product_name is not None:
                for i in range(text_products.elements_len()):
                    if text_products[i].text == product_name:
                        target_product = text_products[i]
                        tech_product_index = i
                        break
            else:
                target_product = text_products[tech_product_index]
            assert target_product, "Продукт не найден в форме смены ПП"
            name_product = target_product.text
            assert target_product, "Имя продукта не найдено в форме смены ПП"

            try:
                choose_btn = chose_product_buttons[tech_product_index]
            except IndexError:
                raise AssertionError(
                    f"В форме смены ПП нет кнопки выбора ПП с индексом {tech_product_index} "
                    f"для продукта №{product_number}"
                )

            choose_btn.wait_to_be_enabled(timeout=8000)
            choose_btn.click()

            self.change_product_form.INNER_ACCEPT_BTN.click()

        with allure.step("Изменить данные формирования договора"):
            self.create_request_form.CREATE_ADD_AGREEMENT.wait_to_be_enabled(timeout=30000)
            self.create_request_form.CREATE_ADD_AGREEMENT.select_by_value(
                InquiryDocumentFormationMode.CreateAuto if auto_contract else InquiryDocumentFormationMode.CreateManual
            )
            self.create_request_form.ADD_KP.wait_to_be_enabled(timeout=30000)
            self.create_request_form.ADD_KP.select_by_value(InquiryDocumentFormationMode.CreateAuto)
            if future_date:
                with allure.step("Активировать 'Запланировать выполнение заказа на дату' и заполнить дату"):
                    if not self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.has_attribute_value("checked", ""):
                        self.create_request_form.SCHEDULE_EXECUTION_CHECKBOX.click()
                    self.create_request_form.EXECUTION_DATE.wait_to_be_visible(timeout=10000)
                    self.create_request_form.EXECUTION_DATE.check_attribute_by_value("aria-required", "true")
                    self.create_request_form.EXECUTION_DATE.fill(future_date)
                    self.press_keyboard_button("Enter")
            self.create_request_form.SAVE_BTN.click()

        return name_product  # type: ignore

    @allure.step("Проверить, что основной продукт изменён на '{expected_name}'")
    def check_main_product_changed(self, expected_name: str) -> None:
        self.locators.SUBSCRIBER.wait_to_be_visible(timeout=15000)
        self.locators.PRODUCT_NAME[0].wait_to_have_text(expected_name, timeout=15000)

    @allure.step("Проверка: На продукте отображается индивидуализированная цена")
    def check_individualized_price_on_products_page(
        self,
        expected_base_price: float,
        expected_final_price: float,
        product_index: int = 0,
        individualized_price_index: int = 0,
    ) -> None:
        """
        Проверка отображения цен в продуктовом профиле клиента после индивидуализации.
        :param product_index: порядковый номер продукта
        :param expected_base_price: ожидаемая цена до индивидуализации
        :param expected_final_price: ожидаемая цена после индивидуализации
        :param individualized_price_index: индекс цены после индивидуализации
        """

        self.locators.PRODUCTS_SUBSCRIPTION_FEE.wait_to_be_visible(timeout=10000)
        check_price(self.locators.PRODUCTS_SUBSCRIPTION_FEE[product_index], expected_final_price, check_format=False)
        check_price(
            self.locators.PRODUCTS_SUBSCRIPTION_FEE_BEFORE_INDIVIDUALIZATION[individualized_price_index],
            expected_base_price,
            check_format=False,
        )

    @allure.step("Проверить отображение налога на вкладке 'Цены' сайдбара продукта")
    def check_taxes_on_product_sidebar(self, product_index: int = 0) -> None:
        """Открыть сайдбар продукта в продуктовом профиле и проверить налоги на вкладке 'Цены'.

        :param product_index: порядковый номер продукта в продуктовом профиле
        """
        self.locators.PRODUCT_NAME.wait_elements_visible(product_index, timeout=10000)
        self.locators.PRODUCT_NAME[product_index].click()
        self.product_info_form.PRODUCT_NAME.wait_to_be_visible(timeout=10000)
        self.product_info_form.open_price_tab()
        self.product_info_form.check_taxes_on_price_tab()

    @allure.step("Проверить отображение налога на вкладке 'Цены' сайдбара опции")
    def check_taxes_on_option_sidebar(self, option_index: int = 0) -> None:
        """Раскрыть опции продукта, открыть сайдбар опции и проверить налоги на вкладке 'Цены'.

        :param option_index: порядковый номер опции у продукта
        """
        self.locators.OPEN_OPTIONS_BTN.wait_elements_visible(option_index, timeout=10000)
        self.locators.OPEN_OPTIONS_BTN[option_index].click(force=True)
        self.locators.OPTION_NAME.wait_elements_visible(option_index, timeout=10000)
        self.locators.OPTION_NAME[option_index].click()
        self.product_info_form.PRODUCT_NAME.wait_to_be_visible(timeout=10000)
        self.product_info_form.open_price_tab()
        self.product_info_form.check_taxes_on_price_tab()

    @allure.step("Перейти к деталям потребления по продукту")
    def open_product_consumption_details(self, product_index: int = 0) -> None:
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].wait_to_be_visible(timeout=5000)
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].click(force=True)
        self.locators.PRODUCTS_CONSUMPTION_DETAILS_BTN.wait_to_be_visible(timeout=5000)
        self.locators.PRODUCTS_CONSUMPTION_DETAILS_BTN.click(force=True)

    @allure.step("Нажать кнопку редактировать продукт")
    def create_product_edit_inquiry(self, product_index: int = 0) -> None:
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].wait_to_be_visible(timeout=10000)
        delay(1, "Чтобы кнопка стала активной")
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].click(force=True)
        self.locators.PRODUCT_EDIT_BTN.wait_to_be_visible(timeout=25000)
        self.locators.PRODUCT_EDIT_BTN.click(force=True)

        self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=15000)
        self.create_request_form.SAVE_BTN.wait_to_be_enabled(timeout=15000)
        self.create_request_form.CREATE_ADD_AGREEMENT.wait_to_be_enabled()
        self.create_request_form.CREATE_ADD_AGREEMENT.select_by_value(InquiryDocumentFormationMode.CreateAuto)
        self.create_request_form.ADD_KP.select_by_value(InquiryDocumentFormationMode.NotCreate)
        self.create_request_form.SAVE_BTN.click()

        self.inquiries_form.LOAD_SPIN_THIRD.not_to_be_visible(timeout=60000)
        self.inquiries_form.LOAD_SPINS.not_to_be_visible(timeout=30000)
        self.inquiries_form.ADDED_PRODUCT.wait_to_be_visible(timeout=30000)

    @allure.step("Создать заявку на редактирование продукта")
    def create_product_disconnect_inquiry(
        self,
        product: MainProduct | AdditionalProduct,
        product_index: int = 0,
        is_active: bool = True,
        create_add_agreement: str = None,
        future_date: str | None = None,
    ) -> None:
        create_inquiry_form = CreateSalesAndServiceManagement()
        self.locators.PRODUCT_NAME.wait_to_be_visible(timeout=15000)

        with allure.step("Инициировать отключение продукта"):
            if is_active:
                self.locators.PRODUCTS_STATUS_COLOR.to_have_css_color("background-color", "green")
            self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].wait_to_be_visible()
            delay(1, "Чтобы кнопка стала активной")
            self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].click(force=True)
            self.locators.TURN_OFF_BTN.wait_to_be_visible(timeout=25000)
            delay(2, "Чтобы опции успели раскрыться и кнопка отключения стала активной")
            self.locators.TURN_OFF_BTN.click(force=True)

        self.create_request_form.TITLE.wait_to_have_text("Создание продажи и управление услугами", timeout=25000)
        if "satellite" in product.category:
            create_inquiry_form.EQUIPMENT_RETURNED_ACTION.wait_to_be_visible()
            create_inquiry_form.EQUIPMENT_RETURNED_ACTION.select_by_value("Передать на склад для оценки состояния")
        if create_add_agreement == "manual":
            create_inquiry_form.CREATE_ADD_AGREEMENT.wait_to_be_visible(timeout=15000)
            create_inquiry_form.CREATE_ADD_AGREEMENT.select_by_value(InquiryDocumentFormationMode.CreateManual)
        if create_add_agreement == "auto":
            create_inquiry_form.CREATE_ADD_AGREEMENT.wait_to_be_visible(timeout=15000)
            create_inquiry_form.CREATE_ADD_AGREEMENT.select_by_value(InquiryDocumentFormationMode.CreateAuto)
        if future_date:
            with allure.step("Активировать 'Запланировать выполнение заказа на дату' и заполнить дату"):
                if not create_inquiry_form.SCHEDULE_EXECUTION_CHECKBOX.has_attribute_value("checked", ""):
                    create_inquiry_form.SCHEDULE_EXECUTION_CHECKBOX.click()
                create_inquiry_form.EXECUTION_DATE.wait_to_be_visible(timeout=10000)
                create_inquiry_form.EXECUTION_DATE.check_attribute_by_value("aria-required", "true")
                create_inquiry_form.EXECUTION_DATE.fill(future_date)
                self.press_keyboard_button("Enter")
        self.create_request_form.SAVE_BTN.wait_to_be_enabled()
        self.create_request_form.SAVE_BTN.click()

    @allure.step("Раскрыть список продуктов секции Прочие продукты (АУС)")
    def expand_other_products(self) -> None:
        self.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=15000)
        self.locators.OTHER_PRODUCTS_EXPAND_ICON[0].wait_to_be_visible(timeout=10000)
        self.locators.OTHER_PRODUCTS_EXPAND_ICON[0].click()

    @allure.step("Нажать кнопку редактировать продукт")
    def edit_product(self, product_index: int = 0) -> None:
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].wait_to_be_visible(timeout=10000)
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].click(force=True)
        self.locators.PRODUCT_EDIT_BTN.wait_to_be_visible(timeout=10000)
        self.locators.PRODUCT_EDIT_BTN.click()

    @allure.step("Нажать кнопку редактировать продукт")
    def edit_product_activation_date(self, product_index: int = 0) -> None:
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].wait_to_be_visible(timeout=10000)
        self.locators.PRODUCTS_DETAILS_OPEN_BTN[product_index].click(force=True)
        self.locators.PRODUCT_EDIT_ACTIVATION_DATE_BTN.wait_to_be_visible(timeout=10000)
        self.locators.PRODUCT_EDIT_ACTIVATION_DATE_BTN.click()

    @allure.step("Нажать кнопку редактировать продукт на сайдбаре")
    def edit_product_activation_date_on_sidebar(self, subscriber: str, product_name: str) -> None:
        self.click_first_product(subscriber=subscriber, product_name=product_name, product_active=False)
        self.locators.PRODUCT_SIDEBAR_EDIT_ACTIVATION_DATE_BTN.wait_to_be_visible(timeout=10000)
        self.locators.PRODUCT_SIDEBAR_EDIT_ACTIVATION_DATE_BTN.click()

    @allure.step("Проверить что абонентская плата за продукт равна {expected_price}")
    def check_subscription_fee(self, expected_price: float) -> None:
        subscription_fee_text = self.locators.PRODUCTS_SUBSCRIPTION_FEE[0].text
        subscription_fee, _ = get_price_and_currency(subscription_fee_text)

        assert_that(
            lambda: subscription_fee == expected_price,
            f"Ожидалась базовая цена {expected_price:.2f}, но отображается {subscription_fee:.2f}",
        )

    @allure.step("Проверить дату активации продукта")
    def check_product_activation_date(self, expected_activation_date: str, product_index: int = 0) -> None:
        check_that(
            lambda: expected_activation_date in self.locators.PRODUCT_ACTIVATION_DATE[product_index].text,
            exception=IncorrectActivationDateException,
            message=f"Отображается некорректная дата активации продукта: {self.locators.PRODUCT_ACTIVATION_DATE[product_index].text}, "
            f"Ожидаемая дата активации: {expected_activation_date}",
        )

    @allure.step("Раскрыть продукты всех абонентов")
    def open_products_all_subscriber(self) -> None:
        self.locators.SUBSCRIBER_SECTION.wait_to_be_visible(timeout=15000)
        for index in range(self.locators.SUBSCRIBER_SECTION.elements_len()):
            self.locators.SUBSCRIBER_SECTION[index].wait_to_be_visible(timeout=15000)
            if self.locators.SUBSCRIBER_SECTION[index].has_attribute_value(attribute="aria-expanded", value="false"):
                self.locators.OTHER_PRODUCTS_EXPAND_ICON[index].click()
            self.locators.PRODUCTS[index].wait_to_be_visible(timeout=15000)

    @allure.step("Развернуть все продукты клиента")
    def expand_all_products(self) -> None:
        """
        Раскрывает все свернутые продукты клиента на странице продуктов.

        Метод проходит по всем продуктам и раскрывает те, которые свернуты (aria-expanded="false").
        Ждет появления каждого раскрытого продукта перед переходом к следующему.
        Может раскрыться несколько продуктов одновременно от одного клика.
        """

        self.locators.PRODUCTS_HEADER_LIST.wait_to_be_visible(timeout=15000)
        self.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=15000)
        for i in range(self.locators.PRODUCTS_HEADER_LIST.elements_len()):
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

    @allure.step("Изменить дату активации продукта")
    def fill_activation_date_and_create_request(self, activation_date: str, reason: str = "Просьба клиента") -> None:
        self.edit_product_activation_date_form.ACTIVATION_DATE.wait_to_be_visible()
        self.edit_product_activation_date_form.ACTIVATION_DATE.fill(activation_date)
        self.edit_product_activation_date_form.ACTIVATION_DATE.to_contain_text(activation_date)
        self.edit_product_activation_date_form.REASON.wait_to_be_visible()
        self.edit_product_activation_date_form.REASON.fill(reason)
        self.edit_product_activation_date_form.INNER_ACCEPT_BTN.click()

    @allure.step("Проверить сообщение о доступной дате активации продукта")
    def check_edit_product_activation_date_message(self, delta_days: int = 1) -> None:
        activation_date = date.today() + timedelta(days=delta_days)
        self.edit_product_activation_date_form.INFORMATION_MESSAGE.wait_to_be_visible()
        self.edit_product_activation_date_form.INFORMATION_MESSAGE.wait_to_have_text(
            f"Активировать продукт можно не ранее {activation_date:%d.%m.%Y}"
        )

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

    @allure.step("Добавить конечного пользователя которого нет в системе")
    def add_non_existing_end_user(self, user_data: IndividualClient) -> None:
        self.end_user_form.ADD_END_USER_BUTTON.click()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES.fill(user_data.document_serial)
        self.end_user_form.DOCUMENT_NUMBER.fill(user_data.document_num)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.SURNAME_INPUT.wait_to_be_visible()
        self.end_user_form.LOADER.not_to_be_visible()
        self.end_user_form.SURNAME_INPUT.fill(user_data.sur_name)
        self.end_user_form.NAME_INPUT.fill(user_data.first_name)
        self.end_user_form.PATRONYMIC_INPUT.fill(user_data.patronymic)
        self.end_user_form.GENDER_DROPDOWN.select_by_value(user_data.gender)
        self.end_user_form.WHO_ISSUED_THE_DOCUMENT_INPUT.fill(user_data.document_provide_by)
        self.end_user_form.SUBDIVISION_CODE_INPUT.fill(user_data.document_division_code)
        self.end_user_form.DATE_OF_ISSUE_INPUT.type(user_data.issue_date)
        self.press_keyboard_button("Enter")
        self.end_user_form.DOCUMENT_VALID_FOR_INPUT.fill(user_data.document_valid_date)
        delay(0.5, "Чтобы календарь успел отобразить изменения")
        self.end_user_form.BIRTHDAY_INPUT.type(user_data.birth_date)
        self.press_keyboard_button("Enter")
        self.end_user_form.PLACE_OF_BIRTH_INPUT.fill(user_data.birth_place)
        self.end_user_form.REGISTRATION_ADDRESS_INPUT.select_by_value(
            user_data.registration_address, include_last_symbol=True
        )
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

    @allure.step("Добавить существующего конечного пользователя")
    def add_existing_end_user(self, user_data: IndividualClient) -> None:
        self.end_user_form.ADD_END_USER_BUTTON.click()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES.fill(user_data.document_serial)
        self.end_user_form.DOCUMENT_NUMBER.fill(user_data.document_num)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_be_visible(timeout=10000)
        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_have_text("Найден существующий клиент")
        self.end_user_form.CLIENT.wait_to_be_visible()
        self.end_user_form.CLIENT.click(0)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.wait_to_be_enabled()
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()
        self.end_user_form.DATA_TITLE.wait_to_have_text("Данные конечного пользователя")

    @allure.step("Заменить конечного пользователя на существующего")
    def replace_existing_end_user(self, user_data: IndividualClient) -> None:
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.wait_to_be_visible()
        self.end_user_form.DOCUMENT_TYPE_DROPDOWN.select_by_value(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES.fill(user_data.document_serial)
        self.end_user_form.DOCUMENT_NUMBER.fill(user_data.document_num)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()

        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_be_visible(timeout=10000)
        self.end_user_form.EXISTING_CLIENT_FOUND_TITLE.wait_to_have_text("Найден существующий клиент")
        self.end_user_form.CLIENT.click(0)
        self.end_user_form.ADD_END_USER_NEXT_BUTTON.click()
        self.end_user_form.DATA_TITLE.wait_to_have_text("Данные конечного пользователя")

    @allure.step("Проверить форму конечного пользователя")
    def check_end_user_form(self, user_data: IndividualClient, masked: bool = False) -> None:
        self.end_user_form.LOADER.not_to_be_visible(timeout=10000)
        self.end_user_form.FIO.to_contain_text(f"{user_data.sur_name} {user_data.first_name} {user_data.patronymic}")
        self.end_user_form.GENDER.to_contain_text(user_data.gender)
        self.end_user_form.DOCUMENT_TYPE.to_contain_text(user_data.document_type)
        self.end_user_form.DOCUMENT_SERIES_AND_NUMBER.to_contain_text(
            f"{user_data.document_serial} {user_data.document_num}" if not masked else "*** ***"
        )
        self.end_user_form.DOCUMENT_PROVIDE_BY.to_contain_text(user_data.document_provide_by) if not masked else "***"
        self.end_user_form.SUBDIVISION_CODE.to_contain_text(user_data.document_division_code if not masked else "***")
        self.end_user_form.DATE_OF_ISSUE.to_contain_text(user_data.issue_date if not masked else "01.01.1100")
        self.end_user_form.DOCUMENT_VALID_FOR.to_contain_text(
            user_data.document_valid_date if not masked else "01.01.1100"
        )
        self.end_user_form.PLACE_OF_BIRTH.to_contain_text(user_data.birth_place if not masked else "***")
        self.end_user_form.BIRTH_DATE.to_contain_text(user_data.birth_date if not masked else "01.01.1100")
        self.end_user_form.COUNTRY.to_contain_text(user_data.nationality)
        self.end_user_form.LANGUAGE.to_contain_text(user_data.speaking_language)
        self.end_user_form.REGISTRATION_ADDRESS.to_contain_text(user_data.registration_address)
        self.end_user_form.IS_PUBLIC.to_contain_text(user_data.is_public)
        self.end_user_form.IS_RESIDENT.to_contain_text(user_data.is_resident)

import re
from dataclasses import dataclass, field

import allure
from playwright.sync_api import Page

from api.requests.client_requests import ClientInfo, InfoAboutProduct
from common.helpers.checker import assert_that
from common.helpers.data_generator import faker_ru, get_current_datetime_string
from common.helpers.env_helper import BASE_URL as base_url
from common.helpers.string_helper import check_price, get_price_and_currency
from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
from pages.locators.client_profile import ClientProfile
from pages.locators.dynamic_form_elements import CreateSalesAndServiceManagement, DynamicForms
from pages.locators.home_page_elements import HomePage
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.ui_elements import Dropdown, Element, ElementsList, Select


@dataclass
class InfoAboutBundle:
    bundle_name: str = ""
    products: list[InfoAboutProduct] = field(default_factory=list)
    one_time_payment: float = 0.0
    subscription_fee: float = 0.0

    def add_product(self, product: InfoAboutProduct) -> None:
        self.products.append(product)
        self.one_time_payment += product.one_time_payment
        self.subscription_fee += product.subscription_fee


class InquiriesPage(BaseElements):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.product_offer_form = SelectProductOffersForm(page)

        self.CLIENT = Element("//a[contains(@href, 'overview')]/span", "Клиент", self.page)
        self.INQUIRY_ID = Element("//a[contains(@href, 'inquiries/')]/span", "Номер заявки", self.page)
        self.INQUIRY_NAME = Element(
            "//a[contains(@href, 'customer-hierarchy-management')]/..//h2", "Название заявки", self.page
        )
        self.INQUIRY_STATUS = Element("//div[@display='inline-block'] //div", "Статус заявки", self.page)
        self.INQUIRY_STEP = Element("//h2/parent::div/parent::div/div[2]/div/p", "Шаг продажи", self.page)

        self.TABS = ElementsList("[role=tablist] [role=tab]", "Вкладки", self.page)
        self.LOCATOR_SALE = Element(".platform-empty-box-container", "Элемент о текущих продуктах", self.page)

        self.LOAD_SPIN = Element("(//div[contains(@class, 'ant-spin-spinning')])[2]", "Лоадер", self.page)
        self.LOAD_SPIN_STATUS_NAME_1 = Element(
            "//div[contains(@class, 'ant-spin')]/following-sibling::h3", "Название статуса около Лоадера", self.page
        )
        self.LOAD_SPIN_STATUS_NAME_2 = Element(
            "//div[contains(@class, 'ant-spin')]/div/h3", "Название статуса около Лоадера", self.page
        )
        self.LOAD_SPIN_HELP_TEXT_1 = Element(
            "//div[contains(@class, 'ant-spin')]/following-sibling::p", "Текст подсказка для пользователя", self.page
        )
        self.LOAD_SPIN_HELP_TEXT_2 = Element(
            "//div[contains(@class, 'ant-spin')]/div/p", "Текст подсказка для пользователя", self.page
        )
        self.LOAD_SPIN_FIRST = Element("(//*[contains(@class, 'ant-spin-dot')])[1]", "Лоадер", self.page)
        self.LOAD_SPIN_SECOND = Element('[class*="ant-spin ant-spin-spin"]', "Лоадер второй", self.page)
        self.LOAD_SPIN_AFTER_SALE = Element(
            '(//div[contains(@class, "ant-spin ant-spin-spinning")])[1]', "Лоадер после продажи", self.page
        )

        self.NEXT_STEP_BTN = Element(
            "(//a[contains(@href, 'customer-hierarchy-management')]/..//button[1])[1]", "Кнопка 'Далее'", self.page
        )
        self.AUTO_AGREEMENT_BTN = Element(
            "[data-menu-id*=AUTO_CREATE_AGR_ACC]", "Кнопка 'Автоматическое управление Договором/ДС и ЛС'", self.page
        )
        self.COMMERCIAL_OFFER_BTN = Element(
            "[data-menu-id*=COMMERCIAL_OFFER]", "Кнопка 'Формирование и согласование документа КП'", self.page
        )
        self.NO_TRANSITION_FOUND = Element("[data-menu-id*=notfound]", "Кнопка 'Переходы не найдены'", self.page)
        self.LEFT_ARROW_BTN = Element(
            "(//button[contains(@class, 'ant-dropdown-trigger')])[1]", "Кнопка 'Стрелка влево'", self.page
        )
        self.RIGHT_ARROW_BTN = Dropdown(
            "(//button[contains(@class, 'ant-dropdown-trigger')])[2]", "Кнопка 'Стрелка вправо'", self.page
        )
        self.MORE_BTN = Select(
            "//a[contains(@href, 'customer-hierarchy-management')]/..//button[2]", "Кнопка 'Еще'", self.page
        )
        self.HEADER_RIGHT_BTNS = ElementsList(
            "//a[contains(@href, 'customer-hierarchy-management')]/..//h2/..//button",
            "Кнопки в правой части шапки заявки",
            self.page,
        )

        self.STEP_TITLE = Element(".ant-tabs-content h2", "Название шага", self.page)
        self.ADD_SALE_BTN = Element("#add", "Кнопка 'Добавить'", self.page)
        self.REFRESH_BTN = Element("#refresh", "Кнопка 'Обновить'", self.page)
        self.CHECK_CONFIGURATION_BTN = Element("#checkConfiguration", "Проверить конфигурацию", self.page)
        self.CHECK_TECHNICAL_FEASIBILITY_BTN = Element(
            "#checkTechnicalFeasibility", "Проверить техническую возможность", self.page
        )
        self.PRODUCT_CHECK_STATUS = Element(
            "(//div[@role='tabpanel'] //span[contains(@class, 'collapse-header-text')])[1]",
            "Статус проверки продукта",
            self.page,
        )

        # ACTIVE_STEP_TAB
        self.SCROLLABLE_PRODUCT_BLOCK = Element(
            ".ant-tabs-tabpane .platform-scrollable:nth-child(2)", "Блок продуктов, который можно скролить", self.page
        )
        self.ADDED_PRODUCT = ElementsList(
            "(//div[@role='tabpanel'] //div[contains(@class, 'platform-scrollable')] //div[contains(@class, 'ant5-collapse-expand-icon')]/../..)",
            "Добавленные продукты",
            self.page,
        )
        self.ADDED_BUNDLE = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=0]",
            "Добавленные бандлы",
            self.page,
        )
        self.ADDED_MONOPRODUCT = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=-1]",
            "Добавленные монопродукты",
            self.page,
        )
        self.ADDED_BUNDLE_NAMES = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=0] /span/div/div[2]/div[1]/div/p[1]",
            "Названия бандлов",
            self.page,
        )
        self.ADDED_PRODUCT_NAMES = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab'] //button/.. //p",
            "Названия продуктов",
            self.page,
        )
        self.ADDED_PRODUCT_ADD_OPTION_BTN = ElementsList(
            "//div[@role='tab'] //div[2] //p/../button", "Кнопка 'Добавить опцию'", self.page
        )
        self.ADDED_PRODUCT_EDIT_BTN = ElementsList(
            "//div[@role='tab'] //div[2] //div[2] //button[not(contains(@class, 'ant-dropdown-trigger'))]",
            "Кнопка 'Редактировать'",
            self.page,
        )
        self.ADDED_PRODUCT_MENU_BTN = ElementsList(
            "//div[@role='tab'] //div[2] //div[2] //button[contains(@class, 'ant-dropdown-trigger')]",
            "Три точки у добавленного монопродукта",
            self.page,
        )
        self.COPY_BTN = Element("[data-menu-id*=copy]", "Кнопка 'Копировать' монопродукт", self.page)
        self.ADDED_PRODUCT_INTERACTION_BTN = ElementsList(
            "((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']) //button)",
            "Кнопка 'Взаимодействия с продуктом'",
            self.page,
        )
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "//div[contains(@class, 'ant-collapse-content-box')] //span[contains(@class, 'ant-collapse-header-text')] //div[contains(@style, 'justify-items')] /div[2] //button/p",
            "'Разовый платёж' продукта",
            self.page,
        )
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE = ElementsList(
            "//div[contains(@class, 'ant-collapse-content-box')] //span[contains(@class, 'ant-collapse-header-text')] //div[contains(@style, 'justify-items')] /div[3] //button/p",
            "'Абонентская плата' продукта",
            self.page,
        )
        self.ADDED_BUNDLE_ONE_TIME_PAYMENT = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=0] //div[contains(@style, 'justify-items')]/div[2]/div/p[1]",
            "'Разовый платёж' бандл продукта",
            self.page,
        )
        self.ADDED_BUNDLE_SUBSCRIPTION_FEE = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=0] //div[contains(@style, 'justify-items')]/div[3]/div/p[1]",
            "'Абонентская плата' бандл продукта",
            self.page,
        )
        self.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=-1] //div[contains(@style, 'justify-items')]/div[2]/div/p[1]",
            "'Разовый платёж' бандл продукта",
            self.page,
        )
        self.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@tabindex=-1] //div[contains(@style, 'justify-items')]/div[3]/div/p[1]",
            "'Абонентская плата' бандл продукта",
            self.page,
        )

        self.TOTAL_ONE_TIME_PAYMENT = Element(
            "//*[.='Итого']/.. //div [p[.='Разовый платёж']]/../div/div/p", "Итого 'Разовый платёж'", self.page
        )  # требует дата атрибута от фронтов
        self.TOTAL_SUBSCRIPTION_FEE = Element(
            "//*[.='Итого']/.. //div [p[.='Абонентская плата']]/../div/div/p", "Итого 'Абонентская плата'", self.page
        )  # требует дата атрибута от фронтов

        self.PRODUCT_INFO_STATUS = Element(".platform-empty-box-container", "Информация о продукте", self.page)
        self.CHECK_CONFIGURATION_BTN = Element('[id="checkConfiguration"]', "Кнопка 'Проверить конфигурацию'", self.page)
        self.SUCCESS_SETUP = Element("[id*='-panel-0'] > div > div", "Уведомление об успешной настройке", self.page)
        self.AUTOMATIC_CREATE_CONTRACT_BTN = Element(
            '[data-menu-id*="AUTO_CREATE_AGR_ACC"]', "Кнопка 'Автоматическое создание контракта'", self.page
        )
        self.SUCCESS_COMPLITED = Element('[role="tabpanel"] > div > div', "Уведомление 'Успешно выполнено'", self.page)
        self.PRODUCT_PROFILE_BTN = Element(
            '[role="tabpanel"] [type="button"]', "Кнопка 'Перейти в продуктовый профиль'", self.page
        )
        self.CHOICE_CONTRACT_BTN = Element(
            "//button[.='Выбрать договор']", "Выбрать договор", self.page
        )  # требует дата атрибута от фронтов

        self.ADD_CONTRACT_BTN = Element("(//div[@role='tabpanel'] //button)[1]", "Кнопка 'Добавить договор'", self.page)
        self.CONTRACTS = ElementsList("tbody tr", "Договора", self.page)
        self.CONTRACTS_ID = ElementsList("tbody tr > td:nth-child(1) ", "Номер договора", self.page)
        self.CONTRACT_INFO = Element(
            "(//div[contains(@class, 'platform-custom-table')] //p)[1]", "Информация о договоре", self.page
        )

        self.ERROR_TEXT = Element("(//div[@role='tabpanel']//p[@color='interface15'])[1]", "Текст ошибки", self.page)

        self.ADDRESSES_ON_ACCOUNT = ElementsList(
            ".ant-tabs [role=tablist] .ant-collapse-item [role=tab][aria-disabled='false']", "Адреса на ЛС", self.page
        )
        self.ADDRESSES_ON_ACCOUNT_CHECKBOX = ElementsList(
            ".ant-tabs [role=tablist] .ant-collapse-item [role=tab][aria-disabled='false'] input",
            "Адреса на ЛС",
            self.page,
        )

        self.SAVE_DISTRIBUTION_BTN = Element(
            "//button[.='Сохранить распределение']", "Кнопка сохранить распределение", self.page
        )  # требует дата атрибута от фронтов
        # ORDER_ITEMS_TAB
        self.PRODUCTS = ElementsList(
            "[role=tabpanel] [role=tablist] .ant-collapse-content [role=tab]", "Продукты", self.page
        )
        self.PRODUCTS_NAME = ElementsList(
            "(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')])[3]/div[1]/div[1]",
            "Название продукта",
            self.page,
        )
        self.MONOPRODUCT_NAMES = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1]/span/div/div[2]/div[1]/div/p",
            "Название монопродукта",
            self.page,
        )
        self.PRODUCTS_STATUS = ElementsList(
            "(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')])[3]/div[1]/div[2]/div/div[1]/p[2]",
            "Статус продукта",
            self.page,
        )
        self.SUBSCRIBERS = ElementsList(
            "(//div[contains(@class, 'platform-grid-container')])[3]/div[2]/div[1]/div/div[1]/div",
            "Поля 'Абонент'",
            self.page,
        )
        self.MONOPRODUCT_SUBSCRIBERS = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[2]/div[2]/div[1]/div/div[1]/div",
            "Поле 'Абонент' монопродукта",
            self.page,
        )
        self.PRODUCTS_CONTRACT_NUM = ElementsList(
            "(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')] //a)[1]", "Номер договора", self.page
        )
        self.PRODUCTS_PERSONAL_ACCOUNT_NUM = ElementsList(
            "(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')] //a)[2]",
            "Номер лицевого счета",
            self.page,
        )
        self.PRODUCTS_SUBSCRIPTION_FEE = ElementsList(
            "(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')])[5] /div[3]/div",
            "Абонентская плата",
            self.page,
        )
        # SALE_CARD_TAB
        self.DATA_SALE = Element(".ant-tabs-tabpane-active > div > div", "Информация по продаже", self.page)
        # CURRENT_STATE_TAB
        self.PROCESSING_STEP = ElementsList(
            '[class="ant-collapse-item ant-collapse-item-active"]', "Шаг обработки заявки", self.page
        )
        # PROCESSING_HISTORY
        self.HISTORY_STEPS = ElementsList(".scrollable-body > div > div > div", "Шаги", self.page)
        self.STEP_PROCESSES = ElementsList(
            "//div[contains(@class, 'platform-scrollable')] //h4/following-sibling::div /div",
            "События в шаге",
            self.page,
        )

        # TECHNIC_OFFERS_TAB
        self.TECHNIC_OFFER_REFRESH_BTN = Element(
            "#techRequestGrid_control button:nth-child(1)", "Кнопка 'Обновить'", self.page
        )
        self.TECHNIC_OFFER_TAB_SETTINGS = Element(
            "#techRequestGrid_control button:nth-child(2)", "Кнопка 'Настройки'", self.page
        )

        self.TECHNICAL_OFFERS = ElementsList("tbody tr", "Заказы", self.page)
        self.TECHNICAL_OFFERS_ID = ElementsList("tbody tr > td:nth-child(1) ", "Номер заказа", self.page)

        # RESOURCE_REPLACEMENT_TAB
        self.RESOURCE_REPLACEMENT_FORWARD = Element(
            "//li[contains(@data-menu-id, 'FORWARD')]", "Кнопка Передать на обработку в Замена Ресурса", self.page
        )
        self.RESOURCE_REPLACEMENT_STATUS = Element("//p[@color='interface2']", "Статус заявки Замена ресурса", self.page)
        self.RESOURCE_REPLACEMENT_REFRESH_BTN = Element(
            "//button[@variant='default'] [2]", "Кнопка обновить в Замена ресурса", self.page
        )
        self.RESOURCE_REPLACEMENT_APPLY_BTN = Element(
            "//button[@variant='primary']", "Кнопка обновить в Замена ресурса", self.page
        )
        self.RESOURCE_REPLACEMENT_DUE_DATE_INPUT = Element(
            "//input[@id='forwardInquiryForm_dueDate']", "Поле для ввода даты обработки", self.page
        )
        self.RESOURCE_REPLACEMENT_DUE_DATE_TODAY = Element(
            "//input[@id='forwardInquiryForm_dueDate'] //../../.. //a",
            "Кнопка сегодня в выборе даты обработки",
            self.page,
        )

    @allure.step("Создание продажи")
    def sale_initialization(self, client: ClientInfo = None) -> None:
        base_page = BasePage(self.page)
        home_page = HomePage(self.page)
        inquiries_page = InquiriesPage(self.page)
        create_request_form = CreateSalesAndServiceManagement(self.page)

        if not client:
            inquiries_page.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"])
            base_page.base_elements.CREATE_APPLICATION.click()
            create_request_form.CHOOSE_AGREEMENT_BTN.select_by_value(value="Автоматически")
            create_request_form.CHOOSE_PRIORITY_BTN.select_by_value(value="Высокий")
        else:
            base_page.open(f"{base_url}customer-hierarchy-management/customers/{client.user_id}/overview")
            home_page.RIGHT_SIDE_BTN.wait_to_have_count(4, timeout=10000)
            home_page.RIGHT_SIDE_BTN.click(1)
            contact_phone = faker_ru.phone_number()
            contact_email = faker_ru.email()
            agreement_date = get_current_datetime_string(is_full_format=False)
            create_request_form.EMAIL.fill(contact_email)
            create_request_form.PHONE.fill(contact_phone)
            create_request_form.PRIORITY.select_by_value("Высокий")
            with allure.step("Выбор договора клиента"):
                create_request_form.SELECTED_SALE.select_by_value(value=f"{client.agreement_number} от {agreement_date}")
            with allure.step("Выбор ЛС клиента"):
                create_request_form.SALE_ACCOUNT.select_by_value(value=f"{client.account_number}")
            create_request_form.CREATE_ADD_AGREEMENT.to_be_enabled()
            create_request_form.TITLE_CREATE_ADD_AGREEMENT.to_have_class(re.compile(r".*ant-form-item-required.*"))
            create_request_form.CREATE_ADD_AGREEMENT.select_by_value(value="Сформировать автоматически")
            create_request_form.CREATE_ADD_AGREEMENT.to_be_enabled()

        create_request_form.SAVE_BTN.click()
        inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"), timeout=10000)
        inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=25000)

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Мобильная связь'")
    def sale_phone_number(self, client: ClientInfo = None) -> InfoAboutProduct:
        """Метод для продажи продукта из категории Мобильная связь
        client: при необходимости продажи продукта на конкретный ЛС, договор для конкретного клиента
        нужно передавать результат работы фикстуры create_user_with_agreement_and_account
        """
        base_page = BasePage(self.page)
        base_page.bring_to_front(base_page.page.title())
        inquiries_page = InquiriesPage(self.page)
        product_offer = SelectProductOffersForm(self.page)
        product_edit_form = ProductEditForm(self.page)
        product = InfoAboutProduct()

        self.sale_initialization(client)

        with allure.step("Поиск товаров в категории: Монопродукт, Мобильная связь"):
            inquiries_page.ADD_SALE_BTN.click()
            product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
            product_offer.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            product_offer.SEARCH_BTN.click()

        with allure.step("Выбор продукта"):
            product_offer.PRODUCT_CARD.wait_elements_visible(0)
            product.product_name = product_offer.PRODUCT_CARD_NAME[0].text
            product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
            product_offer.ADD_BTN.click()
            inquiries_page.ADDED_PRODUCT.wait_to_have_count(1)
            inquiries_page.ADDED_PRODUCT[0].to_contain_text(product.product_name)
            inquiries_page.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            product.one_time_payment = get_price_and_currency(inquiries_page.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].text)[0]
            inquiries_page.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            product.subscription_fee = get_price_and_currency(inquiries_page.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].text)[0]
            inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Бронирование ресурсов"):
            inquiries_page.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            product_edit_form.TITLE.wait_to_have_text(product.product_name)
            product_edit_form.RESOURCES_TAB.click()
            product.phone_number = product_edit_form.auto_reserve_phone_number_resources()
            product_edit_form.INNER_CANCEL_BTN.click()

        with allure.step("Проверка конфигурации"):
            inquiries_page.CHECK_CONFIGURATION_BTN.click()
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=10000)
            inquiries_page.PRODUCT_CHECK_STATUS.to_contain_text("Продукты заказа настроены корректно.")

        with allure.step("Завершение продажи"):
            inquiries_page.NEXT_STEP_BTN.click()
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=350000)
            inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)
        return product

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Интернет'")
    def sale_internet(self, client: ClientInfo = None) -> InfoAboutProduct:
        base_page = BasePage(self.page)
        base_page.bring_to_front(base_page.page.title())
        client_profile = ClientProfile(self.page)
        inquiries_page = InquiriesPage(self.page)
        product_offer = SelectProductOffersForm(self.page)
        product = InfoAboutProduct()

        self.sale_initialization(client)

        with allure.step("Поиск товаров в категории: Монопродукт, Интернет"):
            inquiries_page.ADD_SALE_BTN.click()
            product_offer.PRODUCT_TYPE.select_by_value("Монопродукт")
            product_offer.PRODUCT_CATEGORY.select_by_value("Интернет")
            product_offer.SEARCH_BTN.click()

        with allure.step("Выбор продукта"):
            product_offer.PRODUCT_CARD.wait_elements_visible(0)
            product.product_name = product_offer.PRODUCT_CARD_NAME[0].text
            product_offer.PRODUCT_CARD_SELECT_BTN[0].click()
            product_offer.ADD_BTN.click()
            inquiries_page.ADDED_PRODUCT.wait_to_have_count(1)
            inquiries_page.ADDED_PRODUCT[0].to_contain_text(product.product_name)
            inquiries_page.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
            product.one_time_payment = get_price_and_currency(inquiries_page.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].text)[0]
            inquiries_page.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
            product.subscription_fee = get_price_and_currency(inquiries_page.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].text)[0]
            inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")

        with allure.step("Проверка конфигурации"):
            inquiries_page.CHECK_CONFIGURATION_BTN.click()
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=15000)
            inquiries_page.PRODUCT_CHECK_STATUS.to_contain_text("Продукты заказа настроены корректно.")

        with allure.step("Проверка технической возможности"):
            inquiries_page.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            inquiries_page.PRODUCT_CHECK_STATUS.wait_to_be_visible(timeout=15000)
            inquiries_page.PRODUCT_CHECK_STATUS.wait_to_have_text(
                'Для всех продуктов заказа есть техническая возможность подключения. Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".'
            )

        with allure.step("Завершение продажи"):
            inquiries_page.NEXT_STEP_BTN.click()
            inquiries_page.LOAD_SPIN_FIRST.wait_to_be_visible()
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            base_page.refresh_page("domcontentloaded")
            inquiries_page.TABS.wait_to_be_visible(timeout=10000)
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=120000)
            base_page.refresh_page("domcontentloaded")
            inquiries_page.TABS.wait_to_be_visible(timeout=10000)
            inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=120000)
            inquiries_page.CLIENT.click()

        client_profile.PRODUCTS_TAB.click()
        client_profile.PRODUCTS.wait_to_be_visible()
        product.internet_number = client_profile.SUBSCRIBER[0].text

        return product

    @allure.step("Нажать кнопку 'Проверить конфигурацию' и дождаться выполнения проверки")
    def check_configuration(self) -> None:
        self.CHECK_CONFIGURATION_BTN.click()
        self.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        self.PRODUCT_CHECK_STATUS.wait_to_have_text("Продукты заказа настроены корректно.", timeout=10000)

    @allure.step(
        "Нажать кнопку 'Проверить техническую возможность' и дождаться выполнения проверки технической возможности подключения продуктов"
    )
    def check_technical_feasibility(self) -> None:
        self.CHECK_TECHNICAL_FEASIBILITY_BTN.click()
        self.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        self.PRODUCT_CHECK_STATUS.wait_to_have_text(
            "Для всех продуктов заказа есть техническая возможность подключения. "
            'Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".',
            timeout=10000,
        )

    @allure.step("Дождаться подключения выбранных пакетных предложений и закрытия заявки")
    def wait_connect_package_offers_and_close_inquiry(self) -> None:
        self.LOAD_SPIN_FIRST.not_to_be_visible(timeout=350000)
        self.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)
        self.INQUIRY_STATUS.wait_to_have_text("Закрыто")

    @allure.step("Проверить отображение продуктов бандлов (количество, названия, начисления)")
    def check_view_bundle_products(self, bundles: list[InfoAboutBundle], product_names: list[str]) -> None:
        self.ADDED_BUNDLE.wait_to_have_count(len(bundles), timeout=15000)
        self.ADDED_MONOPRODUCT.wait_to_have_count(len(product_names))
        self.ADDED_BUNDLE_NAMES.wait_for_text_in_all([bundle.bundle_name for bundle in bundles])
        self.ADDED_PRODUCT_NAMES.wait_for_text_in_all(product_names)
        self.set_products_charge(bundles)

    @allure.step("Проверка Статуса продажи, Названия шага, Активной вкладки на первом шаге продажи")
    def check_firs_step_sale_titles(self) -> None:
        self.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
        self.TABS[0].wait_to_have_text("Активный шаг")
        self.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.ADDED_PRODUCT.wait_to_have_count(0)

    @allure.step("Проверка формы 'Выбор продуктовых предложений'")
    def check_product_offer_form(self) -> None:
        self.product_offer_form.TITLE.to_contain_text("Выбор продуктов")
        self.product_offer_form.PRODUCT_TYPE.wait_to_be_enabled()
        self.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.wait_to_be_enabled()
        self.product_offer_form.TECHNOLOGY.wait_to_be_enabled()
        checked_value = self.product_offer_form.PRODUCT_TYPE.checked_value
        assert_that(
            lambda: checked_value == "Монопродукт",
            f"По умолчанию не выбрано 'Монопродукт'. Текущее значение: {checked_value}",
        )

    @allure.step("Выбор продуктового предложения {product_offer_name}")
    def choose_product_offer_with_name(self, product_offer_name: str) -> InfoAboutProduct | InfoAboutBundle:
        self.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([product_offer_name])
        index = self.product_offer_form.PRODUCT_CARD_NAME.text_list.index(product_offer_name)
        self.product_offer_form.PRODUCT_CARD_SELECT_BTN.click(index)
        self.product_offer_form.PRODUCT_CARD_SELECT_BTN[index].wait_to_have_text("Удалить")
        if (
            len(
                self.page.locator(self.product_offer_form.PRODUCT_CARD.path)
                .nth(index)
                .locator(self.product_offer_form.PRODUCT_CARD_PRODUCTS.path)
                .all()
            )
            > 0
        ):
            bundle = InfoAboutBundle(bundle_name=product_offer_name)
            products = (
                self.page.locator(self.product_offer_form.PRODUCT_CARD.path)
                .nth(index)
                .locator(self.product_offer_form.PRODUCT_CARD_PRODUCTS.path)
            )
            for product_name in products.all_text_contents():
                bundle.add_product(InfoAboutProduct(product_name=product_name))
            bundle.one_time_payment = get_price_and_currency(
                self.product_offer_form.PRODUCT_SINGLE_PAYMENTS[index].text
            )[0]
            bundle.subscription_fee = get_price_and_currency(self.product_offer_form.PRODUCT_CARD_SUMS[index].text)[0]
            return bundle
        else:
            product = InfoAboutProduct(product_name=product_offer_name)
            product.one_time_payment = get_price_and_currency(
                self.product_offer_form.PRODUCT_SINGLE_PAYMENTS[index].text
            )[0]
            product.subscription_fee = get_price_and_currency(self.product_offer_form.PRODUCT_CARD_SUMS[index].text)[0]
            return product

    @allure.step(
        "Для каждого монопродукта через кнопку редактирования заполнить обязательные параметры и ресурсы и сохранить изменения"
    )
    def auto_reserve_all_resources(self) -> None:
        one_scroll_size = 80
        product_edit_form = ProductEditForm(self.page)
        self.ADDED_PRODUCT_EDIT_BTN.wait_to_be_visible(timeout=15000)
        count = self.ADDED_PRODUCT_EDIT_BTN.elements_len()
        scroll = one_scroll_size
        for edit_btn_index in range(count):
            product_edit_form.TITLE.not_to_be_visible()
            self.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(edit_btn_index)
            self.SCROLLABLE_PRODUCT_BLOCK.scroll_scrollable_platform(scroll)
            scroll = one_scroll_size
            self.ADDED_PRODUCT_EDIT_BTN[edit_btn_index].click(force=True)
            product_edit_form.RESOURCES_TAB.click()
            if self.page.locator(product_edit_form.MODAL.path).is_visible():
                product_edit_form.MODAL_DONT_SAVE_BTN.click()
            product_edit_form.RESOURCES.wait_to_be_visible()
            if self.page.locator(product_edit_form.RESERVE_RESOURCES_BTN.path).is_visible():
                product_edit_form.RESERVE_RESOURCES_BTN.click()
                product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible(timeout=15000)
                scroll = one_scroll_size * (edit_btn_index + 1)
            product_edit_form.INNER_CANCEL_BTN.click()

    @allure.step("Получение и проверка стоимости монопродуктов бандлов")
    def set_products_charge(self, bundles: list[InfoAboutBundle]) -> None:
        bundle_names = self.ADDED_BUNDLE_NAMES.text_list
        product_names = self.ADDED_PRODUCT_NAMES.text_list
        for bundle in bundles:
            one_time_payment_summ, subscription_fee_summ = 0.0, 0.0

            bundle_index = bundle_names.index(bundle.bundle_name)
            bundle_names[bundle_index] = ""
            check_price(self.ADDED_BUNDLE_ONE_TIME_PAYMENT[bundle_index], bundle.one_time_payment)
            check_price(self.ADDED_BUNDLE_SUBSCRIPTION_FEE[bundle_index], bundle.subscription_fee)
            for product in bundle.products:
                product_index = product_names.index(product.product_name)
                product_names[product_index] = ""
                product.one_time_payment = get_price_and_currency(
                    self.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT[product_index].text
                )[0]
                product.subscription_fee = get_price_and_currency(
                    self.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE[product_index].text
                )[0]
                one_time_payment_summ += product.one_time_payment
                subscription_fee_summ += product.subscription_fee
            assert_that(
                lambda: bundle.one_time_payment == one_time_payment_summ,
                f"Разовый платеж за бандл {bundle.one_time_payment} "
                f"не равен сумме разовых платежей за монопродукты, входящие в бандл {one_time_payment_summ}",
            )
            assert_that(
                lambda: bundle.subscription_fee == subscription_fee_summ,
                f"Абонентская плата за бандл {bundle.subscription_fee} "
                f"не равна сумме абонентских плат за монопродукты, входящие в бандл {subscription_fee_summ}",
            )

    @allure.step("Получение абонентов монопродуктов бандлов")
    def set_products_subscriber(self, bundles: list[InfoAboutBundle]) -> None:
        self.TABS[1].wait_to_have_text("Элементы заказа")
        self.TABS[1].click()
        bundle_names = [bundle.bundle_name for bundle in bundles]
        self.PRODUCTS_NAME.wait_for_text_in_all(bundle_names)
        bundle_products = []
        for bundle in bundles:
            for product in bundle.products:
                bundle_products.append(product)
        for monoproduct_index in range(self.MONOPRODUCT_NAMES.elements_len()):
            name = self.MONOPRODUCT_NAMES.text_list[monoproduct_index]
            for product in bundle_products:
                if name == product.product_name and product.phone_number == "" and product.internet_number == "":
                    subscriber = self.MONOPRODUCT_SUBSCRIBERS[monoproduct_index].text
                    if subscriber.isdigit():
                        product.phone_number = subscriber
                    else:
                        product.internet_number = subscriber
                    break

    @allure.step("Проверка значений поля Итого")
    def check_total_fields(self, one_time_payment: float, subscription_fee: float) -> None:
        check_price(self.TOTAL_ONE_TIME_PAYMENT, one_time_payment)
        check_price(self.TOTAL_SUBSCRIPTION_FEE, subscription_fee)


class ProductEditForm(DynamicForms):
    """Форма редактирования продукта"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SUBSCRIPTION_FEE = Element(
            ".ant-drawer-content[role=dialog] .ant-drawer-body h4", "Абонентская плата", self.page
        )

        self.VOLUMES_TAB = Element(
            ".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(1)", "Таб 'Объемы'", self.page
        )
        self.SPECIFICATION_TAB = Element(
            ".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(2)", "Таб 'Характеристики'", self.page
        )
        self.SERVICES_TAB = Element(
            ".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(3)", "Таб 'Сервисы'", self.page
        )
        self.RESOURCES_TAB = Element(
            ".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(4)", "Таб 'Ресурсы'", self.page
        )
        self.RESOURCES_TAB_IN_CASE_ONLY_PHONE = Element(
            ".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(3)", "Таб 'Ресурсы'", self.page
        )

        # VOLUMES_TAB
        self.VOLUMES = ElementsList(".ant-drawer-content[role=dialog] div[id*='panel-volumes']", "Объемы", self.page)

        # SPECIFICATION_TAB
        self.SPECIFICATION = ElementsList(
            ".ant-drawer-content[role=dialog] div[id*='panel-characteristics']", "Характеристики", self.page
        )

        # SERVICES_TAB
        self.SERVICES = ElementsList(".ant-drawer-content[role=dialog] .ant-collapse-item", "Сервисы", self.page)

        self.COLOR_NUMBER_FORM = Select(".ant-select-selector", "Форма выбора цвета номера", self.page)
        self.BOOK_RESOURCES = Element(
            "[id*='-panel-resources'] > div > :nth-child(1) [type='button']", "Кнопка 'Забронировать ресурсы'", self.page
        )

        # RESOURCES_TAB
        self.RESOURCES = ElementsList(
            ".ant-drawer-content[role=dialog] div[id*='panel-resources']", "Ресурсы", self.page
        )
        self.RESERVE_RESOURCES_BTN = Element(
            ".ant-drawer-content[role=dialog] div[id*='panel-resources'] button:nth-child(1)",
            "Кнопка 'Забронировать ресурсы'",
            self.page,
        )
        self.CHANGE_RESOURCES_BTN = Element(
            ".ant-drawer-content[role=dialog] div[id*='panel-resources'] button:nth-child(2)",
            "Кнопка 'Замена ресурса'",
            self.page,
        )
        self.RESERVE_RESOURCES_LOADER = Element(
            ".ant-form .ant-spin-dot", "Лоадер во время бронирования ресурсов", self.page
        )
        self.ICCID = Element(
            "(//p[contains(text(), 'SIM')]/../.. //p)[4]", "ICCID SIM-карты", self.page
        )  # требует дата атрибута от фронтов
        self.PHONE_NUMBER = Element(
            "(//p[contains(text(), 'Телефонный номер')]/../.. //p)[4]", "Номер телефона", self.page
        )  # требует дата атрибута от фронтов

        self.CANCEL_BUTTON = Element(
            "(//button[@id='_cancel-button'])[1]", "Кнопка Отмены на форме редактирования", self.page
        )

    def auto_reserve_phone_number_resources(self) -> str | None:
        self.RESERVE_RESOURCES_BTN.click()
        self.RESERVE_RESOURCES_LOADER.not_to_be_visible()
        self.ICCID.not_to_contain_text("—")
        self.PHONE_NUMBER.not_to_contain_text("—")
        return self.PHONE_NUMBER.text


class ChangeResourcesForm:
    """Форма 'Замена ресурса'"""

    def __init__(self, page: Page):
        self.page = page

        self.FORM = Element(
            "(//*[contains(@class, 'ant-drawer-content')][@role='dialog'])[2]", "Форма 'Замена ресурса'", self.page
        )
        self.TITLE = Element("(//*[contains(@class, 'ant-drawer-title')] //h3)[2]", "Заголовок формы", self.page)
        self.SUBTITLE = Element(".ant-drawer-title p", "Подзаголовок формы", self.page)
        self.NUMBERS = ElementsList(
            "(//*[contains(@class, 'platform-scrollable scrollable-body')]/div/div/div/div/div/div[2]/div/p)",
            "Доступные номера телефонов",
            self.page,
        )
        self.INNER_ACCEPT_BTN = Element("(//button[@id='_accept-button'])[2]", "Внутренняя кнопка 'Выбрать'", self.page)


class CloseInquiryForm:
    """Форма 'Закрытие заявки'"""

    def __init__(self, page: Page):
        self.page = page

        self.FORM = Element(".ant-drawer-wrapper-body", "Форма 'Закрытие заявки'", self.page)
        self.TITLE = Element(".ant-drawer-header h3", "Заголовок формы", self.page)
        self.CLOSE_BTN = Element("#_accept-button", "Кнопка 'Закрыть'", self.page)

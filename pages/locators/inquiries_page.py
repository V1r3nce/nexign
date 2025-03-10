import re
from dataclasses import dataclass

import allure
from playwright.sync_api import Page

from common.helpers.string_helper import get_price_and_currency
from pages.base_page import BasePage
from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import DynamicForms, RequestCreate
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.ui_elements import Element, Select, ElementsList, Dropdown


@dataclass
class InfoAboutMobileProduct:
    product_name: str = ""
    phone_number: str = ""
    one_time_payment: float = 0.0
    subscription_fee: float = 0.0


class InquiriesPage(BaseElements):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT = Element("//a[contains(@href, 'overview')]/span", "Клиент", self.page)
        self.INQUIRY_ID = Element("//a[contains(@href, 'inquiries/')]/span", "Номер заявки", self.page)
        self.INQUIRY_NAME = Element("//a[contains(@href, 'customer-hierarchy-management')]/..//h2", "Название заявки", self.page)
        self.INQUIRY_STATUS = Element("//div[@display='inline-block']/p", "Статус заявки", self.page)

        self.TABS = ElementsList("[role=tablist] [role=tab]", "Вкладки", self.page)
        self.LOCATOR_SALE = Element(".platform-empty-box-container", "Элемент о текущих продуктах",
                                    self.page)

        self.LOAD_SPIN = Element("(//div[contains(@class, 'ant-spin-spinning')])[2]", "Лоадер", self.page)
        self.LOAD_SPIN_FIRST = Element(".ant-spin-dot", "Лоадер", self.page)
        self.LOAD_SPIN_SECOND = Element('[class*="ant-spin ant-spin-spin"]', "Лоадер второй", self.page)
        self.LOAD_SPIN_AFTER_SALE = Element('(//div[contains(@class, "ant-spin ant-spin-spinning")])[1]', "Лоадер после продажи", self.page)

        self.NEXT_STEP_BTN = Element("//a[contains(@href, 'customer-hierarchy-management')]/..//button[1]", "Кнопка 'Далее'", self.page)
        self.LEFT_ARROW_BTN = Element("(//button[contains(@class, 'ant-dropdown-trigger')])[1]", "Кнопка 'Стрелка влево'", self.page)
        self.RIGHT_ARROW_BTN = Dropdown("(//button[contains(@class, 'ant-dropdown-trigger')])[2]", "Кнопка 'Стрелка вправо'", self.page)
        self.MORE_BTN = Select("//a[contains(@href, 'customer-hierarchy-management')]/..//button[2]", "Кнопка 'Еще'", self.page)

        self.STEP_TITLE = Element(".ant-tabs-content h2", "Название шага", self.page)
        self.ADD_SALE_BTN = Element("#add", "Кнопка 'Добавить'", self.page)
        self.REFRESH_BTN = Element("#refresh", "Кнопка 'Обновить'", self.page)
        self.CHECK_CONFIGURATION_BTN = Element("#checkConfiguration", "Проверить конфигурацию", self.page)
        self.CHECK_TECHNICAL_FEASIBILITY_BTN = Element("#checkTechnicalFeasibility", "Проверить техническую возможность", self.page)
        self.PRODUCT_CHECK_STATUS = Element("div[id*=panel-0]>div>div>div:nth-child(3) p", "Статус проверки продукта", self.page)

        #ACTIVE_STEP_TAB
        self.ADDED_PRODUCT = ElementsList("(//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab'])", "Добавленные продукты", self.page)
        self.ADDED_PRODUCT_NAMES = ElementsList(
            "//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab'] //button/.. //p",
            "Названия продуктов", self.page)
        self.ADDED_PRODUCT_EDIT_BTN = ElementsList("((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']) //button)[2]", "Кнопка 'Редактировать'", self.page)
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT = ElementsList("((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab'])) /.. //div [p[.='Разовый платёж']]/div", "'Разовый платёж' продукта", self.page)
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE = ElementsList("((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']))/.. //div [p[.='Абонентская плата']]/div", "'Абонентская плата' продукта", self.page)

        self.TOTAL_ONE_TIME_PAYMENT = Element("//*[.='Итого']/.. //div [p[.='Разовый платёж']]/div", "Итого 'Разовый платёж'", self.page) # требует дата атрибута от фронтов
        self.TOTAL_SUBSCRIPTION_FEE = Element("//*[.='Итого']/.. //div [p[.='Абонентская плата']]/div", "Итого 'Абонентская плата'", self.page) # требует дата атрибута от фронтов

        self.PRODUCT_INFO_STATUS = Element(".platform-empty-box-container", "Информация о продукте", self.page)
        self.CHECK_CONFIGURATION_BTN = Element('[id="checkConfiguration"]', "Кнопка 'Проверить конфигурацию'",
                                               self.page)
        self.SUCCESS_SETUP = Element("[id*='-panel-0'] > div > div", "Уведомление об успешной настройке",
                                     self.page)
        self.AUTOMATIC_CREATE_CONTRACT_BTN = Element('[data-menu-id*="AUTO_CREATE_AGR_ACC"]',
                                                     "Кнопка 'Автоматическое создание контракта'",
                                                     self.page)
        self.SUCCESS_COMPLITED = Element('[role="tabpanel"] > div > div', "Уведомление 'Успешно выполнено'",
                                         self.page)
        self.PRODUCT_PROFILE_BTN = Element('[role="tabpanel"] [type="button"]',
                                           "Кнопка 'Перейти в продуктовый профиль'",
                                           self.page)
        self.CHOICE_CONTRACT_BTN = Element("//button[.='Выбрать договор']", "Выбрать договор", self.page) # требует дата атрибута от фронтов

        self.ADD_CONTRACT_BTN = Element("(//div[@role='tabpanel'] //button)[1]", "Кнопка 'Добавить договор'", self.page)
        self.CONTRACTS = ElementsList("tbody tr", "Договора", self.page)
        self.CONTRACTS_ID = ElementsList("tbody tr > td:nth-child(1) ", "Номер договора", self.page)
        self.CONTRACT_INFO = Element("(//div[contains(@class, 'platform-custom-table')] //p)[1]", "Информация о договоре", self.page)

        self.ERROR_TEXT = Element("(//div[@role='tabpanel']//p[@color='interface15'])[1]", "Текст ошибки", self.page)

        self.ADDRESSES_ON_ACCOUNT = ElementsList(".ant-tabs [role=tablist] .ant-collapse-item [role=tab][aria-disabled='false']", "Адреса на ЛС", self.page)
        self.ADDRESSES_ON_ACCOUNT_CHECKBOX = ElementsList(".ant-tabs [role=tablist] .ant-collapse-item [role=tab][aria-disabled='false'] input", "Адреса на ЛС", self.page)

        self.SAVE_DISTRIBUTION_BTN = Element("//button[.='Сохранить распределение']", "Кнопка сохранить распределение", self.page) # требует дата атрибута от фронтов
        #ORDER_ITEMS_TAB
        self.PRODUCTS = ElementsList("[role=tabpanel] [role=tablist] .ant-collapse-content [role=tab]", "Продукты", self.page)
        self.PRODUCTS_CONTRACT_NUM = ElementsList("(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')] //a)[1]", "Номер договора", self.page)
        self.PRODUCTS_PERSONAL_ACCOUNT_NUM = ElementsList("(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')] //a)[2]", "Номер лицевого счета", self.page)
        self.PRODUCTS_SUBSCRIPTION_FEE = ElementsList("(//div[@role='tab'] //div[contains(@class, 'platform-grid-container')])[5] /div[3]/div", "Абонентская плата", self.page)

        #PROCESSING_HISTORY
        self.HISTORY_STEPS = ElementsList(".scrollable-body > div > div > div", "Шаги", self.page)
        self.STEP_PROCESSES = ElementsList("//div[contains(@class, 'platform-scrollable')] //h4/following-sibling::div /div", "События в шаге", self.page)

        #TECHNIC_OFFERS_TAB
        self.TECHNIC_OFFER_REFRESH_BTN = Element("#techRequestGrid_control button:nth-child(1)", "Кнопка 'Обновить'", self.page)
        self.TECHNIC_OFFER_TAB_SETTINGS = Element("#techRequestGrid_control button:nth-child(2)", "Кнопка 'Настройки'", self.page)

        self.TECHNICAL_OFFERS = ElementsList("tbody tr", "Заказы", self.page)
        self.TECHNICAL_OFFERS_ID = ElementsList("tbody tr > td:nth-child(1) ", "Номер заказа", self.page)

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Мобильная связь'")
    def sale_phone_number(self):
        base_page = BasePage(self.page)
        base_page.bring_to_front(base_page.page.title())
        create_request = RequestCreate(self.page)
        inquiries_page = InquiriesPage(self.page)
        product_offer = SelectProductOffersForm(self.page)
        product_edit_form = ProductEditForm(self.page)
        product = InfoAboutMobileProduct()

        with allure.step("Создание продажи"):
            base_page.base_elements.CREATE_APPLICATION.click()
            create_request.CHOOSE_AGREEMENT_BTN.select_by_value(value='Автоматически')
            create_request.CHOOSE_PRIORITY_BTN.select_by_value(value='Низкий')
            create_request.SAVE_BTN.click()
            inquiries_page.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"))
            inquiries_page.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
            inquiries_page.PRODUCT_INFO_STATUS.wait_to_be_visible()

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
            inquiries_page.LOAD_SPIN_FIRST.not_to_be_visible(timeout=300000)
            inquiries_page.PRODUCT_INFO_STATUS.wait_to_have_text("Успешно выполнено", timeout=10000)
        return product


class ProductEditForm(DynamicForms):
    """Форма редактирования продукта"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.SUBSCRIPTION_FEE = Element(".ant-drawer-content[role=dialog] .ant-drawer-body h4", "Абонентская плата", self.page)

        self.VOLUMES_TAB = Element(".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(1)", "Таб 'Объемы'",
                                   self.page)
        self.SPECIFICATION_TAB = Element(".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(2)",
                                         "Таб 'Характеристики'", self.page)
        self.SERVICES_TAB = Element(".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(3)", "Таб 'Сервисы'",
                                    self.page)
        self.RESOURCES_TAB = Element(".ant-drawer-content[role=dialog] .ant-tabs-tab:nth-of-type(4)", "Таб 'Ресурсы'",
                                   self.page)

        #VOLUMES_TAB
        self.VOLUMES = ElementsList(".ant-drawer-content[role=dialog] div[id*='panel-volumes']", "Объемы", self.page)

        #SPECIFICATION_TAB
        self.SPECIFICATION = ElementsList(".ant-drawer-content[role=dialog] div[id*='panel-characteristics']",
                               "Характеристики", self.page)

        #SERVICES_TAB
        self.SERVICES = ElementsList(".ant-drawer-content[role=dialog] .ant-collapse-item", "Сервисы", self.page)

        self.COLOR_NUMBER_FORM = Select(".ant-select-selector", "Форма выбора цвета номера",
                                        self.page)
        self.BOOK_RESOURCES = Element("[id*='-panel-resources'] > div > :nth-child(1) [type='button']","Кнопка 'Забронировать ресурсы'",
                                      self.page)

        #RESOURCES_TAB
        self.RESOURCES = ElementsList(".ant-drawer-content[role=dialog] div[id*='panel-resources']", "Ресурсы", self.page)
        self.RESERVE_RESOURCES_BTN = Element(".ant-drawer-content[role=dialog] div[id*='panel-resources'] button:nth-child(1)", "Кнопка 'Забронировать ресурсы'", self.page)
        self.CHANGE_RESOURCES_BTN = Element(".ant-drawer-content[role=dialog] div[id*='panel-resources'] button:nth-child(2)", "Кнопка 'Замена ресурса'", self.page)
        self.RESERVE_RESOURCES_LOADER = Element(".ant-form .ant-spin-dot", "Лоадер во время бронирования ресурсов", self.page)
        self.ICCID = Element("(//div[contains(@id, 'panel-resources')] //p)[4]", "ICCID SIM-карты", self.page)
        self.PHONE_NUMBER = Element("(//div[contains(@id, 'panel-resources')] //p)[8]", "Номер телефона", self.page)

        self.CANCEL_BUTTON = Element("(//button[@id='_cancel-button'])[1]", "Кнопка Отмены на форме редактирования", self.page)

    def auto_reserve_phone_number_resources(self) -> str:
        self.RESERVE_RESOURCES_BTN.click()
        self.RESERVE_RESOURCES_LOADER.not_to_be_visible()
        self.ICCID.not_to_contain_text("—")
        self.PHONE_NUMBER.not_to_contain_text("—")
        return self.PHONE_NUMBER.text

class ChangeResourcesForm:
    """Форма 'Замена ресурса'"""

    def __init__(self, page: Page):
        self.page = page

        self.FORM = Element("(//*[contains(@class, 'ant-drawer-content')][@role='dialog'])[2]",
                            "Форма 'Замена ресурса'", self.page)
        self.TITLE = Element("(//*[contains(@class, 'ant-drawer-title')] //h3)[2]", "Заголовок формы", self.page)
        self.SUBTITLE = Element(".ant-drawer-title p", "Подзаголовок формы", self.page)
        self.NUMBERS = ElementsList(
            "(//*[contains(@class, 'ant-drawer-content')][@role='dialog'])[2] //*[@class='ant-drawer-body'] //p",
            "Доступные номера телефонов", self.page)
        self.INNER_ACCEPT_BTN = Element("(//button[@id='_accept-button'])[2]", "Внутренняя кнопка 'Выбрать'", self.page)

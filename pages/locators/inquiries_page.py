from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import Element, Select, ElementsList


class InquiriesPage(BaseElements):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.CLIENT = Element("//a[contains(@href, 'overview')]/span", "Клиент", self.page)
        self.INQUIRY_ID = Element("//a[contains(@href, 'inquiries/')]/span", "Номер заявки", self.page)
        self.INQUIRY_NAME = Element("//a[contains(@href, 'customer-hierarchy-management')]/..//h2", "Название заявки", self.page)
        self.INQUIRY_STATUS = Element("//div[@display='inline-block']/p", "Статус заявки", self.page)

        self.ACTIVE_STEP_TAB = Element(".ant-tabs-tab-active", "Вкладка 'Активный шаг'",
                                       self.page)
        self.LOCATOR_SALE = Element(".platform-empty-box-container", "Элемент о текущих продуктах",
                                    self.page)
        self.LOAD_SPIN_FIRST = Element(".ant-spin-dot", "Лоадер", self.page)
        self.LOAD_SPIN_SECOND = Element('[class*="ant-spin ant-spin-spin"]', "Лоадер второй", self.page)

        self.NEXT_STEP_BTN = Element("//a[contains(@href, 'customer-hierarchy-management')]/..//button[1]", "Кнопка 'Далее'", self.page)
        self.MORE_BTN = Select("//a[contains(@href, 'customer-hierarchy-management')]/..//button[2]", "Кнопка 'Еще'", self.page)

        self.ADD_SALE_BTN = Element("#add", "Кнопка 'Добавить'", self.page)
        self.REFRESH_BTN = Element("#refresh", "Кнопка 'Обновить'", self.page)
        self.CHECK_CONFIGURATION_BTN = Element("#checkConfiguration", "Проверить конфигурацию", self.page)
        self.CHECK_TECHNICAL_FEASIBILITY_BTN = Element("#checkTechnicalFeasibility", "Проверить техническую возможность", self.page)
        self.PRODUCT_CHECK_STATUS = Element("#rc-tabs-4-panel-0 >div >div >div:nth-child(3) p", "Статус проверки продукта", self.page) # требует дата атрибута от фронтов

        self.ADDED_PRODUCT = ElementsList("(//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab'])", "Добавленные продукты", self.page)
        self.ADDED_PRODUCT_EDIT_BTN = ElementsList("((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']) //button)[2]", "Кнопка 'Редактировать'", self.page)
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT = ElementsList("((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab'])) /.. //div [p[.='Разовый платёж']]/div", "'Разовый платёж' продукта", self.page)
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE = ElementsList("((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']))/.. //div [p[.='Абонентская плата']]/div", "'Абонентская плата' продукта", self.page)

        self.TOTAL_ONE_TIME_PAYMENT = Element("//*[.='Итого']/.. //div [p[.='Разовый платёж']]/div", "Итого 'Разовый платёж'", self.page) # требует дата атрибута от фронтов
        self.TOTAL_SUBSCRIPTION_FEE = Element("//*[.='Итого']/.. //div [p[.='Абонентская плата']]/div", "Итого 'Абонентская плата'", self.page) # требует дата атрибута от фронтов

        self.PRODUCT_INFO_STATUS = Element(".platform-empty-box__container", "Информация о продукте", self.page)
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


class ProductEditForm(DynamicForms):
    """Форма редактирования продукта"""

    def __init__(self, page: Page):
        super().__init__(page)

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

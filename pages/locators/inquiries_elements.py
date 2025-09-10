from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.locators.dynamic_form_elements import DynamicForms
from pages.locators.select_product_offers_form import SelectProductOffersForm
from pages.ui_elements import Dropdown, Element, ElementsList, RadioOrCheckboxBlock, Select


class InquiriesElements(BaseElements):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.product_offer_form = SelectProductOffersForm(page)

        self.CLIENT = Element(
            "//a[contains(@class, 'platform-text-link') and contains(@href, 'overview')]", "Клиент", self.page
        )
        self.INQUIRY_ID = Element("//a[contains(@href, 'inquiries/')]", "Номер заявки", self.page)
        self.INQUIRY_NAME = Element(
            "//a[contains(@href, 'customer-hierarchy-management')]/..//h2", "Название заявки", self.page
        )
        self.INQUIRY_STATUS = Element("//div[@display='inline-block'] //div", "Статус заявки", self.page)
        self.INQUIRY_STEP = Element("//h2/parent::div/parent::div/div[2]/div/p", "Шаг продажи", self.page)

        self.TABS = ElementsList("[role=tablist] [role=tab]", "Вкладки", self.page)
        self.NO_ELEMENTS = Element(".platform-empty-state-container", "Элементы не найдены", self.page)

        self.LOAD_SPIN = Element("(//div[contains(@class, 'ant-spin-spinning')])[2]", "Лоадер", self.page)
        self.LOAD_SPIN_STATUS_NAME_1 = Element(
            "//div[contains(@class, '-spin')]/following-sibling::h3", "Название статуса около Лоадера", self.page
        )
        self.LOAD_SPIN_STATUS_NAME_2 = Element(
            "//div[contains(@class, '-spin')]/div/h3", "Название статуса около Лоадера", self.page
        )
        self.LOAD_SPIN_HELP_TEXT_1 = Element(
            "//div[contains(@class, '-spin')]/following-sibling::p", "Текст подсказка для пользователя", self.page
        )
        self.LOAD_SPIN_HELP_TEXT_2 = Element(
            "//div[contains(@class, '-spin')]/div/p", "Текст подсказка для пользователя", self.page
        )
        self.LOAD_SPIN_FIRST = Element("(//*[contains(@class, '-spin-dot')])[1]", "Лоадер", self.page)
        self.LOAD_SPIN_SECOND = Element('[class*="ant-spin ant-spin-spin"]', "Лоадер второй", self.page)
        self.LOAD_SPIN_THIRD = Element(
            '(//div[contains(@class, "ant-spin ant-spin-spinning")])[1]', "Лоадер третий", self.page
        )

        self.NEXT_STEP_BTN = Element("button:has([data-icon=KeyboardArrowRight])", "Кнопка 'Далее'", self.page)
        self.AUTO_AGREEMENT_BTN = Element(
            "[data-menu-id*=AUTO_CREATE_AGR_ACC]", "Кнопка 'Автоматическое управление Договором/ДС и ЛС'", self.page
        )
        self.COMMERCIAL_OFFER_BTN = Element(
            "[data-menu-id*=COMMERCIAL_OFFER]", "Кнопка 'Формирование и согласование документа КП'", self.page
        )
        self.NO_TRANSITION_FOUND = Element("[data-menu-id*=notfound]", "Кнопка 'Переходы не найдены'", self.page)
        self.LEFT_ARROW_BTN = Element(
            "button[class*=dropdown-trigger]:has([data-icon=KeyboardArrowLeft])", "Кнопка 'Стрелка влево'", self.page
        )
        self.RIGHT_ARROW_BTN = Dropdown(
            "button[class*=dropdown-trigger]:has([data-icon=KeyboardArrowRight])", "Кнопка 'Стрелка вправо'", self.page
        )
        self.MORE_BTN = Select(
            "//a[contains(@href, 'customer-hierarchy-management')]/..//button[2]", "Кнопка 'Еще'", self.page
        )
        self.CLOSE_INQUIRY_BTN = Element(
            "*:has(>a[href*=customer-hierarchy-management]) button:not([class*=btn-icon]):not([class*=dropdown-trigger])",
            "Кнопка 'Закрыть заявку'",
            self.page,
        )

        self.STEP_TITLE = Element("[class*=tabs-content] h2", "Название шага", self.page)
        self.ADD_SALE_BTN = Element("#add", "Кнопка 'Добавить'", self.page)
        self.REFRESH_BTN = Element("#refresh", "Кнопка 'Обновить'", self.page)
        self.CHECK_CONFIGURATION_BTN = Element("#checkConfiguration", "Проверить конфигурацию", self.page)
        self.CHECK_TECHNICAL_FEASIBILITY_BTN = Element(
            "#checkTechnicalFeasibility", "Проверить техническую возможность", self.page
        )
        self.PRODUCT_CHECK_STATUS = ElementsList(
            "//*[contains(@class, 'platform-attention-label')] //*[contains(@class, 'collapse-header-text')]",
            "Статус проверки продукта",
            self.page,
        )

        # ACTIVE_STEP_TAB
        self.SCROLLABLE_PRODUCT_BLOCK = Element(
            "[class*=tabs-tabpane] .platform-scrollable:nth-child(2)",
            "Блок продуктов, который можно скролить",
            self.page,
        )
        self.ADDED_PRODUCT = ElementsList(
            "//div[contains(@class, 'collapse-expand-icon')]/../..//div[contains(@class, 'collapse-borderless')]",
            "Добавленные продукты",
            self.page,
        )
        self.ADDED_BUNDLE = ElementsList(
            "[class*=collapse-content-box] > [class*=collapse]",
            "Добавленные бандлы",
            self.page,
        )
        self.ADDED_MONOPRODUCT = ElementsList(
            "[class*=collapse-content-box] > :not([class*=collapse]) > div:has([data-icon=Add])",
            "Добавленные монопродукты",
            self.page,
        )
        self.ADDED_OPTION = ElementsList(
            "[class*=collapse-content-box] > :not([class*=collapse]) [class*=collapse-content-box] > div > div",
            "Добавленные опции",
            self.page,
        )
        self.ADDED_BUNDLE_NAMES = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/*[contains(@class, 'collapse')]/div[1]/div[1] //button/../div/p",
            "Названия бандлов",
            self.page,
        )
        self.ADDED_PRODUCT_NAMES = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/div[not(contains(@class, 'collapse'))]/div //button/../div/p",
            "Названия продуктов",
            self.page,
        )
        self.ADDED_PRODUCT_ADD_OPTION_BTN = ElementsList(
            "[class*=collapse-content-box] button:has([data-icon=Add])", "Кнопка 'Добавить опцию'", self.page
        )
        self.ADDED_PRODUCT_EDIT_BTN = ElementsList("button:has([data-icon=Edit])", "Кнопка 'Редактировать'", self.page)
        self.ADDED_PRODUCT_VISIBLE_BTN = ElementsList(
            "button:has([data-icon=Visibility])", "Кнопка 'Просмотр'", self.page
        )
        self.ADDED_PRODUCT_MENU_BTN = ElementsList(
            "//div[contains(@class, 'collapse-borderless')] //div[2] //div[2] //button[contains(@class, 'dropdown-trigger')]",
            "Три точки у добавленного монопродукта",
            self.page,
        )
        self.COPY_BTN = Element("[data-menu-id*=copy]", "Кнопка 'Копировать' монопродукт", self.page)
        self.ADDED_PRODUCT_NOT_FILLED_CHARS_BTN = ElementsList(
            "//*[@data-icon='Error']/..", "Кнопка 'Не заполнены характеристики'", self.page
        )
        self.ADDED_PRODUCT_INTERACTION_BTN = ElementsList(
            "((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']) //button)",
            "Кнопка 'Взаимодействия с продуктом'",
            self.page,
        )
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "//div[contains(@class, 'collapse-content-box')] //span[contains(@class, 'collapse-header-text')] //div[contains(@style, 'justify-items')] /div[2] /div[1]/div/p",
            "'Разовый платёж' продукта",
            self.page,
        )
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE = ElementsList(
            "//div[contains(@class, 'collapse-content-box')] //span[contains(@class, 'collapse-header-text')] //div[contains(@style, 'justify-items')] /div[3] //div[1]/div/p",
            "'Абонентская плата' продукта",
            self.page,
        )
        self.ADDED_BUNDLE_ONE_TIME_PAYMENT = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/*[contains(@class, 'collapse')]/div[1]/div[1] //div[contains(@style, 'justify-items')]/div[2]/div/div/p[1]",
            "'Разовый платёж' бандл продукта",
            self.page,
        )
        self.ADDED_BUNDLE_SUBSCRIPTION_FEE = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/*[contains(@class, 'collapse')]/div[1]/div[1] //div[contains(@style, 'justify-items')]/div[3]/div/div/p[1]",
            "'Абонентская плата' бандл продукта",
            self.page,
        )
        self.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/div[not(contains(@class, 'collapse'))] //div[contains(@style, 'justify-items')]/div[2]/div/div/p[1]",
            "'Разовый платёж' бандл продукта",
            self.page,
        )
        self.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/div[not(contains(@class, 'collapse'))] //div[contains(@style, 'justify-items')]/div[3]/div/div/p[1]",
            "'Абонентская плата' бандл продукта",
            self.page,
        )

        self.TOTAL_ONE_TIME_PAYMENT = Element(
            "//*[.='Итого']/.. //div [p[.='Разовый платёж']]/../div/div/p", "Итого 'Разовый платёж'", self.page
        )  # требует дата атрибута от фронтов
        self.TOTAL_SUBSCRIPTION_FEE = Element(
            "//*[.='Итого']/.. //div [p[.='Абонентская плата']]/../div/div/p", "Итого 'Абонентская плата'", self.page
        )  # требует дата атрибута от фронтов

        self.PRODUCT_INFO_STATUS = Element(".platform-empty-state-container", "Информация о продукте", self.page)
        self.CHECK_CONFIGURATION_BTN = Element('[id="checkConfiguration"]', "Кнопка 'Проверить конфигурацию'", self.page)
        self.SUCCESS_SETUP = Element("[id*='-panel-0'] > div > div", "Уведомление об успешной настройке", self.page)
        self.AUTOMATIC_CREATE_CONTRACT_BTN = Element(
            '[data-menu-id*="AUTO_CREATE_AGR_ACC"]', "Кнопка 'Автоматическое создание контракта'", self.page
        )
        self.SUCCESS_COMPLITED = Element(
            '[role="tabpanel"] > div > div:has([src*=success])', "Уведомление 'Успешно выполнено'", self.page
        )
        self.PRODUCT_PROFILE_BTN = Element(
            '[role="tabpanel"] [type="button"]', "Кнопка 'Перейти в продуктовый профиль'", self.page
        )
        self.CHOICE_CONTRACT_BTN = Element(
            "//button[.='Выбрать договор']", "Выбрать договор", self.page
        )  # требует дата атрибута от фронтов

        self.ADD_CONTRACT_BTN = Element("button:has([data-icon=Add])", "Кнопка 'Добавить договор'", self.page)
        self.CONTRACTS = ElementsList("[class*=table-tbody] tr", "Договора", self.page)
        self.CONTRACTS_ID = ElementsList("[class*=table-tbody] tr > td:nth-child(1) ", "Номер договора", self.page)
        self.CONTRACT_INFO = Element(
            "//div[contains(@class, 'platform-table')]/div/div[1]/div/div/p[1]", "Информация о договоре", self.page
        )
        self.CHOSEN_CONTRACT_INFO = Element(
            "//div[contains(@class, 'platform-table')]/div/div[1]/div/div/p[2]",
            "Дата и номер выбранного договора",
            self.page,
        )

        self.ERROR_TEXT = Element("(//div[@role='tabpanel']//p[@color='interface15'])[1]", "Текст ошибки", self.page)

        self.ADD_ACCOUNT_BTN = Element(
            ".platform-toolbar >div:nth-child(1) button:has([data-icon=Add])", "Кнопка 'Создать Лицевой счет'", self.page
        )
        self.ACCOUNT_NUMBER = ElementsList(
            "//*[contains(@class, 'platform-custom-list-extra-tools')]/.. //div[not(@class)] //p[not(@color)]",
            "Номер ЛС",
            self.page,
        )
        self.PRODUCT_COUNT_ON_ACCOUNT = ElementsList(
            "//*[@role='tabpanel'] //*[contains(@class, 'platform-custom-list-extra-tools')]/.. //div[not(@class)]/div/div[2]",
            "Количество элементов ЛС",
            self.page,
        )
        self.DISTRIBUTE_RADIOBUTTON = RadioOrCheckboxBlock(
            "[class*=radio-group]", "Переключатель нераспределенных/распределенных продуктов", self.page
        )
        self.ADDRESSES_ON_ACCOUNT = ElementsList("[role=button][aria-disabled=false]", "Адрес ЛС", self.page)
        self.ADDRESSES_ON_ACCOUNT_CHECKBOX = ElementsList(
            "[role=button][aria-disabled=false] input", "Чекбокс адреса ЛС", self.page
        )

        self.SAVE_DISTRIBUTION_BTN = Element(
            "//button[.='Сохранить распределение']", "Кнопка сохранить распределение", self.page
        )  # требует дата атрибута от фронтов

        self.AGREEMENT = ElementsList("[role='tabpanel'] [class*=table-row]", "Договор/Доп. соглашение", self.page)

        # ORDER_ITEMS_TAB
        self.PRODUCTS = ElementsList(
            "div[class*='collapse-content-box'] div[class*='collapse-header']", "Продукты", self.page
        )
        self.PRODUCTS_NAME = ElementsList(
            "//div[contains(@class, 'collapse-content-box')] //div[contains(@class, 'collapse-header')] //span/div/div[2]/div/div/div/p",
            "Название продукта",
            self.page,
        )
        self.MONOPRODUCT_NAMES = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1]/span/div/div[2]/div[1]/div/p",
            "Название монопродукта",
            self.page,
        )
        self.PRODUCTS_STATUS = ElementsList(
            "(//div[@role='tabpanel'] //div[contains(@class, 'platform-grid-container')])[3]/div[1]/div[2]/div/div[2]/p[2]",
            "Статус продукта",
            self.page,
        )
        self.MONOPRODUCT_SUBSCRIBERS = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[2]/div[2]/div[1]/div/div[1]/div[1]/div",
            "Поле 'Абонент' монопродукта",
            self.page,
        )
        self.PRODUCTS_CONTRACT_NUM = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[2]/div[2]/div[1]/div/div[1]/div[last() - 1] //a",
            "Номер договора",
            self.page,
        )
        self.PRODUCTS_PERSONAL_ACCOUNT_NUM = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[2]/div[2]/div[1]/div/div[1]/div[last()] //a",
            "Номер лицевого счета",
            self.page,
        )
        self.PRODUCTS_SUBSCRIPTION_FEE = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[3] //p/../div/p",
            "Абонентская плата",
            self.page,
        )
        self.PERSONAL_ACCOUNT_OPTION_ICON = ElementsList(
            ".platform-grid-container:nth-child(2) span:nth-child(2) svg",
            "Иконка учета опции на персональном счете",
            self.page,
        )

        # SALE_CARD_TAB
        self.DATA_SALE = Element(".ant-tabs-tabpane-active > div > div", "Информация по продаже", self.page)
        self.SALE_AGREEMENT = Element(
            "[data-testid=attribute-saleAgreement] p:nth-child(2)", "Договор указанный при создании заявки", self.page
        )
        self.SALE_ACCOUNT = Element(
            "[data-testid=attribute-saleAccount] p:nth-child(2)", "ЛС указанный при создании заявки", self.page
        )
        self.SALE_NEED_SPD = Element(
            "[data-testid=attribute-needSPD] p:nth-child(2)",
            "Параметр 'Заказ на комплекты РПД' указанный при создании заявки",
            self.page,
        )
        self.SALE_ADD_AGREEMENT_ADD = Element(
            "[data-testid=attribute-saleAddAgreementAdd] p:nth-child(2)",
            "Параметр 'Формирование договора ДС' указанный при создании заявки",
            self.page,
        )
        self.CLOSE_REASON = Element(
            "[data-testid='attribute-closeReason'] p:nth-child(2)", "Причина закрытия продажи", self.page
        )

        # CONTACT_INFO_TAB
        self.CONTACT_EDIT_BTN = Element("[data-icon=Edit]", "Кнопка 'Редактировать'", self.page)

        self.CONTACT_CLIENT = Element("[data-testid=attribute-customerName] a", "Клиент", self.page)
        self.CONTACT_PERSON = Element(
            "[data-testid=attribute-linkedPerson] p:nth-child(2)", "Контактное лицо", self.page
        )
        self.CONTACT_EMAIL = Element("[data-testid=attribute-email] p:nth-child(2)", "Предпочтительный email", self.page)
        self.CONTACT_PHONE = Element(
            "[data-testid=attribute-phone] p:nth-child(2)", "Предпочтительный телефон", self.page
        )

        self.CONTRACT_NUMBER = Element("[data-testid*=attribute-AGREEMENT] div", "Номер договора", self.page)
        self.CONTRACT_STATUS = Element("[data-testid=attribute-status] p:nth-child(2)", "Статус договора", self.page)

        # CURRENT_STATE_TAB
        self.PROCESSING_STEP = ElementsList(
            "[class*=collapse-item] [class*=tree-node-content]", "Шаг обработки заявки", self.page
        )
        # PROCESSING_HISTORY
        self.HISTORY_STEPS = ElementsList(".platform-scrollable > div > div > div:not([class])", "Шаги", self.page)
        self.STEP_PROCESSES = ElementsList(
            "//div[contains(@class, 'platform-scrollable')] //h4/../following-sibling::div /div",
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

        self.TECHNICAL_OFFERS = ElementsList("#tech-requests [class*=table-row]", "Заказы", self.page)
        self.TECHNICAL_OFFERS_ID = ElementsList(
            "#tech-requests [class*=table-row] > div:nth-child(1)", "Номер заказа", self.page
        )
        self.TECHNICAL_OFFERS_ACTION = ElementsList(
            "#tech-requests [class*=table-row] > div:nth-child(3)", "Статус заказа", self.page
        )

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

        self.AGREE_BTN = Element("(//span[@data-icon='CheckCircle']) [1]", 'Кнопка "Согласовать"', self.page)

        # DOCUMENTS SIGN STEP
        # TABLE
        self.DOCUMENTS_LIST = ElementsList("//div[contains(@class, 'table-tbody')] //tr", "Список документов", self.page)
        self.AGREEMENT_FLAG = ElementsList(
            "//tr[contains(@class,'table-row')] //span[@data-icon='CheckCircle']",
            "Кружок согласования документа",
            self.page,
        )
        self.AGREE_STATUS = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[1]", "Статус согласования документа", self.page
        )
        self.DOCUMENT_TYPE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[2]", "Статус согласования документа", self.page
        )
        self.FILE_NAME = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[3]", "Статус согласования документа", self.page
        )
        self.DOCUMENT_STATUS = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[4]", "Статус согласования документа", self.page
        )
        self.DELIVERY_TYPE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[5]", "Статус согласования документа", self.page
        )
        self.EMAIL = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[6]", "Статус согласования документа", self.page
        )
        self.FILE_TYPE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[7]", "Статус согласования документа", self.page
        )
        self.FILE_FROM = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[8]", "Статус согласования документа", self.page
        )
        self.CREATE_DATE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[9]", "Статус согласования документа", self.page
        )
        self.DESCRIPTION = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[10]", "Статус согласования документа", self.page
        )


class ProductEditForm(DynamicForms):
    """Форма редактирования продукта"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.VOLUMES_TAB = Element("[data-node-key=volumes]", "Таб 'Объемы'", self.page)
        self.PRICE_TAB = Element("[data-node-key=prices]", "Таб 'Цены'", self.page)
        self.SPECIFICATION_TAB = Element("[data-node-key=characteristics]", "Таб 'Характеристики'", self.page)
        self.SERVICES_TAB = Element("[data-node-key=services]", "Таб 'Сервисы'", self.page)
        self.RESOURCES_TAB = Element("[data-node-key=resources]", "Таб 'Ресурсы'", self.page)
        self.RESOURCES_TAB_IN_CASE_ONLY_PHONE = Element(
            "[class*=-drawer-content][role=dialog] [class*=-tabs-tab]:nth-of-type(3)", "Таб 'Ресурсы'", self.page
        )

        # VOLUMES_TAB
        self.VOLUMES = ElementsList(
            "[class*=-drawer-content][role=dialog] div[id*='panel-volumes']", "Объемы", self.page
        )

        # SPECIFICATION_TAB
        self.SPECIFICATION = ElementsList(
            "[class*=-drawer-content][role=dialog] div[id*='panel-characteristics']", "Характеристики", self.page
        )
        self.NUMBER_COLOR = Element(
            "[id*=panel-characteristics] div:nth-child(4) p:nth-child(2)", "Цвет номера", self.page
        )
        self.SPECIFICATION_ERROR_ICON = Element(
            "[data-node-key='characteristics'] span", "Восклицательный знак около таба 'Характеристики'", self.page
        )
        self.TEST_CHARC = Element(
            "[class*=-drawer-content][role=dialog] div[id*='panel-characteristics'] > div > div:nth-of-type(4) input",
            "Характеристика для тестирования",
            self.page,
        )

        # SERVICES_TAB
        self.SERVICES = ElementsList(
            "[class*=-drawer-content][role=dialog] [class*=-collapse-item]", "Сервисы", self.page
        )

        self.COLOR_NUMBER_FORM = Select(".ant-select-selector", "Форма выбора цвета номера", self.page)
        self.BOOK_RESOURCES = Element(
            "[id*='-panel-resources'] > div > :nth-child(1) [type='button']", "Кнопка 'Забронировать ресурсы'", self.page
        )

        # RESOURCES_TAB
        self.RESOURCES = ElementsList(
            "[class*=-drawer-content][role=dialog] div[id*='panel-resources']", "Ресурсы", self.page
        )
        self.RESERVE_RESOURCES_BTN = Element(
            "[class*=-drawer-content][role=dialog] div[id*='panel-resources'] button:nth-child(1)",
            "Кнопка 'Забронировать'",
            self.page,
        )
        self.RESERVE_RESOURCES_SELECT = Dropdown(
            "[id*=panel-resources] button[class*=dropdown-trigger]", "Выпадающее меню 'Забронировать'", self.page
        )
        self.CHANGE_ICCID_BTN = Element(
            "//p[contains(text(), 'SIM')]/../.. //span[@data-icon='SwapHoriz']",
            "Кнопка 'Замена ресурса' ICCID",
            self.page,
        )
        self.CHANGE_NUMBER_BTN = Element(
            "//p[contains(text(), 'Телефонный номер')]/../.. //span[@data-icon='SwapHoriz']",
            "Кнопка 'Замена ресурса' номер телефона",
            self.page,
        )  # требует дата атрибута от фронтов
        self.RESERVE_RESOURCES_LOADER = Element(
            "(//*[contains(@class, 'form')] //*[contains(@class, 'spin-dot')])[1]",
            "Лоадер во время бронирования ресурсов",
            self.page,
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


class ReserveResourcesForm:
    """Форма бронирования ресурсов (SIM-карты, номера телефона)"""

    def __init__(self, page: Page):
        self.page = page

        self.TITLE = Element("(//*[contains(@class, 'drawer-title')] //h3)[2]", "Заголовок формы", self.page)
        self.RESOURCE_INFO = ElementsList(
            "(//*[contains(@class, 'drawer-title')])[2]/div/div/div", "Информация о ресурсе", self.page
        )
        self.INFO_MESSAGE = Element(
            "(//*[contains(@class, 'drawer-body')])[2] //*[contains(@class, 'platform-attention-label')]",
            "Информационное сообщение",
            self.page,
        )
        self.SEARCH_PARAMETERS_NOT_SET = Element(
            "[class*=drawer-body] .platform-empty-state-container", "Не заданы условия поиска", self.page
        )
        self.CROSS_BTN = Element("(//button[@aria-label='Close'])[2]", "Крестик", self.page)
        self.CANCEL_BTN = Element("(//*[@id='_cancel-button'])[2]", "Кнопка 'Отмена'", self.page)
        self.BOOK_BTN = Element("(//*[@id='_accept-button'])[last()]", "Кнопка 'Забронировать'", self.page)

        # SIM RESERVE FILTER ELEMENTS
        self.SIM_TYPE = RadioOrCheckboxBlock(
            "(//*[contains(@class, 'drawer-body')])[2] //*[contains(@class, 'radio-group')]",
            "Выбор типа SIM-карты",
            self.page,
        )
        self.SEARCH_TYPE = Select("input[id*=parameters_searchType]", "Поле 'Тип поиска'", self.page)

        # NUMBER RESERVE FILTER ELEMENTS
        self.STANDARD_INPUT = Select(
            "//*[contains(@id, 'parameters_standard')]/../../../*[contains(@class, 'select-selection-wrap')]",
            "Поле 'Стандарт'",
            self.page,
        )
        self.NUMBERING_TYPE = Select("input[id*=parameters_numberingType]", "Поле 'Тип нумерации'", self.page)
        self.NUMBER_CLASS = Select("input[id*=parameters_numberClass]", "Поле 'Класс номера'", self.page)
        self.FREE_FOR = Element("input[id*=parameters_freeFor]", "Поле 'Свободные'", self.page)

        # COMMON FILTER ELEMENTS
        self.ONLY_CHOOSE_RADIOBUTTON = Element(
            "[class*=drawer-content] button[role=switch]", "Кнопка 'Только выбранные'", self.page
        )
        self.ONLY_CHOOSE_TEXT = Element("[class*=drawer-content] label[for=switch]", "Только выбранные", self.page)
        self.MASK_INPUT = Element("input[id*=parameters_mask]", "Поле 'Маска'", self.page)
        self.RANGE_LEFT_INPUT = Element(
            "span:nth-child(1) input[id*=parameters_range]", "Левая граница поля 'Диапазон'", self.page
        )
        self.RANGE_RIGHT_INPUT = Element(
            "input[id*=parameters_range_right]", "Правая граница поля 'Диапазон'", self.page
        )
        self.RESOURCE_COUNT = Element(
            "input[id*=parameters_resourceCount]", "Значение поля 'Количество ресурсов'", self.page
        )
        self.SWITCH = Select(
            "//input[contains(@id,'parameters_switch')] //ancestor::div[contains(@class,'select-selector')]",
            "Выпадающее меню 'Коммутатор'",
            self.page,
        )
        self.REGION = Element("input[id*=parameters_region]", "Значение поля 'Регион'", self.page)
        self.CLEAR_BUTTON = Element(
            "(//*[contains(@class, 'platform-dynamic-form-bottom-toolbar-area')] //button)[1]",
            "Кнопка 'Сбросить'",
            self.page,
        )
        self.SEARCH_BUTTON = Element(
            "(//*[contains(@class, 'platform-dynamic-form-bottom-toolbar-area')] //button)[2]",
            "Кнопка 'Найти'",
            self.page,
        )

        # COMMON TABEL ELEMENTS
        self.REFRESH_BTN = Element("(//*[contains(@id, 'table')] //button)[1]", "Кнопка 'Обновить'", self.page)
        self.TABLE_HEADER = ElementsList(".table-header-column", "Заголовки таблицы ресурсов", self.page)
        self.NO_RECORDS_FOUND = Element("[id*=table] .platform-empty-state-container", "Записи не найдены", self.page)

        # SIM TABEL
        self.SIM_CHECKBOX = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(1)", "Чекбокс симкарты", self.page
        )
        self.SIM_ICC = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(2)", "Поле 'ICC' симкарты", self.page
        )
        self.SIM_IMSI = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(3)", "Поле 'IMSI' симкарты", self.page
        )
        self.SIM_TYPE = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(4)", "Поле 'Тип симкарты'", self.page
        )
        self.SIM_EXPIRATION_DATE = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(5)", "Поле 'Срок действия'", self.page
        )
        self.SIM_SWITCH = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(6)", "Поле 'Коммутатор'", self.page
        )

        # NUMBER TABEL
        self.NUMBER_CHECKBOX = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(1)", "Чекбокс номера телефона", self.page
        )
        self.NUMBER = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(2)", "Поле 'Номер'", self.page)
        self.NUMBER_CLASS_NAME = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(3)", "Поле 'Класс номера'", self.page
        )
        self.NUMBER_TYPE_OF_NUMBERING = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(4)", "Поле 'Тип нумерации'", self.page
        )
        self.NUMBER_SWITCH = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(5)", "Поле 'Коммутатор'", self.page
        )


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


class CloseInquiryForm(DynamicForms):
    """Форма 'Закрытие заявки'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.FORM = Element(
            "[class*=drawer-content-wrapper]:not([class*=drawer-content-wrapper-hidden]):has([class*=drawer-footer])",
            "Форма 'Закрытие заявки'",
            self.page,
        )
        self.TITLE = Element("[class*=drawer-title] h3[display=inline]", "Заголовок формы", self.page)
        self.CLOSE_REASON = Select("input#closeInquiryForm_reason", "Поле 'Причина закрытия'", self.page)


class RefundInquiryForm:
    """Форма 'Заявка на возврат средств'"""

    def __init__(self, page: Page):
        self.page = page

        self.REFUND_INQUIRY_NAME = Element(
            "//div[contains(@class, '-spin-container')]/..//h2", "Название заявки", self.page
        )
        self.REFUND_INQUIRY_STATUS = Element("//div[@display='inline-block'] //div", "Статус заявки", self.page)
        self.REFUND_PROCESSING_BTN = Element(
            "(//div[contains(@class, 'platform-root-scrollable-container')]/..//button)[1]",
            "Кнопка 'Обработка'",
            self.page,
        )
        self.REFUND_REFRESH_BTN = Element(
            "(//div[contains(@class, 'platform-root-scrollable-container')]/..//button)[2]",
            "Кнопка 'Обновить'",
            self.page,
        )
        self.REFUND_SUBMIT_PROC_BTN = Element("(//ul[@role='menu']/li)[2]", "Кнопка 'Передать в обработку'", self.page)
        self.REFUND_TAKE_IN_PROC_BTN = Element("(//ul[@role='menu']/li)[3]", "Кнопка 'Взять в обработку'", self.page)
        self.REFUND_EDIT_BTN = Element("//div[@role='tabpanel'] //button", "Кнопка 'Редактировать'", self.page)
        self.APPROVAL_STATUS_REFUND_FORM = Select(
            "input[id*=additional_values_rfdDecision]", "Поле 'Статус согласования возврата'", self.page
        )
        self.REFUND_SAVE_BTN = Element("//div[@role='tabpanel']/div/div/div/button", "Кнопка 'Сохранить'", self.page)
        self.REFUND_INQUIRY_SOLUTION_STATUS = Element(
            "(//div[@data-testid='attribute-rfdDecision']/p)[2]", "Статус решения по заявке", self.page
        )


class EditContactInfoForm(DynamicForms):
    """Форма редактирования контактных данных"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.INFO_TEXT = Element("span[class*='header-text']:has(br)", "Текс информации", self.page)
        self.CLIENT = Element("#customer", "Клиент", self.page)
        self.LINKED_PERSON = Select("#inqrLinkedPerson", "Контактное лицо", self.page)
        self.EMAIL = Select("#email", "Предпочтительный email", self.page)
        self.PHONE = Select("#phone", "Предпочтительный телефон", self.page)

import pytest

from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import AddAddress, DynamicForms
from pages.locators.nbss.select_product_offers_form import SelectProductOffersFormElements
from pages.ui_elements import Dropdown, DropdownWithId, Element, ElementsList, RadioOrCheckboxBlock, Select, SelectWithId


class InquiriesElements(BaseElements):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    @pytest.mark.cpm
    def __init__(self) -> None:
        super().__init__()
        self.product_offer_form = SelectProductOffersFormElements()
        self.add_address_form = AddAddress()

        self.CLIENT = Element("//a[contains(@class, 'platform-text-link') and contains(@href, 'overview')]", "Клиент")
        self.INQUIRY_ID = Element("//a[contains(@href, 'inquiries/')]", "Номер заявки")
        self.INQUIRY_NAME = Element("h3[class*=summary-title]", "Название заявки")
        self.INQUIRY_STATUS = Element("div:has(>h3) span[class*=tag] div", "Статус заявки")
        self.INQUIRY_STEP = Element("[class*=summary-main] p:not([color])", "Шаг продажи")

        self.TABS = ElementsList("[role=tablist] [role=tab]", "Вкладки")
        self.NO_ELEMENTS = Element(".platform-empty-state-container", "Элементы не найдены")

        self.LOAD_SPIN = Element("(//div[contains(@class, 'ant-spin-spinning')])[2]", "Лоадер")
        self.LOAD_SPIN_STATUS_NAME_1 = Element(
            "//div[contains(@class, '-spin')]/following-sibling::h3", "Название статуса около Лоадера"
        )
        self.LOAD_SPIN_STATUS_NAME_2 = Element(
            "//div[contains(@class, '-spin')]/div/h3", "Название статуса около Лоадера"
        )
        self.LOAD_SPIN_HELP_TEXT_1 = Element(
            "//div[contains(@class, '-spin')]/following-sibling::p", "Текст подсказка для пользователя"
        )
        self.LOAD_SPIN_HELP_TEXT_2 = Element(
            "//div[contains(@class, '-spin')]/div/p", "Текст подсказка для пользователя"
        )
        self.LOAD_SPIN_FIRST = Element("(//*[contains(@class, '-spin-dot')])[1]", "Лоадер")
        self.LOAD_SPIN_SECOND = Element('[class*="ant-spin ant-spin-spin"]', "Лоадер второй")
        self.LOAD_SPIN_THIRD = Element('(//div[contains(@class, "ant-spin ant-spin-spinning")])[1]', "Лоадер третий")

        self.NEXT_STEP_BTN = Element("button:has([data-icon=KeyboardArrowRight])", "Кнопка 'Далее'")
        self.DOWNLOAD_DOCUMENT = Element(
            "(//button[.//span[@data-icon='FileDownload']])[1]", "Кнопка 'Скачать документ'"
        )
        self.UPLOAD_DOCUMENT_BTN = Element(
            '(//button[.//span[@data-icon="FileUpload"]])[1]', "Кнопка 'Загрузить Документ'"
        )
        self.UPLOAD_FILE = Element('input[type="file"][multiple]', "Место для загрузки файла")
        self.SELECT_TYPE_UPLOAD_DOCUMENT = Select(
            "//div[contains(@class,'platform-select')][.//input[@id='documentTypeId']]", "Выбор 'Тип Документа'"
        )
        self.DESCRIPTION_UPLOAD_DOCUMENT = Element("textarea#description", "Поле 'Описание'")
        self.UPLOAD_BTN = Element("#_accept-button", "Внутренняя кнопка 'Загрузить'")
        self.APPROVE_BTN = Element('button[title="Согласовать"]', "Кнопка 'Согласовать'")
        self.AUTO_AGREEMENT_BTN = Element(
            "[data-menu-id*=AUTO_CREATE_AGR_ACC]", "Кнопка 'Автоматическое управление Договором/ДС и ЛС'"
        )
        self.COMMERCIAL_OFFER_BTN = Element(
            "[data-menu-id*=COMMERCIAL_OFFER]", "Кнопка 'Формирование и согласование документа КП'"
        )
        self.NO_TRANSITION_FOUND = Element("[data-menu-id*=notfound]", "Кнопка 'Переходы не найдены'")
        self.LEFT_ARROW_BTN = Element(
            "button[class*=dropdown-trigger]:has([data-icon=KeyboardArrowLeft])", "Кнопка 'Стрелка влево'"
        )
        self.RIGHT_ARROW_BTN = Dropdown(
            "button[class*=dropdown-trigger]:has([data-icon=KeyboardArrowRight])", "Кнопка 'Стрелка вправо'"
        )
        self.MORE_BTN = Select("//a[contains(@href, 'customer-hierarchy-management')]/..//button[2]", "Кнопка 'Еще'")
        self.CLOSE_INQUIRY_BTN = Element(
            "//span[contains(text(),'Закрыть заявку')]",
            "Кнопка 'Закрыть заявку'",
        )

        self.STEP_TITLE = Element(":has(>[class$=toolbar]) > :has([data-icon=InfoOutline]) p", "Название шага")
        self.ADD_SALE_BTN = Element(
            "div[class$=platform-toolbar] > div:not([style]) [id*=commercial-order][id*=add]", "Кнопка 'Добавить'"
        )
        self.REFRESH_BTN = Element("div[class$=platform-toolbar] > div:not([style]) [id$=refresh]", "Кнопка 'Обновить'")
        self.CHECK_CONFIGURATION_BTN = Element(
            "div[class$=platform-toolbar] > div:not([style]) button[id*=checkConfiguration]", "Проверить конфигурацию"
        )
        self.ASSIGN_DISCOUNTS_BTN = Element(
            "div[class$=platform-toolbar] > div:not([style]) #add_discount",
            "Кнопка 'Назначить скидки'",
        )
        self.CHECK_TECHNICAL_FEASIBILITY_BTN = Element(
            "div[class$=platform-toolbar] > div:not([style]) #checkTechnicalFeasibility",
            "Проверить техническую возможность",
        )
        self.PRODUCT_CHECK_STATUS = ElementsList(
            "//*[contains(@class, 'platform-attention-label')] //*[contains(@class, 'collapse-header-text')]",
            "Статус проверки продукта",
        )
        self.REFRESH_BTN_INQUIRY = Element("(//span[@data-icon='Refresh'])[1]", "Кнопка 'Обновить' у заявки")

        self.EXECUTION_DATE_EDIT_BTN = Element(
            "div[class$=platform-toolbar] > div:not([style]) [id*=commercial-order][id*=edit][id$=date]",
            "Кнопка 'Редактировать дату'",
        )
        self.EXECUTION_DATE_PLAN_BLOCK = Element(
            "div[class$=platform-toolbar] > div:not([style]) [data-testid*=CommercialOrder]:has(p)",
            "Блок с датой выполнения заказа ('Планируемая дата DD.MM.YYYY')",
        )

        # ACTIVE_STEP_TAB
        self.SCROLLABLE_PRODUCT_BLOCK = Element(
            "[class*=content-active] [class$=platform-scrollable]",
            "Блок продуктов, который можно скролить",
        )
        self.ADDED_PRODUCT = ElementsList(
            "//div[contains(@class, 'collapse-expand-icon')]/../..//div[contains(@class, 'collapse-borderless')]",
            "Добавленные продукты",
        )
        self.ADDED_BUNDLE = ElementsList(
            "[class*=collapse-content-box] > [class*=collapse]",
            "Добавленные бандлы",
        )
        self.ADDED_MONOPRODUCT = ElementsList(
            "[class*=collapse-content-box] > :not([class*=collapse]) > div:has([data-icon=Add])",
            "Добавленные монопродукты",
        )
        self.ADDED_OPTION = ElementsList(
            "[class*=collapse-content-box] > :not([class*=collapse]) [class*=collapse-content-box] > div > div",
            "Добавленные опции",
        )
        self.ADDED_BUNDLE_NAMES = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/*[contains(@class, 'collapse')]/div[1]/div[1] //button/../div/p",
            "Названия бандлов",
        )
        self.ADDED_PRODUCT_NAMES = ElementsList(
            "[class*=product] [class*=header-title] p[data-name]",
            "Названия продуктов",
        )
        self.ADDED_PRODUCT_ADD_OPTION_BTN = ElementsList(
            "[class*=collapse-content-box] button:has([data-icon=AddCircleOutline])", "Кнопка 'Добавить опцию'"
        )
        self.PRODUCT_RESOURCES_UNFILLED_BTN = ElementsList(
            "[class*=header-title] [data-testid*=Error]", "Кнопка 'Характеристика Некорректна'"
        )
        self.ADDED_PRODUCT_VISIBLE_BTN = ElementsList("button:has([data-icon=Visibility])", "Кнопка 'Просмотр'")
        self.ADDED_PRODUCT_MENU_BTN = ElementsList(
            "button.ant-dropdown-trigger:has([data-icon='MoreVert'])",
            "Три точки у добавленного монопродукта",
        )
        self.COPY_BTN = Element("[data-menu-id*=copy]", "Кнопка 'Копировать' монопродукт")
        self.EDIT_MENU_ITEM = Element(
            "//ul[@role='menu']//li[contains(@data-menu-id, 'Edit')] | //li[@role='menuitem']//span[text()='Редактировать']/ancestor::li",
            "Пункт 'Редактировать' в меню продукта",
        )
        self.ADDED_PRODUCT_NOT_FILLED_CHARS_BTN = ElementsList(
            "span[class*=btn-icon]:has(span[data-icon=Error])", "Кнопка 'Не заполнены характеристики'"
        )
        self.ADDED_PRODUCT_INTERACTION_BTN = ElementsList(
            "((//div[@role='tablist'] //div[@role='tabpanel'] //div[@role='tab']) //button)",
            "Кнопка 'Взаимодействия с продуктом'",
        )
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "[class*=collapse-header] [data-price-type-code=FeeProdOfferingPrice] p[data-name*=paragraph], [class*=collapse-header] [data-price-type-code=FeeProdOfferingPrice] a",
            "'Разовый платёж' продукта",
        )
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT_BASE_PRICE = ElementsList(
            "[class*=collapse-header] [data-price-type-code=FeeProdOfferingPrice] p[data-name=paragraphInfo]",
            "Зачеркнутая старая цена разовой платы",
        )
        self.ADDED_PRODUCT_ONE_TIME_PAYMENT_FINAL_PRICE = ElementsList(
            "[class$=collapse-header] [data-price-type-code*=FeeProdOfferingPrice] p[data-name*=paragraphInfoMedium], [class*=collapse-header] [data-price-type-code=FeeProdOfferingPrice] a[class*=text-link]",
            "Синяя новая цена разовой платы со скидкой",
        )
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE = ElementsList(
            "[class*=collapse-header] [data-price-type-code=RecurringChargeProdOfferPriceCharge] p[data-name*=Medium]",
            "'Абонентская плата' продукта",
        )
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE_BASE_PRICE = ElementsList(
            "[class*=collapse-header] [data-price-type-code=RecurringChargeProdOfferPriceCharge] p[color=interface15]",
            "Зачеркнутая старая цена абонентской платы",
        )
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE_FINAL_PRICE = ElementsList(
            "[class$=collapse-header] [data-price-type-code=RecurringChargeProdOfferPriceCharge] p[data-name*=paragraphInfoMedium], [class$=collapse-header] [data-price-type-code=RecurringChargeProdOfferPriceCharge] a[class*=text-link]",
            "Синяя новая цена абонентской платы со скидкой",
        )
        self.ADDED_PRODUCT_SUBSCRIPTION_FEE_MORE_VERT_BTN = ElementsList(
            "//div[contains(@class,'collapse-content-box')] //span[@data-icon='MoreVert']/ancestor::button",
            "Три точки справа от цены абонентской платы",
        )
        self.ADDED_BUNDLE_ONE_TIME_PAYMENT = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/*[contains(@class, 'collapse')]/div[1]/div[1] //div[contains(@style, 'justify-items')]/div[2]/div/div/p[1]",
            "'Разовый платёж' бандл продукта",
        )
        self.ADDED_BUNDLE_SUBSCRIPTION_FEE = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/*[contains(@class, 'collapse')]/div[1]/div[1] //div[contains(@style, 'justify-items')]/div[3]/div/div/p[1]",
            "'Абонентская плата' бандл продукта",
        )
        self.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/div[not(contains(@class, 'collapse'))] //div[contains(@style, 'justify-items')]/div[2]/div/div/p[1]",
            "'Разовый платёж' бандл продукта",
        )
        self.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]/div[not(contains(@class, 'collapse'))] //div[contains(@style, 'justify-items')]/div[3]/div/div/p[1]",
            "'Абонентская плата' бандл продукта",
        )
        self.BOX_BUTTON = ElementsList("button:has([data-icon=BoxClosed])", "Кнопка 'Объемы'")
        self.TOOLTIP_VOLUMES = ElementsList(
            "[class*=tooltip-content] [data-name=paragraphInfoMedium]", "Объемы в тултипе"
        )
        self.VISIBLE_TOOLTIP = Element(
            "[class*=tooltip-placement]:not([class*=tooltip-hidden]) [class*=tooltip-inner]",
            "Раскрытая всплывающая подсказка",
        )
        self.TOTAL_ONE_TIME_PAYMENT_INFO_ICON = Element(
            ".uds-total-panel [data-price-type-code=FeeProdOfferingPrice] [data-icon=InfoOutline]",
            "Иконка 'i' у 'Итого: Разовая плата'",
        )
        self.TOTAL_SUBSCRIPTION_FEE_INFO_ICON = Element(
            ".uds-total-panel [data-price-type-code=RecurringChargeProdOfferPriceCharge] [data-icon=InfoOutline]",
            "Иконка 'i' у 'Итого: Периодическая плата'",
        )
        self.ADDED_PRODUCT_REGIONS = ElementsList(
            "[class$=collapse-header][role=button] p",
            "Регионы продуктов",
        )
        self.ADDED_PRODUCT_ADDRESSES = ElementsList(
            "div[class$=collapse-collapsible-disabled] div[class$=platform-grid-container]:has([data-icon=AddCircleOutline]) > div:not([style]) p:not([color])",
            "Адреса монопродуктов",
        )
        self.ADDED_OPTION_ADDRESSES = ElementsList(
            "div[class$=collapse-collapsible-disabled] div[class$=platform-grid-container] > div:not([style]) p:not([color])",
            "Адреса опций",
        )
        self.TOTAL_ONE_TIME_PAYMENT = Element(
            "[class*=total-panel] [data-price-type-code=FeeProdOfferingPrice] [data-name=paragraphInfoMedium]",
            "Итого 'Разовый платёж'",
        )  # требует дата атрибута от фронтов
        self.TOTAL_SUBSCRIPTION_FEE = Element(
            "[class*=total-panel] [data-price-type-code=RecurringChargeProdOfferPriceCharge] [data-name=paragraphInfoMedium]",
            "Итого 'Абонентская плата'",
        )  # требует дата атрибута от фронтов

        self.PRODUCT_INFO_STATUS = Element(".platform-empty-state-container", "Информация о продукте")
        self.SUCCESS_SETUP = Element("[id*='-panel-0'] > div > div", "Уведомление об успешной настройке")
        self.AUTOMATIC_CREATE_CONTRACT_BTN = Element(
            '[data-menu-id*="AUTO_CREATE_AGR_ACC"]', "Кнопка 'Автоматическое создание контракта'"
        )
        self.SUCCESS_COMPLITED = Element(
            '[role="tabpanel"] > div > div:has([src*=success])', "Уведомление 'Успешно выполнено'"
        )
        self.PRODUCT_PROFILE_BTN = Element('[role="tabpanel"] [type="button"]', "Кнопка 'Перейти в продуктовый профиль'")
        self.CHOICE_CONTRACT_BTN = Element(
            "//button[.='Выбрать договор']", "Выбрать договор"
        )  # требует дата атрибута от фронтов

        self.ADD_CONTRACT_BTN = Element("button:has([data-icon=Add])", "Кнопка 'Добавить договор'")
        self.CONTRACTS = ElementsList("[class*=table-tbody] tr[class*=table-row]", "Договора")
        self.CONTRACTS_ID = ElementsList("[class*=table-tbody] tr > td:nth-child(1) ", "Номер договора")
        self.CONTRACT_LINK = ElementsList("[class*=table-tbody] tr > td:nth-child(1) a", "Ссылка на договор")
        self.CONTRACT_INFO = Element(
            "//div[contains(@class, 'platform-table')]/div/div[1]/div/div/p[1]", "Информация о договоре"
        )
        self.CHOSEN_CONTRACT_INFO = Element(
            "//div[contains(@class, 'platform-table')]/div/div[1]/div/div/p[2]",
            "Дата и номер выбранного договора",
        )

        self.ERROR_TEXT = Element("(//div[@role='tabpanel']//p[@color='interface15'])[1]", "Текст ошибки")
        self.ERROR_NOTIFICATIONS = ElementsList(
            "//div[contains(@class,'ant-collapse-item')]//span[contains(@class,'ant-collapse-header-text')]",
            "Уведомления об ошибках",
        )
        self.ADD_ACCOUNT_BTN = Element(
            ".platform-toolbar >div:nth-child(1) button:has([data-icon=Add])", "Кнопка 'Создать Лицевой счет'"
        )
        self.ACCOUNT_NUMBER = ElementsList(
            "//*[contains(@class, 'platform-custom-list-extra-tools')]/.. //div[not(@class)] //p[not(@color)]",
            "Номер ЛС",
        )
        self.PRODUCT_COUNT_ON_ACCOUNT = ElementsList(
            "//*[@role='tabpanel'] //*[contains(@class, 'platform-custom-list-extra-tools')]/.. //div[not(@class)]/div/div[2]",
            "Количество элементов ЛС",
        )
        self.DISTRIBUTE_RADIOBUTTON = RadioOrCheckboxBlock(
            "[class*=radio-group]", "Переключатель нераспределенных/распределенных продуктов"
        )
        self.ADDRESSES_ON_ACCOUNT = ElementsList("[role=button][aria-disabled=false]", "Адрес ЛС")
        self.ADDRESSES_ON_ACCOUNT_CHECKBOX = ElementsList(
            "[role=button][aria-disabled=false] input", "Чекбокс адреса ЛС"
        )

        self.SAVE_DISTRIBUTION_BTN = Element(
            "//button[.='Сохранить распределение']", "Кнопка сохранить распределение"
        )  # требует дата атрибута от фронтов

        self.AGREEMENT = ElementsList("[role='tabpanel'] [class*=table-row]", "Договор/Доп. соглашение")
        self.AGREEMENT_TYPE = ElementsList("[role='tabpanel'] [class*=table-row] td:nth-child(2)", "Тип документа")

        self.ACTIVATION_DATE_CHANGE_BUTTON = ElementsList(
            "//div[@role='tabpanel']//button", "Кнопки формы шага смены даты активации"
        )
        self.ACTIVATION_DATE_CHANGE = Element("#activationDate", "Поле Дата активации")
        self.ACTIVATION_DATE_CLEAR = Element("//span[@data-icon='SmallClose']", "Очистить Дату активации")
        self.ACTIVATION_DATE_MESSAGE = Element("//div[@id='activationDate_help']", "Сообщение о некорректной дате")
        self.ACTIVATE_DATE = Element("//p[@data-name='paragraphMedium']", "Дата активации")

        self.AGREEMENT_BTN = ElementsList("//span//button[@type='button']", "Кнопка Договор")
        self.ORDER_DESCRIPTION = ElementsList(
            "//*[contains(@class, 'platform-grid')]//p[@data-name='description']/span", "Описание продукта"
        )
        self.PRICE_AFTER_PRICE_CHANGE = ElementsList("//p[@color]/following-sibling::p", "Цена продукта после изменения")
        self.EXPAND_OPTIONS = ElementsList("//span[@data-icon='SmallUncollapse']", "Развернуть опции у продукта")
        # ORDER_ITEMS_TAB
        self.PRODUCTS = ElementsList("div[class*='collapse-content-box'] div[class*='collapse-header']", "Продукты")
        self.PRODUCTS_NAME = ElementsList(
            "div[class*=product-item-title] p[data-name=paragraphInfoMedium]",
            "Название продукта",
        )
        self.MONOPRODUCT_NAMES = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1]/span/div/div[2]/div[1]/div/p",
            "Название монопродукта",
        )
        self.PRODUCTS_STATUS = ElementsList(
            "(//div[@role='tabpanel'] //div[contains(@class, 'platform-grid-container')])[3]/div[1]/div[2]/div/div[2]/p[2]",
            "Статус продукта",
        )
        self.MONOPRODUCT_SUBSCRIBERS = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[2]/div[2]/div[1]/div/div[1]/div[1]/div",
            "Поле 'Абонент' монопродукта",
        )
        self.PRODUCTS_CONTRACT_NUM = ElementsList(
            "[class*=collapse-header] [class*=agreement] a",
            "Номер договора",
        )
        self.PRODUCTS_PERSONAL_ACCOUNT_NUM = ElementsList(
            "[class*=collapse-header] [class*=account] a",
            "Номер лицевого счета",
        )
        self.PRODUCTS_SUBSCRIPTION_FEE = ElementsList(
            "//div[@role='tabpanel'] //div[@tabindex=-1] //div[3] //p/../div/p",
            "Абонентская плата",
        )
        self.PERSONAL_ACCOUNT_OPTION_ICON = ElementsList(
            ".platform-grid-container:nth-child(2) span:nth-child(2) svg",
            "Иконка учета опции на персональном счете",
        )

        # SALE_CARD_TAB
        self.DATA_SALE = Element(".ant-tabs-tabpane-active > div > div", "Информация по продаже")
        self.SALE_AGREEMENT = Element(
            "[data-testid=attribute-saleAgreement] p:nth-child(2)", "Договор указанный при создании заявки"
        )
        self.SALE_ACCOUNT = Element(
            "[data-testid=attribute-saleAccount] p:nth-child(2)", "ЛС указанный при создании заявки"
        )
        self.SALE_NEED_SPD = Element(
            "[data-testid=attribute-needSPD] p:nth-child(2)",
            "Параметр 'Заказ на комплекты РПД' указанный при создании заявки",
        )
        self.SALE_ADD_AGREEMENT_ADD = Element(
            "[data-testid=attribute-saleAddAgreementAdd] p:nth-child(2)",
            "Параметр 'Формирование договора ДС' указанный при создании заявки",
        )
        self.CLOSE_REASON = Element("[data-testid='attribute-closeReason'] p:nth-child(2)", "Причина закрытия продажи")

        # CONTACT_INFO_TAB
        self.CONTACT_EDIT_BTN = Element("[data-icon=Edit]", "Кнопка 'Редактировать'")

        self.CONTACT_CLIENT = Element("[data-testid=attribute-customerName] a", "Клиент")
        self.CONTACT_PERSON = Element("[data-testid=attribute-linkedPerson] p:nth-child(2)", "Контактное лицо")
        self.CONTACT_EMAIL = Element("[data-testid=attribute-email] p:nth-child(2)", "Предпочтительный email")
        self.CONTACT_PHONE = Element("[data-testid=attribute-phone] p:nth-child(2)", "Предпочтительный телефон")

        self.CONTRACT_NUMBER = Element("[data-testid*=attribute-AGREEMENT] div", "Номер договора")
        self.CONTRACT_STATUS = Element("[data-testid=attribute-status] p:nth-child(2)", "Статус договора")

        # OVERVIEW TERMINATE TAB
        self.INFO_TERMINATE_CONTRACT = Element(
            "[data-testid=attribute-agtrmTermAgreementInfo]", "Информация о расторгнутом договоре"
        )
        # CURRENT_STATE_TAB
        self.PROCESSING_STEP = ElementsList("[class*=collapse-item] [class*=tree-node-content]", "Шаг обработки заявки")
        # PROCESSING_HISTORY
        self.HISTORY_STEPS = ElementsList(".platform-scrollable > div > div > div:not([class])", "Шаги")
        self.STEP_PROCESSES = ElementsList(
            "//div[contains(@class, 'platform-scrollable')] //h4/../following-sibling::div /div",
            "События в шаге",
        )

        # TECHNIC_OFFERS_TAB
        self.TECHNIC_OFFER_REFRESH_BTN = Element("#techRequestGrid_control button:nth-child(1)", "Кнопка 'Обновить'")
        self.TECHNIC_OFFER_TAB_SETTINGS = Element("#techRequestGrid_control button:nth-child(2)", "Кнопка 'Настройки'")

        self.TECHNICAL_OFFERS = ElementsList("#tech-nbss [class*=table-row]", "Заказы")
        self.TECHNICAL_OFFERS_ID = ElementsList("#tech-nbss [class*=table-row] > div:nth-child(1)", "Номер заказа")
        self.TECHNICAL_OFFERS_ACTION = ElementsList("#tech-nbss [class*=table-row] > div:nth-child(3)", "Статус заказа")

        # RESOURCE_REPLACEMENT_TAB
        self.RESOURCE_REPLACEMENT_FORWARD = Element(
            "//li[contains(@data-menu-id, 'FORWARD')]", "Кнопка Передать на обработку в Замена Ресурса"
        )
        self.RESOURCE_REPLACEMENT_STATUS = Element("//p[@color='interface2']", "Статус заявки Замена ресурса")
        self.RESOURCE_REPLACEMENT_REFRESH_BTN = Element(
            "//button[@variant='default'] [2]", "Кнопка обновить в Замена ресурса"
        )
        self.RESOURCE_REPLACEMENT_APPLY_BTN = Element("//button[@variant='primary']", "Кнопка обновить в Замена ресурса")
        self.RESOURCE_REPLACEMENT_DUE_DATE_INPUT = Element(
            "//input[@id='forwardInquiryForm_dueDate']", "Поле для ввода даты обработки"
        )
        self.RESOURCE_REPLACEMENT_DUE_DATE_TODAY = Element(
            "//input[@id='forwardInquiryForm_dueDate'] //../../.. //a",
            "Кнопка сегодня в выборе даты обработки",
        )

        self.AGREE_BTN = Element("(//span[@data-icon='CheckCircle']) [1]", 'Кнопка "Согласовать"')

        # DOCUMENTS TAB
        self.DOCUMENTS_ROWS = ElementsList("div[class*=table-row]", "Строки таблицы на вкладке Документы")

        # DOCUMENTS SIGN STEP
        # TABLE
        self.AGREEMENTS_TABLE_REFRESH = Element(
            "(//button[@title]//span[@data-icon='Refresh'])[1]", "Кнопка Обновить для таблицы документов"
        )
        self.DOCUMENTS_LIST = ElementsList("div[data-body-height] [data-row-key]", "Список документов")
        # Есть скрытая копия тулбара, из-за этого пришлось цепляться за текст
        self.AGREEMENT_FLAG = ElementsList(
            "[class*=table-cell] [data-icon=CheckCircle]",
            "Кружок согласования документа",
        )
        self.AGREE_STATUS = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[1]", "Статус согласования документа"
        )
        self.DOCUMENT_TYPE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[2]", "Статус согласования документа"
        )
        self.FILE_NAME = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[3]", "Статус согласования документа"
        )
        self.DOCUMENT_STATUS = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[4]", "Статус согласования документа"
        )
        self.DELIVERY_TYPE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[5]", "Статус согласования документа"
        )
        self.EMAIL = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[6]", "Статус согласования документа"
        )
        self.FILE_TYPE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[7]", "Статус согласования документа"
        )
        self.FILE_FROM = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[8]", "Статус согласования документа"
        )
        self.CREATE_DATE = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[9]", "Статус согласования документа"
        )
        self.DESCRIPTION = ElementsList(
            "(//div[contains(@class, 'table-tbody')] //tr) //td[10]", "Статус согласования документа"
        )
        self.PARALLEL_INQUIRY_ID = ElementsList("h3:has(> a[href]) a", "Номер параллельного заказа")


class ProductsMoveInquiryElements(InquiriesElements):
    def __init__(self) -> None:
        super().__init__()
        self.REFRESH_BTN = Element("//span[@data-icon='Refresh']", "Кнопка 'Обновить'")
        self.TARGET_AGREEMENT_MESSAGE = Element("//div[@alignself]/p", "информационное сообщение о статусе шага")
        self.TARGET_AGREEMENT = Element("#customer_agreement", "Поле 'Целевой договор'")
        self.CLIENT_AGREEMENT = ElementsList("//div[@role='dialog']//p", "Выбор целевого договора")
        self.TARGET_AGREEMENT_SELECTION = ElementsList(
            "//label//span/p", "Выбор целевого договора текущего/другого клиента"
        )
        self.AGREEMENT_NUMBER = Element("#search-customer_agreementNumber", "Поле номера договора для поиска договора")
        self.FIND_AGREEMENT = ElementsList("//form[@id='search-customer']//button[@type='submit']", "Кнопка найти")
        self.SEARCH_RESULT = ElementsList(
            "div[data-body-height] div[data-row-key] div[class*=table-column-sort]", "Результат поиска договора"
        )
        self.AGREEMENT_TERMINATE = Element("//input[@type='checkbox']", "Чекбокс расторжения исходного договора")

        self.CURRENT_AGREEMENT = Element("//p/../label/span", "Чекбокс 'Перенести в рамках текущего договора'")
        self.CUSTOMER_ORDER_SELECT = ElementsList(
            "//div[contains(@class, 'collapse-content')]//div[@role='button']//input",
            "Выбрать все ПП на ЛС",
        )
        self.MOVE_ALL_PRODUCTS_ON_SUBSCRIBER = ElementsList(
            "[class*=collapse-item-active] > [class*=collapse-header] input[type=checkbox]",
            "Чекбокс переноса всех ПП для абонента",
        )
        self.MAIN_PRODUCT_NAME_FOR_MOVE = ElementsList(
            "div[data-testid*=product-title] > p", "Название ПП в таблице для переноса ПП"
        )
        self.SOURCE_ACCOUNT_NUMBER_FOR_MOVE = ElementsList(
            "[data-price-type-code='OriginalPersonalAccount'] p[data-name='paragraphInfoMedium']",
            "Номер ЛС в таблице для переноса ПП",
        )
        self.TARGET_ACCOUNT_NUMBER_FOR_MOVE = ElementsList(
            "[data-price-type-code='TargetPersonalAccount'] p[data-name='paragraphInfoMedium']",
            "Номера целевых ЛС для продуктов",
        )
        self.CUSTOMER_OPTION_SELECT = ElementsList("//div[@tabindex='-1' and @role='button']//input", "Выбрать Опцию")
        self.ACCOUNT_ACTIONS_BUTTONS = ElementsList(
            "//div[@overflow='auto']//p/following-sibling::div//button", "Кнопки 'Назначить ЛС','Сбросить ЛС'"
        )
        self.TARGET_ACCOUNT_ROW = ElementsList(
            "[class*=table-virtual] [class*=table-tbody] [class*=virtual-holder] [class*=table-row] [class*=table-cell]",
            "Выбор целевого ЛС",
        )


class ProductEditForm(DynamicForms):
    """Форма редактирования продукта"""

    def __init__(self) -> None:
        super().__init__()

        self.REGION = Element("[class*=drawer-title] p:last-child", "Значение поля 'Регион'")
        self.PRODUCT_NAME = Element("[class*=drawer-header-title] p:nth-child(2)", "Название продукта")

        self.VOLUMES_TAB = Element("[data-node-key=volumes]", "Таб 'Объемы'")
        self.PRICE_TAB = Element("[data-node-key=prices]", "Таб 'Цены'")
        self.PRICES_DROPDOWN_BTN = ElementsList(
            "[id*=panel-prices] [class*=collapse-header][role=button]", "Дропдауны в табе Цены"
        )
        self.SPECIFICATION_TAB = Element("[data-node-key=characteristics]", "Таб 'Характеристики'")
        self.SERVICES_TAB = Element("[data-node-key=services]", "Таб 'Сервисы'")
        self.RESOURCES_TAB = Element("[data-node-key=resources]", "Таб 'Ресурсы'")

        self.PRODUCT_REGION = Element("[class*='drawer-title'] p:nth-of-type(4)", "Регион")

        # PRICE_TAB
        self.PRICE_CARD = Element("[id*=panel-prices] div[class*=collapse-header]", "Плашка с ценой")
        self.PRICE_CARD_VALUES = Element(
            "[id*=panel-prices] div[class*=collapse-item] > [class*=collapse-content]", "Параметры цены продукта"
        )
        self.SUBSCRIPTION_FEE_BASE_PRICE = ElementsList(
            "div[id*=panel-prices] p[color][data-name=paragraphInfo]", "Поле Базовая цена для Абонентской платы"
        )
        self.SUBSCRIPTION_FEE_DISCOUNT_INPUT = ElementsList(
            "input[id*=amountDiscount]",
            "Поле ввода скидки на абонентскую плату (процент)",
        )
        self.SUBSCRIPTION_FEE_DISCOUNT_ERROR = Element(
            "div[class*=explain-connected]",
            "Сообщение об ошибке валидации поля скидки на абонентскую плату",
        )
        self.SUBSCRIPTION_FEE_FINAL_PRICE = ElementsList(
            "input[id$=Charge_amount]",
            "Итоговая цена абонентской платы после применения скидки",
        )
        self.SUBSCRIPTION_PERIOD = ElementsList("input[id*=paymentPeriod]", "Поле Период списания")
        self.ONE_TIME_PAYMENT_BASE_PRICE = ElementsList(
            "div[id*=panel-prices] p[color][data-name=paragraphInfo]", "Поле Базовая цена для Разового платежа"
        )
        self.ONE_TIME_PAYMENT_DISCOUNT_INPUT = ElementsList(
            "input[id*=amountDiscount]",
            "Поле ввода скидки на разовую плату (процент)",
        )
        self.ONE_TIME_PAYMENT_FINAL_PRICE = ElementsList(
            "input:not([id*=Discount]):not([readonly])[id*=amount]",
            "Итоговая цена разовой платы после применения скидки",
        )
        self.GENERIC_FEE_BASE_PRICE = ElementsList(
            "[id*=prices] [class*=collapse-header][role=button] [class*=-row] > div > div > div p[data-name*=Medium]",
            "Универсальное поле базовой цены",
        )
        self.GENERIC_FEE_DISCOUNT_INPUT = Element(
            "[id*='panel-prices'] input[id*='FeeProdOfferingPrice_Percent']",
            "Универсальное поле ввода скидки (процент)",
        )
        self.GENERIC_FEE_FINAL_PRICE = Element(
            "[id*='panel-prices'] input[id*='FeeProdOfferingPrice'][id*='TotalPrice']",
            "Универсальное поле итоговой цены",
        )
        self.PRICE_COMMENT_TEXTAREA = Element(
            "[id*='panel-prices'] textarea",
            "Поле комментария к цене",
        )
        self.RESET_DISCOUNT_BTN = Element(
            "button[id='reset_discounts']",
            "Кнопка 'Сбросить скидки'",
        )
        self.RESOURCES_TAB_IN_CASE_ONLY_PHONE = Element(
            "[class*=-drawer-content][role=dialog] [class*=-tabs-tab]:nth-of-type(3)", "Таб 'Ресурсы'"
        )

        # VOLUMES_TAB
        self.VOLUMES = ElementsList("[class*=-drawer-content][role=dialog] div[id*='panel-volumes']", "Объемы")
        self.PRODUCT_VOLUMES = ElementsList("[id*=originalMaxVolume]", "Объемы продукта")

        # SPECIFICATION_TAB
        self.SPECIFICATION = ElementsList(
            "[class*=-drawer-content][role=dialog] div[id*='panel-characteristics']", "Характеристики"
        )
        self.NUMBER_COLOR = Element("[id*=panel-characteristics] div:nth-child(4) p:nth-child(2)", "Цвет номера")
        self.CHARACTERISTIC_VALUES = ElementsList("[id*=panel-characteristics] p:nth-child(2)", "Значения характеристик")
        self.SPECIFICATION_ERROR_ICON = Element(
            "[data-node-key='characteristics'] span", "Восклицательный знак около таба 'Характеристики'"
        )
        self.ADDRESS = Element(
            "[class*=tabpane-active] > div > div:first-child > p:last-child",
            "Значение поля 'Адрес'",
        )
        self.TEST_CHARC = Element(
            "[class*=-drawer-content][role=dialog] div[id*='panel-characteristics'] > div > div:nth-of-type(4) input",
            "Характеристика для тестирования",
        )

        # SERVICES_TAB
        self.SERVICES = ElementsList("[id*='panel-services'] [class*='collapse-header-text']", "Сервисы")

        self.COLOR_NUMBER_FORM = Select(".ant-select-selector", "Форма выбора цвета номера")
        self.BOOK_RESOURCES = Element(
            "[id*='-panel-resources'] > div > :nth-child(1) [type='button']", "Кнопка 'Забронировать ресурсы'"
        )

        # RESOURCES_TAB
        self.RESOURCES = ElementsList("[class*=-drawer-content][role=dialog] div[id*='panel-resources']", "Ресурсы")
        self.RESERVE_RESOURCES_BTN = Element(
            "[class*=-drawer-content][role=dialog] div[id*='panel-resources'] button:nth-child(1)",
            "Кнопка 'Забронировать'",
        )
        self.RESERVE_RESOURCES_SELECT = DropdownWithId("booking", "Выпадающее меню 'Забронировать'")
        self.CHANGE_ICCID_BTN = Element(
            "//p[contains(text(), 'SIM')]/../.. //span[@data-icon='SwapHoriz']",
            "Кнопка 'Замена ресурса' ICCID",
        )
        self.CHANGE_NUMBER_BTN = Element(
            "//p[contains(text(), 'Телефонный номер')]/../.. //span[@data-icon='SwapHoriz']",
            "Кнопка 'Замена ресурса' номер телефона",
        )  # требует дата атрибута от фронтов
        self.DELETE_RESOURSE_BTN = ElementsList("button:has(span[data-icon='Delete'])", "Кнопка очистить выбранные")
        self.CHANGE_EQUIPMENT_BTN = Element(
            "//p[contains(text(), 'Оборудование')]/../.. //span[@data-icon='SwapHoriz']",
            "Кнопка 'Замена ресурса' Оборудование",
        )
        self.CHANGE_APN_BTN = Element(
            "//p[contains(text(), 'APN')]/../.. //span[@data-icon='SwapHoriz']",
            "Кнопка 'Замена ресурса' APN",
        )
        self.RESERVE_RESOURCES_LOADER = Element(
            "(//*[contains(@class, 'form')] //*[contains(@class, 'spin-dot')])[1]",
            "Лоадер во время бронирования ресурсов",
        )
        self.ICCID = Element(
            "//p[contains(text(), 'ICCID')]/../../p", "ICCID SIM-карты"
        )  # требует дата атрибута от фронтов
        self.PHONE_NUMBER = Element(
            "//p[contains(text(), 'Номер телефона')]/../../p", "Номер телефона"
        )  # требует дата атрибута от фронтов


class ReserveResourcesForm:
    """Форма бронирования ресурсов (SIM-карты, номера телефона)"""

    def __init__(self) -> None:
        self.TITLE = Element("(//*[contains(@class, 'drawer-title')] //h3)[2]", "Заголовок формы")
        self.RESOURCE_INFO = ElementsList(
            "(//*[contains(@class, 'drawer-title')])[2]/div/div/div", "Информация о ресурсе"
        )
        self.INFO_MESSAGE = Element(
            "(//*[contains(@class, 'drawer-body')])[2] //*[contains(@class, 'platform-attention-label')]",
            "Информационное сообщение",
        )
        self.SEARCH_PARAMETERS_NOT_SET = Element(
            "[class*=drawer-body] .platform-empty-state-container", "Не заданы условия поиска"
        )
        self.CROSS_BTN = Element(
            "(//div[contains(@class,'drawer')] //button[contains(@class,'close')])[last()]", "Крестик"
        )
        self.CANCEL_BTN = Element(
            "[data-testid*=ResourceBooking][data-testid*=cancel][data-testid$=btn]", "Кнопка 'Отмена'"
        )
        self.BOOK_BTN = Element(
            "[data-testid*=ResourceBooking][data-testid*=accept][data-testid$=btn]", "Кнопка 'Забронировать'"
        )

        # SIM RESERVE FILTER ELEMENTS
        self.SIM_TYPE = RadioOrCheckboxBlock(
            "(//*[contains(@class, 'drawer-body')])[2] //*[contains(@class, 'radio-group')]",
            "Выбор типа SIM-карты",
        )
        self.SEARCH_TYPE = Select("input[id*=parameters_searchType]", "Поле 'Тип поиска'")

        # NUMBER RESERVE FILTER ELEMENTS
        self.STANDARD_INPUT = Select(
            "//*[contains(@id, 'parameters_standard')]/../../../*[contains(@class, 'select-selection-wrap')]",
            "Поле 'Стандарт'",
        )
        self.NUMBERING_TYPE = Select("input[id*=parameters_numberingType]", "Поле 'Тип нумерации'")
        self.NUMBER_CLASS = Select("input[id*=parameters_numberClass]", "Поле 'Класс номера'")
        self.NUMBER_CLASS_TOOLTIP = Element(
            "label[for*='numberClass'] [data-icon='ErrorOutline']", "Тултип поля 'Класс номера'"
        )
        self.NUMBER_CLASS_TOOLTIP_TEXT = Element(
            "[class*=tooltip-placement]:not([class*=hidden]) [class*='tooltip-inner'] p",
            "Текст тултипа поля 'Класс номера'",
        )
        self.FREE_FOR = Element("input[id*=parameters_freeFor]", "Поле 'Свободные'")

        # COMMON FILTER ELEMENTS
        self.ONLY_CHOOSE_RADIOBUTTON = Element(
            "[class*=drawer-content] button[role=switch]", "Кнопка 'Только выбранные'"
        )
        self.CLEAR_SELECTED_BTN = Element("button:has(span[data-icon='Delete'])", "Кнопка очистить выбранные")
        self.CLEAR_SELECTED_CONFIRM_BTN = Element(
            "[class*='modal'] button[class*='btn-color-primary']", "Кнопка 'Ок' в модальном окне"
        )
        self.ONLY_CHOOSE_TEXT = Element("[class*=drawer-body] label > p[data-name*=paragraph]", "Только выбранные")
        self.MASK_INPUT = Element("input[id*=parameters_mask]", "Поле 'Маска'")
        self.RANGE_LEFT_INPUT = Element("input[id*=parameters_rangeFrom]", "Левая граница поля 'Диапазон'")
        self.RANGE_RIGHT_INPUT = Element("input[id*=parameters_rangeTo]", "Правая граница поля 'Диапазон'")
        self.RESOURCE_COUNT = Element("input[id*=parameters_resourceCount]", "Значение поля 'Количество ресурсов'")
        self.SWITCH = Select(
            "//input[contains(@id,'parameters_switch')] //ancestor::div[contains(@class,'select-selector')]",
            "Выпадающее меню 'Коммутатор'",
        )
        self.REGION = Element(
            "//input[contains(@id, 'parameters_region')]/following::span[contains(@class, 'selection-item')]",
            "Значение поля 'Регион'",
        )
        self.CLEAR_BUTTON = Element(
            "(//*[contains(@class, 'platform-dynamic-form-bottom-toolbar-area')] //button)[1]",
            "Кнопка 'Сбросить'",
        )
        self.SEARCH_BUTTON = Element(
            "(//*[contains(@class, 'platform-dynamic-form-bottom-toolbar-area')] //button)[2]",
            "Кнопка 'Найти'",
        )

        # COMMON TABEL ELEMENTS
        self.REFRESH_BTN = Element("(//*[contains(@id, 'table')] //button)[1]", "Кнопка 'Обновить'")
        self.TABLE_HEADER = ElementsList(".table-header-column", "Заголовки таблицы ресурсов")
        self.NO_RECORDS_FOUND = Element("[id*=table] .platform-empty-state-container", "Записи не найдены")

        # SIM TABEL
        self.SIM_CHECKBOX = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(1)", "Чекбокс симкарты")
        self.SIM_ICC = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(2)", "Поле 'ICC' симкарты")
        self.SIM_IMSI = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(3)", "Поле 'IMSI' симкарты")
        self.SIM_TYPE = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(4)", "Поле 'Тип симкарты'")
        self.SIM_EXPIRATION_DATE = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(5)", "Поле 'Срок действия'"
        )
        self.SIM_SWITCH = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(6)", "Поле 'Коммутатор'")

        # NUMBER TABEL
        self.NUMBER_CHECKBOX = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(1)", "Чекбокс номера телефона"
        )
        self.NUMBER = ElementsList("[class*=table-tbody] [class*=table-row] div:nth-child(2)", "Поле 'Номер'")
        self.NUMBER_CLASS_NAME = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(3)", "Поле 'Класс номера'"
        )
        self.NUMBER_TYPE_OF_NUMBERING = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(4)", "Поле 'Тип нумерации'"
        )
        self.NUMBER_SWITCH = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(5)", "Поле 'Коммутатор'"
        )

        # EQUIPMENT TABEL
        self.EQUIPMENT_NUMBER = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(3)", "Поле 'Серийный номер' оборудования"
        )
        self.EQUIPMENT_NAME = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(2)", "Поле 'Наименование' оборудования"
        )
        self.EQUIPMENT_CHECKBOX = ElementsList(
            "[class*=table-tbody] [class*=table-row] div:nth-child(1)", "Чекбокс оборудования"
        )

        # APN
        self.APN_SELECT = Select("#selectedApn", "Селектор APN")
        self.GET_AUTO_IP = Element(
            "form[class*=form-vertical]:has(input[id*=ipAddress]) button[class*=default]",
            "Кнопка 'Подобрать автоматически'",
        )


class ChangeResourcesForm:
    """Форма 'Замена ресурса'"""

    def __init__(self) -> None:
        self.FORM = Element("(//*[contains(@class, 'ant-drawer-content')][@role='dialog'])[2]", "Форма 'Замена ресурса'")
        self.TITLE = Element("(//*[contains(@class, 'ant-drawer-title')] //h3)[2]", "Заголовок формы")
        self.SUBTITLE = Element(".ant-drawer-title p", "Подзаголовок формы")
        self.NUMBERS = ElementsList(
            "(//*[contains(@class, 'platform-scrollable scrollable-body')]/div/div/div/div/div/div[2]/div/p)",
            "Доступные номера телефонов",
        )
        self.INNER_ACCEPT_BTN = Element("(//button[@id='_accept-button'])[2]", "Внутренняя кнопка 'Выбрать'")


class CloseInquiryForm(DynamicForms):
    """Форма 'Закрытие заявки'"""

    def __init__(self) -> None:
        super().__init__()

        self.FORM = Element(
            "[class*=drawer-content-wrapper]:not([class*=drawer-content-wrapper-hidden]):has([class*=drawer-footer])",
            "Форма 'Закрытие заявки'",
        )
        self.TITLE = Element("[class*=drawer-title] h3[display=inline]", "Заголовок формы")
        self.CLOSE_REASON = Select("input#closeInquiryForm_reason", "Поле 'Причина закрытия'")


class RefundInquiryForm(InquiriesElements):
    """Форма 'Заявка на возврат средств'"""

    def __init__(self) -> None:
        super().__init__()
        self.REFUND_PROCESSING_BTN = Element(
            "(//div[contains(@class, 'platform-root-scrollable-container')]/..//button)[1]",
            "Кнопка 'Обработка'",
        )
        self.REFUND_REFRESH_BTN = Element(
            "(//div[contains(@class, 'platform-root-scrollable-container')]/..//button)[2]",
            "Кнопка 'Обновить'",
        )
        self.REFUND_SUBMIT_PROC_BTN = Element("(//ul[@role='menu']/li)[2]", "Кнопка 'Передать в обработку'")
        self.REFUND_TAKE_IN_PROC_BTN = Element("(//ul[@role='menu']/li)[3]", "Кнопка 'Взять в обработку'")
        self.REFUND_EDIT_BTN = Element("//div[@role='tabpanel'] //button", "Кнопка 'Редактировать'")
        self.APPROVAL_STATUS_REFUND_FORM = SelectWithId(
            "additional_values_rfdDecision", "Поле 'Статус согласования возврата'"
        )
        self.REFUND_SAVE_BTN = Element("//div[@role='tabpanel']/div/div/div/button", "Кнопка 'Сохранить'")
        self.REFUND_INQUIRY_SOLUTION_STATUS = Element(
            "(//div[@data-testid='attribute-rfdDecision']/p)[2]", "Статус решения по заявке"
        )


class EditContactInfoForm(DynamicForms):
    """Форма редактирования контактных данных"""

    def __init__(self) -> None:
        super().__init__()

        self.INFO_TEXT = Element("span[class*='header-text']:has(br)", "Текс информации")
        self.CLIENT = Element("#customer", "Клиент")
        self.LINKED_PERSON = Select("#inqrLinkedPerson", "Контактное лицо")
        self.EMAIL = Select("#email", "Предпочтительный email")
        self.PHONE = Select("#phone", "Предпочтительный телефон")


class EditTerminationForm(DynamicForms):
    """Форма редактирования по расторжению договора"""

    def __init__(self) -> None:
        super().__init__()

        self.CANCEL_OUT_FIND_ENTITY_BTN = Element(
            "//div[@role='dialog']//div[contains(@class,'footer')]//button[1]",
            "Кнопка 'Отмена' с уведомления 'Поиск блокирующих сущностей'",
        )
        self.ACCEPT_OUT_FIND_ENTITY_BTN = Element(
            "//button[contains(@class,'ant-btn') and contains(@class,'ant-btn-primary')]",
            "Кнопка 'Перейти' с уведомления 'Поиск блокирующих сущностей'",
        )


class MassDiscountEditForm(DynamicForms):
    """Форма массового редактирования скидок"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element(
            "[class*='drawer-open'] [class*=drawer-title] h3", "Заголовок формы массового редактирования скидок"
        )
        self.WARNING_MESSAGE = Element(
            "[class*=drawer-body] [class*='attention-label'] p[data-name='paragraphInfo']",
            "Предупреждающее сообщение о массовом изменении цен",
        )
        self.SUBSCRIPTION_FEE_DISCOUNT_INPUTS = ElementsList(
            "input[id*='RecurringChargeProdOfferPriceCharge_discount']",
            "Поля ввода скидки на абонентскую плату (процент) для всех продуктов",
        )
        self.SUBSCRIPTION_FEE_FINAL_PRICE = ElementsList(
            "input:not([id*=WithoutTax])[id*='RecurringChargeProdOfferPriceCharge_amount']",
            "Итоговые цены абонентской платы после применения скидки",
        )
        self.ONE_TIME_BASE_PRICE = ElementsList(
            "input[id*=FeeProdOfferingPrice_amountWithoutTax]", "Базовые цены разовых платежей до применения скидки"
        )
        self.ONE_TIME_FINAL_PRICE = ElementsList(
            "input:not([id*=WithoutTax])[id*=FeeProdOfferingPrice_amount]",
            "Итоговые цены разовых платежей после применения скидки",
        )
        self.ONE_TIME_DISCOUNT_INPUTS = ElementsList(
            "input[id*=FeeProdOfferingPrice][id$=_discount]",
            "Поля ввода скидки на разовую плату (процент) для всех продуктов",
        )
        self.PRICE_COMMENT_INPUTS = ElementsList(
            "input[id*=comment]",
            "Поля ввода комментария по цене для всех продуктов",
        )

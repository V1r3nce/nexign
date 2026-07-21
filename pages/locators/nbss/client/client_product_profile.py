from pages.locators.nbss.dynamic_form_elements import DynamicElements
from pages.ui_elements import Element, ElementsList


class ClientProductProfileElements(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/products
    'Продуктовый профиль клиента'"""

    def __init__(self) -> None:
        super().__init__()

        self.PRODUCTS_CLEAR_FILTER_BTN = Element("button:has([data-icon=FilterRemove])", "Кнопка 'Сбросить'")
        self.PRODUCTS_FILTER_SETTINGS_BTN = Element(
            "[id*=panel-products] [class*=toolbar] > div:not([style]) [data-icon*=FilterSettings]",
            "Кнопка 'Настройки фильтра'",
        )
        self.PRODUCTS_FILTER_IP_INPUT = Element(
            "[class*=drawer-open] input[id*=ipAddress]",
            "Поле ввода IP-адреса ресурса в фильтрах продуктов",
        )
        self.PRODUCTS_FILTER_LINE_NUMBER_INPUT = Element(
            "[class*=drawer-open] input[id*=lineNumber]",
            "Поле ввода номера линии ресурса в фильтрах продуктов",
        )
        self.PRODUCTS_FILTER_SERIAL_NUMBER_INPUT = Element(
            "[class*=drawer-open] input[id='products-filter_serialNumber']",
            "Поле ввода серийного номера в фильтрах продуктов",
        )
        self.PRODUCTS_UPDATE_BTN = Element(
            "[id*=panel-products] [class*=toolbar] > div:not([style]) button:has([data-icon=Refresh])",
            "Кнопка 'Обновить'",
        )
        self.PRODUCTS_LIST = ElementsList(
            "(//*[contains(@class, 'collapse-borderless')])[1]/*[contains(@class, 'collapse-item')]",
            "Развернутые и свернутые Продукты клиента",
        )
        self.PRODUCTS_HEADER_LIST = ElementsList(
            "(//*[contains(@class, 'collapse-borderless')])[1]/*[contains(@class, 'collapse-item')]/div[1]",
            "Заголовки продуктов клиента",
        )
        self.OTHER_PRODUCTS_EXPAND_ICON = ElementsList(
            "div[class*=collapse-icon]:last-child span[data-icon='KeyboardArrowUp']",
            "Иконка раскрытия секции 'Прочие продукты'",
        )
        self.OPTIONS_EXPAND_ICON = Element(
            "//span[@data-icon='SmallUncollapse']/child::*[1]",
            "Иконка раскрытия секции 'Опции'",
        )
        self.OPTION_ELEMENTS = ElementsList(
            "[class*=csm-product-header] [class*=product-header] [class*=header-title]", "Элементы опции продукта"
        )
        self.SUBSCRIBER_EXPAND_BUTTON = ElementsList(
            "//div[@aria-expanded='false']/div/span[@data-icon='KeyboardArrowUp']", "Иконка раскрытия секции 'Абонент'"
        )
        self.PRODUCTS_LIST_STATUS_COLOR = ElementsList(
            "//a[contains(@href,'/nbss/customer')]/parent::div/div", "Цвет статуса абонента"
        )
        self.SUBSCRIBER = ElementsList(
            "[class*=collapse-item] > [class*=collapse-header] a[href*=subscription]", "Абонент"
        )
        self.SUBSCRIBER_SECTION = ElementsList(
            "div[class*=collapse-header]:has(a[href*=subscription])", "Секция Абонента"
        )
        self.PRODUCTS = ElementsList("[class*=subscription-products][data-subscription-id]", "Продукты")
        self.PRODUCT_LIMIT = ElementsList("//*[contains(@class, 'ant-progress-line')]/..", "Лимиты продуктов")
        self.PRODUCT_LIMIT_VALUES = ElementsList(
            "div:has(> [role='progressbar']) p[data-name='paragraphInfoMedium']", "Значения объемов продуктов"
        )
        self.OPTION_LIMIT_ICON = ElementsList(
            "//*[contains(@class, 'ant-progress-line')]/.. //span", "Значок лимита опции"
        )
        self.PRODUCT_NAME = ElementsList(
            "[class*=subscription-products][data-subscription-id] [class*=header-main] a",
            "Названия продуктов",
        )
        self.PRODUCT_ADDRESS = Element(
            "div:has([data-testid*=product-title])[class*=grid-container] > div:nth-child(1)  > div > div:nth-child(2) p:nth-child(1)",
            "Адрес подключения продукта",
        )
        self.PRODUCT_ACTIVATION_DATE = ElementsList(
            "[class*=subscription-products-wrapper] p[data-name=description] span:nth-child(3)",
            "Поле 'Ожидает активации с'",
        )
        self.PRODUCTS_CONTRACT_NUM = ElementsList(
            "[class*=subscription-products][data-subscription-id] [class*=header-agreement] a", "Договор продукта"
        )
        self.PRODUCTS_PERSONAL_ACCOUNT_NUM = ElementsList(
            "[class*=subscription-products][data-subscription-id] [class*=header-account] a",
            "Лицевой счет продукта",
        )
        self.PRODUCT_ONE_TIME_PAYMENT = ElementsList(
            "//p[normalize-space(.)='Разовый платёж' or normalize-space(.)='Разовый платеж']"
            "/ancestor::div[1]/preceding-sibling::div[1]//p[not(@color='interface15')]",
            "Разовый платеж",
        )
        self.PRODUCT_ONE_TIME_PAYMENT_BEFORE_INDIVIDUALIZATION = ElementsList(
            "//p[normalize-space(.)='Разовый платёж' or normalize-space(.)='Разовый платеж']/ancestor::div[1]/preceding-sibling::div[1]//p[@color='interface15']",
            "",
        )
        self.PRODUCTS_SUBSCRIPTION_FEE = ElementsList(
            "[class*=subscription-products][data-subscription-id] [class*=header-fee] [class*=price-amount]",
            "Абонентская плата",
        )
        self.PRODUCTS_SUBSCRIPTION_FEE_BEFORE_INDIVIDUALIZATION = ElementsList(
            "//p[normalize-space(.)='Абонентская плата']/ancestor::div[1]/preceding-sibling::div[1]//p[@color='interface15']",
            "Абонентская плата до индивидуализации",
        )
        self.PRODUCT_CONTAINER_FROM_NAME = "xpath=ancestor::*[contains(@class,'platform-grid-container')][1]"
        self.PRODUCTS_STATUS_COLOR = ElementsList(
            "[class*=product][data-subscription-id] [class*=header-status]",
            "Цвет статуса продукта",
        )
        self.OPTION_STATUS_COLOR = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]//*[contains(@class, 'collapse-content-box')]//a[@color='accent']/../div",
            "Цвет статуса Опции",
        )
        self.PRODUCTS_DETAILS_OPEN_BTN = ElementsList(
            "//div[contains(@class, 'collapse-content-box')]//button[contains(@class, 'dropdown-trigger')]",
            "Кнопка выпадашки для кнопки редактирования продукта",
        )
        self.SUBSCRIBERS_DETAILS_OPEN_BTN = ElementsList(
            "[class*=subscription-header] [class*=actions] [data-icon=MoreVert]",
            "Кнопка выпадашки для кнопки редактирования абонента",
        )
        self.PRODUCTS_CONSUMPTION_DETAILS_BTN = Element(
            '[data-menu-id*="OpenConsuming"]', "Кнопка 'Перейти к деталям потребления'"
        )
        self.TURN_OFF_BTN = Element("[role=menuitem][data-menu-id*=Disable]", "Кнопка 'Отключить'")
        self.PRODUCT_EDIT_BTN = Element("li[data-menu-id*=Edit]", "Кнопка 'Редактировать'")
        self.PRODUCT_EDIT_ACTIVATION_DATE_BTN = Element(
            "li[data-menu-id*=ChangeDate]", "Кнопка 'Изменить дату активации'"
        )
        self.PRODUCTS_OPTIONS_OPEN_BTN = ElementsList(
            "[class*=subscription-products][data-subscription-id] [class*=actions] button",
            "Кнопка выпадашки для кнопки добавления опций",
        )
        self.PERSONAL_ACCOUNT_OPTION_ICON = ElementsList(
            ".platform-grid-container:nth-child(2) span:nth-child(2) svg",
            "Иконка учета опции на персональном счете",
        )
        self.PRODUCTS_OPTIONS_ADD_BTN = Element('[role=menuitem][data-menu-id*="ADD_OPTION"]', 'Кнопка "Добавить Опцию"')
        self.PRODUCTS_OPTIONS_CHANGE_MAIN_RODUCT_BTN = Element(
            '[role=menuitem][data-menu-id*="TRANSITION_TO_MAIN_PRODUCT"]', "Кнопка 'Сменить основной продукт'"
        )
        self.CURRENT_OPTION_PRODUCT = ElementsList(
            "[class*=collapse-item] [class*=collapse-item]:has([data-icon=SmallCollapse]) div [role=button]",
            "Подключенные опции у продукта",
        )
        self.OPEN_PRODUCT_BTN = ElementsList(
            "//div[contains(@class, 'platform-scrollable')]/div/div/div[contains(@class, 'collapse-header')]/div/span[contains(@class, 'collapse-arrow')]",
            "Кнопка Открыть продукты у абонента",
        )
        self.OPEN_OPTIONS_BTN = ElementsList(
            "//*[contains(@class, 'collapse-content-box')]//span[contains(@class, 'collapse-arrow')]",
            "Кнопка Открыть опции продукта",
        )
        self.OPTION_NAME = ElementsList(
            "//*[contains(@class, 'collapse-content-box')] //div[contains(@class, 'collapse-item-disabled')] //a ",
            "Названия подключенных опций продукта",
        )
        self.NO_SUBSCRIBERS_BLOCK = Element(
            "[id*=panel-products] .platform-empty-state-container", "Блок Абонентов пока нет"
        )

        self.PRODUCTS_SIDEBAR_OPEN = Element(
            "(//div[@role='tablist'] //div[contains(@class, 'platform-grid-container')]) [1]",
            "Область клика для открытия сайдбара",
        )

        # PRODUCTS_TAB_SIDEBAR
        self.PRODUCT_SIDEBAR_EDIT_ACTIVATION_DATE_BTN = Element(
            "[class*=platform-toolbar] > div:nth-child(1) button:has(span[data-icon=DateChange])",
            "Кнопка сайдбара 'Изменить дату активации'",
        )

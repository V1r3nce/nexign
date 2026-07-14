from pages.locators.nbss.dynamic_form_elements import DynamicElements
from pages.ui_elements import ElementsList


class ClientProductProfileElements(DynamicElements):
    """Страница /customer-hierarchy-management/customers/{customer_id}/products
    'Продуктовый профиль клиента'"""

    def __init__(self) -> None:
        super().__init__()

        self.SUBSCRIBER = ElementsList(
            "[class*=collapse-item] > [class*=collapse-header] a[href*=subscription]", "Абонент"
        )
        self.PRODUCTS = ElementsList("[class*=subscription-products][data-subscription-id]", "Продукты")
        self.PRODUCTS_LIST = ElementsList(
            "(//*[contains(@class, 'collapse-borderless')])[1]/*[contains(@class, 'collapse-item')]",
            "Развернутые и свернутые Продукты клиента",
        )
        self.PRODUCTS_HEADER_LIST = ElementsList(
            "(//*[contains(@class, 'collapse-borderless')])[1]/*[contains(@class, 'collapse-item')]/div[1]",
            "Заголовки продуктов клиента",
        )
        self.PRODUCTS_STATUS_COLOR = ElementsList(
            "[class*=product][data-subscription-id] [class*=header-status]",
            "Цвет статуса продукта",
        )

        self.PRODUCT_LIMIT = ElementsList("//*[contains(@class, 'ant-progress-line')]/..", "Лимиты продуктов")
        self.PRODUCT_LIMIT_VALUES = ElementsList(
            "div:has(> [role='progressbar']) p[data-name='paragraphInfoMedium']", "Значения объемов продуктов"
        )
        self.PRODUCT_NAME = ElementsList(
            "[class*=subscription-products][data-subscription-id] [class*=header-main] a",
            "Названия продуктов",
        )

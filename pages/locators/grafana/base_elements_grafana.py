from pages.ui_elements import Element, ElementsList


class BaseGrafanaElements:
    def __init__(self) -> None:
        self.APP_LOGO = Element("img[alt=Grafana]", "Логотип сервиса")
        self.NAV_MENU = ElementsList("a[data-testid*=Nav]", "Элементы навбара")

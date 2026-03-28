from pages.locators.grafana.base_elements_grafana import BaseGrafanaElements
from pages.ui_elements import Element, ElementsList


class HomeGrafanaElements(BaseGrafanaElements):
    """Страница Домашняя Grafana UI"""

    def __init__(self) -> None:
        super().__init__()

        self.ALERTS_DASHBOARD = Element("section[data-testid*=Alerts]", "Панель Алертов")
        self.LOGS_DASHBOARD = Element("section[data-testid*=Logs]", "Панель Логов")
        self.PRODUCTS_LOGS = ElementsList(
            "//section[contains(@data-testid, 'Logs')]//a[@href]", "Список продуктов внутри Панели Логов"
        )
        self.PRODUCTS_ALERTS = ElementsList(
            "//section[contains(@data-testid, 'Alerts')]//a[@href]", "Список продуктов внутри Панели Алертов"
        )
        self.K8S_DASHBOARD = Element("section[data-testid*=K8s]", "Панель K8S")
        self.PRODUCTS_K8S = ElementsList(
            "//section[contains(@data-testid, 'K8s')]//a[@href]", "Список продуктов внутри Панели K8s"
        )
        self.SOLUTION_MONITORING_DASHBOARD = Element("section[data-testid*=Solution]", "Панель Мониторинга")
        self.PRODUCTS_MONITORING = ElementsList(
            "//section[contains(@data-testid, 'Solution')]//a[@href]", "Список продуктов внутри Панели Логов"
        )
        self.APPLICATION_MONITORING_DASHBOARD = Element("section[data-testid*=Shared]", "Панель Application")
        self.APPLICATION_MONITORING_PRODUCTS = ElementsList(
            "//section[contains(@data-testid, 'Application')]//a[@href]",
            "Список продуктов внутри Панели мониторинга приложений",
        )
        self.MONITORING_HOSTS_DASHBOARD = Element("section[data-testid*=System]", "Панель Системного мониторинга")
        self.MONITORING_HOSTS_PRODUCT = ElementsList(
            "//section[contains(@data-testid, 'System')]//a[@href]",
            "Список продуктов внутри Панели Системного мониторинга",
        )

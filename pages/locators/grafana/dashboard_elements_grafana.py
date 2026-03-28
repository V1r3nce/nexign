from pages.locators.grafana.base_elements_grafana import BaseGrafanaElements
from pages.ui_elements import Element, ElementsList, GrafanaVariableSelect


class DashboardGrafanaElements(BaseGrafanaElements):
    """Панель Grafana UI"""

    def __init__(self) -> None:
        super().__init__()

        self.ALERTS_TYPES = ElementsList("button[data-testid*=dashboard-row]", "Список Категорий Алертов")
        self.PRODUCT_STATISTICS = ElementsList("section[data-testid*=Panel]", "График по Статистику Продукта")

        self.NAME_GRAPH = ElementsList("section[data-testid*=Panel] div[class*=panel-title] h2", "Названия графиков")
        self.LINK_PRODUCT = ElementsList(
            "section[data-testid*=Panel] div[class*=panel-content] a", "Кликабельное имя продукта"
        )
        self.FILTER_BTN = ElementsList("button[data-testid*=filter]", "Кнопка Фильтра в каждом столбце")
        self.FILTER_WINDOW = Element("div[class*=filterContainer]", "Окно выбора фильтра")
        self.NAMES_PRODUCT_FILTER = ElementsList(
            "div[class*=filterContainer] div[class*=filterListRow] span", "Список продуктов доступных в Фильтре"
        )
        self.CONFIRM_FILTER_BTN = Element(
            "//div[contains(@class, 'filterContainer')]//span[text()='Ok']/..", "Кнопка применения Фильтра"
        )
        self.BTN_FILTER_TIME = Element("button[data-testid*=TimePicker]", "Кнопка Фильтра для настроек по времени")
        self.TIME_FILTERS = ElementsList("div[id=TimePickerContent] ul li:has(input)", "Доступные временные промежутки")
        self.CONTENT_PANEL = ElementsList("div[data-testid*=content]", "Панель с информацией о логах")
        self.EXISTING_FILTERS = ElementsList("button[class*=grafana-select-multi-value-remove]", "Выбранные фильтры")
        self.FILTER_PRODUCT_LOGS = GrafanaVariableSelect(
            "(//div[contains(@data-testid, 'DropDown')])[1]", "Фильтры логов по Продуктам"
        )
        self.FILTER_APPLICATION_LOGS = GrafanaVariableSelect(
            "(//div[contains(@data-testid, 'DropDown')])[2]", "Фильтры логов по Приложениям"
        )
        self.FILTER_LVL_LOGS = GrafanaVariableSelect(
            "(//div[contains(@data-testid, 'DropDown')])[3]", "Фильтры логов по Уровням"
        )
        self.LOG_MENU = ElementsList("button[aria-label*=Log]", "Меню логов")
        self.REFRESH_BTN = Element("button[data-testid*=RefreshPicker][aria-label=Refresh]", "Кнопка перезагрузить")
        self.BACKWARD_TIME = Element(
            "button[class*=toolbar-button][aria-label*=backward]", "Кнопка для Перемещения по диапазону времени"
        )
        self.ROW_DASHBOARD = ElementsList("button[data-testid*=dashboard-row-title]", "Список категорий дэшбордов")
        self.HOST_MONITORING = Element(
            "button[data-testid*='Dashboard link dropdown']",
            "Выбора элемента мониторинга",
        )
        self.TYPE_HOST_MONITORING = ElementsList("a[rel*=noopener][href]", "Доступные типы для выбора хоста мониторинга")

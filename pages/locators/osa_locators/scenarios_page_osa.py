from pages.osa_pages.home_page_osa import HomeOsaPage
from pages.ui_elements import Element, ElementsList


class ScenariosOsaPage(HomeOsaPage):
    """Страница Сценариев OSA"""

    def __init__(self) -> None:
        super().__init__()

        self.LIST_SCENARIOS = ElementsList(
            "div[class*=tree] ul[class*=treemenu-root] a[class*=ui-droppable]", "Список Сценариев"
        )
        self.BUTTON_REFRESH = Element("div[class=pad] button[id=button-refresh-scenarios]", "Кнопка обновления")
        self.TITLE_SCENARIOS = ElementsList(
            "table[name=scenarioslist]  td[class=title] a[href]", "Кликабельные Имена Сценариев"
        )
        self.TAB_TASKS = Element("div[id=scenario-tab-container] div[name=tasklist][class=tab]", "Таб Задачи")
        self.NEW_TASKS = Element("div[class=toolbar] button[id=button-scenario-add-task]", "Кнопка добавления задач")
        self.BTN_ADD_TASK = Element("div[class*=autoform] button[class=button]", "Кнопка 'Добавить задачу'")
        self.INPUT_PARAMETERS = Element("div[class*=autoform] textarea[name=options]", "Поле заполнения параметров")

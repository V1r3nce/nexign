from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class LifeCircleRulesElements(BaseElements):
    """Страница /nlm/rules-list 'Правила ЖЦ сущностей'"""

    def __init__(self) -> None:
        super().__init__()

        self.GRAPHS_LIST = ElementsList(
            "//*[contains(@id, 'panel-rules')] //div[not(@class or @style or ancestor::*[contains(@id, 'panel-transitions')])]",
            "Список графов",
        )
        self.ADD_TRANSITION_BTN = Element(
            "[id*=panel-transitions] button[variant=primary]", "Кнопка 'Создание перехода'"
        )
        self.NO_TRANSITIONS_MESSAGE = Element(
            "//*[contains(@id, 'panel-transitions')] //div[1] //div[2] //*[contains(@class, 'platform-empty-state-container')]",
            "Сообщение 'Переходы правила не найдены'",
        )
        self.TRANSITIONS_LIST = ElementsList(
            "//*[contains(@id, 'panel-transitions')] //div[not(@class or @style)]",
            "Список переходов правил",
        )
        self.ADD_FIRST_TRANSITION_BTN = Element(
            "[id*=panel-transitions] [class*='empty-state-container'] button:has([data-icon=Add])",
            "Кнопка для создания первого перехода",
        )

        self.TRANSITION_INFO = Element(
            "//*[contains(@id, 'panel-transitions')] //div[contains(@class, '-tabs ')]/../div[1]",
            "Данные о переходе",
        )
        self.TRANSITION_STATUS = Element("[id*=panel-transitions] [class*=-tag]:nth-child(1)", "Статус перехода")
        self.MANUAL_START_STATUS = Element(
            "[id*=panel-transitions] [class*=-tag]:nth-child(2)", "Возможность ручного запуска"
        )
        self.CREATE_INFO = ElementsList(
            "//div[contains(@class, '-tabs ')]/../div[1]/div[2]/div/div[2]", "Данные о создании перехода"
        )

        self.CONDITIONALS_BTN = Element("[id*=tab-conditions]", "Вкладка 'Условия перехода'")
        self.CONDITIONALS = ElementsList("[id*=panel-conditions] [class*=-collapse-item]", "Условия перехода")
        self.ACTIONS_BTN = Element("[id*=tab-actions]", "Вкладка 'Действия при переходе'")
        self.ACTIONS = ElementsList("[id*=panel-actions] [class*=-collapse-item]", "Действия при переходе")

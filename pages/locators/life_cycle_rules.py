from playwright.sync_api import Page

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class LifeCircleRules(BaseElements):
    """Страница /nlm/rules-list 'Правила ЖЦ сущностей'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.GRAPHS_LIST = ElementsList(
            "//*[contains(@id, 'panel-rules')] //div[not(@class or @style or ancestor::*[contains(@id, 'panel-transitions')])]",
            "Список графов",
            self.page,
        )
        self.ADD_TRANSITION_BTN = Element(
            "[id*=panel-transitions] button[variant=primary]", "Кнопка 'Создание перехода'", self.page
        )
        self.NO_TRANSITIONS_MESSAGE = Element(
            "//*[contains(@id, 'panel-transitions')] //div[1] //div[2] //*[contains(@class, 'platform-empty-state-container')]",
            "Сообщение 'Переходы правила не найдены'",
            self.page,
        )
        self.TRANSITIONS_LIST = ElementsList(
            "//*[contains(@id, 'panel-transitions')] //div[not(@class or @style)]",
            "Список переходов правил",
            self.page,
        )
        self.ADD_FIRST_TRANSITION_BTN = Element(
            "[id*=panel-transitions] [class*='empty-state-container'] button:has([data-icon=Add])",
            "Кнопка для создания первого перехода",
            self.page,
        )

        self.TRANSITION_INFO = Element(
            "//*[contains(@id, 'panel-transitions')] //div[contains(@class, '-tabs ')]/../div[1]",
            "Данные о переходе",
            self.page,
        )
        self.TRANSITION_STATUS = Element(
            "[id*=panel-transitions] [class*=-tag]:nth-child(1)", "Статус перехода", self.page
        )
        self.MANUAL_START_STATUS = Element(
            "[id*=panel-transitions] [class*=-tag]:nth-child(2)", "Возможность ручного запуска", self.page
        )
        self.CREATE_INFO = ElementsList(
            "//div[contains(@class, '-tabs ')]/../div[1]/div[2]/div/div[2]", "Данные о создании перехода", self.page
        )

        self.CONDITIONALS_BTN = Element("[id*=tab-conditions]", "Вкладка 'Условия перехода'", self.page)
        self.CONDITIONALS = ElementsList("[id*=panel-conditions] [class*=-collapse-item]", "Условия перехода", self.page)
        self.ACTIONS_BTN = Element("[id*=tab-actions]", "Вкладка 'Действия при переходе'", self.page)
        self.ACTIONS = ElementsList("[id*=panel-actions] [class*=-collapse-item]", "Действия при переходе", self.page)

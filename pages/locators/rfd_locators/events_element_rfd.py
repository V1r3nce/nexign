from playwright.sync_api import Page

from pages.locators.rfd_locators.base_elements_rfd import BaseElementsRfd
from pages.ui_elements import Element, ElementsList


class EventsElementsRfd(BaseElementsRfd):
    """Страница История событий /ps/refdata/events-history Refdata UI"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.EVENTS_TAB = ElementsList('a[class="n-tab__title"]', "Табы страницы", self.page)
        # NOTIFICATIONS
        self.EVENTS = ElementsList('tr[class="n-grid__row bi-focus-element-wrapper__ng"]', "События", self.page)
        self.CONSUMER_CODE_FLD = Element(
            "input[ng-model=\"$ctrl.notificationsHistoryGrid.filters['referenceConsumerId']\"]",
            "Поле поиска код потребителя",
            self.page,
        )
        self.REFRESH_EVENTS_BTN = Element(
            'ps-button[icon="refresh"][ng-click="$ctrl.fetchEventsHistoryNotifications()"]',
            "Кнопка 'Обновить'",
            self.page,
        )
        self.DESCRIPTION_JSON = Element(
            '[data="$ctrl.notificationsHistoryGrid.selectedItem"] > div > pre',
            "Описание события в формате JSON",
            self.page,
        )

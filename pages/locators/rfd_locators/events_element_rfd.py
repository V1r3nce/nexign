from pages.locators.rfd_locators.base_elements_rfd import BaseRfdElements
from pages.ui_elements import Element, ElementsList


class EventsRfdElements(BaseRfdElements):
    """Страница История событий /ps/refdata/events-history Refdata UI"""

    def __init__(self) -> None:
        super().__init__()

        self.EVENTS_TAB = ElementsList('a[class="n-tab__title"]', "Табы страницы")
        # NOTIFICATIONS
        self.EVENTS = ElementsList('tr[class="n-grid__row bi-focus-element-wrapper__ng"]', "События")
        self.CONSUMER_CODE_FLD = Element(
            "input[ng-model=\"$ctrl.notificationsHistoryGrid.filters['referenceConsumerId']\"]",
            "Поле поиска код потребителя",
        )
        self.REFRESH_EVENTS_BTN = Element(
            'ps-button[icon="refresh"][ng-click="$ctrl.fetchEventsHistoryNotifications()"]',
            "Кнопка 'Обновить'",
        )
        self.DESCRIPTION_JSON = Element(
            '[data="$ctrl.notificationsHistoryGrid.selectedItem"] > div > pre',
            "Описание события в формате JSON",
        )

from pages.locators.base_elements import BaseElements
from pages.ui_elements import Element, ElementsList


class HomePage(BaseElements):
    """Страница /welcome Домашняя"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER PANEL
        self.CUSTOMER_NAME = Element("#customerName", "Клиент")
        self.INN = Element("#taxIdentificationNumber", "ИНН")

        # WORK_TABLE
        self.SETTINGS_BTN = Element("//span[@data-icon='Settings']", "Кнопка настройки")
        self.WIDGETS = ElementsList(".react-grid-layout > div", "Виджеты")
        self.WIDGET_LABEL = ElementsList(".react-grid-layout > div h4", "Название виджета")
        self.WIDGET_TEXT = ElementsList(".react-grid-layout > div h1", "Текст виджета")
        self.WIDGET_DRAG_INDICATOR = ElementsList(
            "//span[@data-icon='DragIndicator']", "Индикатор для перетаскивания виджета"
        )
        self.WIDGET_RESIZE_HANDLE = ElementsList(
            "//span[@data-icon='ResizeHandle']", "Индикатор для изменения размера виджета"
        )
        self.WIDGET_MORE_BTN = ElementsList("//span[@data-icon='MoreVert']", "Кнопки больше на виджетах")
        self.WIDGET_DELETE_BTN = ElementsList("//ul[@role='menu']", "Кнопка удалить в вертикальном меню виджета")
        self.WIDGET_REFRESH_BTN = ElementsList("//span[@data-icon='Refresh']", "Кнопка обновить на виджете")

        # QUICK_ACTIONS_WIDGET
        self.CREATE_ORG_BTN = Element("#createOrganization", "Создать клиент ЮЛ")
        self.CREATE_CUSTOMER_BTN = Element("#createIndividual", "Создать клиент ФЛ")
        self.CREATE_ENTREPRENEUR_BTN = Element("#createEntrepreneur", "Создать клиента ИП")
        self.LAST_INQUIRY_BTN = Element("#lastInquiry", "Последняя заявка")

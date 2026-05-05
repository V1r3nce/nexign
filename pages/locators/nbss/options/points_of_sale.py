from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import Autocomplete, Element, ElementsList, ScrollableList, Select


class PointsOfSale(BaseElements):
    """Страница 'Точки Продаж'"""

    def __init__(self) -> None:
        super().__init__()

        self.CREATE_BTN = Element(
            "div[role=tabpanel] div[class*=platform-table] button[type=button][class*=btn-primary]", "Кнопка 'Создать'"
        )
        self.POINTS_SALE = ElementsList(
            "[role=tabpanel] [class*=table-wrapper] [class*=table-tbody] [class*=table-column]",
            "Торговые точки",
        )
        self.EDIT_BTN = Element(
            "div[role=tabpanel] div[class*=platform-table] button[class*=btn-default]:not([title])",
            "Кнопка 'Редактировать'",
        )
        self.USER_LIST = ElementsList(
            "div[class*=spin-nested-loading] div[class*=scrollable-body] div[overflow]", "Список Пользователей"
        )
        self.ADD_BTN = Element(
            "div[class*=platform-table] button[type=button][class*=variant-solid]", "Кнопка 'Добавить'"
        )
        self.LIST_POINTS_SALE_USER = ElementsList(
            "div[class*=table-tbody] div[data-row-key]", "Список Точек Продаж Пользователя"
        )
        self.INPUT_NAME_IN_SEARCH = Element(
            "(//span[contains(@class, 'input-affix')]//input[contains(@class, 'input') and @placeholder])[2]",
            "Поле для поиска по ФИО",
        )
        self.USER_POINTS_SALE = ElementsList(
            "ul[class*=dropdown-menu] p[data-name=paragraph]", "Точки продаж пользователя"
        )
        self.USERS_LIST_SCROLLABLE = Element(
            "[class*=platform-custom-list-scrollable-body]", "Скроллящийся контейнер списка пользователей"
        )
        self.USER_NAME = ElementsList(
            "[class*=platform-custom-list-scrollable-body] p[data-name=description]", "Имя пользователя в списке"
        )
        self.USERS_VIRTUAL_LIST = ScrollableList(
            path="[class*=platform-custom-list-scrollable-body]",
            item_path="p[data-name=description]",
            locator_name="Список пользователей точек продаж",
        )
        self.DELETE_BTN = Element(
            "div[class*=platform-table] button[type=button][class*=variant-outlined]:not([aria-describedby])",
            "Кнопка 'Удалить'",
        )
        self.REFRESH_BTN = Element("//span[@data-icon='Refresh']/..", "Кнопка 'Обновить'")
        self.FIND_NAME_POINT = Element(
            "(//thead[contains(@class,'table-thead')]//span[contains(@class,'input-outlined')]//input)[1]",
            "Поле 'Точка'",
        )

        # MODAL WINDOW
        self.ACCEPT_BTN = Element(
            "div[class*=modal-content] div[class*=footer] button", "Подтверждающая кнопка удаления"
        )


class FormCreatePointsOfSale(DynamicForms):
    """Форма 'Создание точки продаж'"""

    def __init__(self) -> None:
        super().__init__()

        self.INPUT_NAME = Element("#name", "Поле 'Наименование'")
        self.INPUT_CODE = Element("#code", "Поле 'Код точки'")
        self.SELECT_STATUS = Select("#partnerPointStatusId", "'Поле Статус'")
        self.INPUT_ADDRESS = Autocomplete("#address", "Поле 'Адрес'")


class FormAddUserPointsOfSale(DynamicForms):
    """Форма 'Добавление точки продаж'"""

    def __init__(self) -> None:
        super().__init__()
        self.SELECT_POINTS_SALE = Select("span[class*=selection-item]", "Выбор точки продаж")
        self.POINTS_SALE = ElementsList(
            "div[class*=drawer-content][role]:not([style]) div[class*=list-scrollable-body] div[overflow][class]",
            "Список точек продаж",
        )

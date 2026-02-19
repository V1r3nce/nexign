from pages.locators.base_elements import BaseElements
from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import Autocomplete, Element, ElementsList, Select


class PointsOfSale(BaseElements):
    """Страница 'Точки Продаж'"""

    def __init__(self) -> None:
        super().__init__()

        self.CREATE_BTN = Element(
            "div[role=tabpanel] div[class*=platform-table] button[type=button][class*=btn-primary]", "Кнопка 'Создать'"
        )
        self.POINTS_SALE = ElementsList(
            "div[role=tabpanel] div[class*=table-wrapper] div[class*=table-body] td[class*=table-column]",
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
            "div[class*=table-small] tbody[class*=table-tbody] tr[data-row-key]", "Список Точек Продаж Пользователя"
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

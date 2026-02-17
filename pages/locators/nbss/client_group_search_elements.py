from pages.ui_elements import Element, Select


class ClientGroupsSearchElements:
    """Страница /customer-hierarchy-management/customer-groups/search
    'Поиск группы клиентов'"""

    def __init__(self) -> None:
        super().__init__()

        self.ADD_BTN = Element(
            "[class*='platform-table'] button[class*='btn-primary']",
            "Кнопка '+ Добавить'",
        )

        self.NAME_INPUT = Element("#customer-group-creation_corporateName", "Поле 'Имя'")
        self.TYPE_SELECT = Select("#customer-group-creation_type", "Дропдаун 'Тип'")
        self.COMMENT_INPUT = Element("#customer-group-creation_note", "Поле 'Комментарий'")

        self.EDIT_NAME_INPUT = Element("#customer-group-card-edit_corporateName", "Поле редактирования 'Имя'")
        self.EDIT_COMMENT_INPUT = Element("#customer-group-card-edit_note", "Поле редактирования 'Комментарий'")

        self.CREATE_BTN = Element(
            "[class*='bottom-toolbar-area'] div:not([data-item-key]) > button[type='submit']", "Кнопка 'Создать'"
        )
        self.EDIT_BTN = Element("[class*='btn-default']", "Кнопка 'Редактировать'")

        self.GROUP_NAME = Element("[class*='scrollable-container'] h3", "Заголовок 'Имя группы клиентов'")
        self.GROUP_TYPE = Element("[class*='select-selection-item']", "Поле 'Тип'")
        self.COMMENT = Element("#customer-group-card-view_note", "Поле 'Комментарий'")

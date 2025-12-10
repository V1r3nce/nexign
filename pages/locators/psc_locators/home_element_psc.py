from pages.locators.psc_locators.base_elements_psc import BasePscElements
from pages.ui_elements import Element, ElementsList


class HomePscElements(BasePscElements):
    """Страница Домашняя PSC UI"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER PANEL
        self.PROJECTS_BTN = Element("a[data-test='item:projects']", "Кнопка 'Проекты'")
        self.SPECIFICATIONS_BTN = Element("a[data-test='item:specifications']", "Кнопка 'Спецификации'")

        # HEADERS SPECIFICATIONS TAB
        self.FUNCTION_TECH_LAYER_BTN = Element("#tab-functional-layer", "Кнопка 'Функционально-технический слой'")

        # HEADERS FUNCTION_TECH_LAYER
        self.PS_BTN = Element("#tab-specifications-ps", "Кнопка 'PS'")

        # PS TAB
        self.CREATE_PS_BTN = Element("button[data-test='PscButton:create']", "Кнопка 'Создать' PS")
        self.PS_NAMES = ElementsList("[data-test='PscTableCellUniversal'] button", "Таблица строки 'Название'")
        self.PS_STATUSES = ElementsList("[data-test='PscTableCell:status'] div", "Таблица строки 'Статус'")

        # PROJECT TAB
        self.CREATE_PROJECT_BTN = Element("button[data-test='PscButton:create-project']", "Кнопка 'Создать'")
        self.PROJECT_NAMES = ElementsList("[data-test='PscTableCell:title'] a", "Таблица строки 'Название'")
        self.PROJECT_STATUSES = ElementsList(
            "[data-test='PscTableCell:lifecycleStatus-isDraft'] div", "Таблица строки 'Статус'"
        )


class CreateProductSpecificationForm(BasePscElements):
    """Форма Создание продуктовой спецификации"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[data-test='PscDialog'] h3", "Заголовок формы")
        self.STEP_NAME = ElementsList("//*[@class='psc-dialog']//p", "Название шага")
        self.NAME_INPUT = Element("input[data-test='ElInput:name']", "Поле ввода 'Название'")
        self.CODE_INPUT = Element("input[data-test='ElInput:code']", "Поле ввода 'Код'")
        self.TYPE_DROPDOWN_BTN = Element(
            "[data-test*='DictionarySingleSelect:product_specification_type'] [data-test='PscIcon:arrow-triangle-down']",
            "Кнопка открытия 'Тип'",
        )
        self.TYPE_OPTIONS = ElementsList("[data-test='PscOption']", "Варианты 'Тип'")
        self.IS_ONE_TIME_INPUT = Element(
            "[data-test='PscBooleanSelect:is-one-time'] input", "Поле ввода 'Продукт одноразовый'"
        )
        self.START_DATE_INPUT = Element("[data-test='ElDatePicker:daterange-from'] input", "Поле ввода 'Дата начала'")
        self.DESCRIPTION_INPUT = Element("[data-test='ElInput:description']", "Поле ввода 'Описание'")
        self.ADD_CFSS_BTN = Element("//button[contains(@title, 'CFSS')]", "Кнопка 'Добавить CFSS'")
        self.CFSS_INPUT = Element("[data-test='PscSelectDropdown'] input", "Поле ввода 'CFSS'")
        self.CHOSEN_CFSS_OPTIONS = ElementsList(".list-item [data-test='PscLinkButton'] button", "Варианты 'CFSS'")
        self.CFSS_OPTIONS = ElementsList("div.option-double-string-title", "Варианты 'CFSS'")
        self.CHARACTERISTICS_STATUS_BTN = ElementsList(
            "[data-test='PscTabSwitcher'] div", "Кнопки статусов 'Характеристики'"
        )
        self.CHARACTERISTIC_DROPDOWN_BTN = Element(
            ".characteristic-value-container [data-test='PscIcon:arrow-triangle-down']",
            "Кнопка открытия 'Характеристики'",
        )
        self.CHARACTERISTIC_OPTIONS = ElementsList("[class*='psc-option']", "Значения для выбранной 'Характеристики'")
        self.CHARACTERISTIC_MENU = Element("[data-test='ElButton:show-menu']", "Меню 'Характеристики'")
        self.META_CHARACTERISTIC_BTN = Element(
            "[data-test='ElDropdownItem:OPEN_META_CHARS']", "Пункт меню ' Метахарактеристики '"
        )
        self.RADIO_OPTIONS_FOR_ATTRIBUTES = ElementsList(
            "label .font-size-medium", "Радио батоны 'В разработке/Действует'"
        )
        self.CREATE_BTN = Element("button.button-done", "Кнопка 'Создать'")


class CreateProjectForm(BasePscElements):
    """Форма Создание проекта"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[data-test='ProjectCreateDialog'] h3", "Заголовок формы")
        self.TYPE_BTNS = ElementsList("[data-test='PscTabSwitcher'] div", "Кнопки 'Проект/Черновик проекта'")
        self.PROJECT_NAME = ElementsList("input[data-test='ElInput:title']", "Название проекта")
        self.START_DATE_INPUT = Element(
            "[data-test='PscDatePicker:start-date'] input", "Поле ввода 'Дата вступления в силу'"
        )
        self.DESCRIPTION_INPUT = Element("[data-test='ElInput:description']", "Поле ввода 'Описание'")

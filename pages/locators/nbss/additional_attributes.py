from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import DynamicForms
from pages.ui_elements import DynamicField, Element, ElementsList, Select, VirtualSelect


class AdditionalAttributesElements(DynamicForms):
    """Форма Дополнительные атрибуты"""

    def __init__(self) -> None:
        super().__init__()
        self.base_page = BasePage()

        self.ADD_BUTTON = Element(
            "[class*=platform-toolbar] > div:nth-child(1) button:has([data-icon=Add])",
            "Кнопка 'Добавить'",
        )
        self.RESET_FILTER = Element(
            "[class*=platform-toolbar] > div:nth-child(1) button:has([data-icon=Refresh])",
            "Кнопка очистить фильтры",
        )
        self.ENTITY_CODE = ElementsList("[class*=table-row] [class*=table-cell]:nth-child(4)", "Код атрибута")
        self.ENTITY_TYPE = ElementsList("[class*=table-row] [class*=table-cell]:nth-child(1)", "Тип сущности")
        self.ENTITY_STATUS = ElementsList("[class*=table-row] [class*=table-cell]:nth-child(3)", "Статус сущности")
        self.ATTRIBUTE_TYPE = ElementsList("[class*=table-row] [class*=table-cell]:nth-child(5)", "Тип атрибута")
        self.ENTITY_SORT = ElementsList("//div[contains(@class, 'able-column-has-sorters')]", "Столбцы с сортировкой")
        self.ERROR_WINDOW = Element(
            "//div[@role='dialog' and contains(@class,'ant-modal')]", "Окно с сообщением об ошибке"
        )
        self.EDIT_BUTTON = Element(
            "[class*=platform-toolbar] > div:nth-child(1) button:has([data-icon=Edit])",
            "Кнопка редактировать",
        )
        self.ENTITY_SEARCH = Element(
            "[class*=platform-table-header-column-filter] span:has([data-icon=SmallClose]) input",
            "Поле с вводом для поиска по коду атрибута",
        )
        self.ENTITY_SEARCH_CLEAR = Element("//th [4] //button[contains(@class,'-input-clear-icon')]", "Очистка фильтра")
        self.STATUS_BUTTON = VirtualSelect(
            "(//div[contains(@class, '-column-filter')]) [3]",
            "Поле для выбора статуса атрибута",
        )
        self.ENTITY_BUTTON = VirtualSelect(
            "(//div[contains(@class, '-column-filter')]) [1]",
            "Поле для выбора статуса атрибута",
        )
        self.DELETE_BUTTON = Element(
            "[class*=platform-toolbar] > div:nth-child(1) button:has([data-icon=Delete])", "Кнопка удалить"
        )
        # Sidebar

        self.NAME = Element("//input[contains(@id,'attribute_nameOfAttr')]", "Поля для ввода названия атрибута")
        self.ENTITY = Select("//input[contains(@id,'attribute_entity')]", "Поле для выбора сущности")
        self.CODE = Element("//input[contains(@id,'attribute_codeOfAttr')]", "Поле для ввода кода атрибута")
        self.TYPE = Select("//input[contains(@id,'attribute_typeOfAttr')]", "Поле для выбора типа атрибута")
        self.UI_TYPE = Select("//input[contains(@id,'attribute_uiType')]", "Поле для выбора типа атрибута на интерфейсе")
        self.HINT_TEXT = Element("//input[@id='add-attribute_helpText']", "Поле для ввода текста подсказки")
        self.CHECKBOXES = ElementsList(
            "//div[contains(@class,'form-item')] //label[contains(@class,'checkbox-wrapper-checked')]",
            "Чекбоксы в сайдбаре",
        )
        self.APPLY_BUTTON = Element(
            "[class*=platform-toolbar] > div:nth-child(1) [type=submit][class*=btn-primary]",
            "Кнопка добавить в сайдбаре",
        )
        self.APPLY_EDIT_BUTTON = Element(
            "(//div[@role='dialog']//div[contains(@class, 'platform-toolbar')])[3]//button",
            "Кнопка сохранить при редактировании атрибута",
        )
        self.MIN_CARDINALITY = Element(
            "//input[@id='add-attribute_numberOfValues']", "Поле для ввода минимального количества значений"
        )
        self.MAX_CARDINALITY = Element(
            "//input[contains(@id,'add-attribute_numberOfValues_right')]",
            "Поле для ввода максимального количества значений",
        )
        self.GET_DICT_METHOD = Select(
            "//input[contains(@id,'attribute_wayToGetTheValuesDictionary')]",
            "Поле способ получения справочника",
        )
        self.SIDEBAR_DICTIONARY = Element(
            "//input[contains(@id,'attribute_typeOfAttr')] /../../span[@title='DICTIONARY']",
            "Локатор выбранный тип словарь",
        )
        self.GET_DICT_STR = Element(
            "//input[contains(@id,'attribute_callMethodGetDict')]", "Поле способ получения справочника"
        )
        self.GET_DICT_STR_METHOD = Select(
            "//input[contains(@id,'attribute_method')]", "Поле способ получения справочника"
        )
        self.RESPONSE_ID_ATTRIBUTE = Element(
            "//input[contains(@id,'attribute_idValue')]", "Поле способ получения справочника"
        )
        self.RESPONSE_NAME_ATTRIBUTE = Element(
            "//input[contains(@id,'attribute_nameValue')]", "Поле способ получения справочника"
        )
        self.INPUT_QUERY_PARAM = Element(
            "//input[contains(@id,'attribute_queryParam')]", "Поле способ получения справочника"
        )
        self.EDIT_CLEAR_NAMES = ElementsList(
            "//span[contains(@class,'platform-multilingual-input-input')] //button[contains(@class,'-input-clear-icon')]",
            "Кнопки стереть",
        )
        self.CLOSE = Element("button:has([data-icon='Close'])", "Кнопка закрыть сайдбар")
        self.TEMPLATE = Select("//input[contains(@id,'attribute_templateOfAttr')]", "Поле для выбора шаблона атрибута")
        self.NAME_FILL_ERROR = ElementsList(
            "//span[contains(@class,'item-explain-error')]", "Надпись с ошибкой заполнения имени"
        )
        self.FILL_ERROR = ElementsList("//div[contains(@class,'item-explain-error')]", "Надпись с ошибкой заполнения")
        self.ATTRIBUTES_CREATE_CLIENT_FORM = DynamicField(
            ".platform-grid-container", ".platform-grid-item", "input", "Селектор для выбора атрибута"
        )
        self.ATTRIBUTES_PROFILE_CHECKBOX = DynamicField(
            ".platform-grid-container",
            ".platform-grid-item",
            "label > span:last-child",
            "Селектор для выбора атрибута",
        )
        self.ATTRIBUTE_CODE_LIST = DynamicField(
            "[class*=table-tbody]",
            "[class*=table-row]",
            "[class*=table-cell]:nth-child(4)",
            "Селектор для выбора атрибута",
        )

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.dynamic_form_elements import DynamicForms
from pages.ui_elements import DynamicField, Element, ElementsList, Select, VirtualSelect


class AdditionalAttributes(DynamicForms):
    """Форма Дополнительные атрибуты"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.base_page = BasePage(page)

        self.ADD_BUTTON = Element(
            "(//div[contains(@class,'platform-toolbar-item')] //button[@variant='primary']) [1]",
            "Кнопка 'Добавить'",
            self.page,
        )
        self.RESET_FILTER = Element(
            "(//div[contains(@class,'platform-toolbar-item')] //button[@variant='default']) [2]",
            "Кнопка очистить фильтры",
            self.page,
        )
        self.ENTITY_CODE = ElementsList("//table //td[4] /div", "Код атрибута", self.page)
        self.ENTITY_TYPE = ElementsList("//table //td[1] /div", "Тип сущности", self.page)
        self.ENTITY_STATUS = ElementsList("//table //td[3] //div", "Статус сущности", self.page)
        self.ENTITY_SORT = ElementsList(
            "//div[contains(@class, '-table-column-sorters')]", "Столбцы с сортировкой", self.page
        )
        self.ERROR_WINDOW = Element(
            "//div[@role='dialog' and contains(@class,'ant-modal')]", "Окно с сообщением об ошибке", self.page
        )
        self.EDIT_BUTTON = Element(
            "(//button[@type='button' and @variant='default']) [3]", "Кнопка редактировать", self.page
        )
        self.ENTITY_SEARCH = Element(
            "//th[contains(@class, '-table-column-has-sorters')] //input[contains(@class,'-input') and @type='text']",
            "Поле с вводом для поиска по коду атрибута",
            self.page,
        )
        self.ENTITY_SEARCH_CLEAR = Element(
            "//th [4] //button[contains(@class,'-input-clear-icon')]", "Очистка фильтра", self.page
        )
        self.STATUS_BUTTON = VirtualSelect(
            "(//div[contains(@class, 'platform-custom-table-header-column-filter')]) [3]",
            "Поле для выбора статуса атрибута",
            self.page,
        )
        self.ENTITY_BUTTON = VirtualSelect(
            "(//div[contains(@class, 'platform-custom-table-header-column-filter')]) [1]",
            "Поле для выбора статуса атрибута",
            self.page,
        )
        self.DELETE_BUTTON = Element(
            "(//button[@type='button' and @variant='default']) [4]", "Кнопка удалить", self.page
        )
        self.DELETE_MESSAGE_BUTTON = Element(
            "(//button[@type='button' and @variant='primary'])[3]", "Кнопка для подтверждения удаления", self.page
        )
        # Sidebar

        self.NAMES = ElementsList(
            "//input[contains(@id,'attribute_nameOfAttr')]", "Поля для ввода названия атрибута", self.page
        )
        self.ENTITY = Select("//input[contains(@id,'attribute_entity')]", "Поле для выбора сущности", self.page)
        self.CODE = Element("//input[contains(@id,'attribute_codeOfAttr')]", "Поле для ввода кода атрибута", self.page)
        self.TYPE = Select("//input[contains(@id,'attribute_typeOfAttr')]", "Поле для выбора типа атрибута", self.page)
        self.UI_TYPE = Select(
            "//input[contains(@id,'attribute_uiType')]", "Поле для выбора типа атрибута на интерфейсе", self.page
        )
        self.HINT_TEXT = Element("//input[@id='add-attribute_helpText']", "Поле для ввода текста подсказки", self.page)
        self.CHECKBOXES = ElementsList(
            "//div[contains(@class,'platform-dynamic-form-form-item')] //label[contains(@class,'checkbox-wrapper-checked')]",
            "Чекбоксы в сайдбаре",
            self.page,
        )
        self.APPLY_BUTTON = Element(
            "(//button[@type='submit' and @variant='primary']) [1]", "Кнопка добавить в сайдбаре", self.page
        )
        self.APPLY_EDIT_BUTTON = Element(
            "(//div[contains(@class,'-drawer-wrapper-body')] //button[@type='button' and @variant='primary']) [1]",
            "Кнопка сохранить при редактировании атрибута",
            self.page,
        )
        self.MIN_CARDINALITY = Element(
            "//input[@id='add-attribute_numberOfValues']", "Поле для ввода минимального количества значений", self.page
        )
        self.MAX_CARDINALITY = Element(
            "//input[contains(@id,'add-attribute_numberOfValues_right')]",
            "Поле для ввода максимального количества значений",
            self.page,
        )
        self.GET_DICT_METHOD = Select(
            "//input[contains(@id,'attribute_wayToGetTheValuesDictionary')]",
            "Поле способ получения справочника",
            self.page,
        )
        self.SIDEBAR_DICTIONARY = Element(
            "//input[contains(@id,'attribute_typeOfAttr')] /../../span[@title='DICTIONARY']",
            "Локатор выбранный тип словарь",
            page,
        )
        self.GET_DICT_STR = Element(
            "//input[contains(@id,'attribute_callMethodGetDict')]", "Поле способ получения справочника", self.page
        )
        self.GET_DICT_STR_METHOD = Select(
            "//input[contains(@id,'attribute_method')]", "Поле способ получения справочника", self.page
        )
        self.RESPONSE_ID_ATTRIBUTE = Element(
            "//input[contains(@id,'attribute_idValue')]", "Поле способ получения справочника", self.page
        )
        self.RESPONSE_NAME_ATTRIBUTE = Element(
            "//input[contains(@id,'attribute_nameValue')]", "Поле способ получения справочника", self.page
        )
        self.INPUT_QUERY_PARAM = Element(
            "//input[contains(@id,'attribute_queryParam')]", "Поле способ получения справочника", self.page
        )
        self.EDIT_CLEAR_NAMES = ElementsList(
            "//span[contains(@class,'platform-multilingual-input-input')] //button[contains(@class,'-input-clear-icon')]",
            "Кнопки стереть",
            self.page,
        )
        self.CLOSE = Element(
            "//div[contains(@class,'-drawer-content')] //button[@aria-label='Close']",
            "Кнопка закрыть сайдбар",
            self.page,
        )
        self.TEMPLATE = Select(
            "//input[contains(@id,'attribute_templateOfAttr')]", "Поле для выбора шаблона атрибута", self.page
        )
        self.NAME_FILL_ERROR = ElementsList(
            "//span[contains(@class,'item-explain-error')]", "Надпись с ошибкой заполнения имени", self.page
        )
        self.FILL_ERROR = ElementsList(
            "//div[contains(@class,'item-explain-error')]", "Надпись с ошибкой заполнения", self.page
        )
        self.ATTRIBUTES_CREATE_CLIENT_FORM = DynamicField(
            ".platform-grid-container", ".platform-grid-item", "span > input", "Селектор для выбора атрибута", self.page
        )
        self.ATTRIBUTES_PROFILE_CHECKBOX = DynamicField(
            ".platform-grid-container",
            ".platform-grid-item",
            "label > span:last-child",
            "Селектор для выбора атрибута",
            self.page,
        )
        self.ATTRIBUTE_CODE_LIST = DynamicField(
            "//tbody",
            "//tr",
            "td:nth-child(4) > div",
            "Селектор для выбора атрибута",
            self.page,
        )

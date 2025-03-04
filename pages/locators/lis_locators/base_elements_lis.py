from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList


class BaseElementsLis:

    def __init__(self, page: Page):
        self.page = page

        self.ADD_BUTTON = Element(".n-popup ps-button[on-submit*='onFormSubmit()']", "Кнопка 'Добавить'",
                                  self.page)
        self.SAVE_BUTTON = Element(".n-popup ps-button[on-submit*='updatePhoneNumber()']",
                                   "Кнопка 'Сохранить'", self.page)
        self.MASS_SAVE_BUTTON = Element(".n-popup ps-button[on-submit*='massUpdatePhoneNumber']",
                                        "Кнопка 'Сохранить'", self.page)
        self.CANCEL_BUTTON = Element(".n-popup ps-button[icon*='block']", "Кнопка 'Отменить'", self.page)

        # MODAL
        self.MODAL = ElementsList("div.n-popup", "Модальное окно", self.page)
        self.MODAL_X_BTN = Element("[ng-show*='titleButtons.close.visible']", "Кнопка Х закрыть модального окна",
                                   self.page)
        self.MODAL_TITLE = ElementsList("div.n-popup-head__title", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = ElementsList("div.n-popup-message-text", "Текст модального окна", self.page)
        self.MODAL_BODY_INPUT = Element("div.n-popup textarea", "Поле ввода модального окна", self.page)
        self.MODAL_DROP_DOWN_BTN = Element("div.n-popup ps-button[ng-if*='options.showDropDownButton']",
                                           "Кнопка всплывающего списка модального окна", self.page)
        self.FIRST_BTN = ElementsList("div.n-popup ps-button:first-child", "Первая кнопка модального окна",
                                      self.page)
        self.SECOND_BTN = ElementsList("div.n-popup ps-button:last-child", "Вторая кнопка модального окна",
                                       self.page)
        self.OK_BTN = Element("//ps-button[contains(text(), 'OK')]", "Кнопка 'ОК'",
                              self.page)
        self.FIRST_BTN_CONFIRMATION = Element("[ps-dialog-controller*='psDialog'] ps-button:first-child",
                                              "Первая кнопка модального окна подтверждения операции", self.page)
        self.SECOND_BTN_CONFIRMATION = Element("[ps-dialog-controller*='psDialog'] ps-button:last-child",
                                               "Вторая кнопка модального окна подтверждения операции", self.page)
        self.TABLE_FIRST_COLUMN_ELEMENTS = ElementsList("div.n-popup tbody tr td:nth-child(1)",
                                                        "Элементы первой колонки таблицы модального окна", self.page)
        self.REFRESH_MODAL_TABLE_BTN = Element("div.n-popup [ng-click*='refreshGrid']",
                                               "Кнопка 'Обновить данные'", self.page)

        # Шаблоны
        self.CHOOSE_SEARCH_TEMPLATE_BTN = Element("//div[contains(@ng-click, 'loadTemplates()')][2]",
                                                  "Кнопка 'Выбрать шаблон поиска'", self.page)
        self.TEMPLATE_OPTIONS = ElementsList("[ng-repeat*='item in templates.data'][ng-click]",
                                             "Варианты шаблонов поиска'", self.page)
        self.SAVE_SEARCH_TEMPLATE_BTN = Element("//div[contains(@ng-click, 'loadTemplates()')][1]",
                                                "Кнопка 'Сохранить шаблон поиска'", self.page)
        self.NEW_TEMPLATE_BTN = Element("//span[text()='Новый шаблон']/parent::div",
                                        "Кнопка 'Новый шаблон'", self.page)
        self.REMOVE_TEMPLATE_BTN = Element("[ng-click*='dialogs.deleteTemplate.open']",
                                           "Кнопка 'Удалить текущий шаблон'", self.page)
        self.HIDE_FILTER_BTN = Element("a.lis-search-numbers-params__hide", "Кнопка 'Скрыть параметры поиска'",
                                       self.page)

        # Модальное окно сохранения шаблона
        self.NEW_TEMPLATE_NAME_INPUT = Element("[ng-model*='dialogs.addTemplate.templateName']",
                                               "Поле ввода названия шаблона", self.page)
        self.TEMPLATE_SAVE_BTN = Element("[on-submit*='dialogs.addTemplate.addNewTemplate']",
                                         "Кнопка 'Сохранить' шаблон", self.page)
        self.TEMPLATE_CANCEL_BTN = Element("[ng-click*='dialogs.addTemplate.close']",
                                           "Кнопка 'Отменить' создание шаблона", self.page)

        # Модальное окно выбора коммутатора
        self.COMMUTATOR_TYPE_NAMES = ElementsList("//ps-grid[contains(@rows, 'commutatorDialog.model.equipments.rows')]"
                                                  "//tbody/tr/td[1]", "Варианты выбора коммутатора в таблице",
                                                  self.page)
        self.COMMUTATOR_TYPE_NAME_SEARCH = ElementsList("[ng-model*='commutatorDialog.model.equipments.filter.name']",
                                                        "Поиск по вариантам выбора коммутатора в таблице", self.page)
        self.COMMUTATOR_SUBMIT_BTN = Element("[on-submit*='commutatorDialog.submit']",
                                             "Кнопка 'Выбрать'", self.page)

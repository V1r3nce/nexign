from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList


class BaseElementsLis:
    def __init__(self, page: Page):
        self.page = page

        self.PAGE_TITLE = Element("h2.content-section-header", "Заголовок страницы", self.page)

        self.ADD_BUTTON = Element(".n-popup ps-button[on-submit*='onFormSubmit()']", "Кнопка 'Добавить'", self.page)
        self.SAVE_BUTTON = Element(
            ".n-popup ps-button[on-submit*='updatePhoneNumber()']", "Кнопка 'Сохранить'", self.page
        )
        self.MASS_SAVE_BUTTON = Element(
            ".n-popup ps-button[on-submit*='massUpdatePhoneNumber']", "Кнопка 'Сохранить'", self.page
        )
        self.CANCEL_BUTTON = Element(".n-popup ps-button[icon*='block']", "Кнопка 'Отменить'", self.page)

        # MODAL
        self.MODAL = ElementsList("div.n-popup", "Модальное окно", self.page)
        self.MODAL_X_BTN = Element(
            "[ng-show*='titleButtons.close.visible']", "Кнопка Х закрыть модального окна", self.page
        )
        self.MODAL_TITLE = ElementsList("div.n-popup-head__title", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = ElementsList("div.n-popup-message-text", "Текст модального окна", self.page)
        self.MODAL_BODY_INPUT = Element("div.n-popup textarea", "Поле ввода модального окна", self.page)
        self.MODAL_DROP_DOWN_BTN = Element(
            "div.n-popup ps-button[ng-if*='options.showDropDownButton']",
            "Кнопка всплывающего списка модального окна",
            self.page,
        )
        self.MODAL_FIRST_BTN = ElementsList(
            "div.n-popup ps-button:first-child", "Первая кнопка модального окна", self.page
        )
        self.MODAL_SECOND_BTN = ElementsList(
            "div.n-popup ps-button:last-child", "Вторая кнопка модального окна", self.page
        )
        self.OK_BTN = Element("//ps-button[contains(text(), 'OK')]", "Кнопка 'ОК'", self.page)
        self.FIRST_BTN_CONFIRMATION = Element(
            "[ps-dialog-controller*='psDialog'] ps-button:first-child",
            "Первая кнопка модального окна подтверждения операции",
            self.page,
        )
        self.SECOND_BTN_CONFIRMATION = Element(
            "[ps-dialog-controller*='psDialog'] ps-button:last-child",
            "Вторая кнопка модального окна подтверждения операции",
            self.page,
        )
        self.TABLE_FIRST_COLUMN_ELEMENTS = ElementsList(
            "div.n-popup tbody tr td:nth-child(1)", "Элементы первой колонки таблицы модального окна", self.page
        )
        self.REFRESH_MODAL_TABLE_BTN = Element(
            "div.n-popup [ng-click*='refreshGrid']", "Кнопка 'Обновить данные'", self.page
        )

        # Шаблоны
        self.CHOOSE_SEARCH_TEMPLATE_BTN = Element(
            "//div[contains(@ng-click, 'loadTemplates()')][2]", "Кнопка 'Выбрать шаблон поиска'", self.page
        )
        self.TEMPLATE_OPTIONS = ElementsList(
            "[ng-repeat*='item in templates.data'][ng-click]", "Варианты шаблонов поиска'", self.page
        )
        self.SAVE_SEARCH_TEMPLATE_BTN = Element(
            "//div[contains(@ng-click, 'loadTemplates()')][1]", "Кнопка 'Сохранить шаблон поиска'", self.page
        )
        self.NEW_TEMPLATE_BTN = Element("//span[text()='Новый шаблон']/parent::div", "Кнопка 'Новый шаблон'", self.page)
        self.REMOVE_TEMPLATE_BTN = Element(
            "[ng-click*='dialogs.deleteTemplate.open']", "Кнопка 'Удалить текущий шаблон'", self.page
        )
        self.HIDE_FILTER_BTN = Element(
            "a.lis-search-numbers-params__hide", "Кнопка 'Скрыть параметры поиска'", self.page
        )

        # Модальное окно сохранения шаблона
        self.NEW_TEMPLATE_NAME_INPUT = Element(
            "[ng-model*='dialogs.addTemplate.templateName']", "Поле ввода названия шаблона", self.page
        )
        self.TEMPLATE_SAVE_BTN = Element(
            "[on-submit*='dialogs.addTemplate.addNewTemplate']", "Кнопка 'Сохранить' шаблон", self.page
        )
        self.TEMPLATE_CANCEL_BTN = Element(
            "[ng-click*='dialogs.addTemplate.close']", "Кнопка 'Отменить' создание шаблона", self.page
        )

        # Модальное окно выбора коммутатора
        self.COMMUTATOR_TYPE_NAMES = ElementsList(
            "//ps-grid[contains(@rows, 'commutatorDialog.model.equipments.rows')]//tbody/tr/td[1]",
            "Варианты выбора коммутатора в таблице",
            self.page,
        )
        self.COMMUTATOR_TYPE_NAME_SEARCH = ElementsList(
            "[ng-model*='commutatorDialog.model.equipments.filter.name']",
            "Поиск по вариантам выбора коммутатора в таблице",
            self.page,
        )
        self.COMMUTATOR_SUBMIT_BTN = Element("[on-submit*='commutatorDialog.submit']", "Кнопка 'Выбрать'", self.page)

        # Модальное окно Изготовление SIM-карт/Создание предсвязок
        self.QUANTITY_INPUT_CREATE_SIM = Element(
            "[ng-model*='localModel.params.count']", "Поле ввода 'Количество штук в заказе'", self.page
        )
        self.START_RANGE_INPUT_CREATE_SIM = Element(
            "[ng-model*='simcardRangeParams.startIMSI']", "Поле ввода IMSI 'Начальное значение'", self.page
        )
        self.END_RANGE_INPUT_CREATE_SIM = Element(
            "[ng-model*='simcardRangeParams.endIMSI']", "Поле ввода IMSI 'Конечное значение'", self.page
        )
        self.NEXT_BTN = Element("[ng-click*='next']", "Кнопка 'Далее'", self.page)
        self.CANCEL_BTN = Element("[ng-click*='master.show=false']", "Кнопка 'Отменить'", self.page)
        self.FORM_BTN = Element("[on-submit*='createTask()']", "Кнопка 'Сформировать/Аннулировать'", self.page)

        # Модальное окно Изготовление SIM-карт с резервирования MSISDN/Создание предсвязок
        self.CHOOSE_COMMUTATOR_BTN = Element(
            ".n-popup [ng-model*='equipmentId'] ps-button:last-child", "Кнопка выбора 'Коммутатор'", self.page
        )
        self.NUMBER_TYPE_FIELD = Element(
            "[ng-click*='loadPhoneNumberTypes'] > div:nth-child(1)", "Поле 'Тип нумерации'", self.page
        )
        self.NUMBER_TYPE_OPTIONS = ElementsList(
            "//ps-list-item[contains(@user-value, 'item.phoneNumberTypeId')]",
            "Варианты списка 'Тип нумерации'",
            self.page,
        )
        self.USE_GOAL_FIELD = Element(
            "[ng-click*='loadPhoneNumberPurpose'] > div > div", "Поле 'Цель использования'", self.page
        )
        self.TAKE_FREE_AFTER_INPUT = Element(
            "[ng-model*='phoneNumberRangeParams.freeMonths']", "Поле 'Брать освобожденные после'", self.page
        )
        self.TEMPLATE_INPUT = Element("[ng-model*='phoneNumberRangeParams.patternMSISDN']", "Поле 'Шаблон'", self.page)
        self.START_MSISDN_INPUT = Element(
            "[ng-model*='phoneNumberRangeParams.startMSISDN']", "Поле 'Начальное значение'", self.page
        )
        self.END_MSISDN_INPUT = Element(
            "[ng-model*='phoneNumberRangeParams.endMSISDN']", "Поле 'Конечное значение'", self.page
        )
        self.NUMBER_TYPE_CLASSES = ElementsList(
            "//body/div[contains(@class, 'n-popup')][1]//tr/td[2]", "Классы 'Разметка классов'", self.page
        )

        # Строки таблицы Изготовление SIM-карт/Управление предсвязками
        self.OPERATIONS_IDS = ElementsList(
            "tr.n-grid__row td:nth-child(2) a", "Значения столбца 'ID операции'", self.page
        )
        self.OPERATIONS_TYPES = ElementsList(
            "tr.n-grid__row td:nth-child(3)", "Значения столбца 'Тип операции'", self.page
        )
        self.PROCES_START_FIELDS = ElementsList(
            "tr.n-grid__row td:nth-child(4)", "Значения столбца 'Начало выполнения'", self.page
        )
        self.PROCES_END_FIELDS = ElementsList(
            "tr.n-grid__row td:nth-child(5)", "Значения столбца 'Конец выполнения'", self.page
        )
        self.STATUS_FIELDS = ElementsList("tr.n-grid__row td:nth-child(6)", "Значения столбца 'Статус'", self.page)

        # Подробности операции Отгрузка SIM-карт/Управление предсвязками
        self.OPERATION_DETAIL_TITLE = Element(
            "//*[@ng-if='model.views.details.show']/div/span[1]", "Заголовок 'Подробности операции'", self.page
        )
        self.COMPLETE_PERCENT = Element(
            "//*[@ng-if='model.views.details.show']/div/span[2]", "Процент выполнения задания", self.page
        )
        self.OPERATION_DETAIL_IMSI_LIST = ElementsList(
            "[rows*='model.tasksItems.data'] tbody tr td:nth-child(2)", "Список IMSI", self.page
        )
        self.OPERATION_DETAIL_STATUS_LIST = ElementsList(
            "[rows*='model.tasksItems.data'] tbody tr td:nth-child(9)", "Список Состояние обработки", self.page
        )

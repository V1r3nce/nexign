from pages.locators.lis_locators.base_elements_lis import BaseElementsLis
from pages.ui_elements import Element, ElementsList


class SimCardElementsLis(BaseElementsLis):
    """Страница SIM-карты LIS"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER
        self.PAGE_TABS = ElementsList("a.n-tab__title", "Вкладки страницы")

        # TAB Список SIM-карт верхние кнопки
        self.REFRESH_BTN = Element("[user-value*='simSearch'] [ng-click*='searchSim']", "Кнопка 'Обновить'")
        self.HISTORY_BTN = Element("[user-value*='simSearch'] [ng-click*='historyDialog.open']", "Кнопка 'История'")
        self.EDIT_ATTRIBUTE_BTN = Element(
            "[user-value*='simSearch'] [ng-click*='dialogs.massEditSim.open']",
            "Кнопка 'Редактировать атрибуты'",
        )
        self.EDIT_EXPIRATION_DATE_BTN = Element(
            "[user-value*='simSearch'] [ng-click*='dialogs.periodChange.open']",
            "Кнопка 'Изменить срок действия'",
        )
        self.CHOOSE_COMMUTATOR_BTN = Element(
            "[user-value*='simSearch'] [ng-click*='commutatorDialog.show']", "Кнопка 'Задать коммутатор'"
        )
        self.SEND_TO_SELLER_BTN = Element(
            "[user-value*='simSearch'] [ng-click*='dialogs.simTransferToDealer']",
            "Кнопка 'Передать SIM дилеру'",
        )
        self.DOWNLOAD_BTN = Element(
            "[user-value*='simSearch'] [ng-click*='dialogs.csvExport.export']", "Кнопка 'Выгрузить в Excel'"
        )
        self.SEARCH_BTN = Element("[user-value*='simSearch'] a.lis-toolbar-search__link", "Кнопка 'Поиск'")
        self.NUMBERS_COUNTER = Element(
            "[user-value*='simSearch'] div.toolbar-right a.toolbar-quick-filter__item_active",
            "Счетчик номеров",
        )

        # Поиск
        self.IMSI_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][1]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'IMSI'",
        )
        self.IMSI_FILTER_OPTIONS = ElementsList(
            "//ps-list-item[contains(@ng-click, 'IMSI')]/parent::div/ps-list-item[position() > 2 and position() < 7]",
            "Опции фильтра 'IMSI'",
        )
        self.IMSI_SELECTED_OPTIONS = Element(
            "//div[@class='lis-search-numbers-params__item'][1]//div[contains(@ps-link-element, 'elements.value')]",
            "Выбранное значение 'IMSI'",
        )
        self.IMSI_FILTER_INPUT = Element(
            "//div[@class='lis-search-numbers-params__item'][1]//input", "Поле ввода фильтр 'IMSI'"
        )
        self.ICC_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][4]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'ICC'",
        )
        self.ICC_FILTER_OPTIONS = ElementsList(
            "//ps-list-item[contains(@ng-click, 'ICC')]/parent::div/ps-list-item[position() > 2 and position() < 7]",
            "Опции фильтра 'ICC'",
        )
        self.ICC_SELECTED_OPTIONS = Element(
            "//div[@class='lis-search-numbers-params__item'][4]//div[contains(@ps-link-element, 'elements.value')]",
            "Выбранное значение 'ICC'",
        )
        self.MSISDN_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][7]//div[contains(@class, 'button')]",
            "Кнопка открыть фильтр 'MSISDN'",
        )
        self.MSISDN_FILTER_OPTIONS = ElementsList(
            "//ps-list-item[contains(@ng-click, 'MSISDN')]/parent::div/ps-list-item[position() > 2 and position() < 7]",
            "Опции фильтра 'MSISDN'",
        )
        self.MSISDN_SELECTED_OPTIONS = Element(
            "//div[@class='lis-search-numbers-params__item'][7]//div[contains(@ps-link-element, 'elements.value')]",
            "Выбранное значение 'MSISDN'",
        )
        self.PIN1_INPUT = Element("[ng-model*='model.simCards.filter.PIN1']", "Поле ввода 'PIN1'")
        self.PIN2_INPUT = Element("[ng-model*='model.simCards.filter.PIN2']", "Поле ввода 'PIN2'")
        self.STATUS_FILTER_BTN = Element(
            "//div[@ng-click='loadSimStatus(model.dictionaries)']/parent::div/div/div[2]",
            "Кнопка открыть фильтр 'Статус'",
        )
        self.STATUS_OPTION_FREE = Element("//span[contains(text(), 'Свободен')]", "Фильтр 'Статус' опция 'Свободен'")
        self.CHOSEN_STATUSES = ElementsList(
            "//div[@ng-click='loadSimStatus(model.dictionaries)']/parent::div//span[@class='b-multiselect-item__title']",
            "Выбранные опции 'Статус'",
        )
        self.STATE_FILTER_BTN = Element(
            "//div[@ng-click='loadSimStates(model.dictionaries)']/parent::div/div/div[2]",
            "Кнопка открыть фильтр 'Состояние'",
        )
        self.STATE_FILTER_OPTIONS = ElementsList("//*[@user-value='item.SIMCardStateId']", "Опции фильтр 'Состояние'")
        self.PUK1_INPUT = Element("[ng-model*='model.simCards.filter.PUK1']", "Поле ввода 'PUK1'")
        self.PUK2_INPUT = Element("[ng-model*='model.simCards.filter.PUK2']", "Поле ввода 'PUK2'")
        self.EXPIRATION_DATE_INPUT = Element(
            "[value*='model.simCards.filter.expirationDate'] input", "Поле ввода 'Срок действия'"
        )
        self.ACC_INPUT = Element("[ng-model*='model.simCards.filter.ACC']", "Поле ввода 'ACC'")
        self.BBB_INPUT = Element("[ng-model*='model.simCards.filter.BBB']", "Поле ввода 'BBB'")
        self.CHOSEN_COMMUTATOR_INPUT = Element(
            "[ng-model*='model.simCards.filter.equipmentId'] input", "Поле 'Коммутатор'"
        )
        self.PROJECT_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][9]//ps-button[contains(@ng-if, 'showDropDownButton')]",
            "Кнопка открыть фильтр 'Проект'",
        )
        self.ESN_INPUT = Element("[ng-model*='model.simCards.filter.ESN']", "Поле ввода 'ESN'")
        self.CHOSEN_TYPE_INPUT = Element("[ng-model*='filter.SIMCardTypeIds'] input", "Поле 'Тип'")
        self.MEMORY_INPUT = Element("[ng-model*='model.simCards.filter.MEMORY']", "Поле ввода 'Память'")
        self.UNIT_INPUT = Element("[ng-model*='model.simCards.filter.UNIT']", "Поле ввода 'Единица'")
        self.LINK_POOL_INPUT = Element("[ng-model*='tariffTemplates.model'] input", "Поле 'Набор связывания'")
        self.MAP_INPUT = Element("[ng-model*='model.simCards.filter.initialPaymentAmount']", "Поле ввода 'МАП'")
        self.BLOCKING_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][8]//div[contains(@class, 'line__half_left')][1]//ps-button",
            "Кнопка открыть фильтр 'Блокировка'",
        )
        self.NOT_BLOCKED_OPTION = Element(
            "//ps-list-item//span[contains(text(), 'Не установлена')]",
            "Фильтр 'Блокировка' вариант 'Не установлена'",
        )
        self.BILLING_LINK_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][13]/div/div[2]//"
            "ps-button[contains(@ng-if, 'showDropDownButton')][1]",
            "Кнопка открыть фильтр 'Принадлежность к биллингу'",
        )
        self.AGENT_INPUT = Element("[ng-model*='model.simCards.filter.agent'] input", "Поле 'Дилер'")
        self.TARIFF_INPUT = Element("[ng-model*='filter.ratePlanIds'] input", "Поле 'Тарифный план'")
        self.TECH_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][15]//div[contains(@class,"
            " 'line__half_left')][1]//ps-button",
            "Кнопка открыть фильтр 'Технология'",
        )
        self.SEGMENT_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][14]//div[contains(@class, 'line__half_right')][1]//ps-button",
            "Кнопка открыть фильтр 'Сегмент'",
        )
        self.REGISTRY_DATE_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][2]//ps-button",
            "Кнопка открыть фильтр 'Дата регистрации'",
        )
        self.EID_INPUT = Element("[ng-model*='model.simCards.filter.EIDs']", "Поле ввода 'EID'")
        self.SUPPLIER_FILTER_BTN = Element(
            "//div[@class='lis-search-numbers-params__item'][15]//ps-button",
            "Кнопка открыть фильтр 'Поставщик'",
        )
        self.FILTER_SEARCH_BTN = Element("[ng-click*='searchSim'][icon='search']", "Кнопка 'Найти'")
        self.CLEAR_FILTER_BTN = Element("[ng-click*='searchSimClear']", "Кнопка 'Очистить фильтры'")

        # TAB Список SIM-карт заголовки столбцов таблицы
        self.MSISDN_HEADER = Element(
            "[user-value*='simSearch'] tr th.n-grid__title:nth-child(3)", "Заголовок/Кнопка 'MSISDN'"
        )
        self.STATE_DATE_CHANGE_HEADER = Element(
            "[user-value*='simSearch'] tr th.n-grid__title:nth-child(10)",
            "Заголовок/Кнопка 'Дата смены состояния'",
        )

        # TAB Список SIM-карт
        self.CHECK_ALL_BTN = Element("[user-value*='simSearch'] tr th:nth-child(2)", "Кнопка 'Выбрать все'")
        self.TABLE_LINE = ElementsList("[user-value*='simSearch'] tr.n-grid__row", "Строки таблицы")
        self.LINE_CHECKBOXES = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row span.n-check-checkbox", "Чекбоксы строк таблицы"
        )
        self.IMSI_NUMBERS = ElementsList("[user-value*='simSearch'] tr.n-grid__row td:nth-child(3)", "Номера IMSI")
        self.NUMBERS_STATUSES = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row td:nth-child(7)", "Статусы номеров"
        )
        self.NUMBERS_STATES = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row td:nth-child(9)", "Состояния номеров"
        )
        self.NUMBERS_BLOCK_STATUS = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row td:nth-child(11)", "Статус блокировки номеров"
        )
        self.NUMBERS_COMMUTATOR = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row td:nth-child(12)", "Коммутатор номеров"
        )
        self.EXPIRATIONS_DATES = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row td:nth-child(14)", "Сроки действия"
        )
        self.SELLER_FIELDS = ElementsList("[user-value*='simSearch'] tr.n-grid__row td:nth-child(27)", "Поля 'Дилер'")
        self.BRAND_FIELDS = ElementsList("[user-value*='simSearch'] tr.n-grid__row td:nth-child(32)", "Поля 'Бренд'")
        self.MARKET_SEGMENT_FIELDS = ElementsList(
            "[user-value*='simSearch'] tr.n-grid__row td:nth-child(33)", "Поля 'Рыночный сегмент'"
        )

        # Модальное окно Изменение срока действия
        self.MODAL_EXPIRATION_DATE_INPUT = Element(
            "[value*='dialogs.periodChange.expirationDate'] input", "Поле ввода 'Изменение срока действия'"
        )
        self.CONFIRM_CHANGE_EXPIRATION_DATE_BTN = Element(
            "[on-submit*='dialogs.periodChange.changeExpirationDate']", "Кнопка 'Сохранить'"
        )

        # Модальное окно редактировать атрибуты
        self.MODAL_CHOOSE_BRAND_BTN = Element(
            "[ng-model*='simBrandId']  [ng-click*='onPreAction']", "Кнопка выбора 'Бренд'"
        )
        self.MODAL_CHOOSE_MARKET_SEGMENT_BTN = Element(
            "[ng-model*='SIMCardMarketId']  [ng-click*='onPreAction']", "Кнопка выбора 'Рыночный сегмент'"
        )
        self.BRAND_OPTION_NEXIGN = Element(
            "//div[contains(@class,'dialog-content-container')]//td/div[contains(text(), 'Nexign')]",
            "Опция бренда 'Nexign'",
        )
        self.MARKET_SEGMENT_OPTION_B2X = Element(
            "//div[contains(@class,'dialog-content-container')]//td/div[contains(text(), 'B2X')]",
            "Опция Рыночный сегмент 'B2X'",
        )
        self.MODAL_CHANGE_ATTRIBUTE_SAVE_BTN = Element(
            ".n-popup-foot [on-submit='massUpdateSim()']", "Кнопка редактирования атрибутов 'Сохранить'"
        )

        # Модальное окно История по IMSI
        self.HISTORY_TYPE_BTN = ElementsList("a[ng-click*='historyDialog']", "Кнопки типов истории изменений")

        # Модальное окно Передать SIM дилеру
        self.MODAL_CHOSEN_INPUT = Element("div.n-popup [ng-required*='states.required']", "Поле выбранный дилер")
        self.MODAL_OPEN_SELLER_LIST = Element(
            "div.n-popup ps-button[ng-if*='options.isDropButton']", "Кнопка открыть список дилеров"
        )
        self.SELLER_SERVICE_STORE = Element(
            "//ps-list-item//span[contains(text(), 'NEXIGN Service Store')]",
            "Опция дилер 'NEXIGN Service Store'",
        )
        self.SELLER_TECH_WAREHOUSE = Element(
            "//ps-list-item//span[contains(text(), 'NEXIGN технологический склад')]",
            "Опция дилер 'NEXIGN технологический склад'",
        )
        self.MODAL_SEND_BTN = Element("[ng-click*='dialogs.simTransferToDealer.transfer']", "Кнопка 'Передать'")
        self.MODAL_CANCEL_BTN = Element("[icon='block'][ng-click*='dialogs.simTransferToDealer']", "Кнопка 'Отменить'")

        # Вкладка Загрузка SIM-карт
        self.START_USAGE_BTN = Element("[ng-click*='massActions.startSimUsage']", "Кнопка 'В эксплуатацию'")
        self.UPLOAD_CARDS_BTN = Element(
            "[user-value*='simUploads'] [ng-click*='dialogs.importSimDialog.show']",
            "Кнопка 'Загрузить карты'",
        )
        self.CHANGE_COMMUTATOR_BTN = Element(
            "[user-value*='simUploads'] [ng-click*='commutatorDialog.show']", "Кнопка 'Задать коммутатор'"
        )
        self.PROJECT_CHANGE_BTN = Element(
            "[user-value*='simUploads'] [ng-click*='showProjectChangeDialog']", "Кнопка 'Изменить проект'"
        )
        self.PERIOD_CHANGE_BTN = Element(
            "[user-value*='simUploads'] [ng-click*='dialogs.periodChange']", "Кнопка 'Изменить срок действия'"
        )
        self.REFRESH_BTN_UPLOAD_SIMS = Element(
            "[user-value*='simUploads'] ps-button[icon*='refresh'][ng-click*='ReloadData']",
            "Кнопка 'Обновить'",
        )

        # TAB Список Загрузка SIM-карт заголовки столбцов таблицы и строки таблицы
        self.IMSI_HEADER_UPLOAD_SIMS = Element(
            "[user-value*='simUploads'] tr th.n-grid__title:nth-child(3)", "Заголовок/Кнопка 'IMSI'"
        )
        self.LINE_CHECKBOXES_UPLOAD_SIMS = ElementsList(
            "[user-value*='simUploads'] tr.n-grid__row span.n-check-checkbox", "Чекбоксы строк таблицы"
        )
        self.IMSI_NUMBERS_UPLOAD_SIMS = ElementsList("[id*='uploadsGrid'] tr.n-grid__row td:nth-child(3)", "Номера IMSI")
        self.ICC_NUMBERS_UPLOAD_SIMS = ElementsList("[id*='uploadsGrid'] tr.n-grid__row td:nth-child(4)", "Номера ICC")
        self.EXPIRATIONS_DATE_UPLOAD_SIMS = ElementsList(
            "[id*='uploadsGrid'] tr.n-grid__row td:nth-child(16)", "Поля Дата окончания действия"
        )
        self.COMMUTATORS_UPLOAD_SIMS = ElementsList(
            "[id*='uploadsGrid'] tr.n-grid__row td:nth-child(18)", "Поля Коммутатор"
        )
        self.PROJECTS_UPLOAD_SIMS = ElementsList("[id*='uploadsGrid'] tr.n-grid__row td:nth-child(19)", "Поля Проект")

        # Модальное окно Добавление SIM-карт
        self.UPLOAD_SIMS_INPUT = Element("input[uploader='importSimDialog.uploader']", "Кнопка 'Обзор'")
        self.COMMUTATOR_CHOOSE_BTN = Element(
            "form[name='importSimForm'] [ng-model*='commutatorDialog.equipmentName'] ps-button:nth-child(2)",
            "Кнопка выбора коммутатора",
        )
        self.CHOSEN_PROJECT_ADD_SIM_MODAL = Element(
            "[ng-init*='importSimDialog.loadSimProjects'] div div", "Поле 'Проект'"
        )
        self.TYPE_CHOOSE_BTN = Element(
            "form[name='importSimForm'] [ng-model*='selectedValues.SIMCardTypeId'] ps-button:nth-child(2)",
            "Кнопка выбора типа",
        )
        self.TYPE_NAMES_ADD_SIM_MODAL = ElementsList(
            "//ps-grid[@rows='directoriesDialog.gridModel.rows']//tbody/tr/td[1]",
            "Варианты выбора типа в таблице",
        )
        self.TEMPLATE_INPUT_ADD_SIM_MODAL = Element(
            "[ng-model*='templateId.loadSIMCardTemplateId'] input", "Поле Шаблон"
        )
        self.EXPIRATION_DATE_INPUT_ADD_SIM_MODAL = Element(
            "[ng-model*='selectedValues.expirationDate'] input", "Поле Срок действия"
        )
        self.ADD_BUTTON_ADD_SIM_MODAL = Element(
            "form[name='importSimForm'] ps-button[on-submit*='submit']", "Кнопка 'Добавить'"
        )
        self.CANCEL_BTN_ADD_SIM_MODAL = Element(
            "ps-button[ng-click*='importSimDialog.cancel(importSimForm)']", "Кнопка 'Отменить'"
        )

        # Модальное окно 'Изменить проект'
        self.PROJECT_OPTIONS_CHANGE_PROJECT_MODAL = ElementsList(
            "//ps-list-item[@user-value='value.SIMCardProjectId']", "Опции проектов"
        )
        self.CHECKBOX_NULL_PROJECT_MODAL = Element(
            "[ng-model*='dialogs.projectChange.projectNull'] > span:first-child",
            "Чекбокс Очистить поле 'Проект'",
        )
        self.SAVE_BUTTON_PROJECT_MODAL = Element(
            "ps-button[on-submit*='massActions.changeProject']", "Кнопка 'Сохранить'"
        )
        self.CANCEL_BTN_PROJECT_MODAL = Element(
            "ps-button[ng-click*='dialogs.projectChange.isOpened=false']", "Кнопка 'Отменить'"
        )

        # Модальное окно 'Устанавливаемый срок действия'
        self.NEW_DATE_INPUT_MODAL = Element(
            "[value*='model.dialogs.expirationDate'] input", "Поле ввода 'Устанавливаемый срок действия'"
        )
        self.SAVE_BTN_DATE_MODAL = Element(
            "ps-button[on-submit*='assActions.changeExpirationDate']", "Кнопка 'Сохранить'"
        )
        self.CANCEL_BTN_DATE_MODAL = Element(
            "ps-button[ng-click*='dialogs.periodChange.isOpened=false']", "Кнопка 'Отменить'"
        )

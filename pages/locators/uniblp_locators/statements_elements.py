from pages.locators.uniblp_locators.base_elements_uniblp import BaseUniblpElements
from pages.ui_elements import Element, ElementsList


class StatementsUniblpElements(BaseUniblpElements):
    """Страница Выписки UNIBLP UI"""

    def __init__(self) -> None:
        super().__init__()

        # STATEMENT DOCUMENTS
        self.STATEMENT_DOCUMENTS_TITLE = Element(
            "//div[contains(@class, 'onyx-details-header')]//span[contains(@class, 'onyx-details-header__text')]",
            "Заголовок 'Документы выписки'",
        )
        self.SAVE_TO_BILLING_BTN = Element(
            "//ps-button[contains(@icon, 'upload') and not(contains(@class, 'ng-hide')) and contains(@ng-click, 'documentsWorkBilling')]",
            "Кнопка 'Сохранить в биллинг'",
        )
        self.STATEMENT_DOCUMENTS_TABLE = ElementsList(
            "//div[contains(@class, 'grid-filler') and contains(@class, 'onyx-popup-grid-container')]//ps-grid[contains(@controller, 'documents.controller')]//div[contains(@class, 'n-grid-holder__body')]//table[contains(@class, 'n-grid_checkable')]//tbody[contains(@class, 'n-grid__body')]//tr[contains(@class, 'n-grid__row')]",
            "Строки таблицы документов выписки",
        )
        self.STATEMENT_DOCUMENTS_CHECKBOX = ElementsList(
            "//div[contains(@class, 'grid-filler') and contains(@class, 'onyx-popup-grid-container')]//ps-grid[contains(@controller, 'documents.controller')]//div[contains(@class, 'n-grid-holder__body')]//table[contains(@class, 'n-grid_checkable')]//tbody[contains(@class, 'n-grid__body')]//tr[contains(@class, 'n-grid__row')]//td[contains(@class, 'n-grid__select')]//div[contains(@class, 'n-grid__text')]//span[contains(@class, 'n-check-checkbox')]",
            "Чекбокс в таблице документов выписки",
        )
        self.CLIENT_BILLING_NAME = ElementsList(
            "(//table[contains(@class, 'n-grid') and contains(@class, 'n-grid_checkable')])[1]//tbody//tr//td[@data-column-index='11']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Клиент биллинга (имя клиента)'",
        )
        self.STATEMENT_CLIENT_TYPE = ElementsList(
            "(//table[contains(@class, 'n-grid') and contains(@class, 'n-grid_checkable')])[1]//tbody//tr//td[@data-column-index='13']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Тип клиента'",
        )

        # STATEMENT DOCUMENTS PAYS
        self.PAYMENTS_COLUMN_STATUS = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='2']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Статус определения клиента'",
        )
        self.PAYMENTS_COLUMN_PAYMENT_TYPE = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='3']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Тип платежа'",
        )
        self.PAYMENTS_COLUMN_AMOUNT = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='4']//div[contains(@class, 'n-grid__text')]//span",
            "Колонка 'Σ платежа'",
        )
        self.PAYMENTS_COLUMN_BILLING_SYSTEM = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='6']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Тип платежа'",
        )
        self.PAYMENTS_COLUMN_CLIENT_NAME = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='7']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Клиент биллинга'",
        )
        self.PAYMENTS_COLUMN_PERSONAL_ACCOUNT = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='8']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Лиц.счет'",
        )
        self.PAYMENTS_COLUMN_INN = ElementsList(
            "//ps-grid[contains(@rows, 'documentsPays.rows')]//tbody//td[@data-column-index='9']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'ИНН'",
        )
        self.TARGET_POST_PAYS_BTN = Element("//ps-button[contains(@icon, 'operation')]", "Кнопка 'Целеуказания'")

        # PAYMENTS DIALOG
        self.PAYMENTS_TITLE = Element(
            "//div[contains(@class, 'ps-dialog') and .//ps-grid[@controller='documentsPays.controller']]//div[@class='n-popup-head__title' and @ps-mousedown='onCaptionMouseDown($event)']",
            "Заголовок формы 'Платежи'",
        )
        self.SEARCH_PAYER_BTN = Element(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'grid-props-header')]//ps-button[contains(@icon, 'search-doc')]",
            "Кнопка 'Поиск плательщика'",
        )
        self.PAYMENTS_SAVE_BTN = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//div[contains(@class, 'n-popup-foot')]//ps-button[contains(@icon, 'save')]",
            "Кнопка 'Сохранить'",
        )
        self.PAYMENT_PERSONAL_ACCOUNT = ElementsList(
            "//div[contains(@class, 'grid-filler')]//ps-grid[@rows='documentsPays.rows']//tbody//td[@data-column-index='5']//div[contains(@class, 'n-grid__text')]//span[contains(@class, 'td-row-content') and string()!='']",
            "Поле 'ЛС клиента'",
        )
        self.PAYMENT_CLIENT_NAME = ElementsList(
            "//div[contains(@class, 'ps-dialog')]//ps-splitter-zone[1]//ps-grid[contains(@controller, 'documentsPays.controller')]//tbody//td[@data-column-index='12']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Имя клиента' в таблице платежей",
        )

        # SEARCH PAYER
        self.SEARCH_PAYER_TITLE = Element(
            "//div[contains(@class, 'ps-dialog')][.//ps-grid[@controller='clients.controller']]//div[@ps-mousedown='onCaptionMouseDown($event)']",
            "Заголовок 'Поиск плательщика'",
        )
        self.SEARCH_PAYER_ATTR_PERSONAL_ACCOUNT = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addAccount')]",
            "Атрибут поиска 'Лиц.счет'",
        )
        self.SEARCH_PAYER_ATTR_INN = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addInn')]",
            "Атрибут поиска 'ИНН'",
        )
        self.SEARCH_PAYER_ATTR_DEALER_ACCOUNT = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addBillNumDiler')]",
            "Атрибут поиска 'Счет дилера'",
        )
        self.SEARCH_PAYER_ATTR_CONTRACT = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addContractNum')]",
            "Атрибут поиска 'Договор'",
        )
        self.SEARCH_PAYER_ATTR_CLIENT_ACCOUNT = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addBillNum')]",
            "Атрибут поиска 'Счет клиента'",
        )
        self.SEARCH_PAYER_ATTR_INVOICE = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addFuctNum')]",
            "Атрибут поиска 'Счет-фактура'",
        )
        self.SEARCH_PAYER_ATTR_PHONE = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//input[contains(@ng-model, 'documentsPays.focused.addMSISDN')]",
            "Атрибут поиска 'Телефон'",
        )
        self.SEARCH_PAYER_FIND_BTN = Element(
            "//div[contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog') and contains(@class, 'ps-dialog')]//div[contains(@class, 'b-groupbox__body')]//ps-button[contains(@icon, 'search') and not(contains(@class, 'ng-hide'))]",
            "Кнопка 'Найти'",
        )
        self.SEARCH_PAYER_SELECT_CLIENT_BTN = Element(
            "//div[contains(@class, 'ps-dialog') and .//ps-grid[@controller='clients.controller']]//div[contains(@class, 'n-popup-foot')]//ps-button[@icon='ok']",
            "Кнопка 'Выбрать клиента'",
        )
        self.SEARCH_PAYER_CLIENTS_LIST_ROWS = ElementsList(
            "//div[contains(@class, 'ps-dialog') and .//ps-grid[@controller='clients.controller']]//table[contains(@class, 'n-grid')]//tbody[contains(@class, 'n-grid__body')]//tr[contains(@class, 'n-grid__row')]",
            "Строки списка клиентов",
        )

        # PAYMENTS RIGHT PANEL CLIENT INFO
        self.CLIENT_HEADER = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-header')])[1]",
            "Заголовок панели 'Клиент'",
        )
        self.CLIENT_NAME = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[1]",
            "Поле 'Клиент (имя клиента)'",
        )
        self.PERSONAL_ACCOUNT = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[2]",
            "Поле 'Лиц.счет (номер ЛС)'",
        )
        self.CONTRACT_NUMBER = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[3]",
            "Поле 'Договор клиента (номер договора)'",
        )
        self.INN = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[4]",
            "Поле 'ИНН'",
        )
        self.KPP = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[5]",
            "Поле 'КПП'",
        )
        self.SETTLEMENT_ACCOUNT = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[6]",
            "Поле 'Расч.счет (Расчетный счет клиента)'",
        )
        self.CLIENT_TYPE = Element(
            "(//ps-button[contains(@icon, 'search-doc')]/ancestor::div[contains(@class, 'grid-props')]//div[contains(@class, 'grid-props-table-inner__text')])[8]",
            "Поле 'Тип Клиента'",
        )

        # TARGET_PAYS
        self.TARGET_PAYS_DIALOG_TITLE = Element(
            "//div[contains(@class, 'ps-dialog') and .//ps-grid[@controller='documentsPays.controller']]//div[contains(@class, 'n-popup-head')]//div[contains(@class, 'n-popup-head__title')]",
            "Заголовок формы 'Поиск непогашенных счетов'",
        )
        self.TARGET_PAYS_TABLE_ROWS = ElementsList(
            "//div[contains(@class, 'ps-dialog')]//ps-grid[contains(@rows, 'targetPays.rows')]//tbody[contains(@class, 'n-grid__body')]//tr[contains(@class, 'n-grid__row')]",
            "Строки таблицы непогашенных счетов",
        )
        self.TARGET_PAYS_REDEMPTION_AMOUNT = ElementsList(
            "//div[contains(@class, 'ps-dialog')]//ps-grid[contains(@rows, 'targetPays.rows')]//tbody[contains(@class, 'n-grid__body')]//tr//td[@data-column-index='8']//div[contains(@class, 'n-grid__text')]//span[contains(@class, 'td-row-content')]",
            "Колонка 'Сумма погашения'",
        )
        self.TARGET_PAYS_REMAINDER_AMOUNT = Element(
            "//div[contains(@class, 'fields-layout__line__half_left')]//i",
            "Поле 'Остаток платежа, подлежащий авторазнесению'",
        )
        self.TARGET_PAYS_SAVE_BTN = Element(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'n-popup-foot__right')]//div[contains(@style, 'float: right;')]//ps-button[contains(@icon, 'ok')]",
            "Кнопка 'Сохранить'",
        )

        # POST PAY
        self.POST_PAY_AMOUNT_DIALOG_TITLE = Element(
            "//div[contains(@class, 'ps-dialog') and .//div[contains(@class, 'fields-layout')]//input[contains(@class, 'inp-text') and @ng-model='targetPays.selected.redemptionAmount']]//div[contains(@class, 'n-popup-head')]//div[contains(@class, 'n-popup-head__title')]",
            "Заголовок формы 'Сумма ручного разнесения'",
        )
        self.POST_PAY_AMOUNT_INPUT = Element(
            "//div[contains(@class, 'ps-dialog')]//input[contains(@class, 'inp-text') and contains(@ng-model, 'targetPays.selected.redemptionAmount')]",
            "Поле ввода 'Сумма погашения'",
        )
        self.POST_PAY_AMOUNT_SAVE_BTN = Element(
            "//div[.//input[@ng-model='targetPays.selected.redemptionAmount']]//ps-button[@icon='ok']",
            "Кнопка 'Сохранить'",
        )

        # TARGET PAYS DIALOG
        self.TARGET_PAYS_MESSAGE = Element(
            "//div[contains(@class, 'ps-dialog')]//table[contains(@class, 'n-popup-message-align') and contains(@ng-show, 'dialogsInfo.mode===0')]//tbody//tr//td[contains(@class, 'n-popup-message-align__text')]//div[contains(@class, 'n-popup-message-text')]//div[contains(@class, 'b-label') and contains(@class, 'content-info')]",
            "Текст сообщения об успешном сохранении целеуказаний",
        )
        self.TARGET_PAYS_CLOSE_BTN = Element(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'n-popup-foot__right')]//ps-button[contains(@ng-click, 'dialogsInfo.onClose')]",
            "Кнопка 'Закрыть'",
        )

        # SAVE TO BILLING DIALOG
        self.SAVE_TO_BILLING_DIALOG_TITLE = Element(
            "//div[.//ps-grid[@rows='docsResult.rows']]//div[@class='n-popup-head']/div[@class='n-popup-head__title']",
            "Заголовок модального окна 'Подготовлено к сохранению в биллинг'",
        )
        self.SAVE_TO_BILLING_DOCUMENTS_COUNT = Element(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'dialog-content-container')]//div[contains(@class, 'n-popup-message-text')]//div[contains(@class, 'b-label') and position()=1]",
            "Поле 'Количество документов'",
        )
        self.SAVE_TO_BILLING_ERRORS_COUNT = Element(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'dialog-content-container')]//div[contains(@class, 'n-popup-message-text')]//div[contains(@class, 'b-label') and position()=last()]",
            "Поле 'Количество ошибок'",
        )
        self.SAVE_TO_BILLING_CLOSE_BTN = Element(
            "//ps-button[contains(@icon, 'ok') and contains(@ng-click, 'dialogsAnnulResult.onClose')]",
            "Кнопка 'Закрыть'",
        )

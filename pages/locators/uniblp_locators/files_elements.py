from pages.locators.uniblp_locators.base_elements_uniblp import BaseUniblpElements
from pages.ui_elements import Element, ElementsList, SelectUniblp


class FilesUniblpElements(BaseUniblpElements):
    """Страница Файлы UNIBLP UI"""

    def __init__(self) -> None:
        super().__init__()

        # FILES SECTION
        self.FILES_HEADER = Element(
            "[ng-controller='filesController'] .layout-vertical-stretch > .layout-vertical-stretch__auto > h2.content-section-header",
            "Заголовок раздела 'Файлы'",
        )
        self.UPLOAD_FROM_DISK = Element(
            "ps-button[ng-click='dialogsFilesUpload.onShow()']:not(.ng-hide)", "Кнопка 'Загрузить с диска'"
        )
        self.DELETE_BTN = Element("ps-button[ng-click='dialogDeleteFiles.onShow()']:not(.ng-hide)", "Кнопка 'Удалить'")
        self.SEARCH_BTN = Element("ps-button[ng-click='files_refresh()']:not(.ng-hide)", "Кнопка 'Найти'")
        self.STATS_BTN = Element(
            "ps-button[ng-click='files_stat_refresh(); dialogsFilesStatsLoad.onShow()']",
            "Кнопка 'Статистика загрузки файлов'",
        )

        # DIALOG DOWNLOADING STATEMENT
        self.DIALOG_LOAD_STATEMENT_TITLE = Element(
            "//div[contains(@class, 'ps-dialog') and .//div[contains(@class, 'b-combobox') and contains(@class, 'ps-list-drop-single')]]//div[@class='n-popup-head__title' and @ps-mousedown='onCaptionMouseDown($event)']",
            "Заголовок окна 'Загрузка выписки'",
        )
        self.FORMAT_STATEMENT_DROPDOWN_BTN = Element(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'b-combobox') and contains(@class, 'ps-list-drop-single')]//*[contains(@class, 'b-button_arrow')]",
            "Кнопка раскрытия списка формата выписки",
        )
        self.FORMAT_STATEMENT = SelectUniblp(
            "//div[contains(@class, 'ps-dialog')]//div[contains(@class, 'b-combobox') and contains(@class, 'ps-list-drop-single')]//div[contains(@class, 'b-combobox__value')]",
            "Выпадающий список 'Формат банковской выписки'",
        )
        self.FILE_PATH_INPUT = Element(
            "//div[contains(@class, 'ps-input-file')]//input[contains(@class, 'b-combobox__input')]",
            "Поле 'Путь к файлу'",
        )
        self.UPLOAD_FILE_INPUT = Element("ps-button.js-button-select-file", "Скрытый input для загрузки файла")
        self.CANCEL_BTN = Element("ps-button[ng-click='dialogsFilesUpload.onClose()']", "Кнопка 'Отменить'")
        self.UPLOAD_STATEMENT_BTN = Element(
            "ps-button[ng-click='dialogsFilesUpload.onLoad()']", "Кнопка 'Загрузить выписку'"
        )

        # FILES TABLE
        self.FILES_TABLE_COLUMN_FILENAME = ElementsList(
            "//ps-grid[@controller='files.controller']//tbody[contains(@class, 'n-grid__body')]//tr//td[@data-column-index='1']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Имя файла'",
        )
        self.FILES_TABLE_COLUMN_STATUS = ElementsList(
            "//ps-grid[@controller='files.controller']//tbody[contains(@class, 'n-grid__body')]//tr//td[@data-column-index='5']//div[contains(@class, 'n-grid__text')]",
            "Колонка 'Статус'",
        )

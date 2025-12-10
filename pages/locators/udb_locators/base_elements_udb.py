from pages.ui_elements import Element, ElementsList


class BaseUdbElements:
    def __init__(self) -> None:
        self.PAGE_TITLE = Element("h2", "Заголовок страницы")

        # MODAL
        self.MODAL = ElementsList(".ui-modal-content", "Модальное окно")
        self.MODAL_X_BTN = ElementsList(".ui-modal-close-x", "Кнопка Х закрыть модального окна")
        self.MODAL_TITLE = ElementsList(".ui-modal-title", "Заголовок модального окна")
        self.MODAL_BODY_TEXT = ElementsList(".ui-modal-body p", "Текст модального окна")

        self.FIRST_BTN = ElementsList(".ui-modal-footer button:first-child", "Первая кнопка модального окна")
        self.SECOND_BTN = ElementsList(".ui-modal-footer button:last-child", "Вторая кнопка модального окна")

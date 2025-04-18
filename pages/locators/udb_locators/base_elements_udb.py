from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList


class BaseElementsUdb:
    def __init__(self, page: Page):
        self.page = page

        self.PAGE_TITLE = Element("h2", "Заголовок страницы", self.page)

        # MODAL
        self.MODAL = ElementsList(".ui-modal-content", "Модальное окно", self.page)
        self.MODAL_X_BTN = ElementsList(".ui-modal-close-x", "Кнопка Х закрыть модального окна", self.page)
        self.MODAL_TITLE = ElementsList(".ui-modal-title", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = ElementsList(".ui-modal-body p", "Текст модального окна", self.page)

        self.FIRST_BTN = ElementsList(".ui-modal-footer button:first-child", "Первая кнопка модального окна", self.page)
        self.SECOND_BTN = ElementsList(".ui-modal-footer button:last-child", "Вторая кнопка модального окна", self.page)

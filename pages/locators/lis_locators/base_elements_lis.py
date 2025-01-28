from playwright.sync_api import Page

from pages.ui_elements import Element, ElementsList


class BaseElementsLis:

    def __init__(self, page: Page):
        self.page = page

        #MODAL
        self.MODAL = Element("div.n-popup", "Модальное окно", self.page)
        self.MODAL_X_BTN = Element("[ng-show*='titleButtons.close.visible']", "Кнопка Х закрыть модального окна", self.page)
        self.MODAL_TITLE = Element("div.n-popup-head__title", "Заголовок модального окна", self.page)
        self.MODAL_BODY_TEXT = Element("div.n-popup-message-text", "Текст модального окна", self.page)
        self.FIRST_BTN = Element("div.n-popup ps-button:first-child", "Первая кнопка модального окна",
                                 self.page)
        self.SECOND_BTN = Element("div.n-popup ps-button:last-child", "Вторая кнопка модального окна",
                                  self.page)

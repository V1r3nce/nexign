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
        self.MODAL_BODY_TEXT = Element("div.n-popup-message-text", "Текст модального окна", self.page)
        self.MODAL_BODY_INPUT = Element("div.n-popup textarea", "Поле ввода модального окна", self.page)
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

from playwright.sync_api import Page

from pages.locators.psc_locators.base_elements_psc import BaseElementsPsc
from pages.ui_elements import Element, ElementsList


class ProjectDetailsElements(BaseElementsPsc):
    """Страница детали проекта"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER PANEL
        self.PROJECT_STATUS = Element("[data-test='ProjectHeader'] [data-test='PscLabel']", "Статус проекта", self.page)
        self.PROJECT_NAME = Element("[data-test='ProjectHeader'] h1", "Название проекта", self.page)
        self.ACTION_INPUT = Element("[data-test='ElSelect:project-actions'] input", "Поле ввода 'Действия'", self.page)
        self.ACTION_OPTIONS = ElementsList(".el-select-dropdown__item", "Варианты 'Действия'", self.page)
        self.PROJECT_NOTIFICATIONS = ElementsList(
            "[data-test='ProjectInlineNotification'] > div:first-child", "Уведомления в проекте", self.page
        )

        self.PP_TAB = Element("#tab-project-product-offerings", "Таб 'Продуктовые предложения'", self.page)

        # PP TAB
        self.ADD_PP_BUTTON = Element(
            "[data-test='ProductOfferingsAddPopover'] button", "Кнопка '+ Добавить продуктовоe предложение'", self.page
        )
        self.ADD_NEW_PP_BUTTON = Element("[data-test='productOffering:CREATE']", "Кнопка 'Создать новое'", self.page)
        self.TABLE_PP_NAME = ElementsList("[data-test='PscLinkButton'] a", "Названия ПП", self.page)


class CreateProductProposalForm(BaseElementsPsc):
    """Форма Создание продуктового предложения"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("[data-test='ProjectProductOfferingsCreate'] h3", "Заголовок формы", self.page)
        self.PP_NAME = Element("[data-test='ElInput:title']", "Название", self.page)
        self.PP_FORMAT = ElementsList("[data-test='PscTabSwitcher'] div", "Кнопки 'Формат'", self.page)
        self.PP_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='product-type-code'] [data-test*='arrow-triangle-down']", "Кнопка открытия 'Тип'", self.page
        )
        self.TYPE_OPTIONS = ElementsList("[data-test='PscOption']", "Варианты 'Тип'", self.page)
        self.PS_INPUT = Element(
            "[data-test*='POActionProductSpecSelect'] [data-test*='PscSelectValueContainer'] input",
            "Поле ввода 'Спецификация'",
            self.page,
        )
        self.PS_FIELD = Element(
            "[data-test*='POActionProductSpecSelect'] [data-test*='PscSelectValueContainer']",
            "Поле 'Спецификация'",
            self.page,
        )
        self.PS_OPTIONS = ElementsList("[data-test='PscOption']", "Варианты 'Тип'", self.page)
        self.SUPPLIER_DROPDOWN_BTN = Element(
            "[data-test*='service-provider-codes'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Поставщик услуг'",
            self.page,
        )
        self.DESCRIPTION_INPUT = Element("[data-test='ElInput:description']", "Поле ввода 'Описание'", self.page)


class PublishConfirmationForm(BaseElementsPsc):
    """Форма 'Перевести проект в тестирование'"""

    def __init__(self, page: Page):
        super().__init__(page)

        self.TITLE = Element("[data-test='PscConfirmPublicationParameters'] h4", "Заголовок формы", self.page)
        self.PUBLISH_PARAMS = ElementsList(
            "[data-test='PscConfirmPublicationParameters'] label > span:first-child", "Параметры публикации", self.page
        )
        self.MOVE_BTN = Element(".psc-confirm-action > button:last-child", "Кнопка 'Перевести/Опубликовать'", self.page)

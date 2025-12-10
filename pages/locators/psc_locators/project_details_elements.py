from pages.locators.psc_locators.base_elements_psc import BasePscElements
from pages.ui_elements import Element, ElementsList


class ProjectDetailsElements(BasePscElements):
    """Страница детали проекта"""

    def __init__(self) -> None:
        super().__init__()

        # HEADER PANEL
        self.PROJECT_STATUS = Element("[data-test='ProjectHeader'] [data-test='PscLabel']", "Статус проекта")
        self.PROJECT_NAME = Element("[data-test='ProjectHeader'] h1", "Название проекта")
        self.ACTION_INPUT = Element("[data-test='ElSelect:project-actions'] input", "Поле ввода 'Действия'")
        self.ACTION_OPTIONS = ElementsList(".el-select-dropdown__item", "Варианты 'Действия'")
        self.PROJECT_NOTIFICATIONS = ElementsList(
            "[data-test='ProjectInlineNotification'] > div:first-child", "Уведомления в проекте"
        )

        self.PP_TAB = Element("#tab-project-product-offerings", "Таб 'Продуктовые предложения'")

        # PP TAB
        self.ADD_PP_BUTTON = Element(
            "[data-test='ProductOfferingsAddPopover'] button", "Кнопка '+ Добавить продуктовоe предложение'"
        )
        self.ADD_NEW_PP_BUTTON = Element("[data-test='productOffering:CREATE']", "Кнопка 'Создать новое'")
        self.TABLE_PP_NAME = ElementsList("[data-test='PscLinkButton'] a", "Названия ПП")


class CreateProductProposalForm(BasePscElements):
    """Форма Создание продуктового предложения"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[data-test='ProjectProductOfferingsCreate'] h3", "Заголовок формы")
        self.PP_NAME = Element("[data-test='ElInput:title']", "Название")
        self.PP_FORMAT = ElementsList("[data-test='PscTabSwitcher'] div", "Кнопки 'Формат'")
        self.PP_TYPE_DROPDOWN_BTN = Element(
            "[data-test*='product-type-code'] [data-test*='arrow-triangle-down']", "Кнопка открытия 'Тип'"
        )
        self.TYPE_OPTIONS = ElementsList("[data-test='PscOption']", "Варианты 'Тип'")
        self.PS_INPUT = Element(
            "[data-test*='POActionProductSpecSelect'] [data-test*='PscSelectValueContainer'] input",
            "Поле ввода 'Спецификация'",
        )
        self.PS_FIELD = Element(
            "[data-test*='POActionProductSpecSelect'] [data-test*='PscSelectValueContainer']",
            "Поле 'Спецификация'",
        )
        self.PS_OPTIONS = ElementsList("[data-test='PscOption']", "Варианты 'Тип'")
        self.SUPPLIER_DROPDOWN_BTN = Element(
            "[data-test*='service-provider-codes'] [data-test*='arrow-triangle-down']",
            "Кнопка открытия 'Поставщик услуг'",
        )
        self.DESCRIPTION_INPUT = Element("[data-test='ElInput:description']", "Поле ввода 'Описание'")


class PublishConfirmationForm(BasePscElements):
    """Форма 'Перевести проект в тестирование'"""

    def __init__(self) -> None:
        super().__init__()

        self.TITLE = Element("[data-test='PscConfirmPublicationParameters'] h4", "Заголовок формы")
        self.PUBLISH_PARAMS = ElementsList(
            "[data-test='PscConfirmPublicationParameters'] label > span:first-child", "Параметры публикации"
        )
        self.MOVE_BTN = Element(".psc-confirm-action > button:last-child", "Кнопка 'Перевести/Опубликовать'")

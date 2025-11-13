import re
from typing import Literal

import allure
from playwright.sync_api import Page

from api.nbss.client_requests.client_requests import InfoAboutBundle, ProductInfo
from common.helpers.checker import assert_that
from common.helpers.data_generator import get_current_datetime_string
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import check_price, get_price_and_currency
from common.helpers.time_helpers import delay
from models.context import test_context
from models.user import BaseClient, IndividualClient
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ContractCreate, CreateSalesAndServiceManagement
from pages.locators.nbss.inquiries_elements import InquiriesElements, ProductEditForm, ReserveResourcesForm


class InquiriesPage(BasePage):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = InquiriesElements(page)
        self.category_map = {"mobile": "Мобильная связь", "satellite": "Спутниковая связь", "internet": "Интернет"}

    @allure.step("Создание продажи")
    def sale_initialization(
        self,
        client: BaseClient | None = None,
        need_contact_data: bool = False,
        agreement: int | None = None,
        account: int | None = None,
        need_spd: Literal["auto", "with adjustment", "no"] = "no",
        delivery_type: Literal["email", "address"] | None = None,
        courier: Literal["СДЭК", "Почта России"] | None = None,
        add_kp: Literal["auto", "manual", "no"] | None = None,
        create_add_agreement: Literal["auto", "manual", "no"] = "auto",
        priority: str | None = None,
    ) -> None:
        need_spd_value = {
            "auto": "Автоматически",
            "with adjustment": "Автоматически, с корректировкой",
            "no": "Не формировать",
        }
        delivery_type_value = {
            "email": "Отправка на e-mail ",
            "address": "Доставка по адресу",
        }
        add_kp_value = {
            "auto": "Сформировать, факт согласования автоматически",
            "manual": "Сформировать, факт согласования вручную",
            "no": "Не формировать",
        }
        create_add_agreement_value = {
            "auto": "Сформировать, факт согласования автоматически",
            "manual": "Сформировать, факт согласования вручную",
            "no": "Не формировать документ",
        }
        create_request_form = CreateSalesAndServiceManagement(self.page)
        self.locators.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"], timeout=20000)
        self.locators.CREATE_APPLICATION.click()
        create_request_form.NEED_SPD.wait_to_be_visible(timeout=20000)

        if need_contact_data is not None and client is not None:
            create_request_form.EMAIL.fill(client.contact_email)
            create_request_form.PHONE.fill(client.contact_phone)

        if agreement is not None and account is not None:
            create_request_form.SALE_ACCOUNT.not_to_be_visible()
            agreement_date = get_current_datetime_string(is_full_format=False)
            create_request_form.SELECTED_AGREEMENT.select_by_value(f"{agreement} от {agreement_date}")
            create_request_form.ADD_ACCOUNT.check_attribute_by_value("aria-required", "true")
            create_request_form.SALE_ACCOUNT.select_by_value(f"{account}")
            create_request_form.ADD_ACCOUNT.not_to_be_visible()

        create_request_form.NEED_SPD.check_attribute_by_value("aria-required", "true")
        if self.page.locator(create_request_form.ADD_KP.path).is_visible():
            create_request_form.ADD_KP.check_attribute_by_value("aria-required", "true")
        create_request_form.CREATE_ADD_AGREEMENT.check_attribute_by_value("aria-required", "true")

        create_request_form.NEED_SPD.select_by_value(need_spd_value[need_spd])
        if need_spd != "no":
            create_request_form.DELIVERY_TYPE.check_attribute_by_value("aria-required", "true")
            create_request_form.DELIVERY_TYPE.select_by_value(delivery_type_value[delivery_type])
            if delivery_type == "email":
                create_request_form.EMAIL_FOR_DELIVERY.check_attribute_by_value("aria-required", "true")
                create_request_form.EMAIL_FOR_DELIVERY.fill(client.contact_email)
            else:
                create_request_form.COURIER.check_attribute_by_value("aria-required", "true")
                create_request_form.ADDRESS_FOR_DELIVERY.check_attribute_by_value("aria-required", "true")
                create_request_form.COURIER.select_by_value(courier)
                create_request_form.ADDRESS_FOR_DELIVERY.fill(client.registration_address)
        if add_kp:
            create_request_form.ADD_KP.select_by_value(add_kp_value[add_kp])
            delay(1, "Не сразу открываются варианты выбора")
        create_request_form.CREATE_ADD_AGREEMENT.wait_to_be_enabled()
        create_request_form.CREATE_ADD_AGREEMENT.select_by_value(create_add_agreement_value[create_add_agreement])
        if priority:
            create_request_form.CHOOSE_PRIORITY_BTN.select_by_value(priority)
        delay(1)
        create_request_form.SAVE_BTN.click()
        self.check_open_sale_inquiry()

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Мобильная связь'")
    def sale_phone_number(self, client: BaseClient | IndividualClient = None) -> ProductInfo:
        """Метод для продажи продукта из категории Мобильная связь
        client: при необходимости продажи продукта на конкретный ЛС, договор для конкретного клиента
        нужно передавать результат работы фикстуры create_user_with_agreement_and_account
        """
        self.bring_to_front(self.page.title())
        product_edit_form = ProductEditForm(self.page)

        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.sale_initialization(
            client, True, test_context.client.agreements[0].number, client.agreements[0].accounts[0].number
        )

        with allure.step("Поиск товаров в категории: Монопродукт, Мобильная связь"):
            self.locators.ADD_SALE_BTN.click()
            self.locators.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.locators.product_offer_form.PRODUCT_CATEGORY.select_by_value("Мобильная связь")
            self.locators.product_offer_form.SEARCH_BTN.click()

        product = self.choose_first_product()

        with allure.step("Бронирование ресурсов"):
            self.locators.ADDED_PRODUCT_EDIT_BTN[0].click(force=True)
            product_edit_form.TITLE.wait_to_have_text(product.product_name)
            product_edit_form.RESOURCES_TAB.click()
            product.phone_number = self.auto_reserve_phone_number_resources()[1]
            product_edit_form.INNER_CANCEL_BTN.click()

        self.check_configuration()

        with allure.step("Завершение продажи"):
            self.locators.NEXT_STEP_BTN.click()
            self.wait_connect_package_offers_and_close_inquiry()
        return product

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Интернет'")
    def sale_internet(self, client: BaseClient | IndividualClient = None) -> ProductInfo:
        self.bring_to_front(self.page.title())

        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.sale_initialization(
            client, True, test_context.client.agreements[0].number, client.agreements[0].accounts[0].number
        )

        with allure.step("Поиск товаров в категории: Монопродукт, Интернет"):
            self.locators.ADD_SALE_BTN.click()
            self.locators.product_offer_form.PRODUCT_TYPE.select_by_value("Монопродукт")
            self.locators.product_offer_form.PRODUCT_CATEGORY.select_by_value("Интернет")
            self.locators.product_offer_form.SEARCH_BTN.click()

        product = self.choose_first_product()
        self.check_configuration()
        self.check_technical_feasibility()

        with allure.step("Завершение продажи"):
            self.locators.NEXT_STEP_BTN.click()
            self.wait_connect_package_offers_and_close_inquiry()
            self.locators.TABS[1].wait_to_have_text("Элементы заказа")
            self.locators.TABS[1].click()
            product.internet_number = self.locators.MONOPRODUCT_SUBSCRIBERS[0].text
        return product

    @allure.step("Проведение продажи для B2B бандла 'Все для бизнеса'")
    def sale_bundle(self) -> InfoAboutBundle:
        product_names = ["Интернет в офис", "Гибкий бизнес", "Телефонная связь"]
        self.sale_initialization()

        with allure.step("Нажать кнопку 'Добавить', установить фильтры"):
            self.locators.ADD_SALE_BTN.click()
            self.locators.product_offer_form.PRODUCT_TYPE.select_by_value("Бандл")
            self.locators.product_offer_form.SEARCH_BTN.click()

        with allure.step("Выбрать Бандл из списка, нажать кнопку 'Добавить'"):
            bundle = self.choose_product_offer_with_name("Все для бизнеса")
            self.locators.product_offer_form.ADD_BTN.click()
            self.check_view_bundle_products([bundle], product_names)

        self.auto_reserve_all_resources()
        self.check_configuration()
        self.check_technical_feasibility()
        self.locators.NEXT_STEP_BTN.click()
        self.locators.AUTO_AGREEMENT_BTN.click()
        self.wait_connect_package_offers_and_close_inquiry()
        self.set_products_subscriber([bundle])
        return bundle

    @allure.step("Проверка заявки на продажу после создания")
    def check_open_sale_inquiry(self, check_info_status: bool = True) -> None:
        self.locators.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"), timeout=15000)
        self.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=100000)
        if check_info_status:
            self.locators.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=25000)

    @allure.step("Выбор первого продукта")
    def choose_first_product(self) -> ProductInfo:
        product = ProductInfo()
        self.locators.product_offer_form.PRODUCT_CARD.wait_elements_visible(0)
        product.product_name = self.locators.product_offer_form.PRODUCT_CARD_NAME[0].text
        self.locators.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()
        self.locators.product_offer_form.ADD_BTN.click()
        self.locators.ADDED_PRODUCT.wait_to_have_count(1)
        self.locators.ADDED_PRODUCT[0].to_contain_text(product.product_name)
        self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
        product.one_time_payment = get_price_and_currency(self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].text)[0]
        self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()
        product.subscription_fee = get_price_and_currency(self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].text)[0]
        self.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        return product

    @allure.step("Нажать кнопку 'Проверить конфигурацию' и дождаться выполнения проверки")
    def check_configuration(self) -> None:
        self.locators.CHECK_CONFIGURATION_BTN.click()
        self.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=40000)
        self.locators.PRODUCT_CHECK_STATUS.wait_elements_visible(0, timeout=10000)
        self.locators.ADD_SALE_BTN.wait_to_be_enabled(timeout=10000)
        delay(3, "Без ожидания переход на следующий этап до завершения проверки конфигурации")
        self.locators.PRODUCT_CHECK_STATUS[0].wait_to_have_text(
            "Конфигурация не содержит ошибок. Для перехода на следующий шаг заявки нажмите Далее", timeout=25000
        )
        self.locators.ADD_SALE_BTN.wait_to_be_enabled(timeout=10000)

    @allure.step(
        "Нажать кнопку 'Проверить техническую возможность' и дождаться выполнения проверки технической возможности подключения продуктов"
    )
    def check_technical_feasibility(self) -> None:
        self.locators.CHECK_TECHNICAL_FEASIBILITY_BTN.click(timeout=15000)
        self.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=60000)
        self.locators.PRODUCT_CHECK_STATUS.wait_elements_visible(0, timeout=10000)
        self.locators.PRODUCT_CHECK_STATUS[0].wait_to_have_text(
            "Для всех продуктов заказа есть техническая возможность подключения. "
            'Для продолжения оформления продажи перейдите на следующий шаг, нажав на кнопку "Далее".',
            timeout=25000,
        )

    @allure.step("Нажать 'Далее' и дождаться перехода на шаг '{step}")
    def click_next(self, step: str) -> None:
        self.locators.RIGHT_ARROW_BTN.wait_to_be_enabled(timeout=10000)
        self.locators.RIGHT_ARROW_BTN.click()
        self.locators.INQUIRY_STEP.wait_to_have_text(step, timeout=120000)

    @allure.step("Выбрать договор, нажав на него, нажать кнопку 'Выбрать договор'")
    def choose_agreement(self, agreement_number: int | None = None, agreement_date: str | None = None) -> None:
        self.locators.CONTRACTS.wait_to_have_count(1, timeout=10000)
        self.locators.CONTRACTS[0].click()
        self.locators.CHOICE_CONTRACT_BTN.click()
        self.locators.LOAD_SPIN.not_to_be_visible(timeout=10000)
        self.locators.CONTRACT_INFO.wait_to_have_text("Выбран договор:", timeout=10000)
        if agreement_number is not None and agreement_date is not None:
            self.locators.CHOSEN_CONTRACT_INFO.wait_to_have_text(
                f"Дата подписания: {agreement_date}, номер: {agreement_number}"
            )
        delay(1.5, "Ожидание для корректного перехода на следующий шаг продажи")

    @allure.step("Добавить договор и выбрать его")
    def add_and_choose_agreement(self) -> None:
        create_contract_form = ContractCreate(self.page)
        self.locators.ADD_CONTRACT_BTN.click()

        create_contract_form.OPERATOR_FIO.select_by_value(test_context.client.operator_name)
        create_contract_form.OPERATOR_BANK_DATA.select_by_value(test_context.client.operator_bank_details)
        create_contract_form.USE_EXISTING_BANK_CHECKBOX.click()
        create_contract_form.CLIENT_BANK_CURRENT_ACCOUNT.fill(test_context.client.bank_account)
        create_contract_form.CLIENT_BANK.select_by_value(test_context.client.bank_name)
        create_contract_form.SAVE_BTN.click()

        self.choose_agreement()

    @allure.step("Добавить ЛС и выбрать его")
    def add_and_choose_account(self) -> None:
        create_contract_form = ContractCreate(self.page)
        self.locators.ADD_ACCOUNT_BTN.click()
        create_contract_form.SAVE_BTN.click()

        self.choose_account()

    @allure.step("Выбрать ЛС {account_number}, выбрать первый продукт, нажать 'Сохранить распределение'")
    def choose_account(self, account_number: int | None = None) -> None:
        if account_number is not None:
            self.locators.ACCOUNT_NUMBER.wait_for_text_in_all([account_number])
            account_index = self.locators.ACCOUNT_NUMBER.text_list.index(account_number)
        else:
            account_index = 0
        self.locators.ACCOUNT_NUMBER.click(account_index)
        product_count = int(self.locators.PRODUCT_COUNT_ON_ACCOUNT[account_index].text)
        self.locators.ADDRESSES_ON_ACCOUNT.wait_to_have_count(1)
        self.locators.ADDRESSES_ON_ACCOUNT_CHECKBOX.click(0)
        self.locators.SAVE_DISTRIBUTION_BTN.click()
        product_count += 1
        self.locators.PRODUCT_COUNT_ON_ACCOUNT[account_index].wait_to_have_text(str(product_count))

        with allure.step("Справа появилось количество распределенных продуктов в графе 'Распределеенные на этот ЛС'"):
            assert_that(
                lambda: self.locators.DISTRIBUTE_RADIOBUTTON.find_by_value(f"Распределенные на этот ЛС {product_count}")
                is not None,
                "Не появилось количество распределенных продуктов",
            )

    @allure.step("Пройти шаги с ручным созданием договора, ЛС и согласованием документов")
    def agreement_and_account_steps_pass(self) -> None:
        self.add_and_choose_agreement()
        self.click_next("Распределение продуктов заказа по ЛС")
        self.add_and_choose_account()
        self.click_next("Формирование и подписание документа Договор/ДС")
        if hasattr(test_context.client, "inquiry") and test_context.client.inquiry.product.category == "satellite":
            self.locators.AGREEMENT.wait_to_have_count(2)
            agreement_index = next(
                (index for index, doc_type in enumerate(self.locators.AGREEMENT_TYPE) if doc_type.text == "Договор"),  # type: ignore
                None,
            )
            self.locators.AGREEMENT[agreement_index].click()
        else:
            self.locators.AGREEMENT.wait_to_have_count(1)
            self.locators.AGREEMENT[0].click()
        self.locators.AGREE_BTN.click()
        self.refresh_page(wait="load")
        self.locators.RIGHT_ARROW_BTN.wait_to_be_enabled(timeout=15000)
        delay(5, "Чтобы заявка успела загрузиться")
        self.locators.RIGHT_ARROW_BTN.click()
        delay(2, "Чтобы заявка успела перейти на следующий шаг")

    @allure.step("Ожидание закрытия заявки")
    def wait_close_inquiry(self) -> None:
        self.locators.INQUIRY_STEP.wait_to_have_text("Контрольная Проверка КЗ", timeout=100000)
        self.locators.INQUIRY_STEP.wait_to_have_text("Управление продуктами", timeout=30000)
        self.locators.INQUIRY_STEP.wait_to_have_text("Завершение продажи", timeout=100000)
        self.locators.PRODUCT_INFO_STATUS.wait_to_have_text(re.compile("Успешно выполнено"), timeout=30000)

    @allure.step("Дождаться подключения выбранных пакетных предложений и закрытия заявки")
    def wait_connect_package_offers_and_close_inquiry(
        self, auto_create_agreement: bool = True, generate_documents: bool = True
    ) -> None:
        if auto_create_agreement:
            self.locators.INQUIRY_STEP.wait_to_have_text("Автоматическое управление Договором/ДС и ЛС", timeout=20000)
        if generate_documents:
            self.locators.INQUIRY_STEP.wait_to_have_text("Формирование документов (тех.шаг)", timeout=80000)
        self.wait_close_inquiry()

    @allure.step("Ручное согласование документа")
    def manual_agree_document(self, document_index: int = 0) -> None:
        self.locators.NEXT_STEP_BTN.click()

        self.locators.INQUIRY_STEP.wait_to_have_text("Формирование документов (тех.шаг)", timeout=40000)
        self.locators.INQUIRY_STEP.wait_to_have_text("Формирование и подписание документа Договор/ДС", timeout=40000)

        self.locators.DOCUMENTS_LIST[document_index].click()
        self.locators.AGREE_BTN.wait_to_be_visible()
        self.locators.AGREE_BTN.click()
        self.locators.AGREEMENT_FLAG.wait_to_be_visible()

    @allure.step("Проверить отображение продуктов бандлов (количество, названия, начисления)")
    def check_view_bundle_products(self, bundles: list[InfoAboutBundle], product_names: list[str]) -> None:
        self.locators.ADDED_BUNDLE.wait_to_have_count(len(bundles), timeout=20000)
        self.locators.ADDED_MONOPRODUCT.wait_to_have_count(len(product_names))
        self.locators.ADDED_BUNDLE_NAMES.wait_for_text_in_all([bundle.bundle_name for bundle in bundles])
        self.locators.ADDED_PRODUCT_NAMES.wait_for_text_in_all(product_names)
        self.set_products_charge(bundles)

    @allure.step("Проверка Статуса продажи, Названия шага, Активной вкладки на первом шаге продажи")
    def check_first_step_sale_titles(self, product_count: int = 0) -> None:
        self.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
        self.locators.TABS.wait_to_be_visible()
        self.locators.TABS[0].wait_to_have_text("Активный шаг")
        self.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.locators.ADDED_PRODUCT.wait_to_have_count(product_count)

    @allure.step("Проверка формы 'Выбор продуктовых предложений'")
    def check_product_offer_form(self) -> None:
        self.locators.product_offer_form.TITLE.to_contain_text("Выбор продуктов")
        self.locators.product_offer_form.PRODUCT_TYPE.wait_to_be_enabled()
        self.locators.product_offer_form.PRODUCT_CATEGORY_CHECKBOX.wait_to_be_enabled()
        self.locators.product_offer_form.TECHNOLOGY.wait_to_be_enabled()
        checked_value = self.locators.product_offer_form.PRODUCT_TYPE.checked_value
        assert_that(
            lambda: checked_value == "Монопродукт",
            f"По умолчанию не выбрано 'Монопродукт'. Текущее значение: {checked_value}",
        )

    @allure.step("Добавление продуктового предложения")
    def add_product_offer_to_commercial_order(self, product: ProductInfo) -> ProductInfo | InfoAboutBundle:
        self.locators.ADD_SALE_BTN.wait_to_be_visible(timeout=10000)
        self.locators.ADD_SALE_BTN.click()
        with allure.step("Выбор категории продуктового предложения"):
            category_index = next(
                (  # type: ignore
                    index
                    for index, category in enumerate(self.locators.product_offer_form.PRODUCT_CATEGORY_NAMES)
                    if self.category_map[product.category] in category.text
                ),
                None,
            )
            assert_that(lambda: category_index is not None, "Категория не найдена в списке")
            self.locators.product_offer_form.PRODUCT_CATEGORY_NAMES[category_index].click()
            self.locators.product_offer_form.SEARCH_BTN.click()
        added_product = self.choose_product_offer_with_name(product.product_name)
        product.subscription_fee = added_product.subscription_fee
        product.one_time_payment = added_product.one_time_payment
        self.locators.product_offer_form.ADD_BTN.wait_to_be_enabled()
        self.locators.product_offer_form.ADD_BTN.click()
        return product

    @allure.step("Выбор продуктового предложения {product_offer_name}")
    def choose_product_offer_with_name(self, product_offer_name: str) -> ProductInfo | InfoAboutBundle:
        self.locators.product_offer_form.PRODUCT_CARD_NAME.wait_to_be_visible(timeout=20000)
        self.locators.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([product_offer_name], timeout=10000)
        index = self.locators.product_offer_form.PRODUCT_CARD_NAME.text_list.index(product_offer_name)
        self.locators.product_offer_form.PRODUCT_CARD_SELECT_BTN.click(index)
        self.locators.product_offer_form.PRODUCT_CARD_SELECT_BTN[index].wait_to_have_text("Удалить")
        product = ProductInfo()
        if product_offer_name == "Все для бизнеса":
            bundle = InfoAboutBundle(bundle_name=product_offer_name)
            products = (
                self.page.locator(self.locators.product_offer_form.PRODUCT_CARD.path)
                .nth(index)
                .locator(self.locators.product_offer_form.PRODUCT_CARD_PRODUCTS.path)
            )
            for product_name in products.all_text_contents():
                product.product_name = product_name
                bundle.add_product(product)
            bundle.one_time_payment = get_price_and_currency(
                self.locators.product_offer_form.PRODUCT_SINGLE_PAYMENTS[index].text
            )[0]
            bundle.subscription_fee = get_price_and_currency(
                self.locators.product_offer_form.PRODUCT_CARD_SUMS[index].text
            )[0]
            return bundle
        else:
            product.product_name = product_offer_name
            product.one_time_payment = get_price_and_currency(
                self.locators.product_offer_form.PRODUCT_SINGLE_PAYMENTS[index].text
            )[0]
            product.subscription_fee = get_price_and_currency(
                self.locators.product_offer_form.PRODUCT_CARD_SUMS[index].text
            )[0]
            return product

    @allure.step(
        "Для каждого монопродукта через кнопку редактирования заполнить обязательные параметры и ресурсы и сохранить изменения"
    )
    def auto_reserve_all_resources(self, category: str = "mobile") -> None:
        scroll = 80
        product_edit_form = ProductEditForm(self.page)
        self.locators.ADDED_PRODUCT_EDIT_BTN.wait_to_be_visible(timeout=15000)
        self.locators.LOAD_SPIN.not_to_be_visible()
        count = self.locators.ADDED_PRODUCT_EDIT_BTN.elements_len()
        for edit_btn_index in range(count):
            product_edit_form.TITLE.not_to_be_visible()
            self.locators.LOAD_SPIN_THIRD.not_to_be_visible()
            self.locators.ADDED_PRODUCT_EDIT_BTN.wait_elements_visible(edit_btn_index)
            self.locators.ADDED_PRODUCT_EDIT_BTN[edit_btn_index].scroll_into_view_if_needed()
            self.locators.SCROLLABLE_PRODUCT_BLOCK.scroll_scrollable_platform(scroll)
            self.locators.ADDED_PRODUCT_EDIT_BTN[edit_btn_index].click(force=True)
            product_edit_form.RESOURCES_TAB.wait_to_be_enabled()
            if self.page.locator(product_edit_form.SPECIFICATION_ERROR_ICON.path).is_visible():
                product_edit_form.TEST_CHARC.fill("test")
            product_edit_form.RESOURCES_TAB.click()
            if self.page.locator(product_edit_form.MODAL.path).is_visible():
                product_edit_form.MODAL_SECOND_BTN.click()
            product_edit_form.RESOURCES.wait_to_be_visible(timeout=10000)
            self.auto_reserve_phone_number_resources()
            if category == "satellite":
                self.reserve_equipment()
            product_edit_form.INNER_ACCEPT_BTN.click()

    @allure.step("Получение и проверка стоимости монопродуктов бандлов")
    def set_products_charge(self, bundles: list[InfoAboutBundle]) -> None:
        bundle_names = self.locators.ADDED_BUNDLE_NAMES.text_list
        product_names = self.locators.ADDED_PRODUCT_NAMES.text_list
        for bundle in bundles:
            one_time_payment_summ, subscription_fee_summ = 0.0, 0.0

            bundle_index = bundle_names.index(bundle.bundle_name)
            bundle_names[bundle_index] = ""
            check_price(self.locators.ADDED_BUNDLE_ONE_TIME_PAYMENT[bundle_index], bundle.one_time_payment)
            check_price(self.locators.ADDED_BUNDLE_SUBSCRIPTION_FEE[bundle_index], bundle.subscription_fee)
            for product in bundle.products:
                product_index = product_names.index(product.product_name)
                product_names[product_index] = ""
                product.one_time_payment = get_price_and_currency(
                    self.locators.ADDED_MONOPRODUCT_ONE_TIME_PAYMENT[product_index].text
                )[0]
                product.subscription_fee = get_price_and_currency(
                    self.locators.ADDED_MONOPRODUCT_SUBSCRIPTION_FEE[product_index].text
                )[0]
                one_time_payment_summ += product.one_time_payment
                subscription_fee_summ += product.subscription_fee
            assert_that(
                lambda: bundle.one_time_payment == one_time_payment_summ,
                f"Разовый платеж за бандл {bundle.one_time_payment} "
                f"не равен сумме разовых платежей за монопродукты, входящие в бандл {one_time_payment_summ}",
            )
            assert_that(
                lambda: bundle.subscription_fee == subscription_fee_summ,
                f"Абонентская плата за бандл {bundle.subscription_fee} "
                f"не равна сумме абонентских плат за монопродукты, входящие в бандл {subscription_fee_summ}",
            )

    @allure.step("Получение абонентов монопродуктов бандлов")
    def set_products_subscriber(self, bundles: list[InfoAboutBundle]) -> None:
        self.locators.TABS[1].wait_to_have_text("Элементы заказа")
        self.locators.TABS[1].click()
        bundle_names = [bundle.bundle_name for bundle in bundles]
        self.locators.PRODUCTS_NAME.wait_for_text_in_all(bundle_names)
        bundle_products = []
        for bundle in bundles:
            for product in bundle.products:
                bundle_products.append(product)
        for monoproduct_index in range(self.locators.MONOPRODUCT_NAMES.elements_len()):
            name = self.locators.MONOPRODUCT_NAMES.text_list[monoproduct_index]
            for product in bundle_products:
                if name == product.product_name and product.phone_number == "" and product.internet_number == "":
                    subscriber = self.locators.MONOPRODUCT_SUBSCRIBERS[monoproduct_index].text
                    if subscriber.isdigit():
                        product.phone_number = subscriber
                    else:
                        product.internet_number = subscriber
                    break

    @allure.step("Проверка значений поля Итого")
    def check_total_fields(self, one_time_payment: float, subscription_fee: float) -> None:
        check_price(self.locators.TOTAL_ONE_TIME_PAYMENT, one_time_payment)
        check_price(self.locators.TOTAL_SUBSCRIPTION_FEE, subscription_fee)

    @allure.step("Бронирование SIM-карты и Телефонного номера")
    def auto_reserve_phone_number_resources(self, number_class: str = "Обычный") -> tuple[str | None, str | None]:
        reserve_form = ReserveResourcesForm(self.page)
        product_edit_form = ProductEditForm(self.page)
        iccid, number = None, None
        if self.page.locator(product_edit_form.RESERVE_RESOURCES_SELECT.path).is_visible():
            # TODO https://jira.nexign.com/browse/TUDS-4427 после фикса вернуть product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("SIM-карта")
            product_edit_form.CHANGE_ICCID_BTN.click()
            iccid = self.reserve_sim()
            product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
            # TODO https://jira.nexign.com/browse/TUDS-4427 после фикса вернуть product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("Телефонный номер (мобильный)")
            product_edit_form.CHANGE_NUMBER_BTN.click()
            number = self.reserve_number(number_class=number_class)
        else:
            product_edit_form.RESERVE_RESOURCES_BTN.click()
            if reserve_form.TITLE.text == "Бронирование SIM-карты":
                iccid = self.reserve_sim()
            if reserve_form.TITLE.text == "Бронирование номера":
                number = self.reserve_number(number_class=number_class, switch="Коммутатор_ABC")
        product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
        if iccid:
            product_edit_form.ICCID.wait_to_have_text(iccid)
        if number:
            product_edit_form.PHONE_NUMBER.wait_to_have_text(number)
        return iccid, number

    @allure.step("Бронирование SIM-карты")
    def reserve_sim(
        self,
        search_type: str = None,
        mask: str = None,
        left_range: str = None,
        right_range: str = None,
        switch: str = None,
    ) -> str | None:
        reserve_form = ReserveResourcesForm(self.page)
        delay(1, "Ожидание для корректного получения значений полей")
        if search_type:
            reserve_form.SEARCH_TYPE.select_by_value(search_type)
        if mask:
            delay(1, "Ожидание для корректного заполнения поля")
            reserve_form.MASK_INPUT.fill(mask)
        if left_range:
            reserve_form.RANGE_LEFT_INPUT.fill(left_range)
        if right_range:
            reserve_form.RANGE_RIGHT_INPUT.fill(right_range)
        if switch:
            reserve_form.SWITCH.select_by_value(switch)
        reserve_form.SEARCH_BUTTON.click()
        reserve_form.SIM_ICC.wait_elements_visible(0)
        icc = reserve_form.SIM_ICC[0].text
        reserve_form.SIM_CHECKBOX.click(0)
        reserve_form.BOOK_BTN.click()
        reserve_form.TITLE.not_to_be_visible(timeout=10000)
        return icc

    @allure.step("Бронирование Телефонного номера")
    def reserve_number(
        self,
        mask: str = None,
        left_range: str = None,
        right_range: str = None,
        resource_count: int = 1,
        standard: str = "GSM",
        switch: str = "Коммутатор_DEF",
        numbering_type: str = None,
        number_class: str = "Обычный",
        free_for: str = None,
    ) -> str | None:
        reserve_form = ReserveResourcesForm(self.page)
        delay(1, "Ожидание для корректного получения значений полей")
        if reserve_form.RESOURCE_COUNT.text == "0":
            reserve_form.RESOURCE_COUNT.fill(str(resource_count))
        if (
            not self.page.locator(reserve_form.STANDARD_INPUT.path)
            .locator("[class*=select-selection-item]")
            .is_visible()
        ):
            reserve_form.STANDARD_INPUT.select_by_value(standard)
        if mask:
            delay(1, "Ожидание для корректного заполнения поля")
            reserve_form.MASK_INPUT.fill(mask)
        if left_range:
            reserve_form.RANGE_LEFT_INPUT.fill(left_range)
        if right_range:
            reserve_form.RANGE_RIGHT_INPUT.fill(right_range)
        if reserve_form.SWITCH.get_attribute("disabled") is not None:
            reserve_form.SWITCH.select_by_value(switch)
        reserve_form.NUMBER_CLASS.select_by_value(number_class)
        if numbering_type:
            reserve_form.NUMBERING_TYPE.select_by_value(numbering_type)
        if free_for:
            reserve_form.FREE_FOR.fill(free_for)
        reserve_form.SEARCH_BUTTON.click()
        reserve_form.NUMBER.wait_elements_visible(0)
        number = reserve_form.NUMBER[0].text
        reserve_form.NUMBER_CHECKBOX.click(0)
        reserve_form.BOOK_BTN.click()
        reserve_form.RESOURCE_COUNT.not_to_be_visible(timeout=10000)
        return number

    @allure.step("Бронирование Оборудования")
    def reserve_equipment(
        self,
    ) -> str | None:
        reserve_form = ReserveResourcesForm(self.page)
        product_edit_form = ProductEditForm(self.page)
        product_edit_form.CHANGE_EQUIPMENT_BTN.click()
        delay(1, "Ожидание для корректного получения значений полей")
        reserve_form.SEARCH_BUTTON.click()
        reserve_form.EQUIPMENT_NUMBER.wait_elements_visible(1)
        equipment_index = next(
            (index for index, equipment in enumerate(reserve_form.EQUIPMENT_NAME) if "_L_" in equipment.text),  # type: ignore
            None,
        )
        assert_that(lambda: equipment_index is not None, "Нет нужных ресурсов для бронирования на стенде")
        number = reserve_form.EQUIPMENT_NUMBER[equipment_index].text
        reserve_form.EQUIPMENT_CHECKBOX[equipment_index].click()
        reserve_form.BOOK_BTN.click()
        reserve_form.RESOURCE_COUNT.not_to_be_visible(timeout=10000)
        product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible(timeout=10000)
        return number

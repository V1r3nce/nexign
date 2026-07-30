import re
from typing import Literal, cast

import allure

from api.exceptions import IncorrectServicesInListException, SwitchDropdownIsNotDisabledException
from api.nbss.client_requests.client_requests import InfoAboutBundle, MainProduct
from common.enums.inquiry import InquiryStep
from common.helpers.checker import assert_that, check_that
from common.helpers.data_generator import (
    calc_price_after_discount,
    generate_english_string,
    get_current_datetime_string,
    get_shifted_datetime_string,
)
from common.helpers.download_helper import CheckFile
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import (
    check_price,
    check_price_with_tax,
    extract_volume_in_inquiry,
    get_price_and_currency,
)
from common.helpers.time_helpers import delay
from models.address_info import BasicSystemAddress
from models.client import BaseClient, IndividualClient
from models.context import test_context
from models.stand_context import stand_context
from pages.base_page import BasePage
from pages.locators.nbss.client.client_product_profile import ClientProductProfileElements
from pages.locators.nbss.client.client_profile import ClientProfileElements
from pages.locators.nbss.dynamic_form_elements import (
    AddOptionsForm,
    ChooseRequestTopic,
    ContractCreate,
    CreateSalesAndServiceManagement,
    RequestCreate,
)
from pages.locators.nbss.inquiries_elements import (
    InquiriesElements,
    MassDiscountEditForm,
    ProductEditForm,
    ProductsMoveInquiryElements,
    ReserveResourcesForm,
)


class InquiriesPage(BasePage):
    """Страница /inquiries/{inquiries_id} 'Продажа и управление услугами'"""

    def __init__(self) -> None:
        super().__init__()

        self.choose_request_topic = ChooseRequestTopic()
        self.client_profile_elements = ClientProfileElements()
        self.client_product_profile_elements = ClientProductProfileElements()
        self.request_create = RequestCreate()
        self.locators = InquiriesElements()
        self.product_edit_form = ProductEditForm()
        self.mass_discount_form = MassDiscountEditForm()
        self.move_inquiry_locators = ProductsMoveInquiryElements()
        self.product_edit_form = ProductEditForm()
        self.reserve_resources_form = ReserveResourcesForm()
        self.category_map = {
            "mobile": "Мобильная связь",
            "satellite_sale": "Спутниковая связь",
            "satellite_rent": "Спутниковая связь",
            "equipment_sale": "Товары и оборудование",
            "equipment_rent": "Товары и оборудование",
            "internet": "Интернет",
        }

    @allure.step("Открыть страницу с заявкой")
    def open_inquiry_page(self, inquiry_id: int) -> None:
        self.open(f"{BASE_URL}inquiries/{inquiry_id}")
        self.locators.INQUIRY_STEP.wait_to_be_visible(timeout=20000)

    @allure.step("Открыть страницу с заявкой")
    def open_inquiry_commercial_order_step(self, inquiry_id: int, product_count: int = 2) -> None:
        self.open_inquiry_page(inquiry_id)
        self.check_first_step_sale_titles(product_count=product_count)

    @allure.step("Создание продажи и заполнение данных в форме")
    def sale_initialization(
        self,
        client: BaseClient | None = None,
        need_contact_data: bool = False,
        agreement: str | None = None,
        account: int | None = None,
        need_spd: Literal["auto", "with adjustment", "no"] = "no",
        delivery_type: Literal["email", "address"] | None = None,
        courier: Literal["СДЭК", "Почта России"] | None = None,
        add_kp: Literal["auto", "manual", "no"] | None = None,
        create_add_agreement: Literal["auto", "manual", "no"] = "auto",
        priority: str | None = None,
        need_initialization: bool = True,
        future_date: bool | str = False,
        verify_open: bool = True,
    ) -> None:
        """Создание продажи и заполнение данных в форме инициализации

        :param client: Клиент, данные которого используются для заполнения контактной информации и адреса
        :param need_contact_data: Флаг необходимости заполнения контактных данных клиента
        :param agreement: Идентификатор соглашения для выбора в форме
        :param account: Идентификатор лицевого счёта для привязки к продаже
        :param need_spd: Параметр формирования РПД ("auto", "with adjustment", "no")
        :param delivery_type: Тип доставки СПД ("email", "address")
        :param courier: Курьерская служба при доставке по адресу ("СДЭК", "Почта России")
        :param add_kp: Параметр формирования КП ("auto", "manual", "no")
        :param create_add_agreement: Параметр формирования соглашения ("auto", "manual", "no")
        :param priority: Приоритет заявки
        :param need_initialization: Флаг необходимости нажатия кнопки создания заявки перед заполнением формы
        :param future_date: Отложенная активация: True (дата = завтра), строка с датой "ДД.ММ.ГГГГ" или False
        :param verify_open: Флаг проверки открытия заявки после сохранения (учитывается только при need_initialization=True)
        """
        create_request_form = CreateSalesAndServiceManagement()
        self.locators.CONTEXT_ELEMENT.wait_for_text_in_all(["Клиент"], timeout=20000)
        if need_initialization:
            self.locators.CREATE_APPLICATION.click()
        self.fill_inquiry_create_form(
            client,
            need_contact_data,
            agreement,
            account,
            need_spd,
            delivery_type,
            courier,
            add_kp,
            create_add_agreement,
            priority,
            future_date=future_date,
        )
        delay(1, "Чтобы UI форма успела подхватить изменения")
        create_request_form.SAVE_BTN.click()
        if need_initialization and verify_open:
            self.check_open_sale_inquiry()

    @allure.step("Заполнение данных в форме создания заявки")
    def fill_inquiry_create_form(
        self,
        client: BaseClient | None = None,
        need_contact_data: bool = False,
        agreement: str | None = None,
        account: int | None = None,
        need_spd: Literal["auto", "with adjustment", "no"] = "no",
        delivery_type: Literal["email", "address"] | None = None,
        courier: Literal["СДЭК", "Почта России"] | None = None,
        add_kp: Literal["auto", "manual", "no"] | None = None,
        create_add_agreement: Literal["auto", "manual", "no"] = "auto",
        priority: str | None = None,
        select_contact_person: bool = False,
        future_date: bool | str = False,
    ) -> None:
        need_spd_value = {
            "auto": "Автоматически",
            "with adjustment": "Автоматически, с корректировкой",
            "no": "Не формировать",
        }
        delivery_type_value = {
            "email": "Отправка на email",
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
        create_request_form = CreateSalesAndServiceManagement()
        create_request_form.NEED_SPD.wait_to_be_visible(timeout=25000)

        if select_contact_person:
            create_request_form.CONTACT_PERSON.select_by_index(0)

        if need_contact_data is not None and client is not None:
            create_request_form.EMAIL.wait_to_be_enabled()
            create_request_form.EMAIL.fill(client.contact_email)
            create_request_form.PHONE.wait_to_be_enabled()
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

        if future_date:
            with allure.step("Активировать чекбокс 'Запланировать выполнение заказа на дату' и заполнить дату"):
                date_value = (
                    future_date
                    if isinstance(future_date, str)
                    else get_shifted_datetime_string("+1d", template="%d.%m.%Y %H:%M")
                )
                create_request_form.SCHEDULE_EXECUTION_CHECKBOX.wait_to_be_enabled(timeout=10000)
                if not create_request_form.SCHEDULE_EXECUTION_CHECKBOX.has_attribute_value("checked", ""):
                    create_request_form.SCHEDULE_EXECUTION_CHECKBOX.click()
                create_request_form.EXECUTION_DATE.wait_to_be_visible(timeout=10000)
                create_request_form.EXECUTION_DATE.check_attribute_by_value("aria-required", "true")
                create_request_form.EXECUTION_DATE.fill(date_value)
                self.press_keyboard_button("Enter")

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Мобильная связь'")
    def sale_phone_number(self, client: BaseClient | IndividualClient = None) -> MainProduct:
        """Метод для продажи продукта из категории Мобильная связь
        client: при необходимости продажи продукта на конкретный ЛС, договор для конкретного клиента
        нужно передавать результат работы фикстуры create_user_with_agreement_and_account
        """
        self.bring_to_front(self.page.title())

        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.sale_initialization(
            client, True, test_context.client.agreements[0].number, client.agreements[0].accounts[0].number
        )

        with allure.step("Поиск товаров в категории: Монопродукт, Мобильная связь"):
            self.locators.ADD_SALE_BTN.click()
            self.search_products_in_form(product_category_name="Мобильная связь", product_type="Монопродукт")

        product = self.choose_first_product()

        with allure.step("Бронирование ресурсов"):
            self.locators.PRODUCT_RESOURCES_UNFILLED_BTN[0].click(force=True)
            self.product_edit_form.TITLE.wait_to_have_text(product.product_name)
            self.product_edit_form.RESOURCES_TAB.click()
            product.phone_number = self.auto_reserve_phone_number_resources()[1]
            self.product_edit_form.INNER_CANCEL_BTN.click()

        self.check_configuration()

        with allure.step("Завершение продажи"):
            self.locators.NEXT_STEP_BTN.click()
            self.wait_connect_package_offers_and_close_inquiry()
        return product

    @allure.step("Проведение продажи для B2C монопродукта из категории 'Интернет'")
    def sale_internet(self, client: BaseClient | IndividualClient = None) -> MainProduct:
        self.bring_to_front(self.page.title())

        self.open(f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/overview")
        self.sale_initialization(
            client, True, test_context.client.agreements[0].number, client.agreements[0].accounts[0].number
        )

        with allure.step("Поиск товаров в категории: Монопродукт, Интернет"):
            self.locators.ADD_SALE_BTN.click()
            self.search_products_in_form(product_category_name="Интернет", product_type="Монопродукт")

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
            self.search_products_in_form(product_type="Пакетные предложения")

        with allure.step("Выбрать Бандл из списка, нажать кнопку 'Добавить'"):
            bundle = self.choose_product_offer_with_name("Все для бизнеса")
            self.locators.product_offer_form.ADD_BTN.click()
            self.check_view_bundle_products([bundle], product_names)  # type: ignore

        self.auto_reserve_all_resources()
        self.check_configuration()
        self.check_technical_feasibility()
        self.locators.NEXT_STEP_BTN.click()
        self.locators.AUTO_AGREEMENT_BTN.click()
        self.wait_connect_package_offers_and_close_inquiry()
        self.set_products_subscriber([bundle])  # type: ignore
        return bundle  # type: ignore

    @allure.step("Проверка заявки на продажу после создания")
    def check_open_sale_inquiry(self, check_info_status: bool = True) -> None:
        self.locators.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Продажа и управление услугами"), timeout=20000)
        self.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=100000)
        self.locators.ADD_SALE_BTN.wait_to_be_visible(timeout=15000)
        if check_info_status:
            self.locators.PRODUCT_INFO_STATUS.wait_to_be_visible(timeout=25000)

    @allure.step("Выбор первого продукта")
    def choose_first_product(self) -> MainProduct:
        product = MainProduct()
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
        self.locators.LOAD_SPIN_FIRST.not_to_be_visible_for(invisible_time=10000)
        self.locators.CHECK_CONFIGURATION_BTN.wait_to_be_visible(timeout=50000)
        self.locators.CHECK_CONFIGURATION_BTN.click()
        self.locators.LOAD_SPIN_FIRST.not_to_be_visible(timeout=40000)
        self.locators.PRODUCT_CHECK_STATUS.wait_elements_visible(0, timeout=10000)
        self.locators.ADD_SALE_BTN.wait_to_be_enabled(timeout=20000)
        delay(3, "Без ожидания переход на следующий этап до завершения проверки конфигурации")
        self.locators.PRODUCT_CHECK_STATUS[0].wait_to_have_text(
            'Конфигурация не содержит ошибок, для перехода на следующий шаг заявки нажмите "Далее"', timeout=45000
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
        self.locators.CONTRACT_INFO.wait_to_have_text("Выбран договор:", timeout=20000)
        if agreement_number is not None and agreement_date is not None:
            self.locators.CHOSEN_CONTRACT_INFO.wait_to_have_text(f"{agreement_number} от {agreement_date}")
        delay(1.5, "Ожидание для корректного перехода на следующий шаг продажи")

    @allure.step("Добавить договор и выбрать его")
    def add_and_choose_agreement(self) -> None:
        create_contract_form = ContractCreate()
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
        create_contract_form = ContractCreate()
        self.locators.ADD_ACCOUNT_BTN.click()
        create_contract_form.SAVE_BTN.click()

        self.choose_account()

    @allure.step("Выбрать ЛС {account_number}, выбрать первый продукт, нажать 'Сохранить распределение'")
    def choose_account(self, account_number: int | None = None) -> None:
        if account_number is not None:
            self.locators.ACCOUNT_NUMBER.wait_for_text_in_all([str(account_number)])
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
                lambda: (
                    self.locators.DISTRIBUTE_RADIOBUTTON.find_by_value(f"Распределенные на этот ЛС {product_count}")
                    is not None
                ),
                "Не появилось количество распределенных продуктов",
            )

    @allure.step("Пройти шаги с ручным созданием договора, ЛС и согласованием документов")
    def agreement_and_account_steps_pass(self, num_agreement: int = 1) -> None:
        self.add_and_choose_agreement()
        self.click_next("Распределение продуктов заказа по ЛС")
        self.add_and_choose_account()
        self.click_next("Формирование и подписание документа Договор/ДС")
        if hasattr(test_context.client, "inquiry") and "satellite" in test_context.client.inquiry.product.category:
            self.locators.AGREEMENT.wait_to_have_count(2)
            agreement_index = next(
                (index for index, doc_type in enumerate(self.locators.AGREEMENT_TYPE) if doc_type.text == "Договор"),
                None,
            )
            self.locators.AGREEMENT[agreement_index].click()
        else:
            self.locators.AGREEMENT.wait_to_have_count(num_agreement)
            self.locators.AGREEMENT[num_agreement - 1].click()
        self.locators.AGREE_BTN.click()
        self.refresh_page(wait="load")
        self.locators.RIGHT_ARROW_BTN.wait_to_be_enabled(timeout=15000)
        delay(5, "Чтобы заявка успела загрузиться")
        self.locators.RIGHT_ARROW_BTN.click()
        delay(2, "Чтобы заявка успела перейти на следующий шаг")

    @allure.step("Ожидание завершения заявки")
    def wait_sale_completion(self) -> None:
        self.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.SaleCompletion, timeout=100000)
        self.locators.PRODUCT_INFO_STATUS.wait_to_have_text(
            re.compile(InquiryStep.SaleCompletedSuccessfully), timeout=30000
        )

    @allure.step("Ожидание закрытия заявки")
    def wait_close_inquiry(self) -> None:
        self.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.ControlCommercialOrderCheck, timeout=100000)
        self.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.ManageProducts, timeout=40000)
        self.wait_sale_completion()

    @allure.step("Дождаться подключения выбранных пакетных предложений и закрытия заявки")
    def wait_connect_package_offers_and_close_inquiry(
        self, auto_create_agreement: bool = True, generate_documents: bool = True
    ) -> None:
        if auto_create_agreement:
            self.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.AutoAgreementAndAccountManagement, timeout=60000)
        if generate_documents:
            self.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.DocumentGenerationTechnicalStep, timeout=80000)
        self.wait_close_inquiry()

    @allure.step("Пройти шаги заявки на перенос ПП")
    def manual_inquiry_product_move_steps_pass(
        self,
        agreement_delete_step: bool = False,
        docs_form: bool = True,
        docs_form_sign: bool = False,
        docs_agreement_form_sign: bool = True,
        next_button_necessary: bool = True,
    ) -> None:
        if agreement_delete_step:
            self.locators.INQUIRY_STEP.wait_to_have_text("Подтверждение расторжения договора", timeout=40000)
            self.move_inquiry_locators.AGREEMENT_TERMINATE.click()
            self.locators.NEXT_STEP_BTN.click()
        if docs_form:
            self.locators.INQUIRY_STEP.wait_to_have_text(InquiryStep.DocumentGenerationTechnicalStep, timeout=40000)
        if docs_form_sign:
            self.locators.INQUIRY_STEP.wait_to_have_text("Формирование и подписание документов", timeout=40000)
            self.refresh_page(wait="load")
            self.manual_agree_document()
            self.locators.NEXT_STEP_BTN.click()
        if docs_agreement_form_sign:
            self.locators.INQUIRY_STEP.wait_to_have_text("Формирование и подписание документа Договор/ДС", timeout=40000)
        if next_button_necessary:
            self.locators.NEXT_STEP_BTN.click()
        self.locators.INQUIRY_STEP.wait_to_have_text("Завершение переоформления", timeout=40000)
        self.refresh_page(wait="load")
        self.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=50000)

    @allure.step("Ручное согласование документов")
    def manual_agree_document(self) -> None:
        self.locators.DOCUMENTS_LIST.wait_to_be_visible(timeout=20000)
        self.locators.AGREEMENTS_TABLE_REFRESH.wait_to_be_enabled()
        self.locators.AGREEMENTS_TABLE_REFRESH.click()
        self.locators.DOCUMENTS_LIST.wait_to_be_visible(timeout=15000)
        self.refresh_page(wait="load")
        self.locators.DOCUMENTS_LIST.wait_to_be_visible(timeout=20000)
        for index in range(self.locators.DOCUMENTS_LIST.elements_len()):
            self.locators.DOCUMENTS_LIST[index].click()
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
        self.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа", timeout=15000)
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

    @allure.step("Поиск ПП внутри формы")
    def search_products_in_form(
        self,
        product_offer_name: str = None,
        product_category_name: str = "Интернет",
        product_type: str = "Монопродукт",
        type_transfer_rent: bool = False,
    ) -> None:
        self.locators.product_offer_form.SEARCH_BTN.wait_to_be_enabled()
        self.locators.product_offer_form.PRODUCT_TYPE.select_by_value(product_type)
        if product_type == "Монопродукт":
            self.locators.product_offer_form.PRODUCT_CATEGORY.select_by_value(product_category_name)
        if product_offer_name:
            self.locators.product_offer_form.PRODUCT_SEARCH.fill(product_offer_name)
        self.locators.product_offer_form.SEARCH_BTN.wait_to_be_enabled()
        self.locators.product_offer_form.SEARCH_BTN.click()
        self.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=30000)
        self.locators.product_offer_form.PRODUCT_CARD_NAME.wait_to_be_visible(timeout=15000)
        if type_transfer_rent:
            self.locators.product_offer_form.PRODUCT_TYPE_TRANSFER[1].click()
            self.locators.product_offer_form.PRODUCT_TYPE_TRANSFER[1].wait_to_be_enabled()
            delay(1, "Не успевает обновиться информация в карточке")

    @allure.step("Добавление ПП внутри формы поиска")
    def search_and_select_product(
        self, product_offer_name: str, product_category_name: str, type_transfer_rent: bool = False
    ) -> None:
        self.search_products_in_form(
            product_offer_name=product_offer_name,
            product_category_name=product_category_name,
            type_transfer_rent=type_transfer_rent,
        )
        self.locators.product_offer_form.PRODUCT_CARD_SELECT_BTN[0].click()

    @allure.step("Добавление ПП по названию через форму поиска с любым типом передачи")
    def find_product_in_form(
        self, product_offer_name: str, product_category_name: str, type_transfer_rent: bool = False
    ) -> None:
        self.search_and_select_product(product_offer_name, product_category_name, type_transfer_rent)
        self.locators.product_offer_form.ADD_BTN.click()
        self.locators.product_offer_form.ADD_BTN.not_to_be_visible(timeout=10000)

    @allure.step("Добавление продуктового предложения")
    def add_product_offer_to_commercial_order(
        self, product: MainProduct, future_date: str | None = None, latitude: str = None, longitude: str = None
    ) -> MainProduct | InfoAboutBundle:
        self.locators.ADD_SALE_BTN.wait_to_be_visible(timeout=10000)
        self.locators.ADD_SALE_BTN.click()
        self.locators.product_offer_form.PRODUCT_CATEGORY_NAMES.wait_to_be_visible(timeout=30000)
        if latitude and longitude:
            self.fill_geocoordinates_on_add_product_form(latitude, longitude)
        with allure.step("Выбор категории продуктового предложения"):
            category_index = next(
                (
                    index
                    for index, category in enumerate(self.locators.product_offer_form.PRODUCT_CATEGORY_NAMES)
                    if self.category_map[product.category] in category.text
                ),
                None,
            )
            assert_that(lambda: category_index is not None, "Категория не найдена в списке")
            self.locators.product_offer_form.PRODUCT_CATEGORY_NAMES[category_index].click()
            self.locators.product_offer_form.SEARCH_BTN.click()
            self.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=30000)
        if future_date:
            self.set_execution_date_on_product_form(future_date)
            self.locators.LOAD_SPINS.wait_not_to_be_visible(timeout=30000)
        added_product = self.choose_product_offer_with_name(product.product_name)
        product.subscription_fee = added_product.subscription_fee
        product.one_time_payment = added_product.one_time_payment
        self.locators.product_offer_form.ADD_BTN.wait_to_be_enabled()
        self.locators.product_offer_form.ADD_BTN.click()
        self.locators.PRODUCTS_NAME.wait_to_be_visible(timeout=20000)
        self.locators.PRODUCTS_NAME.to_contain_text_in_any(product.product_name)
        return product

    @allure.step("Указать геокоординаты на форме Выбор продуктов")
    def fill_geocoordinates_on_add_product_form(self, latitude: str, longitude: str) -> None:
        self.locators.product_offer_form.ADDRESS_TEXT.wait_to_be_visible()
        self.locators.product_offer_form.ADDRESS_TEXT.click()
        self.locators.product_offer_form.ADD_ADDRESS_BUTTON.wait_to_be_visible()
        self.locators.product_offer_form.ADD_ADDRESS_BUTTON.click()
        self.locators.add_address_form.LATITUDE.wait_to_be_visible()
        self.locators.add_address_form.LATITUDE.fill(latitude)
        self.locators.add_address_form.LONGITUDE.fill(longitude)
        self.locators.add_address_form.SAVE_BTN.wait_to_be_visible()
        self.locators.add_address_form.SAVE_BTN.click()
        self.locators.add_address_form.SAVE_BTN.not_to_be_visible(timeout=10000)
        self.locators.add_address_form.INFO_MESSAGE.not_to_be_visible(timeout=10000)

    @allure.step("Выбор продуктового предложения {product_offer_name}")
    def choose_product_offer_with_name(self, product_offer_name: str) -> MainProduct | InfoAboutBundle:
        self.locators.product_offer_form.PRODUCT_CARD_NAME.wait_to_be_visible(timeout=20000)
        self.locators.product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([product_offer_name], timeout=10000)
        index = self.locators.product_offer_form.PRODUCT_CARD_NAME.text_list.index(product_offer_name)
        self.locators.product_offer_form.PRODUCT_CARD_SELECT_BTN.click(index)
        self.locators.product_offer_form.PRODUCT_CARD_SELECT_BTN[index].wait_to_have_text("Удалить")
        product = MainProduct()
        if product_offer_name == "Все для бизнеса":
            bundle = InfoAboutBundle(bundle_name=product_offer_name)
            products = (
                self.page.locator(self.locators.product_offer_form.PRODUCT_CARD.path)
                .nth(index)
                .locator(self.locators.product_offer_form.PRODUCT_CARD_PRODUCTS.path)
            )
            products_names = products.all_text_contents()
            assert_that(lambda: products_names != [], "Список названия продуктов в бандле не найден")
            for product_name in products_names:
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
    def auto_reserve_all_resources(
        self, category: str | list[str] = "mobile", equipment_patterns: list[str] | None = None
    ) -> None:
        scroll = 80
        self.locators.PRODUCT_RESOURCES_UNFILLED_BTN.wait_to_be_visible(timeout=15000)
        self.locators.LOAD_SPINS.not_to_be_visible()
        count = self.locators.PRODUCT_RESOURCES_UNFILLED_BTN.elements_len()
        for edit_btn_index in range(count):
            current_category = category[edit_btn_index] if isinstance(category, list) else category
            self.product_edit_form.TITLE.not_to_be_visible()
            self.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=15000)
            self.locators.PRODUCT_RESOURCES_UNFILLED_BTN.wait_elements_visible(edit_btn_index, timeout=20000)
            self.locators.PRODUCT_RESOURCES_UNFILLED_BTN[edit_btn_index].scroll_into_view_if_needed()
            self.locators.SCROLLABLE_PRODUCT_BLOCK.scroll_scrollable_platform(scroll)
            self.locators.PRODUCT_RESOURCES_UNFILLED_BTN[edit_btn_index].click(force=True)
            self.locators.LOAD_SPINS.wait_not_to_be_visible()
            self.product_edit_form.RESOURCES_TAB.wait_to_be_enabled()
            if self.page.locator(self.product_edit_form.SPECIFICATION_ERROR_ICON.path).is_visible():
                self.product_edit_form.SPECIFICATION_TAB.click()
                self.product_edit_form.TEST_CHARC.wait_to_be_visible()
                self.product_edit_form.TEST_CHARC.fill("test")
            self.product_edit_form.RESOURCES_TAB.hover()
            self.product_edit_form.RESOURCES_TAB.click()
            if self.page.locator(self.product_edit_form.MODAL.path).is_visible():
                self.product_edit_form.MODAL_SECOND_BTN.click()
            self.product_edit_form.RESOURCES.wait_to_be_visible(timeout=10000)
            self.locators.LOAD_SPINS.wait_not_to_be_visible()
            if current_category == "equipment_sale":
                if self.page.locator(self.product_edit_form.RESERVE_RESOURCES_SELECT.path).is_visible(timeout=15000):
                    self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible(timeout=15000)
                    self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("SIM-карта")
                    self.reserve_sim()
                    self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
                else:
                    self.product_edit_form.CHANGE_ICCID_BTN.wait_to_be_visible(timeout=15000)
                    self.product_edit_form.CHANGE_ICCID_BTN.click()
                    reserve_form = ReserveResourcesForm()
                    reserve_form.TITLE.to_contain_text("Бронирование SIM-карты", timeout_sec=10)
                    self.reserve_sim()
                equipment_pattern = (
                    equipment_patterns[edit_btn_index]
                    if equipment_patterns and edit_btn_index < len(equipment_patterns)
                    else "_L_"
                )
                self.reserve_equipment(equipment_pattern=equipment_pattern)
            else:
                if "satellite" in current_category:
                    self.auto_reserve_phone_number_resources(
                        switch=stand_context.stand_equipment.default_satellite_equipment.name
                    )
                    equipment_pattern = (
                        equipment_patterns[edit_btn_index]
                        if equipment_patterns and edit_btn_index < len(equipment_patterns)
                        else "_L_"
                    )
                    self.reserve_equipment(equipment_pattern=equipment_pattern)
                else:
                    self.auto_reserve_phone_number_resources()
            self.product_edit_form.INNER_ACCEPT_BTN.wait_to_be_enabled(timeout=10000)
            self.product_edit_form.INNER_ACCEPT_BTN.click()
            self.product_edit_form.LOAD_SPINS.wait_not_to_be_visible()

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
    def auto_reserve_phone_number_resources(
        self, number_class: str = "Обычный", switch: str = "Коммутатор_DEF"
    ) -> tuple[str | None, str | None]:
        reserve_form = ReserveResourcesForm()
        iccid, number = None, None

        if (
            hasattr(test_context.client, "inquiry")
            and hasattr(test_context.client.inquiry, "product")
            and test_context.client.inquiry.product.switch_name is not None
        ):
            switch = test_context.client.inquiry.product.switch_name

        if self.page.locator(self.product_edit_form.RESERVE_RESOURCES_SELECT.path).is_visible(timeout=15000):
            self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible(timeout=15000)
            self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("SIM-карта")
            iccid = self.reserve_sim(switch=switch)
            self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
            self.product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("Телефонный номер (мобильный)")
            number = self.reserve_number(number_class=number_class, switch=switch)
        else:
            self.product_edit_form.CHANGE_ICCID_BTN.wait_to_be_visible(timeout=15000)
            self.product_edit_form.CHANGE_ICCID_BTN.click()
            reserve_form.TITLE.to_contain_text("Бронирование SIM-карты")
            iccid = self.reserve_sim(switch=switch)
            self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible()
            self.product_edit_form.CHANGE_NUMBER_BTN.wait_to_be_visible(timeout=15000)
            self.product_edit_form.CHANGE_NUMBER_BTN.click()
            reserve_form.TITLE.to_contain_text("Бронирование номера")
            number = self.reserve_number(number_class=number_class, switch=switch)
        self.product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible(timeout=15000)
        if iccid:
            self.product_edit_form.ICCID.wait_to_have_text(iccid)
        if number:
            self.product_edit_form.PHONE_NUMBER.wait_to_have_text(number)
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
        reserve_form = ReserveResourcesForm()
        delay(1, "Ожидание для корректного получения значений полей")
        reserve_form.SEARCH_BUTTON.wait_to_be_visible(timeout=15000)
        if search_type:
            reserve_form.SEARCH_TYPE.select_by_value(search_type)
        if mask:
            delay(1, "Ожидание для корректного заполнения поля")
            reserve_form.MASK_INPUT.fill(mask)
        if left_range:
            reserve_form.RANGE_LEFT_INPUT.fill(left_range)
        if right_range:
            reserve_form.RANGE_RIGHT_INPUT.fill(right_range)
        if (
            hasattr(test_context.client, "inquiry")
            and hasattr(test_context.client.inquiry, "product")
            and test_context.client.inquiry.product.switch_name is not None
        ):
            reserve_form.SWITCH.select_by_value(test_context.client.inquiry.product.switch_name)
        elif switch:
            reserve_form.SWITCH.select_by_value(switch)
        reserve_form.SEARCH_BUTTON.click()
        reserve_form.SIM_ICC.wait_elements_visible(0)
        icc = reserve_form.SIM_ICC[0].text
        reserve_form.SIM_CHECKBOX.click(0)
        reserve_form.BOOK_BTN.click()
        reserve_form.TITLE.not_to_be_visible(timeout=15000)
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
        reserve_form = ReserveResourcesForm()
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
        reserve_form.NUMBER.wait_elements_visible(0, timeout=10000)
        number = reserve_form.NUMBER[0].text
        reserve_form.NUMBER_CHECKBOX.click(0)
        reserve_form.BOOK_BTN.click()
        reserve_form.RESOURCE_COUNT.not_to_be_visible(timeout=10000)
        return number

    @allure.step("Бронирование Оборудования")
    def reserve_equipment(
        self,
        equipment_pattern: str = "_L_",
    ) -> str | None:
        reserve_form = ReserveResourcesForm()
        product_edit_form = ProductEditForm()
        product_edit_form.CHANGE_EQUIPMENT_BTN.click()
        delay(1, "Ожидание для корректного получения значений полей")
        reserve_form.SEARCH_BUTTON.wait_to_be_visible()
        reserve_form.SEARCH_BUTTON.click()
        reserve_form.EQUIPMENT_NUMBER.wait_elements_visible(1)
        from pages.ui_elements import Element

        equipment_index: int | None = None
        for index in range(reserve_form.EQUIPMENT_NAME.elements_len()):
            equipment_item = reserve_form.EQUIPMENT_NAME[index]
            equipment: Element = cast(Element, equipment_item)
            if equipment_pattern in equipment.text:
                equipment_index = index
                break
        assert_that(lambda: equipment_index is not None, "Нет нужных ресурсов для бронирования на стенде")
        number = reserve_form.EQUIPMENT_NUMBER[equipment_index].text
        reserve_form.EQUIPMENT_CHECKBOX[equipment_index].click()
        reserve_form.BOOK_BTN.click()
        reserve_form.RESOURCE_COUNT.not_to_be_visible(timeout=10000)
        product_edit_form.RESERVE_RESOURCES_LOADER.not_to_be_visible(timeout=10000)
        return number

    @allure.step("Скачать документ")
    def download_document(self, document_name: str) -> tuple:
        self.locators.DOCUMENTS_ROWS.wait_to_be_visible(timeout=10000)
        document = self.locators.DOCUMENTS_ROWS.get_element_by_text(document_name)
        document.wait_to_be_visible()
        document.click()

        self.locators.DOWNLOAD_DOCUMENT.wait_to_be_enabled()

        with allure.step("Скачать документ и дождаться загрузки файла"):
            with self.page.expect_download() as download_info:
                self.locators.DOWNLOAD_DOCUMENT.click()
                download = download_info.value

        pdf_file = CheckFile(download.suggested_filename)
        file_path = pdf_file.process_downloaded_pdf(download, delete_after_check=False)
        return pdf_file, file_path

    @allure.step("Скачать документ и загрузить новый")
    def download_upload_file(self) -> None:
        pdf_file, file_path = self.download_document(f"test_{generate_english_string(5)}")

        self.locators.UPLOAD_DOCUMENT_BTN.click()

        with allure.step("Загрузить ранее скачанный файл"):
            self.locators.UPLOAD_FILE.upload_files([str(file_path)])

        with allure.step("Удалить скачанный файл после загрузки"):
            pdf_file.remove_file_from_download()

        self.locators.SELECT_TYPE_UPLOAD_DOCUMENT.select_by_value("Доп. соглашение")
        self.locators.DESCRIPTION_UPLOAD_DOCUMENT.fill("123")
        self.locators.SELECT_TYPE_UPLOAD_DOCUMENT.wait_to_have_text("Доп. соглашение")
        self.locators.DESCRIPTION_UPLOAD_DOCUMENT.wait_to_have_text("123")

        self.locators.UPLOAD_BTN.wait_to_be_enabled()
        self.locators.UPLOAD_BTN.click()

        self.locators.NEXT_STEP_BTN.wait_to_be_enabled()
        self.locators.NEXT_STEP_BTN.click()

    @allure.step("Перейти к закрытию заявки смены продукта (авто-договор)")
    def proceed_to_auto_contract_closure(self) -> None:
        """Шаги для сценария с авто-договором:
        - ждем окончания оформления;
        - жмем 'Далее' и переходим к автоматической обработке.
        """
        self.locators.ADD_SALE_BTN.wait_to_be_enabled(timeout=80000)
        self.locators.NEXT_STEP_BTN.click()

    @allure.step("Перейти на шаг с договором по заявке смены продукта (ручной договор)")
    def go_to_agreement_step(self) -> None:
        """Шаг для сценария с ручным договором:
        - ждем окончания оформления;
        - жмем 'Далее';
        - ждем, пока в таблице появится 1 договор.
        """
        self.locators.NEXT_STEP_BTN.wait_to_be_enabled(timeout=40000)
        self.locators.NEXT_STEP_BTN.click()
        self.locators.AGREEMENT.wait_to_have_count(1, timeout=45000)

    @allure.step("Скачать PDF договора и проверить его корректность")
    def download_and_check_agreement_pdf(self) -> None:
        """Кликает по договору, скачивает PDF и проверяет его через CheckFile.
        Работает как на шаге ручного договора, так и после закрытия заявки
        на вкладке с доп. соглашением.
        """
        self.locators.AGREEMENT[0].click()
        self.locators.DOWNLOAD_DOCUMENT.wait_to_be_enabled(timeout=20000)

        with allure.step("Скачать документ и дождаться загрузки файла"):
            with self.page.expect_download() as download_info:
                self.locators.DOWNLOAD_DOCUMENT.click()
            download = download_info.value

        pdf_file = CheckFile(download.suggested_filename)
        pdf_file.process_downloaded_pdf(download)

    @allure.step("Утвердить договор по заявке смены продукта")
    def approve_agreement(self) -> None:
        self.locators.APPROVE_BTN.click()
        self.locators.NEXT_STEP_BTN.wait_to_be_enabled()
        self.locators.NEXT_STEP_BTN.click()

    @allure.step("Дождаться закрытия заявки и проверить наличие доп. соглашения")
    def wait_closed_and_check_agreement(self) -> None:
        """
        Заявка должна перейти в статус «Закрыто»,
        а в карточке клиента должно быть создано одно доп. соглашение.
        """
        self.locators.INQUIRY_STATUS.wait_to_have_text("Закрыто", timeout=180000)
        self.locators.PRODUCT_PROFILE_BTN.wait_to_be_visible(timeout=40000)
        self.locators.TABS[6].click()
        self.locators.AGREEMENT.wait_to_have_count(1, timeout=10000)
        self.locators.AGREEMENT_TYPE.wait_to_have_text("Доп. соглашение ")

    @allure.step("Проверка отображения индивидуализированной цены на форме Редактирование продукта")
    def check_individualized_price_in_edit_product_form(
        self,
        expected_base_price: float,
        expected_final_price: float,
        fee_type: Literal["subscription", "one_time"] = "subscription",
    ) -> None:
        """
        Проверка индивидуализированной цены на форме Редактирование продукта
        :param expected_base_price: Ожидаемая Базовая цена
        :param expected_final_price: Ожидаемая Итоговая цена
        :param fee_type: Тип наичсления - ["subscription", "one_time"]
        """

        if fee_type == "subscription":
            base_price_locator = self.product_edit_form.SUBSCRIPTION_FEE_BASE_PRICE
            final_price_locator = self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE
        else:
            base_price_locator = self.product_edit_form.ONE_TIME_PAYMENT_BASE_PRICE
            final_price_locator = self.product_edit_form.ONE_TIME_PAYMENT_FINAL_PRICE

        base_price_locator.wait_to_be_visible(timeout=10000)
        check_price(base_price_locator, expected_base_price, check_format=False)
        check_price(final_price_locator, expected_final_price, check_format=False)

    @allure.step("Проверка отображения индивидуализированной цены в заявке")
    def check_individualized_price_in_inquiry(
        self,
        fee_type: Literal["subscription", "one_time"],
        expected_base_price: float,
        expected_final_price: float,
        product_index: int = 0,
        individualized_price_index: int = 0,
    ) -> None:
        """
        Проверка индивидуализированной цены в заявке
        :param product_index: Порядковый номер продукта
        :param fee_type: тип наичсления - ["subscription", "one_time"]
        :param expected_base_price: Ожидаемая Базовая цена
        :param expected_final_price: Ожидаемая Итоговая цена
        """

        if fee_type == "subscription":
            base_price_locator = self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BASE_PRICE[product_index]
            final_price_locator = self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_FINAL_PRICE[individualized_price_index]
        else:
            base_price_locator = self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_BASE_PRICE[product_index]
            final_price_locator = self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_FINAL_PRICE[individualized_price_index]

        base_price_locator.wait_to_be_visible()
        check_price(base_price_locator, expected_base_price, check_format=False)
        check_price(final_price_locator, expected_final_price, check_format=False)

    @allure.step("Проверка отображения индивидуализированной цены на форме массового назначения скидок")
    def check_individualized_price_in_mass_discounts_form(
        self,
        product_index: int,
        fee_type: Literal["subscription", "one_time"],
        expected_base_price: float,
        expected_final_price: float,
    ) -> None:
        """
        :param product_index: Порядковый номер продукта
        :param fee_type: тип наичсления - ["subscription", "one_time"]
        :param expected_base_price: Ожидаемая Базовая цена
        :param expected_final_price: Ожидаемая Итоговая цена
        """

        if fee_type == "subscription":
            base_price_locator = self.mass_discount_form.SUBSCRIPTION_FEE_BASE_PRICE[product_index]
            final_price_locator = self.mass_discount_form.SUBSCRIPTION_FEE_FINAL_PRICE[product_index]
        else:
            base_price_locator = self.mass_discount_form.ONE_TIME_BASE_PRICE[product_index]
            final_price_locator = self.mass_discount_form.ONE_TIME_FINAL_PRICE[product_index]

        base_price_locator.wait_to_be_visible(timeout=10000)
        check_price(base_price_locator, expected_base_price, check_format=False)
        check_price(final_price_locator, expected_final_price, check_format=False)

    @allure.step("Изменение даты активации")
    def activation_date_fill(self, activation_date: str = None, inquiry_finish_need: bool = True) -> None:
        self.locators.ACTIVATION_DATE_CHANGE_BUTTON[1].wait_to_be_enabled(timeout=20000)
        self.locators.ACTIVATION_DATE_CHANGE_BUTTON[1].click()
        self.locators.ACTIVATION_DATE_CHANGE.fill(activation_date)
        self.press_keyboard_button("Enter")
        if inquiry_finish_need:
            self.locators.AGREEMENT_BTN[2].wait_to_be_visible(timeout=20000)
            self.locators.NEXT_STEP_BTN.to_be_enabled()
            self.locators.ACTIVATE_DATE.to_contain_text(activation_date, timeout_sec=20)
            self.refresh_page(wait="commit")
            self.locators.NEXT_STEP_BTN.wait_to_be_visible(timeout=20000)
            self.locators.NEXT_STEP_BTN.wait_to_be_enabled(timeout=20000)
            self.locators.NEXT_STEP_BTN.click()

    @allure.step("Назначение скидок на форме Редактирование продукта")
    def individualize_price(
        self,
        percent: int | None = None,
        final_price: float | None = None,
        product_offering_index: int = 0,
        fee_type: str = "subscription",
        should_check_price: bool = True,
        should_save_discount: bool = True,
        comment: str = None,
    ) -> None:
        """
        Метод для изменения цены ПП в КЗ
        :param percent: процент скидки, если None, то его не вводит
        :param final_price: цена со скидкой, если None, то его не вводит
        :param product_offering_index: индекс ПП в КЗ
        """

        if fee_type == "subscription":
            price_button = self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON
            discount_input = self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT
            base_price = self.product_edit_form.SUBSCRIPTION_FEE_BASE_PRICE
            final_price_input = self.product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE
        else:
            price_button = self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_BUTTON
            discount_input = self.product_edit_form.ONE_TIME_PAYMENT_DISCOUNT_INPUT
            base_price = self.product_edit_form.ONE_TIME_PAYMENT_BASE_PRICE
            final_price_input = self.product_edit_form.ONE_TIME_PAYMENT_FINAL_PRICE

        assert_that(
            lambda: price_button.elements_len() > product_offering_index,
            "Отсутствует нужное продуктовое предложение",
            timeout=15000,
        )
        with allure.step("Ожидание доступности кнопки и нажатие"):
            price_button[product_offering_index].wait_to_be_visible()
            price_button[product_offering_index].click(force=True)
        with allure.step("Ожидание загрузки таба"):
            self.product_edit_form.PRICE_CARD.wait_to_be_visible(timeout=10000)
            self.product_edit_form.PRICE_CARD.click()
            self.product_edit_form.PRICE_CARD_VALUES.wait_to_be_visible(timeout=10000)
            init_value, currency = get_price_and_currency(base_price[0].text)
            if currency is not None or init_value < 0:
                raise AssertionError("Проблема парсинга цены продуктового предложения")

        if percent is not None:
            with allure.step("Заполнение процента скидки и проверка изменения общей стоимости"):
                discount_input[product_offering_index].wait_to_be_visible(timeout=5000)
                discount_input[product_offering_index].fill(str(percent))
                if should_check_price:
                    check_price(
                        element_with_price=final_price_input[product_offering_index],
                        expected_price=calc_price_after_discount(init_value, abs(percent)),
                        check_format=False,
                    )
        if final_price is not None:
            with allure.step("Заполнение общей стоимости и проверка процента, если применимо"):
                final_price_input[product_offering_index].wait_to_be_visible(timeout=5000)
                final_price_input[product_offering_index].type(str(final_price))
                if final_price < init_value:
                    discount_input[product_offering_index].to_contain_text(
                        text=str(100 - (final_price / init_value)), separated=True
                    )
                else:
                    self.product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT.wait_to_have_text("")
        if comment is not None:
            self.product_edit_form.PRICE_COMMENT_TEXTAREA.wait_to_be_visible()
            self.product_edit_form.PRICE_COMMENT_TEXTAREA.fill(comment)
        if should_save_discount:
            self.save_individualized_prices()

    @allure.step("Сохранение цен после индивидуализации")
    def save_individualized_prices(self) -> None:
        self.product_edit_form.INNER_ACCEPT_BTN.wait_to_be_visible(timeout=5000)
        self.product_edit_form.INNER_ACCEPT_BTN.click()

        self.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
        self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

    @allure.step("Проверка адресов в форме заявки")
    def check_product_addresses(
        self,
        product_index: int = 0,
        address: str = BasicSystemAddress.address,
        region: str = BasicSystemAddress.region,
        has_additional_option: bool = False,
    ) -> None:
        """Проверяет отображение адресов и регионов для продукта в форме заявки.

        :param product_index: Индекс продукта в списке
        :param address: Ожидаемый адрес продукта
        :param region: Ожидаемый регион продукта
        :param has_additional_option: Флаг наличия дополнительной опции с адресом
        """
        self.locators.ADDED_PRODUCT_REGIONS[product_index].to_contain_text(region, timeout_sec=2)
        self.locators.ADDED_PRODUCT_ADDRESSES[product_index].to_contain_text(address)
        if has_additional_option:
            self.locators.ADDED_OPTION_ADDRESSES[product_index].to_contain_text(address)

    @allure.step("Добавление доп. опции продукту")
    def add_additional_option_with_address_check(
        self,
        product_name: str = None,
        address: str = BasicSystemAddress.address,
        region: str = BasicSystemAddress.region,
    ) -> None:
        """Добавляет дополнительную опцию к указанному продукту.

        :param product_name: Название продукта, которому нужно добавить опцию
        """
        add_options_form = AddOptionsForm()
        product_index_x = self.locators.ADDED_PRODUCT_NAMES.text_list.index(product_name)
        self.locators.ADDED_PRODUCT_ADD_OPTION_BTN[product_index_x].click(force=True)
        add_options_form.CHOSE_OPTION_BTN.wait_elements_visible(element_index=0)
        add_options_form.CHOSE_OPTION_BTN[0].click()
        self.locators.product_offer_form.REGION_TEXT.wait_to_have_text(region)
        self.locators.product_offer_form.ADDRESS_TEXT.to_contain_text(address)
        self.locators.product_offer_form.ADD_BTN.click()

    @allure.step("Проверка UI после добавления продукта")
    def check_inquiry_state_after_product_addition(
        self, product_count: int, region: str = "Ленинградская область"
    ) -> None:
        self.locators.ADDED_PRODUCT.wait_to_have_count(product_count, timeout=10000)
        self.locators.STEP_TITLE.wait_to_have_text("Наполнение и уточнение коммерческого заказа")
        self.locators.INQUIRY_STATUS.wait_to_have_text("Обрабатывается")
        self.locators.INQUIRY_STEP.wait_to_have_text("Управление составом заказа")
        self.locators.TABS[0].check_attribute_by_value("aria-selected", "true")
        self.locators.ADDED_PRODUCT_REGIONS[0].to_contain_text(region)
        self.locators.CHECK_CONFIGURATION_BTN.wait_to_be_enabled()

        self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT[0].wait_to_be_visible()
        self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE[0].wait_to_be_visible()

    @allure.step("Поиск номера телефона по маске {1}")
    def search_number_by_mask(self, mask: str) -> None:
        reserve_form = ReserveResourcesForm()

        reserve_form.MASK_INPUT.fill(mask)
        reserve_form.RANGE_LEFT_INPUT.not_to_be_enabled()
        reserve_form.RANGE_RIGHT_INPUT.not_to_be_enabled()
        reserve_form.SEARCH_BUTTON.click()

    @allure.step("Открыть информацию о продукте на вкладке Элементы заказа")
    def open_product_info_from_order_elements_tab(self) -> None:
        self.locators.ADDED_PRODUCT_VISIBLE_BTN[0].wait_to_be_visible(timeout=15000)
        self.locators.ADDED_PRODUCT_VISIBLE_BTN[0].hover()
        self.locators.ADDED_PRODUCT_VISIBLE_BTN[0].click(force=True)

    @allure.step("Проверить что поля бронирования номера не отображаются")
    def check_number_reserve_fields_not_displayed(self) -> None:
        reserve_form = ReserveResourcesForm()

        reserve_form.NUMBER.wait_to_have_count(1)
        reserve_form.MASK_INPUT.not_to_be_visible()
        reserve_form.RANGE_LEFT_INPUT.not_to_be_visible()
        reserve_form.RANGE_RIGHT_INPUT.not_to_be_visible()
        reserve_form.RESOURCE_COUNT.not_to_be_visible()
        reserve_form.STANDARD_INPUT.not_to_be_visible()
        reserve_form.SWITCH.not_to_be_visible()
        reserve_form.NUMBERING_TYPE.not_to_be_visible()
        reserve_form.NUMBER_CLASS.not_to_be_visible()
        reserve_form.FREE_FOR.not_to_be_visible()
        reserve_form.REGION.not_to_be_visible()

    @allure.step("Открыть форму бронирования мобильного номера")
    def open_mobile_phone_reserve_form(self, product: str) -> None:
        reserve_form = ReserveResourcesForm()
        product_edit_form = ProductEditForm()

        product_edit_form.RESERVE_RESOURCES_SELECT.select_by_value("Телефонный номер (мобильный)")
        reserve_form.TITLE.wait_to_have_text("Бронирование номера")
        reserve_form.RESOURCE_INFO[0].to_contain_text(product)
        reserve_form.RESOURCE_INFO[1].to_contain_text("Телефонный номер (мобильный)")
        reserve_form.INFO_MESSAGE.wait_to_have_text("Осталось выбрать 1 из 1")

    @allure.step("Проверить вкладку Характеристики")
    def check_characteristics_tab(self, address: str = None) -> None:
        product_edit_form = ProductEditForm()

        if address:
            product_edit_form.CHARACTERISTIC_VALUES[0].wait_to_have_text(address)
            product_edit_form.CHARACTERISTIC_VALUES[1].wait_to_have_text("С даты подключения")
            product_edit_form.CHARACTERISTIC_VALUES[2].wait_to_have_text("Простой")
        else:
            product_edit_form.CHARACTERISTIC_VALUES[0].wait_to_have_text("С даты подключения")
            product_edit_form.CHARACTERISTIC_VALUES[1].wait_to_have_text("Простой")

    @allure.step("Проверить отображение цен на вкладке Цены")
    def check_prices_tab(
        self,
        one_time_price: str,
        one_time_discount: str,
        one_time_final_price: str,
        periodic_price: str,
        periodic_discount: str,
        periodic_final_price: str,
        subscription_period: str,
        subscription_period_count: str,
        product_index: int = 0,
    ) -> None:
        product_edit_form = ProductEditForm()

        self.open_price_tab()

        product_edit_form.ONE_TIME_PAYMENT_BASE_PRICE[product_index].to_have_value(one_time_price)
        product_edit_form.ONE_TIME_PAYMENT_DISCOUNT_INPUT[product_index].to_have_value(one_time_discount)
        product_edit_form.ONE_TIME_PAYMENT_FINAL_PRICE[product_index].to_have_value(one_time_final_price)
        product_edit_form.SUBSCRIPTION_FEE_BASE_PRICE[product_index].to_have_value(periodic_price)
        product_edit_form.SUBSCRIPTION_FEE_DISCOUNT_INPUT[product_index].to_have_value(periodic_discount)
        product_edit_form.SUBSCRIPTION_FEE_FINAL_PRICE[product_index].to_have_value(periodic_final_price)
        product_edit_form.SUBSCRIPTION_PERIOD[product_index].to_contain_value(subscription_period_count)
        product_edit_form.SUBSCRIPTION_PERIOD[product_index].to_contain_value(subscription_period)

    @allure.step("Проверить отображение налога в детальной информации о продукте '{product_offer_name}'")
    def check_product_details_taxes(self, product_offer_name: str, product_index: int = 0) -> None:
        """Открыть детальную информацию о найденном ПП, проверить налоги на вкладке 'Цены' и закрыть её.

        :param product_offer_name: название продуктового предложения
        :param product_index: порядковый номер карточки продукта в результатах поиска
        """
        product_offer_form = self.locators.product_offer_form
        product_info_form = product_offer_form.product_info_form

        product_offer_form.PRODUCT_CARD_NAME.wait_for_text_in_all([product_offer_name], timeout=10000)
        product_offer_form.PRODUCT_CARD_DETAILS.wait_elements_visible(product_index, timeout=10000)
        product_offer_form.PRODUCT_CARD_DETAILS[product_index].click()
        product_info_form.PRODUCT_NAME.wait_to_have_text(product_offer_name, timeout=10000)

        product_info_form.open_price_tab()
        product_info_form.check_taxes_on_price_tab()

        product_info_form.CROSS_BTN.click()
        product_info_form.PRODUCT_NAME.not_to_be_visible(timeout=10000)

    @allure.step("Добавить найденное продуктовое предложение в коммерческий заказ")
    def add_found_product_to_commercial_order(self, product: MainProduct, product_index: int = 0) -> None:
        """Выбрать уже найденный в форме ПП и добавить его в коммерческий заказ.

        В отличие от add_product_offer_to_commercial_order не открывает форму выбора ПП заново,
        что позволяет предварительно посмотреть детальную информацию о продукте.

        :param product: продукт, который добавляется в заказ
        :param product_index: порядковый номер карточки продукта в результатах поиска
        """
        product_offer_form = self.locators.product_offer_form

        product_offer_form.PRODUCT_CARD_SELECT_BTN.wait_elements_visible(product_index, timeout=10000)
        product_offer_form.PRODUCT_CARD_SELECT_BTN[product_index].click()
        product_offer_form.ADD_BTN.wait_to_be_enabled(timeout=10000)
        product_offer_form.ADD_BTN.click()
        self.locators.PRODUCTS_NAME.to_contain_text_in_any(product.product_name)

    @allure.step("Открыть вкладку 'Цены' формы редактирования продукта по ссылке с ценой")
    def open_product_price_tab_by_price_link(
        self, fee_type: Literal["subscription", "one_time"] = "one_time", product_index: int = 0
    ) -> None:
        """Открыть форму редактирования продукта кликом по ссылке с ценой и раскрыть блок с ценами.

        В отличие от open_edit_product_form не зависит от наличия у продукта ошибок конфигурации.

        :param fee_type: тип начисления - ["subscription", "one_time"]
        :param product_index: порядковый номер продукта в коммерческом заказе
        """
        if fee_type == "subscription":
            price_button = self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON
        else:
            price_button = self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_BUTTON

        price_button.wait_elements_visible(product_index, timeout=15000)
        delay(1)
        price_button[product_index].click(force=True)
        self.product_edit_form.PRICE_CARD.wait_to_be_visible(timeout=10000)
        self.product_edit_form.PRICE_CARD.click()
        self.product_edit_form.PRICE_CARD_VALUES.wait_to_be_visible(timeout=10000)

    @allure.step("Проверить отображение налога на вкладке 'Цены' формы редактирования продукта")
    def check_taxes_on_price_tab(
        self, fee_type: Literal["subscription", "one_time"] = "one_time", price_index: int = 0
    ) -> None:
        """Проверить, что на вкладке 'Цены' рассчитаны 'Цена без налога', 'Сумма налога' и 'Цена с налогом'.

        :param fee_type: тип начисления - ["subscription", "one_time"]
        :param price_index: порядковый номер цены выбранного типа начисления
        """
        product_edit_form = ProductEditForm()

        if fee_type == "subscription":
            price_without_tax = product_edit_form.SUBSCRIPTION_FEE_PRICE_WITHOUT_TAX
            tax = product_edit_form.SUBSCRIPTION_FEE_TAX
            price_with_tax = product_edit_form.SUBSCRIPTION_FEE_PRICE_WITH_TAX
        else:
            price_without_tax = product_edit_form.ONE_TIME_PAYMENT_PRICE_WITHOUT_TAX
            tax = product_edit_form.ONE_TIME_PAYMENT_TAX
            price_with_tax = product_edit_form.ONE_TIME_PAYMENT_PRICE_WITH_TAX

        price_without_tax.wait_elements_visible(price_index, timeout=10000)
        tax.wait_elements_visible(price_index, timeout=10000)
        price_with_tax.wait_elements_visible(price_index, timeout=10000)
        check_price_with_tax(price_without_tax[price_index], tax[price_index], price_with_tax[price_index])

    @allure.step("Проверить отображение налога на форме 'Назначение скидок'")
    def check_taxes_in_mass_discount_form(
        self, fee_type: Literal["subscription", "one_time"] = "one_time", product_index: int = 0
    ) -> None:
        """Проверить, что для платы отображаются 'Цена без налога', 'Налог' и 'Цена с налогом'.

        :param fee_type: тип начисления - ["subscription", "one_time"]
        :param product_index: порядковый номер продукта в списке формы
        """
        if fee_type == "subscription":
            price_without_tax = self.mass_discount_form.SUBSCRIPTION_FEE_BASE_PRICE
            tax = self.mass_discount_form.SUBSCRIPTION_FEE_TAX
            price_with_tax = self.mass_discount_form.SUBSCRIPTION_FEE_FINAL_PRICE
        else:
            price_without_tax = self.mass_discount_form.ONE_TIME_BASE_PRICE
            tax = self.mass_discount_form.ONE_TIME_TAX
            price_with_tax = self.mass_discount_form.ONE_TIME_FINAL_PRICE

        price_without_tax.wait_elements_visible(product_index, timeout=10000)
        tax.wait_elements_visible(product_index, timeout=10000)
        price_with_tax.wait_elements_visible(product_index, timeout=10000)
        check_price_with_tax(price_without_tax[product_index], tax[product_index], price_with_tax[product_index])

    @allure.step("Проверить всплывающую подсказку с налогом у итоговой платы")
    def check_total_payment_tax_tooltip(self, fee_type: Literal["subscription", "one_time"] = "one_time") -> str:
        """Навести курсор на 'i' возле итоговой платы и вернуть текст всплывающей подсказки.

        :param fee_type: тип начисления - ["subscription", "one_time"]
        :return: текст всплывающей подсказки
        """
        if fee_type == "subscription":
            info_icon = self.locators.TOTAL_SUBSCRIPTION_FEE_INFO_ICON
        else:
            info_icon = self.locators.TOTAL_ONE_TIME_PAYMENT_INFO_ICON

        info_icon.wait_to_be_visible(timeout=10000)
        info_icon.hover()
        self.locators.VISIBLE_TOOLTIP.wait_to_be_visible(timeout=10000)
        tooltip_text = self.locators.VISIBLE_TOOLTIP.text or ""
        assert_that(
            lambda: any(char.isdigit() for char in tooltip_text),
            f"Во всплывающей подсказке у итоговой платы нет сумм: '{tooltip_text}'",
        )
        return tooltip_text

    @allure.step("Проверить вкладку Сервисы")
    def check_services_tab(self, services: set) -> None:
        product_edit_form = ProductEditForm()

        product_edit_form.SERVICES_TAB.click()
        check_that(
            lambda: set(product_edit_form.SERVICES.text_list) == services,
            exception=IncorrectServicesInListException,
            message="Список сервисов на вкладке 'Сервисы' не соответствует ожидаемому",
        )

    @allure.step("Проверить что выбран коммутатор с наименованием {switch_name} и дропдаун не активен")
    def check_switch_selected_and_disabled(self, switch_name: str) -> None:
        reserve_form = ReserveResourcesForm()
        button_disabled_color_code = "rgb(228, 233, 238)"

        reserve_form.SWITCH.wait_to_have_text(switch_name)
        check_that(
            lambda: reserve_form.SWITCH.get_css_property("background-color") == button_disabled_color_code,
            exception=SwitchDropdownIsNotDisabledException,
            message="Дропдаун 'Коммутатор' не задизейблен",
        )

    @allure.step("Открыть форму массового назначения скидок")
    def open_mass_discount_assignment_form(self) -> None:
        self.locators.ASSIGN_DISCOUNTS_BTN.wait_to_be_visible(timeout=10000)
        self.locators.ASSIGN_DISCOUNTS_BTN.click()

        self.mass_discount_form.WARNING_MESSAGE.wait_to_be_visible(timeout=5000)
        self.mass_discount_form.WARNING_MESSAGE.to_contain_text(
            "Введенные значения изменят цены и комментарии по всем выбранным Продуктовым предложениям"
        )

    @allure.step("Заполнить скидки на форме массового назначения скидок")
    def fill_discounts_on_mass_discount_assignment_form(self, discount_percent: list) -> None:
        self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS.wait_to_have_count_or_greater(len(discount_percent))
        for i in range(len(discount_percent)):
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS[i].wait_to_be_visible()
            self.mass_discount_form.SUBSCRIPTION_FEE_DISCOUNT_INPUTS[i].fill(str(discount_percent[i]))

    @allure.step("Сохранить значения на форме массового назначения скидок")
    def save_discounts_on_mass_discount_assignment_form(self) -> None:
        self.mass_discount_form.ACCEPT_BTN.wait_to_be_visible(timeout=5000)
        self.mass_discount_form.ACCEPT_BTN.click()
        self.mass_discount_form.TITLE.not_to_be_visible(timeout=10000)

    @allure.step("Проверить наличие у продукта изменяемой абонентской платы")
    def check_product_has_editable_subscription_fee(self, product: MainProduct) -> None:
        self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON.wait_to_have_count(1, timeout=10000)
        self.locators.ADDED_PRODUCT_NAMES[0].to_contain_text(product.product_name)

        self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[0].wait_to_be_visible(timeout=10000)

    @allure.step("Открыть форму редактирования продукта")
    def open_edit_product_form(self, product_index: int = 0) -> None:
        self.locators.PRODUCT_RESOURCES_UNFILLED_BTN[product_index].wait_to_be_visible(timeout=10000)
        self.locators.PRODUCT_RESOURCES_UNFILLED_BTN[product_index].click(force=True)
        self.product_edit_form.TITLE.wait_to_be_visible(timeout=10000)

    @allure.step("Открыть вкладку Цены")
    def open_price_tab(self) -> None:
        self.product_edit_form.PRICE_TAB.wait_to_be_visible(timeout=10000)
        self.product_edit_form.PRICE_TAB.click()
        self.product_edit_form.GENERIC_FEE_BASE_PRICE.wait_to_be_visible()
        self.product_edit_form.PRICES_DROPDOWN_BTN.wait_to_be_visible(timeout=10000)
        for dropdown_index in range(self.product_edit_form.PRICES_DROPDOWN_BTN.elements_len()):
            self.product_edit_form.PRICES_DROPDOWN_BTN[dropdown_index].click()

    @allure.step("Закрыть форму редактирования продукта")
    def close_edit_product_form(self) -> None:
        self.product_edit_form.CANCEL_BUTTON.wait_to_be_visible(timeout=5000)
        self.product_edit_form.CANCEL_BUTTON.click()
        self.product_edit_form.TITLE.not_to_be_visible(timeout=10000)

    @allure.step("Нажать на кнопку обновления заявки")
    def refresh_inquiry(self) -> None:
        self.locators.REFRESH_BTN_INQUIRY.wait_to_be_visible(timeout=10000)
        self.locators.REFRESH_BTN_INQUIRY.click()

        self.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)

    @allure.step("Ожидание статуса заявки: {inquiry_status}")
    def wait_inquiry_status(self, inquiry_status: str, count_retry: int = 10, wait_time: float = 3) -> None:
        for i in range(count_retry):
            self.locators.INQUIRY_STATUS.wait_to_be_visible()
            if self.locators.INQUIRY_STATUS.text == inquiry_status:
                break
            delay(wait_time, "Ожидание изменения статуса заявки")
            self.refresh_inquiry()

    @allure.step("Нажать кнопку Сбросить скидки")
    def reset_discount(self) -> None:
        self.product_edit_form.RESET_DISCOUNT_BTN.wait_to_be_visible(timeout=10000)
        self.product_edit_form.RESET_DISCOUNT_BTN.click()

        self.product_edit_form.MODAL_SECOND_BTN.wait_to_be_visible(timeout=10000)
        self.product_edit_form.MODAL_SECOND_BTN.click()
        self.product_edit_form.MODAL_SECOND_BTN.not_to_be_visible(timeout=10000)

        self.locators.LOAD_SPIN_THIRD.not_to_be_visible(timeout=30000)
        self.locators.LOAD_SPINS.not_to_be_visible(timeout=30000)
        self.locators.ADDED_PRODUCT.wait_to_be_visible(timeout=30000)

    @allure.step("Создание заявки на перенос и перенос ПП")
    def create_inquiry_product_move_to_another_account(self, need_agreement_select: bool = True) -> None:
        self.client_profile_elements.CLIENT_FIO.wait_to_be_visible()
        self.client_profile_elements.CREATE_REQUEST.click()
        self.request_create.CREATE_FORM.wait_to_be_visible()
        self.request_create.TITLE.to_contain_text("Создание заявки")
        self.request_create.TOPIC.click()
        self.choose_request_topic.choose_topic(
            [
                "(5) 05 Действия",
                "(RENEWAL_AGREEMENT) Переоформление договора",
                "(TRANSFER_PRODUCTS) Перенос продуктов на другие ЛС",
            ]
        )
        if need_agreement_select:
            self.choose_request_topic.AGREEMENT_SELECT.select_by_index(0)
        self.choose_request_topic.SAVE_BTN.click()

    @allure.step("Перенос ПП")
    def product_move_distribution(
        self,
        account_number: str,
        product_name: str | list[str],
        product_exist: bool = True,
        option: bool = False,
        is_different_agreement: bool = False,
        need_account_select: bool = True,
    ) -> None:
        """В созданной заявке делает сетап для переноса продукта с одного ЛС на другой.
        :param account_number: Номер ЛС на котором находится продукт для переноса
        :param product_name: Название продукта, который необходимо перенести
        :param product_exist: Флаг на наличие продукта на договоре
        :param option: Флаг на наличие дополнительного продукта
        :param is_different_agreement: Флаг на выбор переноса в рамках одного договора или перенос на другой
        :param need_account_select: Флаг на назначение ЛС в рамках заявки на перенос продуктов на другие ЛС
        """
        if len(test_context.client_list) > 1:
            self.move_inquiry_locators.TARGET_AGREEMENT.click()
            self.move_inquiry_locators.CLIENT_AGREEMENT[1].click()
            client_index = 1
            if is_different_agreement:
                client_index = 0
            self.move_inquiry_locators.AGREEMENT_NUMBER.type(test_context.client_list[client_index].agreements[0].number)
            self.move_inquiry_locators.FIND_AGREEMENT[0].click()
            self.move_inquiry_locators.SEARCH_RESULT[0].click()
            self.choose_request_topic.INNER_ACCEPT_BTN.wait_to_be_visible(timeout=30000)
            self.choose_request_topic.INNER_ACCEPT_BTN.click()
            delay(1, "Время на отправку запроса")
        else:
            self.move_inquiry_locators.CURRENT_AGREEMENT.wait_to_be_visible(timeout=15000)
            self.move_inquiry_locators.CURRENT_AGREEMENT.click()
        if product_exist:
            self.locators.REFRESH_BTN_INQUIRY.click()
            if option:
                self.client_product_profile_elements.OPTIONS_EXPAND_ICON.click()
                self.move_inquiry_locators.CUSTOMER_OPTION_SELECT[0].wait_to_be_visible(timeout=20000)
                self.move_inquiry_locators.CUSTOMER_OPTION_SELECT[0].hover()
                self.move_inquiry_locators.CUSTOMER_OPTION_SELECT[0].click(force=True)
            else:
                self.move_inquiry_locators.MAIN_PRODUCT_NAME_FOR_MOVE[0].wait_to_be_visible(timeout=20000)
                for index in range(self.move_inquiry_locators.MAIN_PRODUCT_NAME_FOR_MOVE.elements_len()):
                    account_number_on_page = self.move_inquiry_locators.SOURCE_ACCOUNT_NUMBER_FOR_MOVE[index].text
                    account_number_on_page = account_number_on_page.strip()
                    if (
                        account_number_on_page == account_number
                        and self.move_inquiry_locators.MAIN_PRODUCT_NAME_FOR_MOVE[index].text in product_name
                    ):
                        self.move_inquiry_locators.MOVE_ALL_PRODUCTS_ON_SUBSCRIBER[index].click()
            if need_account_select:
                self.move_inquiry_locators.ACCOUNT_ACTIONS_BUTTONS[0].click()
                self.move_inquiry_locators.TARGET_ACCOUNT_ROW[0].wait_to_be_visible()
                self.move_inquiry_locators.TARGET_ACCOUNT_ROW[0].wait_to_have_text(re.compile(r"\d{1,}"))
                target_account_number = self.move_inquiry_locators.TARGET_ACCOUNT_ROW[0].text
                self.move_inquiry_locators.TARGET_ACCOUNT_ROW[0].click()
                self.choose_request_topic.INNER_ACCEPT_BTN.click()
                if option:
                    self.client_product_profile_elements.OPTIONS_EXPAND_ICON.click()
                self.move_inquiry_locators.TARGET_ACCOUNT_NUMBER_FOR_MOVE.to_contain_text_in_any(target_account_number)
                self.locators.NEXT_STEP_BTN.click()

    @allure.step(
        "Проверить синюю цену продукта. Индекс: {price_index}, тип: {fee_type}, ожидаемое значение: {expected_price}"
    )
    def check_product_individualized_price(
        self, price_index: int, fee_type: Literal["subscription", "one_time"], expected_price: float
    ) -> None:
        if fee_type == "subscription":
            check_price(
                self.locators.ADDED_PRODUCT_SUBSCRIPTION_FEE_BUTTON[price_index], expected_price, check_format=False
            )
        else:
            check_price(
                self.locators.ADDED_PRODUCT_ONE_TIME_PAYMENT_BUTTON[price_index], expected_price, check_format=False
            )

    @allure.step("Открыть вкладку с названием: {tab_name}")
    def open_tab(self, tab_name: str) -> None:
        self.locators.TABS.wait_to_be_visible(timeout=10000)
        tab = self.locators.TABS.get_element_by_text(tab_name)
        tab.wait_to_be_visible()
        tab.click()

    @allure.step("Проверить что объемы соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_on_product_card(self, expected_product_volumes: list[int]) -> None:
        self.locators.product_offer_form.PRODUCT_CARD_VOLUMES.wait_to_have_count(len(expected_product_volumes))

        minutes_volume = self.locators.product_offer_form.PRODUCT_CARD_VOLUMES[0].text
        internet_volume = self.locators.product_offer_form.PRODUCT_CARD_VOLUMES[1].text
        sms_volume = self.locators.product_offer_form.PRODUCT_CARD_VOLUMES[2].text

        product_volumes = [minutes_volume, internet_volume, sms_volume]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Проверить что объемы в сайдбаре соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_in_sidebar(self, expected_product_volumes: list[int]) -> None:
        self.locators.product_offer_form.PRODUCT_CARD_VOLUMES.wait_to_have_count(len(expected_product_volumes))

        minutes_volume_product_info_sidebar = self.locators.product_offer_form.product_info_form.PRODUCT_VOLUMES[0].text
        internet_volume_product_info_sidebar = self.locators.product_offer_form.product_info_form.PRODUCT_VOLUMES[1].text
        sms_volume_product_info_sidebar = self.locators.product_offer_form.product_info_form.PRODUCT_VOLUMES[2].text

        product_volumes = [
            minutes_volume_product_info_sidebar,
            internet_volume_product_info_sidebar,
            sms_volume_product_info_sidebar,
        ]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Проверить что объемы в тултипе соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_in_tooltip(self, expected_product_volumes: list[int]) -> None:
        self.locators.TOOLTIP_VOLUMES.wait_to_have_count(len(expected_product_volumes) + 1)

        internet_volume_subtitle = self.locators.TOOLTIP_VOLUMES[1].text
        minutes_volume_subtitle = self.locators.TOOLTIP_VOLUMES[2].text
        sms_volume_subtitle = self.locators.TOOLTIP_VOLUMES[3].text

        product_volumes = [internet_volume_subtitle, minutes_volume_subtitle, sms_volume_subtitle]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Проверить что объемы а вкладке Объемы соответствуют ожидаемым: {expected_product_volumes}")
    def check_product_volumes_on_volumes_tab(self, expected_product_volumes: list[int]) -> None:
        self.product_edit_form.PRODUCT_VOLUMES.wait_to_have_count(len(expected_product_volumes))

        internet_volume_edit_form = self.product_edit_form.PRODUCT_VOLUMES[0].text
        minutes_volume_edit_form = self.product_edit_form.PRODUCT_VOLUMES[1].text
        sms_volume_edit_form = self.product_edit_form.PRODUCT_VOLUMES[2].text

        product_volumes = [internet_volume_edit_form, minutes_volume_edit_form, sms_volume_edit_form]
        self.check_volumes(product_volumes, expected_product_volumes)

    @allure.step("Сравнение объемов")
    def check_volumes(self, volumes: list[str], expected_volumes: list[int]) -> None:
        for i in range(len(expected_volumes)):
            volume = extract_volume_in_inquiry(volumes[i])
            assert_that(
                lambda: volume == expected_volumes[i],
                f"Объем отличется от ожидаемого: Фактический объем - {volume}, Ожидаемый объем - {expected_volumes[i]}",
            )

    @allure.step("Показать объемы продукта в тултипе")
    def show_volumes_tooltip(self, product_index: int = 0) -> None:
        self.locators.BOX_BUTTON[product_index].wait_to_be_visible(timeout=10000)
        self.locators.BOX_BUTTON[product_index].hover()
        self.locators.TOOLTIP_VOLUMES.wait_to_be_visible()

    @allure.step("Проверка параллельного заказа")
    def check_and_wait_parallel_inquiry(self, inquiry_list: int | list) -> None:
        self.locators.PARALLEL_INQUIRY_ID.wait_to_be_visible(timeout=120000)
        if isinstance(inquiry_list, int):
            inquiry_list = [inquiry_list]
        for inquiry in inquiry_list:
            self.locators.PARALLEL_INQUIRY_ID.to_contain_text_in_any(str(inquiry))
        self.locators.PARALLEL_INQUIRY_ID.not_to_be_visible(timeout=140000)

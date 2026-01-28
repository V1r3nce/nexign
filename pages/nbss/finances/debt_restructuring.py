from typing import Iterable

import allure

from api.nbss.agreement_requests import AgreementRequests
from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.inquiry_requests import AppealRequests
from api.nbss.installment_requests import InstallmentRequests
from common.helpers.checker import wait_that
from common.helpers.data_generator import get_current_datetime_string, get_shifted_datetime_string
from common.helpers.env_helper import BASE_URL
from common.helpers.string_helper import get_price_and_currency
from common.helpers.time_helpers import delay
from models.client import BaseClient
from models.installment import InstallmentTypeStatusMap
from pages.base_page import BasePage
from pages.locators.nbss.dynamic_form_elements import ChooseRequestTopic, DynamicForms, ForwardInquiryForm, RequestCreate
from pages.locators.nbss.finances.debt_restructuring import DebtRestructuringElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.ui_elements import Element


class DebtRestructuringPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.locators = DebtRestructuringElements()
        self.base_page = BasePage()
        self.forward_inquiry = ForwardInquiryForm()
        self.dynamic_forms = DynamicForms()
        self.request_create = RequestCreate()
        self.client_profile_page = ClientProfilePage()
        self.choose_request_topic = ChooseRequestTopic()
        self.client_api = ClientInquiriesRequests()
        self.inquiry_api = AppealRequests()
        self.installment_api = InstallmentRequests()
        self.agreement_api = AgreementRequests()
        self.installment_type = "default"
        self.installment_type_status_map = InstallmentTypeStatusMap().map
        self.init_payment = 50

    @allure.step("Создание заявки на реструктуризацию долга")
    def inquiry_create(self, client: BaseClient, seq_number: int = 1) -> int:
        """
        Создание заявки на реструктуризацию долга
        :param client: объект класса Client, для которого создаем заявку
        :param seq_number: последовательный номер заявки у этого клиента(Например вторая. По дефолту первая)
        :return int: id заявки
        """
        with allure.step("Переход в контекст клиента"):
            self.base_page.open(
                BASE_URL + f"customer-hierarchy-management/accounts/{client.get_agreement().accounts[0].id}/agreements"
            )
            self.client_profile_page.locators.ADD_AGREEMENT_BTN.wait_to_be_enabled(timeout=25000)
        with allure.step("В правом сайдбаре выбрать пункт 'Создание заявки'"):
            self.client_profile_page.locators.CREATE_REQUEST.click()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            self.request_create.TITLE.to_contain_text("Создание заявки")

        with allure.step("Выбрать тему заявки"):
            self.request_create.TOPIC.check_attribute_by_value("aria-required", "true")
            self.request_create.TOPIC.click()
            self.choose_request_topic.choose_topic(
                ["(2) 02 Расчетно-справочное обслуживание", "(203) Реструктуризация долга"]
            )
            self.choose_request_topic.CHOOSE_REQUEST_TOPIC_FORM.not_to_be_visible()
            self.request_create.CREATE_FORM.wait_to_be_visible()
            delay(2, reason="Ожидание подгрузки данных в полях")
            self.request_create.CODE.to_contain_text("203")
            self.request_create.TOPIC.to_contain_text("Реструктуризация долга")

        with allure.step("Выбор договора клиента"):
            self.request_create.AGREEMENT.wait_to_be_visible()
            self.request_create.AGREEMENT.select_by_index(0)
        with allure.step("Выбор ЛС клиента"):
            self.request_create.ACCOUNT.select_by_index(0)

        with allure.step("Передача на обработку"):
            self.dynamic_forms.FORWARD_BTN.wait_to_be_enabled()
            self.dynamic_forms.FORWARD_BTN.click()
            self.forward_inquiry.FORWARD_BTN.wait_to_be_enabled()
            self.forward_inquiry.QUEUE_FIELD.to_contain_text("Регистрация")
            self.forward_inquiry.FORWARD_BTN.click()
        with allure.step("Переход в созданную заявку"):
            wait_that(
                lambda: len(self.client_api.get_inquiry_by_topic(client.user_id, "Реструктуризация долга"))
                == seq_number,
                message="Заявка на реструктуризацию не создалась за 15 секунд",
                timeout=15,
                exception=TimeoutError,
            )
            inquiries = self.client_api.get_inquiry_by_topic(client.user_id, "Реструктуризация долга")
            delay(1, "Заявка не успевает обработаться до активного шага")
            self.base_page.open(BASE_URL + f"inquiries/{inquiries[-1]}")
        return inquiries[-1]

    @allure.step("Проведение заявки")
    def inquiry_forward(self, inquiry_id: int, payment_number: int = 4) -> None:
        self.check_payment_number(payment_number)
        delay(5, "Для того, чтобы заявка не падала в ошибку")
        self.base_page.refresh_page(wait="load")
        self.locators.INSTALLMENTS.wait_to_have_count(1, timeout=15000)
        self.locators.REFRESH_INSTALLMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.REFRESH_INSTALLMENTS_BTN.click()
        with allure.step("Проведение заявки"):
            self.locators.NEXT_BTN.wait_to_be_enabled(timeout=15000)
            self.locators.NEXT_BTN.click()
            self.locators.AGREEMENTS.wait_to_have_count(1, timeout=20000)
            self.agreement_api.check_agreement_complete(inquiry_id)
        self.base_page.refresh_page(wait="load")
        with allure.step("Согласование документа"):
            self.locators.AGREEMENTS.wait_to_have_count(1, timeout=15000)
            self.locators.AGREEMENTS[0].click()
            self.locators.AGREE_BTN.wait_to_be_enabled()
            self.locators.AGREE_BTN.click()
            self.locators.AGREEMENT_FLAG.wait_to_have_count(1)
            delay(2, "Чтобы изменения успели отобразиться")
        with allure.step("Завершение заявки"):
            self.base_page.refresh_page(wait="load")
            self.locators.NEXT_BTN.wait_to_be_enabled(timeout=15000)
            self.locators.NEXT_BTN.click()
            if self.installment_type != "init_payment":
                self.inquiry_api.wait_appeal_status(inquiry_id)
                self.installment_api.check_installment_done_status(status_timeout=30)
            else:
                delay(10, "Для того, чтобы рассрочка успела создаться. Иначе ответит 415")
                self.installment_api.check_installment_done_status(status_timeout=60)
            with allure.step("Проверка статуса заявки"):
                self.base_page.refresh_page(wait="load")
                self.locators.INSTALLMENTS.wait_to_have_count(1, timeout=25000)
                self.locators.INSTALLMENTS[0].click()
                self.locators.STATUS.wait_to_be_visible()
                self.locators.STATUS.to_contain_text(self.installment_type_status_map[self.installment_type])

    @allure.step("Аннулирование рассрочки")
    def installment_cancel(self) -> None:
        with allure.step("Выбор рассрочки"):
            self.locators.INSTALLMENTS.wait_to_have_count(1, timeout=25000)
            self.locators.INSTALLMENTS[0].click()
        with allure.step("Редактирование параметров выбранной рассрочки"):
            delay(1, "Не успевает подгрузиться кнопка")
            self.locators.CANCEL_BTN.click()
            self.locators.CANCEL_ACCEPT_BTN.click()
            delay(1, "Не успевает обработать нажатие кнопки")
        with allure.step("Проверка изменений"):
            if self.installment_type != "draft":
                self.installment_api.check_installment_done_status()
                self.base_page.refresh_page(wait="load")
                self.locators.STATUS.wait_to_be_visible(timeout=15000)
                self.locators.STATUS.to_contain_text(self.installment_type_status_map[self.installment_type])
            else:
                self.base_page.refresh_page(wait="load")
                self.locators.REFRESH_INSTALLMENTS_BTN.wait_to_be_visible(timeout=15000)
                self.locators.REFRESH_INSTALLMENTS_BTN.click()
                self.locators.INSTALLMENTS.wait_to_have_count(0)

    def check_payment_number(self, payment_number: int = 4) -> None:
        self.locators.REFRESH_INSTALLMENTS_BTN.wait_to_be_enabled(timeout=15000)
        self.locators.REFRESH_INSTALLMENTS_BTN.click()
        with allure.step("Выбор рассрочки"):
            self.locators.INSTALLMENTS.wait_to_have_count(1)
            self.locators.INSTALLMENTS[0].click()
        with allure.step("Проверка количества платежей"):
            self.locators.SCHEDULE.click()
            self.locators.INSTALLMENT_DATES.wait_to_have_count(payment_number)
            self.locators.SIDEBAR_CLOSE_BTN.click()

    @allure.step("Проверка корректности черновика")
    def draft_check(self) -> None:
        self.installment_api.check_installment_done_status()
        self.check_payment_number()
        with allure.step("Проверка статуса заявки"):
            self.locators.STATUS.to_contain_text(self.installment_type_status_map[self.installment_type])

    def fill_withdraw_table(self, withdraw: list[int]) -> None:
        """
        Построчное заполнение значений "Отобрано" в таблицу по деталям счета.
        Значения последовательно берутся из withdraw.
        """
        sorted_withdraw = sorted(withdraw, reverse=True)

        bill_debt: Iterable[Element] = self.locators.BILL_DEBT
        self.locators.BILL_DEBT.wait_to_have_count(len(withdraw))

        debt_dict: dict[float, int] = {}

        for idx, row in enumerate(bill_debt):
            value, _ = get_price_and_currency(row.text)
            debt_dict[value] = idx

        debt_list: list[float] = sorted(debt_dict.keys(), reverse=True)

        assert len(sorted_withdraw) == len(debt_list)

        for i in range(len(debt_list)):
            curr_row_idx = debt_dict[debt_list[i]]

            self.locators.BILL_CHECKBOXES[curr_row_idx].click()

            if sorted_withdraw[i] != 0:
                self.locators.BILL_WITHDRAW[curr_row_idx].fill(str(sorted_withdraw[i]))

    @allure.step("Создание рассрочки")
    def installment_create(self, withdraw: list[int], payment_number: int = 4, expected_date_number: int = 4) -> None:
        with allure.step("Нажатие кнопки добавить и ожидание сайдбара"):
            self.locators.ADD_BTN.wait_to_be_enabled(timeout=15000)
            self.locators.ADD_BTN.click()
            self.locators.BILL_CHECKBOXES.wait_to_be_visible()
        with allure.step("Заполнение параметров рассрочки"):
            self.fill_withdraw_table(withdraw)
            self.locators.NEXT_SIDEBAR_BTN.wait_to_be_enabled(timeout=10000)
            self.locators.NEXT_SIDEBAR_BTN.click()
            if self.installment_type == "init_payment":
                self.locators.SUM_OF_PAYMENT.fill("0")
                self.locators.INIT_PAYMENT_CHECKBOX.wait_to_be_enabled()
                self.locators.INIT_PAYMENT_CHECKBOX.click()
                self.locators.INIT_PAYMENT_DATE.fill(get_current_datetime_string(is_full_format=False))
                self.locators.INIT_PAYMENT.fill(str(self.init_payment))
                self.locators.FIRST_PAYMENT_DATE.fill(get_shifted_datetime_string("+1d", is_full_format=False))
            else:
                self.locators.FIRST_PAYMENT_DATE.fill(get_current_datetime_string(is_full_format=False))
            self.locators.PAYMENT_NUMBER.fill(str(payment_number))
            self.locators.CALCULATE_BTN.click()
            self.locators.PAYMENTS.wait_to_have_count(expected_date_number)
            if self.installment_type == "delete":
                self.locators.PAYMENTS[0].click()
                self.locators.PAYMENT_DELETE_BTN.click()
            if self.installment_type not in ["draft", "error"]:
                self.locators.REGISTER_BTN.click()
            if self.installment_type == "draft":
                self.locators.DRAFT_SAVE_BTN.click()

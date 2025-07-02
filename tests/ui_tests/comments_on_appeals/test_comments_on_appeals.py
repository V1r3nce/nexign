import re

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page

from api.requests.client_requests import ClientRequests
from api.requests.inquiry_requests import CustomProperty, ForwardInfo, InquiryInfo, InquiryRequests
from common.helpers.checker import assert_that
from common.helpers.data_generator import generate_russian_string
from common.helpers.time_helpers import get_current_moscow_datetime, get_datetime_from_string
from models.user import IndividualClient
from pages.client_profile_page import ClientProfilePage
from pages.inquiries_page import InquiriesPage
from pages.locators.dynamic_form_elements import CommentsForm


@allure.suite("E2E_89_2 Работа с обращениями (Комментарии к обращениям)")
@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=664654209",
    name="КР [NBSS] Управление комментариями (Упрощенное)",
)
@pytest.mark.regress
class TestCommentsOnAppeals:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_ui_stand_login: Page,
        api_request_auth_context: APIRequestContext,
        create_individual_user: IndividualClient,
    ):
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.inquiries_page = InquiriesPage(nexign_ui_stand_login)
        self.comments_form = CommentsForm(nexign_ui_stand_login)
        self.client_api = ClientRequests(api_request_auth_context)
        self.inquiry_api = InquiryRequests(api_request_auth_context)

        self.client = create_individual_user
        self.inquiry_id = self.inquiry_api.create_inquiry(
            InquiryInfo(self.client.user_id, [CustomProperty("inqrLinkedPerson", 230, "DICTIONARY", [])], 4)
        )
        self.inquiry_api.forward_inquiry(ForwardInfo(inquiry_id=self.inquiry_id, activity_id=9, queue_id=15))
        self.comment_text = generate_russian_string(10)
        self.operator_fio = "Иванов Иван Иванович"

    def open_active_inquiry(self):
        with allure.step("Перейти к активной заявке клиента"):
            self.client_profile.click_tab("Заявки")
            self.client_profile.locators.REQUESTS.wait_to_have_count(1)
            self.client_profile.locators.REQUEST_NUMBER[0].click()
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(
                re.compile(r"\d\. Не согласен с расчетами"), timeout=10000
            )
            self.inquiries_page.locators.VIEW_COMMENTS.wait_to_be_enabled()

    @allure.title("Создание комментария (Заявка)")
    @allure.id(594703)
    def test_create_comment_inquiry(self, base_url: str) -> None:
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.NO_COMMENTS_BLOCK.wait_to_be_visible()
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()

        with allure.step("Ввести текст комментария, нажать кнопку 'Отправить'"):
            self.comments_form.COMMENT_INPUT.fill(self.comment_text)
            create_date = get_current_moscow_datetime()
            self.comments_form.SEND_COMMENT_BTN.click()
            self.comments_form.check_comment(0, self.operator_fio, create_date, self.comment_text)

    @allure.title("Создание комментария (Карточка клиента)")
    @allure.id(594793)
    def test_create_comment_client_card(self, base_url: str) -> None:
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.NO_COMMENTS_BLOCK.wait_to_be_visible()
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()

        with allure.step("Ввести текст комментария, нажать кнопку 'Отправить'"):
            self.comments_form.COMMENT_INPUT.fill(self.comment_text)
            create_date = get_current_moscow_datetime()
            self.comments_form.SEND_COMMENT_BTN.click()
            self.comments_form.check_comment(0, self.operator_fio, create_date, self.comment_text)

    @allure.title("Редактирование комментария")
    @allure.id(594794)
    def test_edit_comment(self, base_url: str) -> None:
        new_comment = generate_russian_string(7)
        self.client_api.create_comment("INQUIRY", self.inquiry_id, self.comment_text)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=self.comment_text)
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()
            self.comments_form.MORE_ACTIONS_BTN[0].wait_to_be_enabled()
            create_date = get_datetime_from_string(self.comments_form.COMMENT_DATE[0].text)

        with allure.step("Выбрать необходимый комментарий, нажать кнопку выбора действия, нажать 'Редактировать'"):
            self.comments_form.MORE_ACTIONS_BTN.click(0)
            self.comments_form.EDIT_BTN.click()
            self.comments_form.EDIT_FORM_TITLE.wait_to_have_text("Редактирование комментария")
            self.comments_form.EDIT_COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.EDIT_COMMENT_INPUT.wait_to_have_text(self.comment_text)
            self.comments_form.EDIT_COMMENT_INPUT.check_attribute_by_value("aria-required", "true")
            self.comments_form.INNER_CANCEL_BTN.wait_to_be_enabled()
            self.comments_form.INNER_ACCEPT_BTN.wait_to_be_enabled()

        with allure.step("Внести изменения в поле 'Текст комментария', нажать 'Сохранить'"):
            self.comments_form.EDIT_COMMENT_INPUT.fill(new_comment)
            self.comments_form.INNER_ACCEPT_BTN.click()
            self.comments_form.EDIT_FORM_TITLE.not_to_be_visible()
            self.comments_form.check_comment(0, self.operator_fio, create_date, new_comment, 0)

    @allure.title("Удаление комментария")
    @allure.id(594795)
    def test_delete_comment(self, base_url: str) -> None:
        self.client_api.create_comment("INQUIRY", self.inquiry_id, self.comment_text)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=self.comment_text)
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()
            self.comments_form.MORE_ACTIONS_BTN[0].wait_to_be_enabled()

        with allure.step("Выбрать необходимый комментарий, нажать кнопку выбора действия, нажать 'Удалить'"):
            self.comments_form.MORE_ACTIONS_BTN.click(0)
            self.comments_form.DELETE_BTN.click()
            self.inquiries_page.locators.MODAL.wait_to_be_visible()
            self.inquiries_page.locators.MODAL_TITLE.wait_to_have_text(
                "Удалить комментарий?" + "После удаления комментарий нельзя будет восстановить"
            )
            self.inquiries_page.locators.MODAL_FIRST_BTN.wait_to_be_enabled()
            self.inquiries_page.locators.MODAL_SECOND_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Удалить'"):
            self.inquiries_page.locators.MODAL_SECOND_BTN.click()
            self.inquiries_page.locators.MODAL.not_to_be_visible()
            self.comments_form.NO_COMMENTS_BLOCK.wait_to_be_visible()

    @allure.title("Просмотр комментария (Клиент не выбран)")
    @allure.id(594798)
    def test_view_comment_no_client(self) -> None:
        self.inquiries_page.locators.VIEW_COMMENTS.not_to_be_visible()

    @allure.title("Просмотр комментария")
    @allure.id(594800)
    def test_view_comment(self, base_url: str) -> None:
        self.client_api.create_comment("INQUIRY", self.inquiry_id, self.comment_text)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=self.comment_text)
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()
            self.comments_form.MORE_ACTIONS_BTN[0].wait_to_be_enabled()
            self.comments_form.COMMENTS_TYPE.wait_to_have_text(f"Заявка {self.inquiry_id}")

    @allure.title("Просмотр комментария (Смена сущности)")
    @allure.id(594801)
    def test_view_comment_change_entity(self, base_url: str) -> None:
        client_comment_text = generate_russian_string(10)
        self.client_api.create_comment("INQUIRY", self.inquiry_id, self.comment_text)
        self.client_api.create_comment("CUSTOMER", self.client.user_id, client_comment_text)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=self.comment_text)
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()
            self.comments_form.MORE_ACTIONS_BTN[0].wait_to_be_enabled()
            self.comments_form.COMMENTS_TYPE.wait_to_have_text(f"Заявка {self.inquiry_id}")

        with allure.step("В навигационном баре, на форме заявки, перейти к выбранному клиенту"):
            self.inquiries_page.locators.LINK_IN_CONTEXT.click(0)
            self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=client_comment_text)
            self.comments_form.COMMENTS_TYPE.wait_to_have_text(
                f"Клиент {self.client.sur_name} {self.client.first_name} {self.client.patronymic}"
            )

    @allure.title("Просмотр комментария (Смена сущности в комментариях)")
    @allure.id(594802)
    def test_view_comment_change_entity_in_comments(self, base_url: str) -> None:
        client_comment_text = generate_russian_string(10)
        self.client_api.create_comment("INQUIRY", self.inquiry_id, self.comment_text)
        self.client_api.create_comment("CUSTOMER", self.client.user_id, client_comment_text)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=self.comment_text)
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()
            self.comments_form.MORE_ACTIONS_BTN[0].wait_to_be_enabled()
            self.comments_form.COMMENTS_TYPE.wait_to_have_text(f"Заявка {self.inquiry_id}")

        with allure.step("Открыть выпадающий список, выбрать текущего клиента"):
            self.comments_form.COMMENTS_TYPE.select_by_value(
                "Клиент", f"{self.client.sur_name} {self.client.first_name} {self.client.patronymic}"
            )
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=client_comment_text)
            self.inquiries_page.locators.INQUIRY_NAME.wait_to_have_text(re.compile(r"\d\. Не согласен с расчетами"))

    @allure.title("Просмотр комментария (Изменение размера окна)")
    @allure.id(594803)
    def test_view_comment_change_window_size(self, base_url: str) -> None:
        self.client_api.create_comment("INQUIRY", self.inquiry_id, self.comment_text)
        self.client_profile.open(f"{base_url}customer-hierarchy-management/customers/{self.client.user_id}/overview")
        self.client_profile.locators.CLIENT_FIO.wait_to_be_visible()

        self.open_active_inquiry()

        with allure.step("Нажать на кнопку 'Комментарии' в правой части экрана"):
            self.inquiries_page.locators.VIEW_COMMENTS.click()
            self.comments_form.TITLE.wait_to_have_text("Комментарии")
            self.comments_form.COMMENT.wait_to_have_count(1)
            self.comments_form.check_comment(comment_text=self.comment_text)
            self.comments_form.COMMENT_INPUT.wait_to_be_enabled()
            self.comments_form.SEND_COMMENT_BTN.wait_to_be_enabled()
            self.comments_form.MORE_ACTIONS_BTN[0].wait_to_be_enabled()
            self.comments_form.COMMENTS_TYPE.wait_to_have_text(f"Заявка {self.inquiry_id}")
            self.comments_form.OPEN_FULL_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Развернуть'"):
            small_size = int(self.comments_form.FORM.get_css_property("min-width")[:-2])
            self.comments_form.OPEN_FULL_BTN.click()
            with allure.step("Проверить, что размер окна увеличился"):
                assert_that(
                    lambda: int(self.comments_form.FORM.get_css_property("min-width")[:-2]) > small_size,
                    "Размер окна 'Комментарии' не увеличился",
                )
            self.comments_form.OPEN_FULL_BTN.not_to_be_visible()
            self.comments_form.CLOSE_FULL_BTN.wait_to_be_enabled()

        with allure.step("Нажать кнопку 'Свернуть'"):
            self.comments_form.CLOSE_FULL_BTN.click()
            self.comments_form.FORM.to_have_css("min-width", f"{small_size}px")
            self.comments_form.CLOSE_FULL_BTN.not_to_be_visible()
            self.comments_form.OPEN_FULL_BTN.wait_to_be_enabled()

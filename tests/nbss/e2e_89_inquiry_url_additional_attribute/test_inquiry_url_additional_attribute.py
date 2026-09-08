import allure
import pytest

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from common.enums.topic import TestTopic
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.dynamic_forms.panel_toolbar.panel_toolbar_page import PanelToolbarPage
from pages.nbss.inquiries_page import InquiriesPage


@allure.epic("E2E_89 Работа с обращениями")
@allure.suite("E2E_89 Работа с обращениями")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestInquiryUrlAdditionalAttribute:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization) -> None:
        self.client_profile = ClientProfilePage()
        self.inquiries_page = InquiriesPage()
        self.panel_toolbar_page = PanelToolbarPage()
        self.client_inquiry_requests = ClientInquiriesRequests()
        self.client = create_organization

        self.theme_group = TestTopic.Group
        self.theme_name_selection = TestTopic.UrlAttributeSupportKeep

        self.label_text_1 = "Ссылка на требование"
        self.attribute_text_1 = "Ссылка на требование"
        self.link_url_1 = "https://nexign.com/ru"
        self.label_text_2 = "Ссылка на требование 2"
        self.attribute_text_2 = "https://nexign.com"
        self.link_url_2 = "https://nexign.com/ru"
        self.editable_attribute_text = '<a href="https://nexign.com/ru">https://nexign.com</a>'

    @allure.title("01. Просмотр дополнительных атрибутов заявки, содержащих в себе ссылки")
    @allure.id(941341)
    def test_view_inquiry_url_additional_attributes(self) -> None:
        self.client_profile.open_client_overview_page(self.client.user_id)
        self.inquiries_page.open_create_inquiry_form()
        self.inquiries_page.choose_request_topic.choose_topic([self.theme_group, self.theme_name_selection])
        self.panel_toolbar_page.create_inquiry_and_check_url_attributes(
            topic=TestTopic.UrlAttributeSupportKeep,
            label_index=0,
            value_index=0,
            label_text=self.label_text_1,
            attribute_value=self.attribute_text_1,
            link_url=self.link_url_1,
        )

        with allure.step("Кликнуть по ссылкам на вкладке 'Обзор' и проверить, что страницы открылись в новой вкладке"):
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS[0],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[0],
                label_text=self.label_text_1,
                link_text=self.attribute_text_1,
                link_url=self.link_url_1,
            )
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS[1],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[1],
                label_text=self.label_text_2,
                link_text=self.attribute_text_2,
                link_url=self.link_url_2,
            )

    @allure.title("02. Редактирование дополнительных атрибутов заявки, содержащих в себе ссылки")
    @allure.id(907653)
    def test_edit_inquiry_url_additional_attributes(self) -> None:
        self.client_profile.open_client_overview_page(self.client.user_id)
        self.inquiries_page.open_create_inquiry_form()
        self.inquiries_page.choose_request_topic.choose_topic([self.theme_group, self.theme_name_selection])
        self.panel_toolbar_page.create_inquiry_and_check_url_attributes(
            topic=TestTopic.UrlAttributeSupportKeep,
            label_index=0,
            value_index=0,
            label_text=self.label_text_1,
            attribute_value=self.attribute_text_1,
            link_url=self.link_url_1,
        )

        with allure.step("Проверить, что на форме отображаются атрибуты со ссылками"):
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS[0],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[0],
                label_text=self.label_text_1,
                link_text=self.attribute_text_1,
                link_url=self.link_url_1,
            )
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS[1],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[1],
                label_text=self.label_text_2,
                link_text=self.attribute_text_2,
                link_url=self.link_url_2,
            )

        with allure.step("Нажать на кнопку 'Редактировать'"):
            self.inquiries_page.locators.EDIT_BTN.wait_to_be_visible()
            self.inquiries_page.locators.EDIT_BTN.click()

        with allure.step("Проверить, что атрибуты, содержащие ссылку, изменить нельзя"):
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS_EDIT_FORM[0],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[0],
                label_text=self.label_text_1,
                link_text=self.attribute_text_1,
                link_url=self.link_url_1,
            )
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS_EDIT_FORM[1],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_INPUTS_EDIT_FORM[0],
                label_text=self.label_text_2,
                link_text=self.editable_attribute_text,
            )

        with allure.step("Проверить доступные действия: 'Отмена' и 'Сохранить'"):
            self.inquiries_page.locators.EDIT_SAVE_BTN.wait_to_be_enabled()
            self.inquiries_page.locators.EDIT_CANCEL_BTN.wait_to_be_enabled()

        with allure.step("Нажать 'Отмена' для выхода из режима редактирования"):
            self.inquiries_page.locators.EDIT_CANCEL_BTN.click()
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS[0],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[0],
                label_text=self.label_text_1,
                link_text=self.attribute_text_1,
                link_url=self.link_url_1,
            )
            self.inquiries_page.check_url_attribute(
                label=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LABELS[1],
                link=self.inquiries_page.inquiry_overview.ADDITIONAL_ATTRIBUTE_LINKS[1],
                label_text=self.label_text_2,
                link_text=self.attribute_text_2,
                link_url=self.link_url_2,
            )

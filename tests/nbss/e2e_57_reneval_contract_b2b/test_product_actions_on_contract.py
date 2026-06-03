import allure
import pytest
from playwright.sync_api import APIRequestContext

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.client_requests.client_requests import ClientRequests
from api.nbss.finances.payments_requests import PaymentsRequests
from api.nbss.personal_account_requests import PersonalAccountData, PersonalAccountRequests
from common.helpers.env_helper import BASE_URL
from models.client import OrganizationClient, generate_organization_client
from models.context import test_context
from models.inquiry import prepare_inquiries
from pages.locators.nbss.inquiries_elements import InquiriesElements, ProductsMoveInquiryElements
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.inquiries_page import InquiriesPage
from pages.nbss.personal_account_page import PersonalAccountPage


@allure.epic("E2E_57 Переоформление договора B2B")
@allure.suite("E2E_57 Переоформление договора B2B")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestSale:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        nexign_stand_login,
        api_request_context: APIRequestContext,
    ) -> None:
        self.personal_account_requests = PersonalAccountRequests()
        self.client_inquiries_requests = ClientInquiriesRequests()
        self.client_profile_page = ClientProfilePage()
        self.client_requests = ClientRequests()
        self.inquiries_page = InquiriesPage()
        self.inquiries_elements = InquiriesElements()
        self.product_move_inquiry_elements = ProductsMoveInquiryElements()
        self.personal_account_page = PersonalAccountPage()
        self.payment_api = PaymentsRequests()
        self.additional_product = "+100 минут"

    @allure.title("01 Создание заявки")
    @allure.id(656649)
    def test_b2b_renewal_inquiry_creation(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        self.inquiries_page.create_inquiry_product_move_to_another_account()
        self.inquiries_page.product_move_distribution(
            account_number=test_context.client_list[0].agreements[0].accounts[0].number,
            product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            product_exist=False,
        )
        with allure.step("Проверить созданную заявку"):
            self.inquiries_elements.INQUIRY_NAME.to_contain_text("Перенос продуктов на другие ЛС")
            self.inquiries_elements.INQUIRY_STEP.to_contain_text("Выбор продуктов для переноса")
            self.product_move_inquiry_elements.TARGET_AGREEMENT_MESSAGE.to_contain_text(
                "Выберите целевой договор и целевые продукты, которые хотите перенести на лицевые счета целевого договора"
            )

    @allure.title("03 Перенос основного продукта на ЛС текущего договора")
    @pytest.mark.skip(reason="https://jira.nexign.com/browse/RMBSS-10854")
    @allure.id(656656)
    def test_b2b_move_inquiry_to_current_account(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        with allure.step("Провести продажу ПП на 1 лс"):
            self.client_inquiries_requests.product_sale(test_context.client, prepare_inquiries("internet"))
            self.payment_api.create_default_payment(
                create_organization.agreements[0].accounts[0].id,
                payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount),
            )
            self.client_inquiries_requests.wait_products_active_by_agreement(
                test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
            )
        with allure.step("Создать второй лс"):
            self.personal_account_requests.create_personal_account(
                PersonalAccountData(
                    agreement_id=test_context.client.agreements[0].id,
                    raiting_type=2,
                    threshold_break=2000,
                    threshold_control=True,
                ),
                test_context.client.user_id,
            )
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                docs_form_sign=True, docs_agreement_form_sign=False, docs_form=False
            )

        with allure.step("Переход в раздел Проудкты и проверка данных после смены ЛС"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client.user_id}/products"
            )
            self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM.to_contain_text(
                test_context.client.agreements[0].accounts[0].number
            )
            self.client_profile_page.locators.PRODUCT_NAME.to_contain_text(
                test_context.client.inquiry.product_list[0].product_name
            )
            self.inquiries_elements.PRODUCTS_CONTRACT_NUM.to_contain_text(test_context.client.agreements[0].number)

    @allure.title("04 Перенос на ЛС другого договора текущего клиента")
    @pytest.mark.skip(reason="https://jira.nexign.com/browse/RMBSS-10854")
    @allure.id(656657)
    def test_b2b_move_account_to_current_client(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement(create_organization, status_id=1)
        self.client_requests.create_organization_with_agreement_and_account(generate_organization_client())
        self.client_inquiries_requests.product_sale(test_context.client_list[0], prepare_inquiries("internet"))
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        self.inquiries_page.create_inquiry_product_move_to_another_account()
        self.inquiries_page.manual_inquiry_product_move_steps_pass(
            agreement_delete_step=True, docs_form_sign=True, docs_agreement_form_sign=False, docs_form=False
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[1].user_id}/products"
        )

    @allure.title("05 Перенос на договор другого клиента")
    @pytest.mark.skip(reason="https://jira.nexign.com/browse/RMBSS-10854")
    @allure.id(656658)
    def test_b2b_move_to_another_client(self, create_organization: OrganizationClient) -> None:
        self.client_requests.create_organization_with_agreement_and_account(generate_organization_client())
        self.client_inquiries_requests.product_sale(test_context.client_list[0], prepare_inquiries("internet"))
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                agreement_delete_step=True, docs_form_sign=True, docs_agreement_form_sign=False, docs_form=False
            )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[1].user_id}/products"
        )

    @allure.title("06 Перенос дополнительного продукта")
    @allure.id(656659)
    def test_b2b_additional_inquiry_move(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        self.personal_account_requests.create_personal_account(
            PersonalAccountData(
                agreement_id=test_context.client.agreements[0].id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            test_context.client.user_id,
        )

        self.client_inquiries_requests.product_sale(
            client=test_context.client_list[0],
            inquiry=prepare_inquiries("mobile", additional_product=self.additional_product),
        )
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount)
            + int(test_context.client_list[0].inquiry_list[0].product.additional_product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.product_move_distribution(
                option=True,
                account_number=test_context.client_list[0].agreements[0].accounts[0].number,
                product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            )
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                agreement_delete_step=False,
                docs_form_sign=True,
                docs_agreement_form_sign=False,
                docs_form=False,
                next_button_necessary=False,
            )

        with allure.step("Проверить корректность изменений после переноса продукта"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[0].user_id}/products"
            )
            with allure.step("Проверить поле абонент у ПП"):
                self.client_profile_page.locators.SUBSCRIBER[0].to_contain_text(
                    test_context.client.inquiry.product.phone_number
                )
            with allure.step("Проверить поле 'Продукт' у первого ПП"):
                self.client_profile_page.locators.PRODUCT_NAME[0].to_contain_text(
                    test_context.client.inquiry.product.product_name
                )
            with allure.step("Проверить договор ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(
                    test_context.client.inquiry.agreement_number
                )
            with allure.step("Проверить Лицевой Счёт ПП"):
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].to_contain_text(
                    test_context.client.agreements[0].accounts[0].number
                )
            with allure.step("Проверить поле 'Доп Опция' у ПП"):
                self.client_profile_page.locators.OPTION_ELEMENTS.to_contain_text_in_any(self.additional_product)
            with allure.step("Проверить Лицевой Счёт ПП"):
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[1].to_contain_text(
                    test_context.client.agreements[0].accounts[1].number
                )

    @allure.title("07 Перенос основного продукта (без дополнительного)")
    @allure.id(656660)
    def test_b2b_main_inquiry_move(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        self.personal_account_requests.create_personal_account(
            PersonalAccountData(
                agreement_id=test_context.client.agreements[0].id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            test_context.client.user_id,
        )
        self.client_inquiries_requests.product_sale(
            client=test_context.client_list[0],
            inquiry=prepare_inquiries("mobile", additional_product=self.additional_product),
        )
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount)
            + int(test_context.client_list[0].inquiry_list[0].product.additional_product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.product_move_distribution(
                account_number=test_context.client_list[0].agreements[0].accounts[0].number,
                product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            )
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                agreement_delete_step=False,
                docs_form_sign=True,
                docs_agreement_form_sign=False,
                docs_form=False,
                next_button_necessary=False,
            )

        with allure.step("Проверить корректность изменений после переноса продукта"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[0].user_id}/products"
            )
            with allure.step("Проверить поле абонент у ПП"):
                self.client_profile_page.locators.SUBSCRIBER[0].to_contain_text(
                    test_context.client.inquiry.product.phone_number
                )
            with allure.step("Проверить поле 'Продукт' у ПП"):
                self.client_profile_page.locators.PRODUCT_NAME[0].to_contain_text(
                    test_context.client.inquiry.product.product_name
                )
            with allure.step("Проверить договор ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(
                    test_context.client.inquiry.agreement_number
                )
            with allure.step("Проверить Лицевой Счёт ПП"):
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[0].to_contain_text(
                    test_context.client.agreements[0].accounts[1].number
                )
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[1].to_contain_text(
                    test_context.client.agreements[0].accounts[1].number
                )
            with allure.step("Проверить поле 'Доп Опция' у ПП"):
                self.client_profile_page.locators.OPTION_ELEMENTS.to_contain_text_in_any(self.additional_product)

    @allure.title("08 Перенос нескольких основных продуктов")
    @allure.id(656663)
    def test_b2b_few_inquiries_move(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        self.personal_account_requests.create_personal_account(
            PersonalAccountData(
                agreement_id=test_context.client.agreements[0].id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            test_context.client.user_id,
        )
        self.client_inquiries_requests.product_sale(
            client=test_context.client_list[0],
            inquiry=prepare_inquiries(
                ["mobile", "mobile"], additional_product=[self.additional_product, self.additional_product], as_list=True
            ),
        )
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount)
            + int(test_context.client_list[0].inquiry_list[1].product.total_amount)
            + int(test_context.client_list[0].inquiry_list[0].product.additional_product.total_amount)
            + int(test_context.client_list[0].inquiry_list[1].product.additional_product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )

        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.product_move_distribution(
                account_number=test_context.client_list[0].agreements[0].accounts[0].number,
                product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            )
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                agreement_delete_step=False,
                docs_form_sign=True,
                docs_agreement_form_sign=False,
                docs_form=False,
                next_button_necessary=False,
            )

        with allure.step("Проверить корректность изменений после переноса продукта"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[0].user_id}/products"
            )

            self.client_inquiries_requests.wait_account_num_update(
                test_context.client.user_id,
                test_context.client.inquiry.product.subs_id,
                test_context.client.agreements[0].accounts[1].number,
            )
            self.client_profile_page.locators.PRODUCTS_UPDATE_BTN.click()
            self.client_profile_page.open_products_all_subscriber()
            with allure.step("Проверить поле абонент у первого ПП"):
                self.client_profile_page.locators.SUBSCRIBER[0].to_contain_text(
                    test_context.client.inquiry_list[0].product.phone_number
                )
            with allure.step("Проверить поле 'Продукт' у первого ПП"):
                self.client_profile_page.locators.PRODUCT_NAME[0].to_contain_text(
                    test_context.client.inquiry.product.product_name
                )
            with allure.step("Проверить поле 'Доп Опция' у первого ПП"):
                self.client_profile_page.locators.OPTION_ELEMENTS.to_contain_text_in_any(self.additional_product)
            with allure.step("Проверить поле Лицевой Счёт у доп опции первого ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(
                    test_context.client.inquiry.agreement_number
                )
            with allure.step("Проверить поле 'Договор' у первого ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(
                    test_context.client.agreements[0].number
                )
            with allure.step("Проверить поле абонент у второго ПП"):
                self.client_profile_page.locators.SUBSCRIBER[1].to_contain_text(
                    test_context.client.inquiry_list[1].product.phone_number
                )
            with allure.step("Проверить поле 'Продукт' у второго ПП"):
                self.client_profile_page.locators.PRODUCT_NAME.to_contain_text_in_any(
                    test_context.client.inquiry_list[1].product.product_name
                )
            with allure.step("Проверить договор второго ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[2].to_contain_text(
                    test_context.client.inquiry_list[1].agreement_number
                )
            with allure.step("Проверить Лицевой Счёт второго ПП"):
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[2].to_contain_text(
                    test_context.client.agreements[0].accounts[1].number
                )

    @allure.title("09 Объединение на одном ЛС продуктов, распределенных на разные ЛC")
    @pytest.mark.skip("_register_inquiry не может распределять на разные лс при создании заявки")
    @allure.id(656664)
    def test_b2b_combine_inquiries_to_account(self, create_organization: OrganizationClient) -> None:
        self.personal_account_requests.create_agreement_and_account(create_organization, status_id=1)
        self.personal_account_requests.create_personal_account(
            PersonalAccountData(
                agreement_id=test_context.client.agreements[0].id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            test_context.client.user_id,
        )
        self.client_inquiries_requests.product_sale(
            client=test_context.client_list[0],
            inquiry=prepare_inquiries(category="mobile"),
        )
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.product_move_distribution(
                account_number=test_context.client_list[0].agreements[0].accounts[0].number,
                product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            )
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                agreement_delete_step=False,
                docs_form_sign=True,
                docs_agreement_form_sign=False,
                docs_form=False,
                next_button_necessary=False,
            )
        with allure.step("Проверить корректность изменений после переноса продукта"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[0].user_id}/products"
            )

    @allure.title("10 Перенос с разных ЛС на разные ЛС другого клиента")
    @allure.id(659969)
    def test_b2b_move_inquiries_from_different_accounts_to_another_client(self) -> None:
        client1 = self.client_requests.create_organization(OrganizationClient())
        self.personal_account_requests.create_agreement_and_account(client1, status_id=1)
        self.personal_account_requests.create_personal_account(
            PersonalAccountData(
                agreement_id=test_context.client.agreements[0].id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            test_context.client_list[0].user_id,
        )

        client2 = self.client_requests.create_organization(OrganizationClient())
        self.personal_account_requests.create_agreement_and_account(client2, status_id=1)
        self.personal_account_requests.create_personal_account(
            PersonalAccountData(
                agreement_id=test_context.client_list[1].agreements[0].id,
                raiting_type=2,
                threshold_break=2000,
                threshold_control=True,
            ),
            test_context.client_list[1].user_id,
        )
        self.client_inquiries_requests.product_sale(
            client=test_context.client_list[0],
            inquiry=prepare_inquiries("mobile", additional_product=self.additional_product),
        )
        self.client_inquiries_requests.product_sale(
            client=test_context.client_list[1],
            inquiry=prepare_inquiries(category="mobile"),
        )
        self.payment_api.create_default_payment(
            test_context.client_list[0].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount)
            + +int(test_context.client_list[0].inquiry_list[0].product.additional_product.total_amount),
        )
        self.payment_api.create_default_payment(
            test_context.client_list[1].agreements[0].accounts[0].id,
            payment_amount=int(test_context.client_list[1].inquiry_list[0].product.total_amount),
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[0].user_id, test_context.client_list[0].agreements[0].id
        )
        self.client_inquiries_requests.wait_products_active_by_agreement(
            test_context.client_list[1].user_id, test_context.client_list[1].agreements[0].id
        )
        self.personal_account_page.open(
            f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
        )
        with allure.step("Создать заявку на перенос"):
            self.inquiries_page.create_inquiry_product_move_to_another_account()
            self.inquiries_page.product_move_distribution(
                is_different_agreement=True,
                account_number=test_context.client_list[1].agreements[0].accounts[0].number,
                product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            )
            self.inquiries_page.manual_inquiry_product_move_steps_pass(
                agreement_delete_step=True,
                docs_form_sign=True,
                docs_agreement_form_sign=False,
                docs_form=False,
                next_button_necessary=False,
            )

        with allure.step("Проверить корректность изменений после переноса продукта"):
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[1].user_id}/products"
            )
            self.client_profile_page.locators.PRODUCTS_UPDATE_BTN.wait_to_be_visible()
            self.personal_account_page.refresh_page(wait="load")
            self.client_profile_page.locators.NO_SUBSCRIBERS_BLOCK.wait_to_be_visible()
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[1].user_id}/inquiries"
            )
            self.client_inquiries_requests.wait_inquiry_number_by_topic(
                user_id=test_context.client.user_id, topic="Расторжение договора"
            )
            self.personal_account_page.refresh_page(wait="load")
            self.client_profile_page.locators.REQUEST_TYPE.wait_to_be_visible()
            self.client_profile_page.locators.REQUEST_TYPE.to_contain_text_in_any(
                expected_text="Расторжение договора", case_sensitive=False
            )
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/customers/{test_context.client_list[0].user_id}/products"
            )
            self.client_profile_page.locators.SUBSCRIBER.wait_to_be_visible(timeout=15000)
            self.client_profile_page.open_products_all_subscriber()
            with allure.step("Проверить поле абонент у первого ПП"):
                self.client_profile_page.locators.SUBSCRIBER[0].to_contain_text(
                    test_context.client_list[0].inquiry.product.phone_number
                )
            with allure.step("Проверить поле 'Продукт' у первого ПП"):
                self.client_profile_page.locators.PRODUCT_NAME[0].to_contain_text(
                    test_context.client.inquiry.product.product_name
                )
            with allure.step("Проверить поле 'Доп Опция' у первого ПП"):
                self.client_profile_page.locators.OPTION_ELEMENTS.to_contain_text_in_any(self.additional_product)
            with allure.step("Проверить поле 'Договор' у доп опции первого ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[0].to_contain_text(
                    test_context.client_list[0].agreements[0].number
                )
            with allure.step("Проверить поле Лицевой Счёт у доп опции первого ПП"):
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[1].to_contain_text(
                    test_context.client_list[0].agreements[0].accounts[0].number
                )
            with allure.step("Проверить поле Абонент для второго ПП"):
                self.client_profile_page.locators.SUBSCRIBER.wait_to_have_count(2, timeout=15000)
                self.client_profile_page.locators.SUBSCRIBER[1].to_contain_text(
                    test_context.client_list[1].inquiry.product.phone_number
                )
            with allure.step("Проверить поле 'Продукт' у второго ПП"):
                self.client_profile_page.locators.PRODUCT_NAME.to_contain_text_in_any(
                    test_context.client.inquiry.product.product_name
                )
            with allure.step("Проверить договор второго ПП"):
                self.client_profile_page.locators.PRODUCTS_CONTRACT_NUM[2].to_contain_text(
                    test_context.client_list[0].agreements[0].number
                )
            with allure.step("Проверить Лицевой Счёт второго ПП"):
                self.client_profile_page.locators.PRODUCTS_PERSONAL_ACCOUNT_NUM[2].to_contain_text(
                    test_context.client_list[0].agreements[0].accounts[0].number
                )

    @allure.title("01 Поиск целевого договора другого клиента до уровня договора")
    @allure.id(846984)
    def test_search_agreement_other_client(self, create_organization: OrganizationClient):
        with allure.step(
            "Создание клиента со статусом договора 'Действующий' и продажа ему продукта, создание второго клиента со статусом договора 'Оформлен'"
        ):
            agreement_id, _ = self.personal_account_requests.create_agreement(create_organization, status_id=1)
            self.personal_account_requests.create_personal_account(
                PersonalAccountData(agreement_id=agreement_id, is_cash_payment_enabled=False),
                test_context.client.user_id,
            )
            self.client_requests.create_organization_with_agreement_and_account(generate_organization_client())
            self.client_inquiries_requests.product_sale(test_context.client_list[0], prepare_inquiries("internet"))
            self.payment_api.create_default_payment(
                test_context.client_list[0].agreements[0].accounts[0].id,
                payment_amount=int(test_context.client_list[0].inquiry_list[0].product.total_amount),
            )
            self.personal_account_page.open(
                f"{BASE_URL}customer-hierarchy-management/agreements/{test_context.client.agreements[0].id}/agreement"
            )
        self.inquiries_page.create_inquiry_product_move_to_another_account(need_select_agreement=False)
        self.inquiries_page.product_move_distribution(
            is_different_agreement=True,
            account_number=test_context.client_list[1].agreements[0].accounts[0].number,
            product_name=test_context.client_list[0].inquiry_list[0].product_list[0].product_name,
            need_select_account=False,
        )

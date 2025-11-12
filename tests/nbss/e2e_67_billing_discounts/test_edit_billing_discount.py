import allure
import pytest
from playwright.sync_api import Page

from api.nbss.client_requests.client_inquiries_requests import ClientInquiriesRequests
from api.nbss.finances.billing_discount import BillingDiscountsRequests
from common.helpers.time_helpers import get_current_moscow_datetime
from models.context import test_context
from models.inquiry import prepare_inquiries
from models.user import IndividualClient
from pages.locators.nbss.finances.discount_and_charges import (
    AddBillingDiscountFormStep4,
    AddBillingDiscountOrChargeFormStep3,
    AddProductOfferForm,
    FilterForm,
)
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.finances.discount_and_charges import DiscountAndChargesPage


@allure.link(
    url="confluence.nexign.com/pages/viewpage.action?pageId=659783906", name="8.6. Управление биллинговыми скидками"
)
@allure.epic("E2E_67 Управление биллинговыми скидками")
@allure.suite("E2E_67 Управление биллинговыми скидками")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestEditBillingDiscount:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, nexign_ui_stand_login, api_request_context) -> None:
        self.client_profile = ClientProfilePage(nexign_ui_stand_login)
        self.client_request_api = ClientInquiriesRequests(api_request_context)
        self.discount_page = DiscountAndChargesPage(page)
        self.discount_requests_api = BillingDiscountsRequests(api_request_context)
        self.add_discount_form_step_2 = AddProductOfferForm(page)
        self.filter_form = FilterForm(page)
        self.start_date = get_current_moscow_datetime().strftime("%d.%m.%Y")
        self.end_date = "01.12.2999"
        self.discount_amount = "50"
        self.priority = "1"
        self.add_discount_form_step_4 = AddBillingDiscountFormStep4(page)
        self.add_discount_form_step_3 = AddBillingDiscountOrChargeFormStep3(page)

    @allure.title("04. Удаление биллинговой скидки")
    @allure.id(676529)
    def test_delete_billing_discount(self, create_individual_user: IndividualClient, base_url: str) -> None:
        inquiry = self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            product=inquiry.product,
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Применение фильтра по типу скидки"):
            self.discount_page.locators.FILTER_BTN.click()
            self.filter_form.TYPE.select_by_value("Скидки")
            self.filter_form.SET_BTN.click()

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Удаление скидку"):
            self.discount_page.locators.DISCOUNT_DELETE_BTN.click()
            self.discount_page.locators.MODAL_SECOND_BTN.click()

        with allure.step("Проверяем, что скидка отсутствует"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(0)

    @allure.title("17. Редактирование условий применимости")
    @allure.id(676642)
    def test_edit_billing_discount_conditions(self, create_individual_user: IndividualClient, base_url: str) -> None:
        new_discount = "60"
        inquiry = self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            product=inquiry.product,
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Редактирование условий"):
            self.discount_page.locators.CONDITIONS_TAB.click()
            self.discount_page.locators.DISCOUNT_VALUE.to_contain_text(self.discount_amount)

            self.discount_page.locators.CONDITION_ATTR_EDIT_BTN.click()
            self.add_discount_form_step_4.VALUE.fill(new_discount)
            self.add_discount_form_step_4.SET_BTN.click()

        self.discount_page.locators.DISCOUNT_VALUE.wait_to_have_text(f"Размер скидки, %{new_discount}")

    @allure.title("15. Удаление абонента в активной скидке")
    @allure.id(676638)
    def test_delete_billing_discount_subscriber(self, create_individual_user: IndividualClient, base_url: str) -> None:
        inquiry = self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            product=inquiry.product,
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Удаление абонента"):
            self.discount_page.locators.SUBSCRIBERS_TAB.click()
            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(1)

            self.discount_page.locators.SUBSCRIBERS[0].click()
            self.discount_page.locators.SUBSCRIBER_DELETE_BTN.click()
            self.discount_page.locators.MODAL_SECOND_BTN.click()

            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(0)

    @allure.title("13. Добавление абонента в активной скидке")
    @allure.id(676637)
    def test_add_subscriber_to_billing_discount(
        self, create_user_with_agreement_and_account: IndividualClient, base_url: str
    ) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        self.discount_page.locators.SUBSCRIBERS_TAB.click()
        self.discount_page.locators.SUBSCRIBER_ADD_BTN.click()
        self.add_discount_form_step_3.SUBSCRIBERS_TABLE.select_by_value(
            str(test_context.client.inquiry_list[1].product.subs_id)
        )
        self.add_discount_form_step_3.INNER_ACCEPT_BTN.click()

        self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(2)
        self.discount_page.locators.SUBSCRIBERS[0].to_contain_text(
            str(test_context.client.inquiry_list[0].product.subs_id), timeout_sec=1
        )
        self.discount_page.locators.SUBSCRIBERS[1].to_contain_text(
            str(test_context.client.inquiry_list[1].product.subs_id)
        )

    @allure.title("14. Добавление нескольких абонентов в активной скидке")
    @allure.id(676639)
    def test_add_multiple_subscribers_to_billing_discount(
        self, create_user_with_agreement_and_account: IndividualClient, base_url: str
    ) -> None:
        products = prepare_inquiries(["mobile", "mobile", "mobile"])
        self.client_request_api.product_sale(inquiry=products)

        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )

        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            product=test_context.client.inquiry.product_list[0],
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        self.discount_page.locators.SUBSCRIBERS_TAB.click()

        product_list = test_context.client.inquiry.product_list

        with allure.step(f"Проверяем начальное состояние - 1 абонент (ID: {product_list[0].subs_id})"):
            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(1)
            self.discount_page.locators.SUBSCRIBERS[0].to_contain_text(str(product_list[0].subs_id), timeout_sec=1)

        with allure.step(f"Добавляем второго абонента (ID: {product_list[1].subs_id})"):
            self.discount_page.locators.SUBSCRIBER_ADD_BTN.click()
            self.add_discount_form_step_3.SUBSCRIBERS_TABLE.select_by_value(str(product_list[1].subs_id))
            self.add_discount_form_step_3.INNER_ACCEPT_BTN.click()

            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(2)
            self.discount_page.locators.SUBSCRIBERS[1].to_contain_text(str(product_list[1].subs_id))

        with allure.step(f"Добавляем третьего абонента (ID: {product_list[2].subs_id})"):
            self.discount_page.locators.SUBSCRIBER_ADD_BTN.click()
            self.add_discount_form_step_3.SUBSCRIBERS_TABLE.select_by_value(str(product_list[2].subs_id))
            self.add_discount_form_step_3.INNER_ACCEPT_BTN.click()

            self.discount_page.locators.SUBSCRIBERS.wait_to_have_count(3)
            self.discount_page.locators.SUBSCRIBERS[2].to_contain_text(str(product_list[2].subs_id))

    @allure.title("08. Добавление продукта в активной скидке")
    @allure.id(676564)
    def test_add_product_to_billing_discount(
        self, create_user_with_agreement_and_account: IndividualClient, base_url: str
    ) -> None:
        self.client_request_api.product_sale()
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем продукт, к которому применена скидка"):
            self.discount_page.locators.PRODUCTS_TAB.click()
            self.discount_page.locators.PRODUCTS.wait_to_have_count(1)
            self.discount_page.locators.PRODUCTS[0].wait_to_have_text(
                test_context.client.inquiry_list[0].product.product_name
            )

        with allure.step("Добавление продукта"):
            self.discount_page.locators.PRODUCT_ADD_BTN.click()
            self.add_discount_form_step_2.PRODUCT_TABLE.select_by_value(
                test_context.client.inquiry_list[1].product.product_name
            )
            self.add_discount_form_step_2.INNER_ACCEPT_BTN.click()

        with allure.step("Проверяем продукты, к которому применена скидка"):
            self.discount_page.locators.PRODUCTS.wait_to_have_count(2)
            self.discount_page.locators.PRODUCTS[0].wait_to_have_text(
                test_context.client.inquiry_list[0].product.product_name
            )
            self.discount_page.locators.PRODUCTS[1].wait_to_have_text(
                test_context.client.inquiry_list[1].product.product_name
            )

    @allure.title("09. Добавление нескольких продуктов в активной скидке")
    @allure.id(676631)
    def test_add_products_to_billing_discount(
        self, create_user_with_agreement_and_account: IndividualClient, base_url: str
    ) -> None:
        products = prepare_inquiries(["mobile", "mobile", "internet"])

        self.client_request_api.product_sale(inquiry=products)
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем продукт, к которому применена скидка"):
            self.discount_page.locators.PRODUCTS_TAB.click()
            self.discount_page.locators.PRODUCTS.wait_to_have_count(1)
            self.discount_page.locators.PRODUCTS[0].wait_to_have_text(
                test_context.client.inquiry_list[0].product.product_name
            )

        with allure.step("Добавление продуктов"):
            self.discount_page.locators.PRODUCT_ADD_BTN.click()
            self.add_discount_form_step_2.PRODUCT_TABLE.select_by_value(
                test_context.client.inquiry_list[1].product.product_name
            )
            self.add_discount_form_step_2.PRODUCT_TABLE.select_by_value(
                test_context.client.inquiry_list[2].product.product_name
            )
            self.add_discount_form_step_2.INNER_ACCEPT_BTN.click()

        with allure.step("Проверяем продукты, к которому применена скидка"):
            self.discount_page.locators.PRODUCTS.wait_to_have_count(3)
            self.discount_page.locators.PRODUCTS[0].wait_to_have_text(
                test_context.client.inquiry_list[0].product.product_name
            )
            self.discount_page.locators.PRODUCTS[1].wait_to_have_text(
                test_context.client.inquiry_list[1].product.product_name
            )
            self.discount_page.locators.PRODUCTS[2].wait_to_have_text(
                test_context.client.inquiry_list[2].product.product_name
            )

    @allure.title("10. Удаление продукта в активной скидке")
    @allure.id(676568)
    def test_delete_product_from_billing_discount(
        self, create_user_with_agreement_and_account: IndividualClient, base_url: str
    ) -> None:
        products = prepare_inquiries(["mobile", "mobile", "internet"])

        self.client_request_api.product_sale(inquiry=products)
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            product=test_context.client.inquiry.product_list,
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем количество продуктов"):
            self.discount_page.locators.PRODUCTS_TAB.click()
            self.discount_page.locators.PRODUCTS.wait_to_have_count(2)

        with allure.step("Удаление продукта"):
            self.discount_page.locators.PRODUCTS[1].click()
            self.discount_page.locators.PRODUCT_DELETE_BTN.click()
            self.discount_page.locators.MODAL_SECOND_BTN.click()

        with allure.step("Проверяем, что осталсь один продукт"):
            self.discount_page.locators.PRODUCTS.wait_to_have_count(1)

    @allure.title("11. Удаление всех продуктов в активной скидке")
    @allure.id(676626)
    def test_delete_all_products_from_billing_discount(
        self, create_user_with_agreement_and_account: IndividualClient, base_url: str
    ) -> None:
        products = prepare_inquiries(["mobile", "mobile", "internet"])

        self.client_request_api.product_sale(inquiry=products)
        self.client_profile.open(
            f"{base_url}customer-hierarchy-management/accounts/{test_context.client.agreements[0].accounts[0].id}/account"
        )
        self.discount_requests_api.add_billing_discount(
            amount=int(self.discount_amount),
            product=test_context.client.inquiry.product_list,
            action_type="Скидка",
            priority=int(self.priority),
        )

        self.client_profile.locators.BURGER_MENU.select_by_value("Финансы > Скидки/доначисления")
        self.discount_page.locators.SELECTED_TAB_TITLE.wait_to_have_text("Скидки/доначисления")
        self.discount_page.refresh_page(wait="domcontentloaded")

        with allure.step("Проверяем, что скидка отображается"):
            self.discount_page.locators.DISCOUNTS.wait_to_have_count(1, timeout=10000)
            self.discount_page.locators.PROPERTIES.wait_to_have_count(6)
            self.discount_page.locators.PROPERTIES[0].wait_to_have_text(self.start_date)
            self.discount_page.locators.PROPERTIES[1].wait_to_have_text(self.end_date)
            self.discount_page.locators.PROPERTIES[2].wait_to_have_text(self.priority)
            self.discount_page.locators.PROPERTIES[3].wait_to_have_text("Admin")
            self.discount_page.locators.PROPERTIES[4].to_contain_text(self.start_date)
            self.discount_page.locators.PROPERTIES[5].wait_to_have_text("—")

        with allure.step("Проверяем количество продуктов"):
            self.discount_page.locators.PRODUCTS_TAB.click()
            self.discount_page.locators.PRODUCTS.wait_to_have_count(2)

        with allure.step("Удаление всех продуктов"):
            self.discount_page.locators.DELETE_ALL_PRODUCTS_BTN.click()
            self.discount_page.locators.MODAL_SECOND_BTN.click()

        with allure.step("Проверяем что удалены все продукты"):
            self.discount_page.locators.PRODUCTS.wait_to_have_count(0)

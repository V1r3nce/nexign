import allure
import pytest

from common.enums.ats import AtsAttributes, PersonalAccountPaymentMethod, TaxScheme
from common.helpers.data_generator import faker
from pages.base_page import BasePage
from pages.nbss.client.client_profile_page import ClientProfilePage
from pages.nbss.personal_account_page import PersonalAccountPage


@pytest.mark.regress
@pytest.mark.nbss_portal
class TestAttributeHistory:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login):
        self.base_page = BasePage()
        self.client_profile_page = ClientProfilePage()
        self.personal_account_page = PersonalAccountPage()

    @allure.title("Просмотр истории изменения атрибутов типа DICTIONARY для ФЛ/ИП")
    @allure.id(933842)
    def test_attribute_history_individual_client(self, create_user_with_agreement_and_account):
        client = create_user_with_agreement_and_account
        new_surname = "Акрапович"
        new_tax_scheme = TaxScheme.non_operational
        with allure.step("Переход в Персональные данные и изменение фамилии и схемы налогообложения"):
            self.client_profile_page.open_client_data_page(client.user_id)
            self.client_profile_page.edit_individual_client(surname=new_surname, tax_scheme=new_tax_scheme)
        with allure.step("Проверка изменений"):
            full_name = client.sur_name + " " + client.first_name + " " + client.patronymic
            new_full_name = new_surname + " " + client.first_name + " " + client.patronymic
            self.client_profile_page.check_attributes_history(
                attributes=[AtsAttributes.full_name, AtsAttributes.surname, AtsAttributes.tax_scheme],
                old_values=[full_name, client.sur_name, client.tax_scheme],
                new_values=[new_full_name, new_surname, new_tax_scheme],
            )

        with allure.step("Переход в Лицевые счета и изменение способа оплаты"):
            payment_method_id = client.agreement.account.rating_type
            match payment_method_id:
                case PersonalAccountPaymentMethod.prepaid.id:
                    payment_method = PersonalAccountPaymentMethod.prepaid
                    new_payment_method = PersonalAccountPaymentMethod.postpaid
                case PersonalAccountPaymentMethod.postpaid.id:
                    payment_method = PersonalAccountPaymentMethod.postpaid
                    new_payment_method = PersonalAccountPaymentMethod.prepaid
                case _:
                    ValueError("Передан неизвестный идентификатор")
            self.personal_account_page.open_personal_account_page(client.agreement.account.id)
            self.personal_account_page.edit_account_payment_method(payment_method=PersonalAccountPaymentMethod.postpaid)
        with allure.step("Проверка изменений"):
            self.client_profile_page.check_attributes_history(
                attributes=[AtsAttributes.payment_method], old_values=[payment_method], new_values=[new_payment_method]
            )

    @allure.title("Просмотр истории изменения атрибутов типа DICTIONARY для ЮЛ")
    @allure.id(933807)
    def test_attribute_history_organization_client(self, create_organization_with_agreement_and_account):
        client = create_organization_with_agreement_and_account
        new_ogrn = faker.ogrn()
        new_tax_scheme = TaxScheme.non_operational
        with allure.step("Переход в Персональные данные и изменение фамилии и схемы налогообложения"):
            self.client_profile_page.open_client_data_page(client.user_id)
            self.client_profile_page.edit_organization_client(ogrn=new_ogrn, tax_scheme=new_tax_scheme)
        with allure.step("Проверка изменений"):
            self.client_profile_page.check_attributes_history(
                attributes=[AtsAttributes.ogrn, AtsAttributes.tax_scheme],
                old_values=[client.ogrn, client.tax_scheme],
                new_values=[new_ogrn, new_tax_scheme],
            )

        with allure.step("Переход в Лицевые счета и изменение способа оплаты"):
            payment_method_id = client.agreement.account.rating_type
            match payment_method_id:
                case PersonalAccountPaymentMethod.prepaid.id:
                    payment_method = PersonalAccountPaymentMethod.prepaid
                    new_payment_method = PersonalAccountPaymentMethod.postpaid
                case PersonalAccountPaymentMethod.postpaid.id:
                    payment_method = PersonalAccountPaymentMethod.postpaid
                    new_payment_method = PersonalAccountPaymentMethod.prepaid
                case _:
                    ValueError("Передан неизвестный идентификатор")
            self.personal_account_page.open_personal_account_page(client.agreements[0].accounts[0].id)
            self.personal_account_page.edit_account_payment_method(payment_method=PersonalAccountPaymentMethod.postpaid)
        with allure.step("Проверка изменений"):
            self.client_profile_page.check_attributes_history(
                attributes=[AtsAttributes.payment_method], old_values=[payment_method], new_values=[new_payment_method]
            )

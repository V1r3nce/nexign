import allure
import pytest

from api.psc_requests.offerings_requests import ProductOfferingRequests
from api.psc_requests.projects_requests import ProjectRequests
from pages.base_page import BasePage
from pages.psc_pages.home_page_psc import HomePscPage
from pages.psc_pages.product_proposal_page import ProductProposalPscPage


@allure.epic("E2E_41_2: Централизованное ведение НСИ (управление ПП. Загрузка ПП через json)")
@allure.suite("E2E_41_2: Централизованное ведение НСИ (управление ПП. Загрузка ПП через json)")
@pytest.mark.extended_regress
@pytest.mark.psc
@pytest.mark.nbss_portal
class TestUploadDownloadOffer:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_pcs) -> None:
        self.base_page = BasePage()
        self.home_page_psc = HomePscPage()
        self.pp_page_psc = ProductProposalPscPage()
        self.offering_api = ProductOfferingRequests()
        self.project_api = ProjectRequests()

    @allure.title("Выгрузка ПП")
    @allure.id(656654)
    def test_upload_offer(self):
        id_offer, name, specification = self.offering_api.export_and_validate_product_offering("Терминал XL")
        with allure.step("Перейти в карточку нужного ПП"):
            self.home_page_psc.locators.PS_FILTER_NAME.fill("Терминал XL")
            self.home_page_psc.locators.PS_NAMES.wait_to_have_count(1)
            self.home_page_psc.locators.PS_NAMES[0].click()
            self.pp_page_psc.locators.MAIN_PARAMETERS_TAB.wait_to_be_enabled()
            self.pp_page_psc.locators.MAIN_PARAMETERS_TAB.click()
            self.pp_page_psc.locators.NAME_PRODUCT_OFFER.wait_to_be_visible()
        with allure.step("Сравнить Название, ID, Спецификации с информацией в экспортированном JSON"):
            assert self.pp_page_psc.locators.NAME_PRODUCT_OFFER.text.strip() == name, (
                f"Название {self.pp_page_psc.locators.NAME_PRODUCT_OFFER.text.strip()} в UI не совпадает с экспортированным {name}"
            )
            assert self.pp_page_psc.locators.ID_PRODUCT_OFFER.text.strip() == str(id_offer), (
                f"ID {self.pp_page_psc.locators.ID_PRODUCT_OFFER.text.strip()} ПП в UI не совпадает с экспортированным {id_offer}"
            )
            assert self.pp_page_psc.locators.NAME_SPECIFICATION.text.strip() == specification, (
                f"Спецификация {self.pp_page_psc.locators.NAME_SPECIFICATION.text.strip()} в UI не совпадает с экспортированной {specification}"
            )

    @allure.title("Загрузка ПП")
    @allure.id(656655)
    def test_download_offer(self):
        with allure.step("Экспорт нужного JSON и его проливка в ПСЦ"):
            id_offer, name, specification = self.offering_api.export_modify_and_import_product_offering(
                "Спутник L Продажа"
            )
            self.project_api.back_project_and_wait_success(
                self.offering_api.get_project_id_by_product_offering_id(id_offer)
            )
            self.project_api.publish_project_and_wait_success(
                self.offering_api.get_project_id_by_product_offering_id(id_offer)
            )
            self.home_page_psc.refresh_page("domcontentloaded")
        with allure.step("Перейти в карточку нужного ПП"):
            self.home_page_psc.locators.PS_FILTER_ID.fill(str(id_offer))
            self.home_page_psc.locators.PS_NAMES.wait_to_have_count(1)
            self.home_page_psc.locators.PS_NAMES[0].click()
            self.pp_page_psc.locators.MAIN_PARAMETERS_TAB.wait_to_be_enabled()
            self.pp_page_psc.locators.MAIN_PARAMETERS_TAB.click()
            self.pp_page_psc.locators.NAME_PRODUCT_OFFER.wait_to_be_visible()
        with allure.step("Сравнить Название, ID, Спецификации с информацией в JSON"):
            assert self.pp_page_psc.locators.NAME_PRODUCT_OFFER.text.strip() == name, (
                f"Название {self.pp_page_psc.locators.NAME_PRODUCT_OFFER.text.strip()} в UI не совпадает с экспортированным {name}"
            )
            assert self.pp_page_psc.locators.ID_PRODUCT_OFFER.text.strip() == str(id_offer), (
                f"ID {self.pp_page_psc.locators.ID_PRODUCT_OFFER.text.strip()} ПП в UI не совпадает с экспортированным {id_offer}"
            )
            assert self.pp_page_psc.locators.NAME_SPECIFICATION.text.strip() == specification, (
                f"Спецификация {self.pp_page_psc.locators.NAME_SPECIFICATION.text.strip()} в UI не совпадает с экспортированной {specification}"
            )

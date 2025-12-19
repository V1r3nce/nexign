import allure
import pytest

from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from pages.locators.rfd_locators.home_element_rfd import CreateElementDirectoryForm
from pages.refdata_pages.events_page_rfd import EventsRfdPage
from pages.refdata_pages.home_page_rfd import HomeRfdPage


@allure.epic("E2E_110 Централизированное управление НСИ")
@allure.suite("E2E_110 Централизированное управление НСИ")
@pytest.mark.refdata
class TestIntegrationRefdata:
    @pytest.fixture(autouse=True)
    def setup(self, stand_login_rfd) -> None:
        self.home_page_rfd = HomeRfdPage()
        self.events_page_rfd = EventsRfdPage()
        self.create_element_directory_form = CreateElementDirectoryForm()

    @allure.title("Добавление валюты")
    @allure.id(616405)
    @allure.link(
        url="confluence.nexign.com/pages/viewpage.action?pageId=683897194",
        name="КР [NBSS] Правила работы со справочниками (Стандартное)",
    )
    @allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=776513158", name="Реестр справочников REFDATA")
    @pytest.mark.regress
    def test_add_currency(self) -> None:
        self.home_page_rfd.locators.SEARCH_CODE_FLD.type_and_press_enter("currencies")
        delay(
            0.5,
            reason="Не успевает подтягивать данные о справчонике, завязаться на какой-либо UI-элемент нет возможности",
        )
        self.home_page_rfd.locators.DIRECTORY[0].wait_to_have_text("currencies")
        self.home_page_rfd.locators.DIRECTORY[0].click()
        self.home_page_rfd.locators.DIRECTORY_INFORMATION.wait_to_be_visible()

        self.home_page_rfd.locators.ELEMENTS_BNT.click()
        self.home_page_rfd.locators.ADD_ELEMENT_DIRECTORY_BTN.click()

        code_element = str(generate_random_number(3))
        self.create_element_directory_form.CODE_FLD.fill(code_element)
        self.home_page_rfd.create_directory_element(element_type="XAU")
        self.create_element_directory_form.CODE_CURRENCIES_FLD.fill("XAU")
        self.create_element_directory_form.DEFAULT_CURRENCIES_FLD.select_by_value("Ложь")
        self.create_element_directory_form.CODE_CURRENCIES_RUS_CLASS_FLD.fill(str(generate_random_number(3)))
        self.create_element_directory_form.SAVE_OK_BTN[0].click()

        self.home_page_rfd.locators.CODE_ELEMENT_CURRENCIES_FLD.type_and_press_enter(code_element)
        self.home_page_rfd.locators.DIRECTORY.to_contain_text(-1, code_element)
        self.home_page_rfd.locators.DIRECTORY.wait_elements_visible(element_index=-1, timeout=4000)
        self.home_page_rfd.locators.DIRECTORY[-1].click()
        self.home_page_rfd.locators.PUBLISH_BTN.element_not_contain_disabled_attribute()
        self.home_page_rfd.locators.PUBLISH_BTN.click()
        self.home_page_rfd.locators.SAVE_OK_BTN.wait_elements_visible(element_index=2, timeout=2000)
        self.home_page_rfd.locators.SAVE_OK_BTN[2].click()

        self.home_page_rfd.locators.LEFT_MENI_ITEM[2].click()

        self.events_page_rfd.locators.EVENTS_TAB[2].click()

        self.events_page_rfd.locators.CONSUMER_CODE_FLD.type_and_press_enter("billing")
        delay(0.2, reason="Не нажимает на событие без этого ожидания, методы ожидания не работают")
        self.events_page_rfd.locators.EVENTS[0].click(force=True)
        # TO DO на данном этапе у события статус ERROR, выяснить на кого заводить баг
        self.events_page_rfd.check_attribute_event(attribute="referenceConsumerId", status="billing")
        self.events_page_rfd.check_attribute_event(attribute="deliveryStatus", status="ERROR")

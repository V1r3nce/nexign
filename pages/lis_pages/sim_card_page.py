import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.locators.lis_locators.sim_cards_elements import SimCardElementsLis


class SimCardsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.sim_cards_elements = SimCardElementsLis(page)

    @allure.step("Проверить элементы Поиск")
    def check_search_elements(self):
        self.sim_cards_elements.IMSI_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.ICC_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.MSISDN_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.PIN1_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.PIN2_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.STATE_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.STATUS_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.PUK1_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.PUK2_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.EXPIRATION_DATE_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.ACC_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.BBB_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.CHOSEN_COMMUTATOR_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.PROJECT_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.ESN_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.CHOSEN_TYPE_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.MEMORY_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.UNIT_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.LINK_POOL_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.MAP_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.BLOCKING_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.BILLING_LINK_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.AGENT_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.TARIFF_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.TECH_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.SEGMENT_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.REGISTRY_DATE_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.EID_INPUT.wait_to_be_enabled()
        self.sim_cards_elements.SUPPLIER_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.FILTER_SEARCH_BTN.wait_to_be_visible()
        self.sim_cards_elements.CLEAR_FILTER_BTN.wait_to_be_visible()
        self.sim_cards_elements.CHOOSE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()
        self.sim_cards_elements.SAVE_SEARCH_TEMPLATE_BTN.wait_to_be_visible()

    @allure.step("Получить новый вариант Дилер для первой строки")
    def get_new_seller_name_for_first_line(self):
        if "NEXIGN Service Store" in self.sim_cards_elements.SELLER_FIELDS[0].text:
            return "NEXIGN технологический склад"
        else:
            return "NEXIGN Service Store"

    @allure.step("Выбрать новый вариант Дилер")
    def choose_new_seller_name(self, seller: str):
        if seller == "NEXIGN технологический склад":
            self.sim_cards_elements.SELLER_TECH_WAREHOUSE.hover()
            self.sim_cards_elements.SELLER_TECH_WAREHOUSE.click()
        elif seller == "NEXIGN Service Store":
            self.sim_cards_elements.SELLER_SERVICE_STORE.hover()
            self.sim_cards_elements.SELLER_SERVICE_STORE.click()

    @allure.step("Найти и выбрать строку со статусами 'Свободен', 'Не связана', блокировка 'Не установлена'")
    def find_useful_line_free_not_linked_not_blocked(self):
        for item in range(100):
            self.sim_cards_elements.NUMBERS_STATUSES.click(item)
            self.page.mouse.wheel(0, 100)
            if ("Свободен" in self.sim_cards_elements.NUMBERS_STATUSES[item].text and
                    "Не связана" in self.sim_cards_elements.NUMBERS_STATES[item].text and
                    "Не установлена" in self.sim_cards_elements.NUMBERS_BLOCK_STATUS[item].text):
                self.sim_cards_elements.LINE_CHECKBOXES.click(item)
                break
            elif item == 100:
                raise AssertionError("В первых 100 строках нет подходящей SIM со статусами 'Свободен', 'Не связана',"
                                     " блокировка 'Не установлена'")

    @allure.step("Получить новый вариант коммутатора для первой строки")
    def get_new_commutator_name_for_first_line(self):
        self.sim_cards_elements.NUMBERS_COMMUTATOR.to_contain_text(0, "Коммутатор")
        if "Коммутатор_DEF" in self.sim_cards_elements.NUMBERS_COMMUTATOR[0].text:
            return "Коммутатор_ABC"
        else:
            return "Коммутатор_DEF"

import allure
import pytest

from common.helpers.data_generator import faker, generate_random_number
from models.client import OrganizationClient
from models.context import test_context
from pages.nbss.client.client_profile_page import ClientProfilePage

ADDRESS_OBJECT_MATRIX = [
    pytest.param("Город", "Город", "", "Аллея", "Корпус", True, id="1"),
    pytest.param("Город", "", "Муниципальный район", "Остров", "Литера", True, id="2"),
    pytest.param("Область", "Поселок", "", "Шоссе", "Сооружение", True, id="3"),
    pytest.param("Область", "Село", "", "Улица", "Корпус", False, id="4"),
    pytest.param("Округ", "Город", "", "Остров", "Литера", True, id="5"),
    pytest.param("Округ", "", "Муниципальный район", "Аллея", "Сооружение", False, id="6"),
    pytest.param("Край", "Поселок", "", "Улица", "Корпус", False, id="7"),
    pytest.param("Край", "Село", "", "Шоссе", "Литера", False, id="8"),
]


@allure.epic("E2E_22 Управление адресной информацией")
@allure.suite("E2E_22 Управление адресной информацией")
@allure.testcase(url="https://allure.nexign.com/project/313/test-cases/913334", name="913334")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=613646886", name="Работа со справочником в LAM")
@allure.link(url="confluence.nexign.com/pages/viewpage.action?pageId=873270641", name="Работа со справочником в LAM")
@pytest.mark.regress
@pytest.mark.nbss_portal
class TestActualAddressObjectTypes:
    @pytest.fixture(autouse=True)
    def setup(self, nexign_stand_login, create_organization: OrganizationClient) -> None:
        self.client_profile_page = ClientProfilePage()
        self.create_address_form = self.client_profile_page.create_address_form
        self.address_type = "Фактический адрес"
        self.country = "Россия"

    @allure.title(
        "Проверка возможности использования только актуальных адресных типов объектов. "
        "Регион: {region_type}, Район/Город: {city_type}{area_type}, Тип улицы: {street_type}, "
        "Дополнительный тип дома: {additional_house_type}"
    )
    @allure.id(913334)
    @pytest.mark.parametrize(
        "region_type, city_type, area_type, street_type, additional_house_type, with_apartment",
        ADDRESS_OBJECT_MATRIX,
    )
    def test_only_actual_address_object_types(
        self,
        region_type: str,
        city_type: str,
        area_type: str,
        street_type: str,
        additional_house_type: str,
        with_apartment: bool,
    ) -> None:
        with allure.step("В Карточке клиента перейти на вкладку 'Адреса' и кликнуть на кнопку 'Добавить'"):
            self.client_profile_page.open_client_addresses_page(test_context.client.user_id)

        with allure.step("Выбрать 'Тип адреса' и в поле 'Адрес' выбрать 'Добавить адрес в справочник'"):
            self.client_profile_page.open_add_address_form(address_type=self.address_type)
            self.create_address_form.TITLE.to_contain_text("Создание нового адреса")

        with allure.step(f"Выбрать тип адресного объекта 'Страна' и Наименование '{self.country}', применить"):
            self.client_profile_page.fill_country_attribute(self.country)

        with allure.step("Добавить адресные объекты матрицы, выбрав требуемые типы адресных объектов"):
            self.client_profile_page.fill_region_attribute(
                faker.city_name(), address_object_exists=False, region_type=region_type
            )
            if area_type:
                self.client_profile_page.fill_area_attribute(faker.city_name(), area_type=area_type)
            else:
                self.client_profile_page.fill_city_attribute(
                    faker.city_name(), address_object_exists=False, city_type=city_type
                )
            self.client_profile_page.fill_street_attribute(
                faker.street_title(), address_object_exists=False, street_type=street_type
            )
            self.client_profile_page.fill_building_number_attribute(
                generate_random_number(3), additional_house_type=additional_house_type
            )
            if with_apartment:
                self.client_profile_page.fill_flat_number_attribute(generate_random_number(2))

from dataclasses import dataclass
from pathlib import Path

import pytest

from api.lis_requests.phone_numbers import PhoneNumbersRequests
from api.lis_requests.sim_cards import SimCardsRequests
from common.helpers.data_generator import generate_random_number
from common.helpers.time_helpers import delay
from models.client import (
    EntrepreneurClient,
    IndividualClient,
    OrganizationClient,
    generate_entrepreneur_client,
    generate_individual_client,
    generate_organization_client,
)
from models.context import test_context
from pages.lis_pages.sim_card_page import SimCardsPage
from pages.lis_pages.sim_card_shipment_page import SimCardsShipmentPage


@dataclass
class CreatedImsis:
    imsi_1: str
    imsi_2: str
    new_sims_file_path: Path
    ship_sims_file_path: Path


@pytest.fixture
def add_two_imsi_free_shipped():
    """Добавить 2 новых IMSI со статусом "Свободен" и в состоянии "Получена" """
    sim_requests = SimCardsRequests()
    sims = sim_requests.get_sim_card_list(sim_sort="-IMSI")
    sims_data = sim_requests.get_sim_cards_data(sims)
    last_sims_imsi, last_sims_icc = (int(sims_data[0].imsi), int(sims_data[0].icc))
    file_name = f"load_sim_f{generate_random_number(2)}.txt"
    new_sims_file_path = SimCardsPage.create_txt_file_to_upload_sim(
        file_name, [str(last_sims_imsi + 1), str(last_sims_imsi + 2)], [str(last_sims_icc + 1), str(last_sims_icc + 2)]
    )
    sim_requests.upload_sims_set_to_use_by_api(new_sims_file_path)
    delay(0.5, reason="Для корректного выполнения API запроса")
    file_shipment_name = f"shipment_imsis{generate_random_number(2)}.csv"
    ship_sims_file_path = SimCardsShipmentPage.create_csv_file_to_upload_sim_shipment(
        file_shipment_name, [str(last_sims_imsi + 1), str(last_sims_imsi + 2)]
    )
    created_imsi = CreatedImsis(
        str(last_sims_imsi + 1), str(last_sims_imsi + 2), new_sims_file_path, ship_sims_file_path
    )
    return created_imsi


@pytest.fixture
def add_two_msisdn_free_and_open_for_use() -> tuple[str, str]:
    """Добавить 2 новых MSISDN со статусом "Свободен" и в состоянии "Открыт для использования" """
    phone_numbers = PhoneNumbersRequests()
    phones = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
    def_data = phone_numbers.get_numbers_data(phones)
    new_number = str(int(def_data[0].MSISDN) + 1)
    new_number_2 = str(int(def_data[0].MSISDN) + 2)
    phone_numbers.add_phone_numbers(new_number, "2")
    delay(0.5, reason="Время для корректного выполнения запросов")
    phones_2 = phone_numbers.get_phone_numbers(num_sort="-MSISDN")
    def_data_2 = phone_numbers.get_numbers_data(phones_2)
    phone_numbers.set_phone_numbers_in_use([def_data_2[0].phone_number_id, def_data_2[1].phone_number_id])
    return new_number, new_number_2


@pytest.fixture()
def get_allure_id(request: pytest.FixtureRequest) -> str:
    """Возвращает id теста из маркера allure.id, если он есть.
    Если по какой-то причине маркеров несколько, возвращается только первый."""
    allure_id = ""
    allure_markers = [marker for marker in request.node.own_markers if marker.kwargs.get("label_type") == "as_id"]
    if allure_markers:
        allure_id = allure_markers[0].args[0]
        test_context.allure_id = allure_id
    return allure_id


@pytest.fixture()
def individual_user_data(get_allure_id) -> IndividualClient:
    return generate_individual_client()


@pytest.fixture()
def organization_user_data(get_allure_id) -> OrganizationClient:
    return generate_organization_client()


@pytest.fixture()
def entrepreneur_user_data(get_allure_id) -> EntrepreneurClient:
    return generate_entrepreneur_client()

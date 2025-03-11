import random
from playwright.sync_api import APIRequestContext

from common.helpers.data_generator import generate_random_ip

def generate_ip_addresses(api_request_auth_context: APIRequestContext, base_url_api: str, ip_count: int) -> str | list:
    """Cоздает в LIS Ip-адрес и возвращает его в виде строки
    
    :param ip_count: Кол-во создаваемых IP-адресов
    :returm: str (если ip_count = 1) или list (если ip_count > 1)
    """
    request_context = api_request_auth_context
    headers = {"Content-Type": "application/json"}

    ip_base = generate_random_ip(3)
    start_knot = random.randint(0, 250)
    end_knot = start_knot + (ip_count - 1)
    ip_list = [f"{ip_base}.{start_knot + i}" for i in range(ip_count)]

    payload = {
        "accessPointId": 100000, 
        "startIPAddress": ip_list[0], 
        "endIPAddress": ip_list[-1],
        "serviceProviderCode":"NEXIGN",
        "allowMixed": False
    }
    
    response = request_context.post(url=f"{base_url_api}/ps/v1/logicalResources/private/IPAddresses/generationBulkAsync",
                                    headers=headers, data=payload)
    
    assert response.status == 204, (
            f"Не выполнен запрос на создание нового(-ых) IP-адреса в LIS.\n"
            f"Status: {response.status}\n"
            f"Message: {response.json().get('userMessage', response.text())}"
        )
    
    return ip_list[0] if ip_count == 1 else ip_list
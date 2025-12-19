import allure

from common.helpers.checker import check_that
from common.helpers.string_helper import clean_text_from_ansi
from common.helpers.time_helpers import delay
from ssh.exceptions import SSHNWMProductOfferingNotFound, SSHNWMTariffsNotReloaded
from ssh.requests.ssh_base import SSHBaseRequests


class SSHNWMRequests(SSHBaseRequests):
    """
    Класс для работы с сервером, на котором стоит NWM, через SSH.
    Используется в связке с фикстурой create_nwm_ssh_connection.
    Пример использования: в setup тестового класса "self.ssh_requests = create_nwm_ssh_connection" и потом уже у возвращенного инстанса вызывать методы данного класса
    """

    def __init__(self) -> None:
        super().__init__("nwm_ocs")
        self.telnet_ports = {"brt": 13823, "recurring_charge": 4423, "hrs_rt": 1725, "subs_be": 6623}
        self.component_cmds = {"default": "reload tariffs", "subs_be": "refdata reload"}

    @allure.step("SSH: Перезагрузка компонента nwm")
    def _reload_component(self, component: str) -> None:
        """
        Внутренний метод для перезагрузки компонента nwm
        :param component: компонент, который нужно перезагрузить
        """
        cmds = [f"telnet 0 {self.telnet_ports[component]}", "", "q\n"]
        cmds[1] = (
            f"{self.component_cmds[component] if component in self.component_cmds else self.component_cmds['default']}\n"
        )
        result, err = self.process_multiple_cmd(cmds)
        check_that(
            lambda: "reload command enqueued" in result if component != "subs_be" else "loadDuration" in result,
            SSHNWMTariffsNotReloaded,
            "Не удалось запустить перечитку тарифов",
        )

    @allure.step("SSH: Поиск продуктового предложения по id и названию")
    def check_product_offering_by_id(
        self, product_offering_id: int, product_offering_name: str, is_main_po: bool
    ) -> None:
        """
        Метод для проверки наличия продуктового предложения в тарификационном контуре
        :param product_offering_id: id ПП
        :param product_offering_name: название ПП
        :param is_main_po: флаг для указания является ли ПП основным
        """
        cmds = [f"telnet 0 {self.telnet_ports['brt']}", "", "q\n"]
        if is_main_po:
            cmds[1] = f"print rate plan {product_offering_id}\n"
        else:
            cmds[1] = f"print packet {product_offering_id}\n"
        result, err = self.process_multiple_cmd(cmds)
        check_that(
            lambda: product_offering_name in result,
            SSHNWMProductOfferingNotFound,
            "Не удалось найти продуктовое предложение",
        )

    @allure.step("SSH: Перезагрузка тарификационной части nwm_ocs")
    def reload_ocs_tariffs(self) -> None:
        """
        Метод для перезагрузки компонентов тарификационной части nwm. Требуется для появления возможности подключить новый ПП
        """
        for component in self.telnet_ports:
            self._reload_component(component)

    @allure.step("SSH: Перезагрузка тарификационной части nwm_ocs и проверка наличия продуктового предложения")
    def reload_ocs_and_check_product_offering(
        self, product_offering_id: int, product_offering_name: str, is_main_po: bool = True
    ) -> None:
        """
        Метод для перезагрузки компонентов тарификационной части nwm и проверки проявления ПП
        :param product_offering_id: id ПП
        :param product_offering_name: название ПП
        :param is_main_po: флаг для указания является ли ПП основным
        """
        self.reload_ocs_tariffs()
        delay(10, "Ожидание вычитывания продуктового предложения")
        self.check_product_offering_by_id(product_offering_id, product_offering_name, is_main_po)

    def check_po_internet_price(
        self, product_offering_id: int, desired_amount: str, is_main_po: bool = True, is_volume: bool = True
    ) -> None:
        """
        Метод для проверки объема интернета у продуктового предложения
        :param product_offering_id: id ПП
        :param desired_amount: нужное значение
        :param is_main_po: флаг для указания является ли ПП основным
        :param is_volume: флаг для указания является ли цена ценой объемом
        """
        cmds = [f"telnet 0 {self.telnet_ports['brt']}", "", "q\n"]
        if is_main_po:
            cmds[1] = f"print rate plan {product_offering_id}\n"
        else:
            cmds[1] = f"print packet {product_offering_id}\n"
        result, err = self.process_multiple_cmd(cmds)
        if is_volume:
            check_str = f'"amountLimit": {{"amount":{desired_amount},"units":"MB"}}'
        else:
            check_str = f'"price": {{"unit":"RUB","value":{desired_amount}}}'
        check_that(
            lambda: check_str in clean_text_from_ansi(result),
            SSHNWMProductOfferingNotFound,
            "Не удалось найти продуктовое предложение",
        )

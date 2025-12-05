import allure

from common.helpers.checker import check_that
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
        self.telnet_ports = {"brt": 13823, "recurring_charge": 4423, "hrs_rt": 1725}

    @allure.step("SSH: Перезагрузка компонента nwm")
    def _reload_component(self, port: int) -> None:
        """
        Внутренний метод для перезагрузки компонента nwm
        :param port: номер порта telnet компонента, который нужно перезагрузить
        """
        cmds = [f"telnet 0 {port}", "reload tariffs\n", "q\n"]
        result, err = self.process_multiple_cmd(cmds)
        check_that(
            lambda: "reload command enqueued" in result,
            SSHNWMTariffsNotReloaded,
            "Не удалось запустить перечитку тарифов",
        )

    @allure.step("SSH: Поиск продуктового предложения по id и названию")
    def check_product_offering_by_id(self, product_offering_id: int, product_offering_name: str) -> None:
        """
        Метод для проверки наличия продуктового предложения в тарификационном контуре
        :param product_offering_id: id ПП
        :param product_offering_name: название ПП
        """
        cmds = [f"telnet 0 {self.telnet_ports['brt']}", f"print rate plan {product_offering_id}\n", "q\n"]
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
            self._reload_component(self.telnet_ports[component])

    @allure.step("SSH: Перезагрузка тарификационной части nwm_ocs и проверка наличия продуктового предложения")
    def reload_ocs_and_check_product_offering(self, product_offering_id: int, product_offering_name: str) -> None:
        """
        Метод для перезагрузки компонентов тарификационной части nwm и проверки проявления ПП
        :param product_offering_id: id ПП
        :param product_offering_name: название ПП
        """
        self.reload_ocs_tariffs()
        delay(3, "Ожидание вычитывания продуктового предложения")
        self.check_product_offering_by_id(product_offering_id, product_offering_name)

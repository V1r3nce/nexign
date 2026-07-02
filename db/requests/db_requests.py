from datetime import datetime, timedelta

import allure

from common.helpers.checker import assert_that
from db.requests.db_base import DBBase


class OMSDBRequests(DBBase):
    """
    Класс для работы с БД OMS.
    Используется в связке с фикстурой create_oms_db_connection.
    Пример использования: в setup тестового класса "self.db = create_oms_db_connection" и потом уже у возвращенного инстанса вызывать методы данного класса
    """

    def __init__(self) -> None:
        super().__init__("oms")
        self.product_management_ortw_id = 7000
        self.service_connect_order_ortw_id = 7005
        self.change_management_ortw_id = 15000
        self.service_disconnect_order_ortw_id = 17000
        self.service_change_order_ortw_id = 21600
        self.activator_order_ortw_id = 20000

    @allure.step("DB: Получение nbssProductManagement из БД OMS")
    def get_main_order_id(self, inquiry_id: int, ortw_id: int = None) -> int:
        """
        Метод для получения заказа со сценарием nbssProductManagement
        :param inquiry_id: id заявки на управление продуктами
        :param ortw_id: id типа заказа
        :return: id заказа nbssProductManagement
        """
        res = self.process_select(
            f"select o.ordr_id from oms.orders_v2 o where o.entity_id = '{inquiry_id}' and o.parent_ordr_id is null and o.ortw_ortw_id = '{ortw_id or self.product_management_ortw_id}';"
        )
        try:
            return int(res[0][0])
        except IndexError:
            raise AssertionError("DB: Не получено ни одного заказа")

    @allure.step("DB: Получение order_id по идентификатору и типу его родительского заказа")
    def get_order_id_by_ortw_id(self, parent_order_id: int, ortw_ortw_id: int) -> list:
        """
        Метод для получения списка заявок с id родительского заказа parent_order_id и id типа искомой заявки ortw_ortw_id
        :param parent_order_id: id родительского заказа
        :param ortw_ortw_id: id типа искомой заявки
        :return: список id заявок подходящих под условия выше
        """
        res = []
        for order in self.process_select(
            f"select o.ordr_id from oms.orders_v2 o where o.parent_ordr_id = '{parent_order_id}' and o.ortw_ortw_id = '{ortw_ortw_id}';"
        ):
            if len(order) == 1:
                res.append(int(order[0]))
        return res

    @allure.step("DB: Получение дочернего nbssServiceActivator заказа из БД OMS")
    def get_sam_service_order_id(self, inquiry_id: int, order_type: str) -> int | None:
        """
        Метод для получения id заказа со сценарием nbssServiceActivator
        :param inquiry_id: id заявки на управление продуктами
        :param order_type: тип заявки. Возможные варианты connect, disconnect, change
        :return: id заявки nbssServiceActivator
        """
        match order_type:
            case "connect" | "disconnect":
                ortw_id = (
                    self.service_connect_order_ortw_id
                    if order_type == "connect"
                    else self.service_disconnect_order_ortw_id
                )
                main_order_id = self.get_main_order_id(inquiry_id)
                service_step_id = self.get_order_id_by_ortw_id(main_order_id, ortw_id)
                activator_ids = self.get_order_id_by_ortw_id(service_step_id[0], self.activator_order_ortw_id)
            case "change":
                main_order_id = self.get_main_order_id(inquiry_id, self.change_management_ortw_id)
                activator_ids = self.get_order_id_by_ortw_id(main_order_id, self.activator_order_ortw_id)
            case _:
                raise ValueError(f"Недопустимый тип order_type: {order_type}")

        return activator_ids[0] if activator_ids and len(activator_ids) == 1 else None

    @allure.step("DB: Проверка наличия статуса DONE у заявки")
    def check_order_success_status(self, order_id: int) -> None:
        """
        Метод для проверки успешного выполнения заявки
        :param order_id: id заявки
        """
        res = self.process_select(f"select o.orst_orst_id from oms.orders_v2 o where o.ordr_id = '{order_id}';")
        assert_that(lambda: int(res[0][0]) == 3, "DB: Заявка не завершилась успешно")


class LisDBRequests(DBBase):
    """
    Класс для работы с БД LIS.
    Используется в связке с фикстурой create_lis_db_connection.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__("lis")

    @allure.step("DB: Поиск безопасного номера (Свободен + Открыт для использования) → MSISDN")
    def get_safe_number_candidate(self) -> str | None:
        """
        Ищет один номер со статусом 'Свободен' и состоянием 'Открыт для использования'.

        :return: MSISDN подходящего номера строкой, либо None если такой номер не найден.
        """
        sql = """
            SELECT msisdn
            FROM lis.lis_numbers
            WHERE lsts_lsts_id = 1
              AND nstt_nstt_id = 2
            LIMIT 1;
        """

        rows = self.process_select(sql, is_empty=True)
        if not rows:
            return None
        return str(rows[0][0])

    @allure.step("DB: Перевод номера {msisdn} в карантин (nstt=4, isolation_end_date)")
    def put_number_into_quarantine(self, msisdn: str, iso_end: datetime | None = None) -> None:
        """
        Переводит указанный номер в состояние 'Освобожден' (карантин) и устанавливает дату окончания карантина.

        :param msisdn: Номер (MSISDN), который нужно перевести в карантин.
        :param iso_end: Дата окончания карантина (дата без времени). Если не задано — ставится завтрашний день 00:00.
        :return: None
        """
        if iso_end is None:
            iso_end = datetime.now().date() + timedelta(days=1)

        iso_end_str = f"{iso_end} 00:00:00"

        sql = f"""
            UPDATE lis.lis_numbers
               SET nstt_nstt_id = 4,
                   isolation_end_date = '{iso_end_str}'
             WHERE msisdn = '{msisdn}';
        """

        self.process_changes(sql)

    @allure.step("DB: Создание карантинного номера → вернуть MSISDN")
    def make_quarantine_number(self, iso_end: datetime | None = None) -> str:
        """
        Находит свободный номер (Свободен + Открыт для использования), переводит его в карантин и возвращает MSISDN.

        :param iso_end: Дата окончания карантина (дата без времени). Если не задано — ставится завтрашний день 00:00.
        :return: MSISDN переведённого в карантин номера.
        :raises AssertionError: Если не найден ни один подходящий номер.
        """
        msisdn = self.get_safe_number_candidate()
        if msisdn is None:
            raise AssertionError("Нет номера со статусом 'Свободен' и состоянием 'Открыт для использования'.")

        self.put_number_into_quarantine(msisdn, iso_end)
        return msisdn


class UDBRequests(DBBase):
    """
    Класс для работы с БД UDB.
    Используется в связке с фикстурой create_udb_connection.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__("udb")

    @allure.step("")
    def discount_template_compare(self) -> str | None:
        """
        Отправляет запрос.

        :return: MSISDN подходящего номера строкой, либо None если такой номер не найден.
        """
        sql = """
            SELECT number_history, dbdt_id, navi_date, navi_user, value, action_type
            FROM discount_templates
        """

        rows = self.process_select(sql, is_empty=True)
        if not rows:
            return None
        return str(rows[0][0])


class UniblpDBRequests(DBBase):
    """
    Класс для работы с БД Uniblp.
    Используется в связке с фикстурой create_uniblp_db_connection.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__("uniblp")

    @allure.step("DB: Изменения значений в app_parameters")
    def change_app_parameters(
        self, param_name: str = None, param_value_string: str = "", param_value_number: int = 0
    ) -> None:
        """
        Изменяет параметры в app_parameters

        :param param_name: Название параметра.
        :param param_value_string: Изменяемый параметр в поле value_string.
        :param param_value_number: Название параметра в поле value_number.
        """
        sql = f"""
                                UPDATE uniblp.app_parameters
                                   SET value_string = '{param_value_string}',
                                       value_number =  {param_value_number}
                                WHERE name = '{param_name}';
        """
        self.process_changes(sql)

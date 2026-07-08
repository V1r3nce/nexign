from datetime import datetime, timedelta

import allure

from common.enums.billing import DiscountTemplateAction
from common.helpers.checker import assert_that, wait_that
from db.requests.db_base import DBBase, allure_attach_select_result


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


class BillingDBRequests(DBBase):
    """
    Класс для работы с БД UDB (в standhelper — "DB Billing (postgres)").
    Используется в связке с фикстурой create_udb_connection.
    """

    def __init__(
        self,
    ) -> None:
        super().__init__("billing")

    @allure.step("DB: Получение истории шаблонов биллинговых скидок")
    @allure_attach_select_result("История шаблонов биллинговых скидок")
    def get_discount_templates_history(self, dbdt_id: int | None = None) -> list:
        """
        Возвращает историю изменений шаблонов биллинговых скидок.

        :param dbdt_id: id шаблона. Если не задан — возвращается история по всем шаблонам.
        :return: список кортежей (number_history, dbdt_id, navi_date, navi_user, value, action_type).
        """
        where = f"WHERE dbdt_id = {dbdt_id}" if dbdt_id is not None else ""
        sql = f"""
            SELECT number_history, dbdt_id, navi_date, navi_user, value, action_type
            FROM dsc_bill_discount_templates_history
            {where}
            ORDER BY dbdt_id, number_history;
        """
        return self.process_select(sql, is_empty=True)

    @allure.step("DB: Поиск id шаблона биллинговой скидки по названию '{template_name}'")
    def get_template_id_by_name(self, template_name: str, timeout: int = 30) -> int:
        """
        Ищет id шаблона биллинговой скидки по названию (любая локализация) в истории шаблонов.
        Ожидает появления записи в БД в течение timeout секунд.

        :param template_name: название шаблона (name_ru или name_en).
        :param timeout: время ожидания появления шаблона в БД, секунды.
        :return: dbdt_id найденного шаблона.
        :raises AssertionError: если за timeout секунд шаблон не найден или найдено больше одного.
        """
        sql = f"""
            SELECT DISTINCT h.dbdt_id
            FROM dsc_bill_discount_templates_history h
            WHERE h.value IS NOT NULL
              AND EXISTS (
                  SELECT 1
                  FROM jsonb_array_elements(h.value::jsonb -> 'name') AS n
                  WHERE n ->> 'value' = '{template_name}'
              );
        """
        rows = []

        def template_found() -> bool:
            nonlocal rows
            rows = self.process_select(sql, is_empty=True)
            return len(rows) == 1

        wait_that(
            condition=template_found,
            exception=AssertionError,
            message=lambda: f"DB: за {timeout} сек не появился ровно один шаблон с названием '{template_name}', "
            f"найдено: {len(rows)}",
            timeout=timeout,
            sleep_seconds=2.5,
        )
        return int(rows[0][0])

    @allure.step("DB: Получение последней записи истории шаблона {dbdt_id}")
    def get_last_history_entry(self, dbdt_id: int) -> dict | None:
        """
        Возвращает запись истории шаблона с максимальным number_history.

        :param dbdt_id: id шаблона биллинговой скидки.
        :return: словарь с полями number_history, dbdt_id, navi_date, navi_user, value, action_type,
                 либо None, если записей по шаблону нет.
        """
        sql = f"""
            SELECT number_history, dbdt_id, navi_date, navi_user, value, action_type
            FROM dsc_bill_discount_templates_history
            WHERE dbdt_id = {dbdt_id}
            ORDER BY number_history DESC
            LIMIT 1;
        """
        rows = self.process_select(sql, is_empty=True)
        if not rows:
            return None
        number_history, dbdt, navi_date, navi_user, value, action_type = rows[0]
        return {
            "number_history": int(number_history),
            "dbdt_id": int(dbdt),
            "navi_date": navi_date,
            "navi_user": navi_user,
            "value": value,
            "action_type": action_type,
        }

    @allure.step("DB: Проверка истории шаблона {dbdt_id}: action_type={action_type}, number_history={number_history}")
    def check_template_history(
        self, dbdt_id: int, action_type: DiscountTemplateAction, number_history: int, timeout: int = 30
    ) -> dict:
        """
        Проверяет, что последняя запись истории шаблона имеет ожидаемые action_type и number_history.
        Ожидает появления записи в БД в течение timeout секунд.

        :param dbdt_id: id шаблона биллинговой скидки.
        :param action_type: ожидаемый тип действия (DiscountTemplateAction).
        :param number_history: ожидаемый порядковый номер версии.
        :param timeout: время ожидания записи в БД, секунды.
        :return: последняя запись истории шаблона (см. get_last_history_entry).
        """
        entry: dict | None = None

        def history_matches() -> bool:
            nonlocal entry
            entry = self.get_last_history_entry(dbdt_id)
            return (
                entry is not None
                and entry["action_type"] == action_type.value
                and entry["number_history"] == number_history
            )

        assert_that(
            condition=history_matches,
            message=lambda: f"DB: последняя запись истории шаблона {dbdt_id} не соответствует ожиданию: "
            f"ожидалось action_type={action_type.value}, number_history={number_history}, получено: {entry}",
            timeout=timeout,
            sleep_seconds=2.5,
        )
        assert entry is not None
        return entry

    @allure.step("DB: Сравнение версий шаблона биллинговой скидки")
    @allure_attach_select_result("Сравнение версий шаблонов биллинговых скидок")
    def discount_template_compare(self, dbdt_id: int | None = None) -> list:
        """
        Выполняет скрипт сравнения версий шаблонов (DSC_Discount_template_compare) и возвращает построчный diff.

        :param dbdt_id: id шаблона. Если не задан — сравнение по всем шаблонам.
        :return: список кортежей (dbdt_id, action_type, old_version, new_version, field_name, was, became, navi_date).
        """
        where = f"WHERE dbdt_id = {dbdt_id}" if dbdt_id is not None else ""
        sql = f"""
            WITH versions AS (
                SELECT
                    dbdt_id,
                    number_history,
                    navi_date,
                    navi_user,
                    action_type,
                    value,
                    value::jsonb AS js,

                    LAG(value::jsonb) OVER (
                        PARTITION BY dbdt_id
                        ORDER BY number_history
                    ) AS prev_js,

                    LAG(number_history) OVER (
                        PARTITION BY dbdt_id
                        ORDER BY number_history
                    ) AS prev_history,

                    LAG(navi_user) OVER (
                        PARTITION BY dbdt_id
                        ORDER BY number_history
                    ) AS prev_navi_user

                FROM dsc_bill_discount_templates_history
                {where}
            ),

            diff AS (

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history AS old_version,
                    number_history AS new_version,
                    NULL::text  AS field_name,
                    NULL::text  AS old_value,
                    value  AS new_value,
                    navi_date
                FROM versions
                WHERE action_type = 'DELETE' or action_type = 'CREATE'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'navi_user',
                    prev_navi_user,
                    navi_user,
                    navi_date
                FROM versions
                WHERE prev_history IS NOT NULL
                  AND NOT (action_type = 'DELETE')
                  AND prev_navi_user IS DISTINCT FROM navi_user

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'name_ru',
                    prev_js #>> '{{name,0,value}}',
                    js #>> '{{name,0,value}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{name,0,value}}'
                      IS DISTINCT FROM
                      js #>> '{{name,0,value}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'startDateTime',
                    prev_js #>> '{{validFor,startDateTime}}',
                    js #>> '{{validFor,startDateTime}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{validFor,startDateTime}}'
                      IS DISTINCT FROM
                      js #>> '{{validFor,startDateTime}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'endDateTime',
                    prev_js #>> '{{validFor,endDateTime}}',
                    js #>> '{{validFor,endDateTime}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{validFor,endDateTime}}'
                      IS DISTINCT FROM
                      js #>> '{{validFor,endDateTime}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'status',
                    prev_js #>> '{{billingDiscountTemplateStatus,name,0,value}}',
                    js #>> '{{billingDiscountTemplateStatus,name,0,value}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{billingDiscountTemplateStatus,name,0,value}}'
                      IS DISTINCT FROM
                      js #>> '{{billingDiscountTemplateStatus,name,0,value}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'discountActionType',
                    prev_js #>> '{{discountActionType,name,0,value}}',
                    js #>> '{{discountActionType,name,0,value}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{discountActionType,name,0,value}}'
                      IS DISTINCT FROM
                      js #>> '{{discountActionType,name,0,value}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'priority',
                    prev_js #>> '{{billingDiscountTemplateActions,0,priority}}',
                    js #>> '{{billingDiscountTemplateActions,0,priority}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{billingDiscountTemplateActions,0,priority}}'
                      IS DISTINCT FROM
                      js #>> '{{billingDiscountTemplateActions,0,priority}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'discountThreshold',
                    prev_js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountThreshold}}',
                    js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountThreshold}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountThreshold}}'
                      IS DISTINCT FROM
                      js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountThreshold}}'

                UNION ALL

                SELECT
                    dbdt_id,
                    action_type,
                    prev_history,
                    number_history,
                    'discountValuePercentage',
                    prev_js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountValuePercentage}}',
                    js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountValuePercentage}}',
                    navi_date
                FROM versions
                WHERE prev_js IS NOT NULL
                  AND NOT (action_type = 'DELETE' AND value IS NULL)
                  AND prev_js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountValuePercentage}}'
                      IS DISTINCT FROM
                      js #>> '{{billingDiscountTemplateActions,0,billingDiscountActionParameters,discountValuePercentage}}'
            )

            SELECT
                dbdt_id,
                action_type,
                old_version,
                new_version,
                field_name,
                old_value AS was,
                new_value AS became,
                navi_date
            FROM diff
            ORDER BY new_version, field_name NULLS FIRST;
        """
        return self.process_select(sql, is_empty=True)


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

from dynamic_form_elements import DynamicElements


class ClientSearch(DynamicElements):
    """Страница /chm-search 'Поиск'"""
    #LEFT_BAR
    CUSTOMER_STATUSES = "#customerStatusIds_control"
    ACCOUNT_STATUSES = "#accountStatusIds_control"
    CONTRACT_STATUS = "#agreementStatusIds_control"

    RESET_BTN = "button[type='reset']"
    SEARCH_BTN = "button[type='submit']"

    #BODY
    REFRESH_BTN = "button[|title='Обновить'],[|title='Edit address']"
    CREATE_CLIENT = "#createClient"
    EXPORT_TO_FILE_BTN = "button[|disabledtooltip='Export found records to XLS file'],[|disabledtooltip='Экспортировать найденные записи в XLS файл']"

    FOUNDED_CLIENT = ".ant-table-tbody tr:nth-child({client_num})"

    #BODY_FOUNDED_CLIENT
    FOUNDED_FIO = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(1)"
    FOUNDED_CUSTOMER_TYPE = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(2)"
    FOUNDED_CUSTOMER_STATUS = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(3)"
    FOUNDED_DOCUMENT = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(4)"
    FOUNDED_CONTRACT = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(5)"
    FOUNDED_CONTRACT_STATUS = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(6)"
    FOUNDED_DOCUMENT_NUM = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(7)"
    FOUNDED_ACCOUNT_NUM = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(8)"
    FOUNDED_ACCOUNT_NUM_STATUS = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(9)"
    FOUNDED_ACCOUNT_NUM_TYPE = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(10)"
    FOUNDED_SUBSCRIBER = ".ant-table-tbody tr:nth-child({client_num}) td:nth-child(11)"
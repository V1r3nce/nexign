from base_elements import BaseElements


class HomePage(BaseElements):
    """Страница /welcome Домашняя"""
    #footer panel
    CUSTOMER_NAME = "#customerName"
    INN = "#taxIdentificationNumber"

    #WORK_TABLE
    WIDGET = ".react-grid-layout > div:nth-child({widget_num})"
    WIDGET_LABEL = ".react-grid-layout > div:nth-child({widget_num}) h4"

    #QUICK_ACTIONS_WIDGET
    CREATE_ORG_BTN = "#createOrganization"
    CREATE_CUSTOMER_BTN = "#createIndividual"
    CREATE_ENTREPRENEUR_BTN = "#createEntrepreneur"
    LAST_INQUIRY_BTN = "#lastInquiry"
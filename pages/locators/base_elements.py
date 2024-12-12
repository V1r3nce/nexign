class BaseElements:
    #header
    BURGER_MENU_BTN = ".sc-gFCCrQ.bEnxbF.cWFlmk" # возможно, нестабильный
    HOME_BTN = 'a[href="/rm-ui/all/welcome"]'
    PAGE_TITLE = "[class='sc-guDLey RHMsq'] > h4" # возможно, нестабильный

    HEADER_ACCOUNT_NUM = "#accountNumber"
    HEADER_SUBSCRIBER = "#subscriptionIdentification"
    HEADER_SEARCH_BTN = ".ant-form-inline > button"
    USER_DROPDOWN_BTN = "p.ant-dropdown-trigger"

    #USER_DROPDOWN
    ENGLISH_LANG_BTN = "li[data-menu-id*='ru']"
    RUSSIAN_LANG_BTN = "li[data-menu-id*='en']"
    DARK_THEME_BTN = "li[data-menu-id*='dark']"
    DEFAULT_THEME_BTN = "li[data-menu-id*='default']"
    LOGOUT_BTN = "li[data-menu-id*='logout']"

    #BURGER_MENU
    BURGER_MENU_PARTITION = ".ant-drawer-body div:nth-child({partition_num}"
    BURGER_MENU_EL_BTN = ".ant-drawer-body a:nth-child({element_num})"

    #RIGHT_SIDE_MENU
    RIGHT_SIDE_BTN = "[class='sc-guDLey sc-djhFyi fIjdvn krfyAa'] > div > div > button:nth-child({element_num})" # возможно, нестабильный

    #MODAL
    MODAL = ".ant-modal-content"
    MODAL_CLOSE_BTN = ".ant-modal-close"
    MODAL_TITLE = ".ant-modal-title"
    MODAL_BODY_TEXT = ".ant-modal-body"
    COPY_DETAILS_BTN = ".ant-modal-footer > div > button"
    FOOTER_CLOSE_BTN = ".ant-modal-footer > div > div > button"

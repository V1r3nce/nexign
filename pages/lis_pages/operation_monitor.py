from pages.base_page import BasePage
from pages.locators.lis_locators.operation_monitor_elements import OperationMonitorElementsLis


class OperationMonitorPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = OperationMonitorElementsLis()

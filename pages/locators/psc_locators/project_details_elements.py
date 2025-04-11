from playwright.sync_api import Page

from pages.locators.psc_locators.base_elements_psc import BaseElementsPsc
from pages.ui_elements import Element


class ProjectDetailsElements(BaseElementsPsc):
    """Страница детали проекта"""

    def __init__(self, page: Page):
        super().__init__(page)

        # HEADER PANEL
        self.PROJECT_STATUS = Element("[data-test='ProjectHeader'] [data-test='PscLabel']", "Статус проекта", self.page)
        self.PROJECT_NAME = Element("[data-test='ProjectHeader'] h1", "Название проекта", self.page)

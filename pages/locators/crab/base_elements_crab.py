from playwright.sync_api import Page


class BaseElementsCrab:

    def __init__(self, page: Page):
        self.page = page


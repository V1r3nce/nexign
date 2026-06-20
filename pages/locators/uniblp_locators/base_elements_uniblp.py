from pages.ui_elements import Element


class BaseUniblpElements:
    def __init__(self) -> None:
        self.PAGE_TITLE = Element("h2.content-section-header", "Заголовок страницы")

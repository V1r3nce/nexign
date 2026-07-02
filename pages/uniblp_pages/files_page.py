import random
from datetime import datetime, timedelta
from pathlib import Path

import allure

from api.uniblp_requests.files_requests import FilesUniblpRequests
from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
from pages.locators.uniblp_locators.files_elements import FilesUniblpElements


class FilesUniblpPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

        self.locators = FilesUniblpElements()
        self.files_requests = FilesUniblpRequests()

    @staticmethod
    @allure.step("Создать txt файл для загрузки выписки")
    def create_txt_file_to_upload_statement(file_name: str, amount: float) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()

        now = datetime.now()
        start_of_year = datetime(now.year, 1, 1)
        random_date = start_of_year + timedelta(days=random.randint(0, (now - start_of_year).days))
        date_str = random_date.strftime("%d.%m.%Y")

        if random_date.date() == now.date():
            max_seconds = now.hour * 3600 + now.minute * 60 + now.second
            random_seconds = random.randint(0, max_seconds)
        else:
            random_seconds = random.randint(0, 23 * 3600 + 59 * 60 + 59)
        time_str = f"{random_seconds // 3600:02d}:{(random_seconds % 3600) // 60:02d}:{random_seconds % 60:02d}"

        amount_str = f"{amount:.2f}".replace(",", ".")

        lines = [
            "1CClientBankExchange",
            "ВерсияФормата=1.02",
            "Кодировка=Windows-1251",
            "Отправитель=",
            "Получатель=",
            f"ДатаСоздания={date_str}",
            f"ВремяСоздания={time_str}",
            f"ДатаНачала={date_str}",
            f"ДатаКонца={date_str}",
            "РасчСчет=40702810538050107202",
            "СекцияРасчСчет",
            f"ДатаНачала={date_str}",
            f"ДатаКонца={date_str}",
            "РасчСчет=40702810538050107202",
            "КонецРасчСчет",
            "СекцияДокумент=Платежное поручение",
            "Номер=999",
            f"Дата={date_str}",
            f"Сумма={amount_str}",
            "ПлательщикСчет=40702810538050107202",
            "ДатаСписано=",
            'Плательщик=ООО "Остин1"',
            "ПлательщикИНН=7728551510",
            "ПлательщикКПП=774850001",
            "ПлательщикРасчСчет=40702810538050107202",
            'ПлательщикБанк1=ПАО "ПРОМСВЯЗЬБАНК1"',
            "ПлательщикБИК=044525555",
            "ПлательщикКорсчет=30101810400000000555",
            "ПолучательСчет=40702810538050107202",
            f"ДатаПоступило={date_str}",
            'Получатель=Столичный филиал ПАО "МегаФон"',
            "ПолучательИНН=7812014560",
            "ПолучательКПП=7714020012",
            "ПолучательРасчСчет=40702810538050107202",
            "ПолучательБанк=ПАО СБЕРБАНК",
            "ПолучательБИК=044525225",
            "ПолучательКорсчет=30101810400000000225",
            "ВидПлатежа=электронно",
            "ВидОплаты=01",
            "Код=0",
            "СтатусСоставителя=",
            "ПоказательКБК=",
            "ОКАТО=",
            "ПоказательОснования=",
            "ПоказательПериода=",
            "ПоказательНомера=",
            "ПоказательДаты=",
            "ПоказательТипа=",
            "Очередность=5",
            "НазначениеПлатежа=Оплата за услуги связи",
            "КонецДокумента",
            "КонецФайла",
            "",
        ]

        content = "\r\n".join(lines)

        with open(file_path, "wb") as f:
            f.write(content.encode("windows-1251"))

        return file_path

    @allure.step("Загрузить выписку из файла {file_name} на сумму {amount}")
    def upload_statement(self, file_name: str, amount: float, remove_file: list, file_format: str = "1cString") -> None:
        self.locators.UPLOAD_FROM_DISK.click()
        self.locators.DIALOG_LOAD_STATEMENT_TITLE.wait_to_be_visible()
        self.locators.DIALOG_LOAD_STATEMENT_TITLE.to_contain_text("Загрузка выписки")
        self.locators.FORMAT_STATEMENT.select_by_value(file_format)

        file_path = self.create_txt_file_to_upload_statement(file_name, amount)

        allure.attach.file(str(file_path), name=f"Файл {file_name}", attachment_type=allure.attachment_type.TEXT)
        remove_file.append(file_path)

        with self.page.expect_file_chooser() as fc_info:
            self.locators.UPLOAD_FILE_INPUT.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

        self.locators.UPLOAD_STATEMENT_BTN.click()
        self.files_requests.wait_for_file_processed()
        self.locators.SEARCH_BTN.click()
        self.locators.FILES_TABLE_COLUMN_FILENAME[0].to_contain_text(file_name)
        self.locators.FILES_TABLE_COLUMN_STATUS[0].wait_to_have_text("Обработан", timeout=15000)

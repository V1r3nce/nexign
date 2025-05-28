import json
from datetime import datetime
from pathlib import Path
from typing import Any

import allure
from playwright.sync_api import Page

from common.helpers.data_generator import generate_random_number
from common.helpers.download_helper import CheckFile
from pages.base_page import BasePage
from pages.locators.rfd_locators.home_element_rfd import (
    CreateDirectoryForm,
    CreateElementDirectoryForm,
    HomeElementsRfd,
)


class HomePageRfd(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.locators = HomeElementsRfd(page)
        self.create_element_directory_form = CreateElementDirectoryForm(page)
        self.create_directory_form = CreateDirectoryForm(page)
        self.edit_element_directory_form = CreateDirectoryForm(page)

    @allure.step("Заполнить форму создания Наименования элемента справочника")
    def create_directory_element(self, only_required_fields: bool = False, **kwargs: Any) -> str:
        self.create_element_directory_form.NAME_FLD.click()
        name_element = (kwargs.get("type")) + str(generate_random_number(10))
        if not only_required_fields:
            self.create_element_directory_form.DEFAULT_VALUE_FLD.fill(kwargs.get("default_value") or name_element)
        if not only_required_fields:
            self.create_element_directory_form.RU_LANG_FLD.fill(
                kwargs.get("ru_lang") or (kwargs.get("type") + str(generate_random_number(10)))
            )
        if not only_required_fields:
            self.create_element_directory_form.EN_LAND_FLD.fill(
                kwargs.get("en_lang") or (kwargs.get("type") + str(generate_random_number(10)))
            )
        self.create_element_directory_form.SAVE_OK_BTN[1].click()
        return name_element

    @allure.step("Заполнить форму создания справочника")
    def create_directory(self, only_required_fields: bool = False, **kwargs: Any) -> None:
        if not only_required_fields:
            self.create_directory_form.CODE_DIRECTORY_FLD.fill(kwargs.get("type"))
        for i in range(2):
            self.create_directory_form.EDIT_FORM_BTN[i].click()
            if not only_required_fields:
                self.create_directory_form.DEFAULT_VALUE_FLD.fill(
                    kwargs.get("default_value") or (kwargs.get("type") + str(generate_random_number(10)))
                )
            if not only_required_fields:
                self.create_directory_form.RU_LANG_FLD.fill(
                    kwargs.get("ru_lang") or (kwargs.get("type") + str(generate_random_number(10)))
                )
            if not only_required_fields:
                self.create_directory_form.EN_LAND_FLD.fill(
                    kwargs.get("en_lang") or (kwargs.get("type") + str(generate_random_number(10)))
                )
            self.create_element_directory_form.SAVE_OK_BTN[1].click()
        self.create_directory_form.EDIT_FORM_BTN[2].click()
        if not only_required_fields:
            self.create_directory_form.TYPE_CODE_FLD.select_by_value(kwargs.get("type_code") or "автоинкрементный")
        self.create_element_directory_form.SAVE_OK_BTN[2].click()
        self.create_element_directory_form.SAVE_OK_BTN[0].click()

    @allure.step("Редактировать элемент справочника по имени")
    def edit_directory_element(self, **kwargs: Any) -> None:
        self.edit_element_directory_form.EDIT_FORM_BTN[0].click()
        self.edit_element_directory_form.DEFAULT_VALUE_FLD.type(kwargs.get("test_value"))
        self.edit_element_directory_form.SAVE_OK_BTN[1].click()
        self.edit_element_directory_form.SAVE_OK_BTN[0].click()

    @allure.step("Создать файл для загрузки справочника")
    def create_json_file_to_upload_directory(self, file_name: str, code_name_directory: str) -> Path:
        file_check = CheckFile(file_name)
        file_path = file_check.get_download_file_path()
        data = generate_json_data_for_directory(name_code=code_name_directory)
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        file_check.is_exist()
        return file_path


def generate_json_data_for_directory(name_code: str) -> dict:
    """
    Возвращает json данные для справчоника
    :param name_code: строка наименование кода справочника
    """

    start_date = datetime.utcnow()
    end_date = datetime(2999, 12, 31)

    data = {
        "referenceCode": name_code,
        "name": {
            "defaultValue": "Типы счетов Пример",
            "localizedStrings": [
                {"language": "EN", "value": "accountTypesExample"},
                {"language": "RU", "value": "Типы счетов Пример"},
            ],
        },
        "description": None,
        "itemCodeDefinition": {"type": "AUTO_INCREMENT", "currentValue": "5"},
        "itemNameDefinition": {"constraints": None, "isUnique": True},
        "itemPropertyDefinitions": [],
        "items": [
            {
                "referenceItemCode": str(i),
                "name": {"defaultValue": default_value, "localizedStrings": []},
                "properties": [],
                "validFor": {
                    "startDateTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "endDateTime": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            }
            for i, default_value in enumerate(
                ["Бизнес-счет", "Личный основной", "Для подписок", "Временный счет", "Счет для партнеров"], start=1
            )
        ],
    }

    return data

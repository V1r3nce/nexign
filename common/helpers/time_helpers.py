import time
from datetime import datetime

import allure


TIME_FOR_UPDATE_LIST = "Время на обновление списка"
TIME_FOR_UPDATE_STATUS = "Время на обновление статуса"
TIME_FOR_DOWNLOAD_FILE = "Время на загрузку файла"
TIME_FOR_UPDATE_COLOR = "Время на обновление цвета"
TIME_FOR_TURN_ON_SWITCH = "Время для включения свича"
TIME_FOR_PAGE_LOAD = "Время для загрузки страницы"
TIME_FOR_UPDATE_CHECKBOX_STATUS = "Время для смены состояния чекбокса"
TIME_FOR_LIST_LOAD = "Время для загрузки списка"
TIME_FOR_UPDATE_DATE = "Время для обновления даты"
TIME_TO_CLEAR_THE_FIELD = "Время для очищения поля"


@allure.step("Ожидание {timeout} сек., причина '{reason}'")
def delay(timeout: [int, float], reason: [str, None] = None):
    time.sleep(timeout)


def get_now_time():
    date = datetime.now()
    return date.strftime("%H:%M:%S")
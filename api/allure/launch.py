from typing import List

import requests

from api.exceptions import AllureLaunchNotFoundException
from common.helpers.env_helper import get_var_from_env
from common.helpers.time_helpers import timestamp_to_datetime_string


class AllureLaunch:
    """Получение данных о ланче Allure"""

    ALLURE_PROJECT_ID = get_var_from_env("ALLURE_PROJECT_ID")
    ALLURE_URL = get_var_from_env("ALLURE_ENDPOINT")
    TOKEN = get_var_from_env("ALLURE_TOKEN")

    def __init__(self, job_url: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self._get_jwt_token()}"})
        self.job_url = job_url
        self.launch_id = self.get_launch_id_by_job_url(self.job_url)

    def _get_jwt_token(self) -> str:
        """Получение токена для авторизации в Allure"""
        data = {"grant_type": "apitoken", "scope": "openid", "token": self.TOKEN}

        response = self.session.post(self.ALLURE_URL + "/api/uaa/oauth/token", data=data)
        assert response.status_code == 200, (
            f"Не удалось авторизоваться в Allure.\nСтатус: {response.status_code}\nОшибка: {response.text}"
        )
        jwt_token = response.json().get("access_token")
        return jwt_token

    def get_launch_statistics(self) -> List[str]:
        """Получение статистики ланча Allure"""
        response = self.session.get(self.ALLURE_URL + f"/api/rs/launch/{self.launch_id}/statistic")
        assert response.status_code == 200, (
            f"Не удалось получить статистику ланча {self.launch_id} в Allure.\nСтатус: {response.status_code}\nОшибка: {response.text}"
        )
        statistics = response.json()
        tests_count = sum(stat["count"] for stat in statistics)
        result = []
        if tests_count > 0:
            for stat in statistics:
                if stat["count"] > 0:
                    result.append(f"{stat['status']}: {stat['count']}")
        return result

    def get_launch_defects(self) -> List[str]:
        """Получение дефектов ланча Allure"""
        response = self.session.get(self.ALLURE_URL + f"/api/rs/launch/{self.launch_id}/defect")
        assert response.status_code == 200, (
            f"Не удалось получить дефекты ланча {self.launch_id} в Allure.\nСтатус: {response.status_code}\nОшибка: {response.text}"
        )
        defects = response.json()["content"]
        defects_count = len(defects)
        result = []
        if defects_count > 0:
            result.append(f"Количество багов: {defects_count}")
            for defect in defects:
                result.append({defect["issue"]["summary"]: defect["issue"]["url"]})
        else:
            result.append("Дефектов не найдено")
        return result

    def get_launch_envs(self) -> list[str]:
        """Получение переменных окружения ланча Allure"""
        response = self.session.get(self.ALLURE_URL + f"/api/rs/launch/{self.launch_id}/env")
        assert response.status_code == 200, (
            f"Не удалось получить переменные окружения ланча {self.launch_id} в Allure.\nСтатус: {response.status_code}\nОшибка: {response.text}"
        )
        envs = response.json()
        return [env["name"] for env in envs if env["variable"]["name"] == "Stand"][0]

    def get_launch_date(self) -> str:
        """Получение даты создания ланча Allure"""
        response = self.session.get(self.ALLURE_URL + f"/api/rs/launch/{self.launch_id}")
        assert response.status_code == 200, (
            f"Не удалось получить дату создания ланча {self.launch_id} в Allure.\nСтатус: {response.status_code}\nОшибка: {response.text}"
        )
        create_timestamp = response.json().get("createdDate")
        return timestamp_to_datetime_string(create_timestamp)

    def get_launch_list(self) -> dict:
        """Получение списка ланчей Allure
        :return: список ланчей Allure"""
        response = self.session.get(
            self.ALLURE_URL + f"/api/rs/launch?search=&projectId={self.ALLURE_PROJECT_ID}&page=0&size=25&preview=true"
        )
        assert response.status_code == 200, (
            f"Не удалось получить список ланчей по проекту {self.ALLURE_PROJECT_ID} в Allure.\nСтатус: {response.status_code}\nОшибка: {response.text}"
        )
        return response.json()

    def get_launch_id_by_job_url(self, job_url: str) -> int:
        """ "Получение id ланча Allure по jenkins job url
        :param job_url: jenkins job url
        :return: id ланча Allure
        """
        launch_list = self.get_launch_list()
        for launch in launch_list.get("content"):
            if jobs := launch.get("jobs"):
                for job in jobs:
                    if job.get("url") == job_url:
                        return launch["id"]
        raise AllureLaunchNotFoundException(f"Не удалось найти ланч Allure по job url: {job_url}")

import gitlab
from gitlab.v4.objects import Project

from api.exceptions import GitlabProjectNotFoundException
from common.helpers.env_helper import get_var_from_env


class Gitlab:
    """Класс для чтения файлов из Gitlab"""

    def __init__(self) -> None:
        self.stand = get_var_from_env("SOLO_STAND") or get_var_from_env("CLONE_NAME")
        self.endpoint = get_var_from_env("GITLAB_ENDPOINT")
        self.private_token = get_var_from_env("GITLAB_TOKEN")
        self.project_id = get_var_from_env("GITLAB_SOLO_CLUSTER_PROJECT_ID")
        self.gl = gitlab.Gitlab(self.endpoint, private_token=self.private_token)

    def get_project(self) -> Project:
        """Получение проекта по id"""
        project = self.gl.projects.get(self.project_id)
        if project:
            return project
        raise GitlabProjectNotFoundException(f"Проект {self.project_id} не найден")

    def get_content(self) -> bytes | None:
        """Получение содержимого файла build_params.txt указанного стенда"""
        project = self.get_project()
        file_content = project.files.get(file_path=f"vp_res/{self.stand}/build_params.txt", ref="master")
        if file_content:
            return file_content.decode()
        return None

    def get_content_dict(self) -> dict | None:
        """Получение содержимого файла build_params.txt указанного стенда в виде словаря"""
        content = self.get_content()
        if content:
            content_list = str(content.decode("utf-8")).split("\n")
            return {i.split("=")[0]: i.split("=")[1] for i in content_list}
        return None

    def get_inventory_branch(self) -> str:
        """Получение ветки инвентори стенда"""
        contend_dict = self.get_content_dict()
        if not contend_dict:
            return "Не удалось получить значение ветки инвентори"
        return contend_dict["inventory_branch"]

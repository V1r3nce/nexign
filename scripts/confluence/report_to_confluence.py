import argparse
import sys
from pathlib import Path

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT_PATH))
from api.allure.launch import AllureLaunch  # noqa: E402
from api.confluence.page import ConfluencePage  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--job_url", type=str, required=False)
args = parser.parse_args()
job_url = args.job_url


def main() -> None:
    """Основная функция отчета статистики прогона из Allure в Confluence.
    ID страницы берется из переменной окружения CONFLUENCE_PAGE_ID
    На входе скрипта передается URL джобы jenkins, в которой шли автотесты.
    По URL находится ланч. Из ланча получаем: статистику, список багов, окружение.
    На странице Confluence находится первая таблица. В таблице добавляется новая строка в конец с найденной информацией.
    """
    allure = AllureLaunch(job_url)

    confluence = ConfluencePage()
    content = {
        "QA сборка": allure.get_launch_envs(),
        "Дата": allure.get_launch_date(),
        "Launch": f"https://allure.nexign.com/launch/{str(allure.launch_id)}",
        "Статистика": allure.get_launch_statistics(),
        "Список багов": allure.get_launch_defects(),
    }
    new_page_content = confluence.prepare_new_page_content(content)
    confluence.update_page(new_page_content, "Статистика по прогонам")


if __name__ == "__main__":
    main()

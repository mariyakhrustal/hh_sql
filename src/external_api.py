import logging
import os
from typing import Any

import requests

logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)  # pragma: no cover

api_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join(logs_dir, "external_api.log"), mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(name)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
api_logger.addHandler(file_handler)
api_logger.setLevel(logging.DEBUG)


class HeadHunterAPI:
    """Класс для работы с платформой hh.ru"""

    def __init__(self, employer_id: list) -> None:
        self.__base_url = "https://api.hh.ru"
        self.__employer_id = employer_id
        self.__params = self._get_params()
        self.__vacancies: list = []

    @property
    def vacancies(self) -> list:
        """Возвращает список вакансий"""
        api_logger.info("Возврат списка вакансий полученных от API")
        return self.__vacancies

    def _get_params(self) -> dict:
        """Генерирует параметры для запроса вакансий, используя self.__employer_id"""
        if not self.__employer_id:  # Проверяем, что employer_id не пуст
            api_logger.critical("Список employer_id пуст")
            raise ValueError("Список employer_id не может быть пустым")

        params = {
            "text": None,
            "search_field": "name",
            "area": 113,
            "period": 1,
            "employer_id": self.__employer_id,
            "only_with_salary": True,
            "per_page": 100,
            "page": 0,
        }
        api_logger.info("Сформированы параметры для подключения к API")
        return params

    def _connect_to_api(self, params: dict) -> Any:
        """Метод для подключения к API сервису"""
        try:
            url = f"{self.__base_url}/vacancies"
            response = requests.get(url, params=params)
            if response.status_code == 200:
                api_logger.info(f"Успешное подключение к API: {response.status_code}")
                return response.json()
            else:
                api_logger.warning(f"Ошибка при запросе к API: статус {response.status_code}. Ответ: {response.text}")
                raise requests.HTTPError(f"Ошибка при запросе к API: статус {response.status_code}")
        except Exception as e:
            api_logger.error(f"Ошибка: {e}")
            return []

    def load_companies_and_vacancies(self) -> None:
        """Метод для получения вакансий по запросу"""
        data_hh = []
        while True:
            data = self._connect_to_api(self.__params)
            if not data or "items" not in data:
                api_logger.warning("Данные отсутствуют или не содержат ключ 'items'. Прерывание.")
                break
            api_logger.info(f"Получено {len(data['items'])} вакансий на странице {self.__params['page']}")
            data_hh.extend(data["items"])
            if data["pages"] <= self.__params["page"]:
                api_logger.info(f"Достигнут конец страниц. Всего {data['pages']} страниц.")
                break
            else:
                self.__params["page"] += 1
                api_logger.info(f"Переход на следующую страницу: {self.__params['page']}")
        self.__vacancies.extend(data_hh)
        api_logger.info(f"Общее количество вакансий: {len(self.__vacancies)}")

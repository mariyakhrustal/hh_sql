from typing import Any

import requests

from src.config import employer_id


class HeadHunterAPI:
    """Класс для работы с платформой hh.ru"""

    def __init__(self) -> None:
        self.__base_url = "https://api.hh.ru"
        self.__params = {
            "text": None,
            "search_field": "name",
            "area": 113,
            "period": 1,
            "employer_id": employer_id,
            "only_with_salary": True,
            "per_page": 100,
            "page": 0,
        }
        self.__vacancies: list = []

    @property
    def vacancies(self) -> list:
        """Возвращает список вакансий"""
        return self.__vacancies

    def _connect_to_api(self, params: dict) -> Any:
        """Метод для подключения к API сервису"""
        try:
            url = f"{self.__base_url}/vacancies"
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка при запросе вакансий: {response.status_code}")
                return []
        except Exception as e:
            print(f"Ошибка: {e}")
            return []

    def _load_companies_and_vacancies(self) -> None:
        """Метод для получения вакансий по запросу"""
        data_hh = []
        while True:
            data = self._connect_to_api(self.__params)
            if not data or "items" not in data:
                break
            data_hh.extend(data["items"])
            if data["pages"] <= self.__params["page"]:
                break
            else:
                self.__params["page"] += 1
        self.__vacancies.extend(data_hh)

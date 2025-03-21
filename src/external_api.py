from typing import Any

import requests


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
        return self.__vacancies

    def _get_params(self) -> dict:
        """Генерирует параметры для запроса вакансий, используя self.__employer_id"""
        if not self.__employer_id:  # Проверяем, что employer_id не пуст
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
        return params

    def _connect_to_api(self, params: dict) -> Any:
        """Метод для подключения к API сервису"""
        try:
            url = f"{self.__base_url}/vacancies"
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Ошибка: {e}")
            return []

    def load_companies_and_vacancies(self) -> None:
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

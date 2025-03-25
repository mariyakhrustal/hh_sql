from abc import ABC, abstractmethod
from typing import Any


class BaseAPI(ABC):
    """Абстрактный метод для работы с API"""

    def __init__(self, employer_id: list) -> None:
        pass

    @abstractmethod
    def _connect_to_api(self, params: dict) -> Any:
        """Метод для подключения к API сервису"""
        pass

    @abstractmethod
    def load_companies_and_vacancies(self) -> None:
        """Метод для получения вакансий по запросу"""
        pass

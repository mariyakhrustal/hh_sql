from abc import ABC, abstractmethod


class BaseDB(ABC):
    """Абстрактный метод для работы с базой данных"""

    def __init__(self, params: dict, database_name: str) -> None:
        pass

    @abstractmethod
    def create_db(self) -> None:
        """Создание базы данных в том случае, если база данных ещё не существует"""
        pass

    @abstractmethod
    def create_tables_in_db(self) -> None:
        """Создание таблиц в базе данных для вакансий и работодателей"""
        pass

    @abstractmethod
    def save_data_to_db_tables(self, vacancies: list[dict]) -> None:
        """Сохранение данных в таблицы в базе данных"""
        pass

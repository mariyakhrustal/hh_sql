from typing import Any

import psycopg2

from src.config import config


class DBManager:
    """Класс для работы с данными в базе данных"""

    def __init__(self, database_name: str = "headhunter") -> None:
        self.database_name = database_name

    def execute_query(self, query: str, params: Any = None) -> Any:
        """Метод выполняющий запросы"""
        fetch = []
        try:
            conn = psycopg2.connect(
                dbname=self.database_name, host=config()["host"], user=config()["user"], password=config()["password"]
            )
            with conn.cursor() as cur:
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                if query.strip().lower().startswith("select"):
                    fetch = cur.fetchall()
            conn.commit()
            conn.close()
            return fetch
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
        finally:
            print("Закрытие соединения")
        return fetch

    def get_companies_and_vacancies_count(self) -> Any:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        result = self.execute_query(
            """
            SELECT employer_name, COUNT(vacancy_id)
            FROM employers
            JOIN vacancies ON employers.employer_id = vacancies.employer_id
            GROUP BY employer_name
        """
        )
        return result

    def get_all_vacancies(self) -> Any:
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию
        """
        result = self.execute_query(
            """
            SELECT employers.employer_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url
            FROM employers
            JOIN vacancies ON employers.employer_id = vacancies.employer_id
        """
        )
        return result

    def get_avg_salary(self) -> Any:
        """Получает среднюю зарплату по вакансиям"""
        result = self.execute_query("SELECT AVG(salary) FROM vacancies")
        return result[0][0] if result else None

    def get_vacancies_with_higher_salary(self) -> Any:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        query = """
        SELECT
        employers.employer_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url, vacancies.city
        FROM employers
        JOIN vacancies ON employers.employer_id = vacancies.employer_id
        WHERE salary > (SELECT AVG(salary) FROM vacancies)
        """
        result = self.execute_query(query)
        return result

    def get_vacancies_with_keyword(self, keyword: str) -> Any:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""
        query = """
        SELECT employers.employer_name, vacancies.vacancy_name, vacancies.salary, vacancies.vacancy_url, vacancies.city
        FROM employers
        JOIN vacancies ON employers.employer_id = vacancies.employer_id
        WHERE vacancy_name LIKE %s
        """
        result = self.execute_query(query, (f"%{keyword}%",))
        return result

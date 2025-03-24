# from typing import Any

import psycopg2


class PostgreSQL:
    """
    Класс для работы с базой данных. Создание базы данных, таблиц и подключение к БД
    """

    def __init__(self, params: dict, database_name: str = "headhunter"):
        self.database_name = database_name
        self.__params = params
        self.conn = None  # Инициализация атрибута conn
        try:
            self.conn = psycopg2.connect(
                dbname="postgres",
                user=self.__params.get("user"),
                password=self.__params.get("password"),
                host=self.__params.get("host", "localhost"),
                port=self.__params.get("port", 5432),
            )
            self.conn.autocommit = True
            print(f"Подключился к базе данных 'postgres'")
        except psycopg2.Error as e:
            print(f"Ошибка подключения к базе данных PostgreSQL: {e}")

    def connect_to_db(self):
        """Метод для подключения к базе данных"""
        if self.conn:  # Проверка наличия соединения
            try:
                self.conn = psycopg2.connect(
                    dbname=self.database_name,
                    user=self.__params.get("user"),
                    password=self.__params.get("password"),
                    host=self.__params.get("host", "localhost"),
                    port=self.__params.get("port", 5432),
                )
                self.conn.autocommit = True  # чтобы изменения автоматически сохранялись
            except psycopg2.Error as e:
                print(f"Ошибка подключения к базе данных {self.database_name}: {e}")
        else:
            print("Ошибка соединения")

    def create_db(self):
        """Создание базы данных в том случае, если база данных ещё не существует"""
        if self.conn:  # Проверка наличия соединения
            try:
                with self.conn.cursor() as cur:
                    cur.execute(f"DROP DATABASE IF EXISTS {self.database_name}")
                    cur.execute(f"CREATE DATABASE {self.database_name}")
                print(f"Создание базы данных {self.database_name}, если её не существует")
            except psycopg2.Error as e:
                print(f"Ошибка при создании базы данных {self.database_name}: {e}")
            finally:
                # Закрытие соединения, если оно существует
                if self.conn:
                    self.conn.close()
                    print("Закрытие соединения")
        else:
            print("Ошибка соединения")

    def create_tables_in_db(self) -> None:
        """Создание таблиц в базе данных для вакансий и работодателей"""
        self.connect_to_db()
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS employers(
                        employer_id INT PRIMARY KEY,
                        employer_name VARCHAR(255),
                        employer_url VARCHAR(255)
                    )
                """)
                print("Создание таблицы работодателей")
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies(
                        vacancy_id SERIAL PRIMARY KEY,
                        vacancy_name VARCHAR(255),
                        employer_id INT,
                        vacancy_url VARCHAR(255),
                        salary INT,
                        city VARCHAR(255),
                        FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
                    )
                """)
                print("Создание таблицы вакансий")
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц {e}")
        finally:
            self.conn.commit()
            self.conn.close()
            print("Закрытие соединения")

    def save_data_to_db_tables(self, vacancies: list[dict]) -> None:
        """Сохранение данных в таблицы в базе данных"""
        self.connect_to_db()
        try:
            with self.conn.cursor() as cur:
                for vacancy in vacancies:
                    employer = vacancy.get("employer")
                    if employer:
                        employer_id = employer.get("id")
                        employer_name = employer.get("name")
                        employer_url = employer.get("alternate_url")
                        cur.execute(
                            """
                            INSERT INTO employers (employer_id, employer_name, employer_url)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (employer_id) DO NOTHING
                            RETURNING employer_id
                            """,
                            (employer_id, employer_name, employer_url),
                        )
                        result = cur.fetchone()  # Вернёт employer_id
                        if result:
                            employer_id = result[0]
                    else:
                        continue
                    vacancy_name = vacancy.get("name")
                    vacancy_url = vacancy.get("alternate_url")
                    salary_from = vacancy.get("salary", {}).get("from")
                    salary_to = vacancy.get("salary", {}).get("to")
                    salary = salary_from if salary_from is not None else salary_to
                    city = vacancy.get("area").get("name")
                    cur.execute(
                        """
                        INSERT INTO vacancies (vacancy_name, employer_id, vacancy_url, salary, city)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (vacancy_name, employer_id, vacancy_url, salary, city),
                    )
                print("Заполнилась таблицы")
        except psycopg2.Error as e:
            print(f"Ошибка при заполнении таблиц данными: {e}")
        finally:
            self.conn.commit()
            self.conn.close()
            print("Закрытие соединения")

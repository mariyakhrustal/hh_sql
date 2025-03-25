import logging
import os

import psycopg2

from src.base_db import BaseDB

logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)  # pragma: no cover

postgres_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join(logs_dir, "postgresql.log"), mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(name)s - %(funcName)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
postgres_logger.addHandler(file_handler)
postgres_logger.setLevel(logging.DEBUG)


class PostgreSQL(BaseDB):
    """
    Класс для работы с базой данных. Создание базы данных, таблиц и подключение к БД
    """

    def __init__(self, params: dict, database_name: str = "headhunter") -> None:
        super().__init__(params, database_name)
        self.database_name = database_name
        self.__params = params
        self.conn = None  # Инициализация атрибута conn
        try:
            postgres_logger.info("Попытка подключения к базе данных PostgreSQL...")
            self.conn = psycopg2.connect(
                dbname="postgres",
                user=self.__params.get("user"),
                password=self.__params.get("password"),
                host=self.__params.get("host", "localhost"),
                port=self.__params.get("port", 5432),
            )
            self.conn.autocommit = True
            postgres_logger.info("Подключился к базе данных 'postgres'")
        except psycopg2.Error as e:
            postgres_logger.error(f"Ошибка подключения к базе данных PostgreSQL: {e}")

    def connect_to_db(self) -> None:
        """Метод для подключения к базе данных"""
        if self.conn:  # Проверка наличия соединения
            postgres_logger.info("Соединение с базой данных установлено.")
            try:
                postgres_logger.info(f"Попытка подключения к базе данных {self.database_name}.")
                self.conn = psycopg2.connect(
                    dbname=self.database_name,
                    user=self.__params.get("user"),
                    password=self.__params.get("password"),
                    host=self.__params.get("host", "localhost"),
                    port=self.__params.get("port", 5432),
                )
                self.conn.autocommit = True  # чтобы изменения автоматически сохранялись
                postgres_logger.info(f"Успешное подключение к базе данных {self.database_name}.")
            except psycopg2.Error as e:
                postgres_logger.error(f"Ошибка подключения к базе данных {self.database_name}: {e}")
        else:
            postgres_logger.critical(f"Не удалось подключиться к базе данных {self.database_name}")
            raise Exception(f"Не удалось подключиться к базе данных {self.database_name}")

    def create_db(self) -> None:
        """Создание базы данных в том случае, если база данных ещё не существует"""
        if self.conn:  # Проверка наличия соединения
            postgres_logger.info("Соединение с базой данных установлено.")
            try:
                postgres_logger.info(f"Попытка создать базу данных {self.database_name}, если её не существует")
                with self.conn.cursor() as cur:
                    cur.execute(f"DROP DATABASE IF EXISTS {self.database_name}")
                    cur.execute(f"CREATE DATABASE {self.database_name}")
                    postgres_logger.info(f"Успешное создание базы данных {self.database_name}, если её не существует")
            except psycopg2.Error as e:
                postgres_logger.error(f"Ошибка при создании базы данных {self.database_name}: {e}")
                print(f"Ошибка при создании базы данных {self.database_name}: {e}")
            finally:
                # Закрытие соединения, если оно существует
                if self.conn:
                    self.conn.close()
                    postgres_logger.info("Закрытие соединения")
        else:
            postgres_logger.critical(f"Не удалось подключиться к базе данных {self.database_name}")
            raise Exception(f"Не удалось подключиться к базе данных {self.database_name}")

    def create_tables_in_db(self) -> None:
        """Создание таблиц в базе данных для вакансий и работодателей"""
        self.connect_to_db()
        postgres_logger.info(f"Соединение с базой данных {self.database_name} для создания таблиц.")
        try:
            postgres_logger.info("Попытка создать таблицу для работодателей")
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS employers(
                        employer_id INT PRIMARY KEY,
                        employer_name VARCHAR(255),
                        employer_url VARCHAR(255)
                    )
                """
                )
                postgres_logger.info("Создание таблицы работодателей")
            postgres_logger.info("Попытка создать таблицу для вакансий")
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vacancies(
                        vacancy_id SERIAL PRIMARY KEY,
                        vacancy_name VARCHAR(255),
                        employer_id INT,
                        vacancy_url VARCHAR(255),
                        salary INT,
                        city VARCHAR(255),
                        FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
                    )
                """
                )
                postgres_logger.info("Создание таблицы вакансий")
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц {e}")
            postgres_logger.error(f"Ошибка при создании таблиц {e}")
        finally:
            self.conn.commit()
            self.conn.close()
            postgres_logger.info("Закрытие соединения")

    def save_data_to_db_tables(self, vacancies: list[dict]) -> None:
        """Сохранение данных в таблицы в базе данных"""
        self.connect_to_db()
        postgres_logger.info(f"Соединение с базой данных {self.database_name} для сохранения данных в таблицы.")
        try:
            postgres_logger.info("Попытка заполнить таблицы")
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
                postgres_logger.info(f"Заполнилась таблицы в базе данных {self.database_name}")
        except psycopg2.Error as e:
            print(f"Ошибка при заполнении таблиц данными: {e}")
            postgres_logger.error(f"Ошибка при заполнении таблиц данными: {e}")
        finally:
            self.conn.commit()
            self.conn.close()
            postgres_logger.info("Закрытие соединения")

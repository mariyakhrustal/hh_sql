from src.config import config
from src.postgresql_db import PostgreSQL
from src.external_api import HeadHunterAPI
from src.db_manager import DBManager

# ID работодателей, от которых вы будете получать данные о вакансиях по API
employer_id = [
    "1942330",  # Перекрёсток
    "49357",  # МАГНИТ
    "78638",  # Т-Банк
    "2748",  # Ростелеком
    "2180",  # Ozon
    "1942336",  # Пятёрочка
    "3529",  # СБЕР
    "816144",  # ВкусВилл
    "41862",  # Контур
    "23186",  # Группа Компаний РУСАГРО
]


def print_vacancies(vacancies: list, title: str="Вакансии") -> None:
    """
    Функция для вывода вакансий
    :param vacancies: список вакансий для отображения
    :param title: заголовок, по умолчанию 'Вакансии'
    """
    print(f"{title}:")
    if vacancies:
        for vacancy in vacancies:
            if len(vacancy) > 4:
                employer_name, vacancy_name, salary, vacancy_url, city = vacancy
                print(f"Компания: {employer_name}, Вакансия: {vacancy_name}, Зарплата:\
{salary}, Ссылка: {vacancy_url}, Город: {city}")
            else:
                employer_name, vacancy_name, salary, vacancy_url = vacancy
                print(f"Компания: {employer_name}, Вакансия: {vacancy_name}, Зарплата: {salary}, Ссылка: {vacancy_url}")
    else:
        print("Вакансии не найдены")


def main() -> None:
    """
    1. Загружает вакансии с API HeadHunter для выбранного работодателя.
    2. Инициализирует базу данных PostgreSQL, создает таблицы и сохраняет вакансии.
    3. Приветствует пользователя и предоставляет информацию о вакансиях:
        - Выводит все вакансии.
        - Выводит список компаний и количество вакансий в каждой из них.
        - Выводит среднюю зарплату по всем вакансиям.
        - Выводит вакансии с зарплатой выше средней.
        - Позволяет пользователю ввести ключевое слово для поиска вакансий.

    Исключения:
    - Обрабатывает ошибки при взаимодействии с API и базой данных.
    """
    try:
        # Загрузка вакансий
        hh_api = HeadHunterAPI(employer_id=employer_id)
        hh_api.load_companies_and_vacancies()
        vacancies = hh_api.vacancies

        # Создание базы данных и таблиц
        params = config()
        postgresql_db = PostgreSQL(params=params)
        postgresql_db.create_db()
        postgresql_db.create_tables_in_db()
        postgresql_db.save_data_to_db_tables(vacancies)

        # Приветствие пользователя
        print("Привет, Пользователь!\nПредоставляю данные по вакансиям.")

        # Работа с базой данных
        db_manager = DBManager()

        # Вывод количества вакансий в компаниях
        vacancy_count = db_manager.get_companies_and_vacancies_count()
        print("Компании и количество вакансий в каждой компании:")
        if vacancy_count:
            for employer_name, count in vacancy_count:
                print(f"Компания: {employer_name}, Количество вакансий: {count}")
        else:
            print("Нет данных по вакансиям")

        # Вывод средней зарплаты
        avg_salary = db_manager.get_avg_salary()
        print("Средняя зарплата по вакансиям:",
              round(avg_salary, 2) if avg_salary else "Нет данных по средней зарплате")

        # Вывод вакансий с зарплатой выше средней
        higher_salary = db_manager.get_vacancies_with_higher_salary()
        print_vacancies(higher_salary, title="Вакансии с зарплатой выше средней")

        # Вывод вакансий с ключевым словом
        print("Вывод вакансий с ключевым словом в названии вакансии")
        keyword = input("Введите ключевое слово для поиска подходящей вакансии: ")
        if keyword:
            searched_vacancies = db_manager.get_vacancies_with_keyword(keyword)
            print_vacancies(searched_vacancies, title=f"Вакансии с ключевым словом '{keyword}'")
        else:
            # Вывод всех вакансий
            print("Вы выбрали вывести все вакансии")
            all_vacancies = db_manager.get_all_vacancies()
            print_vacancies(all_vacancies)

        print("Программа завершила свою работу")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


# код для запуска программы
if __name__ == '__main__':
    main()

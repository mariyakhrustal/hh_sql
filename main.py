from src.config import config
from src.postgresql_db import PostgreSQL
from src.external_api import HeadHunterAPI


def main():
    """"""
    # ID работодателей, от которых вы будете получать данные о вакансиях по API
    employer_id = [
        '41862',  # Контур
        "1942330",  # Пятёрочка
        '638950',  # Ресурс Групп
        '816144',  # ВкусВилл
        '23186',  # Группа Компаний РУСАГРО
        "3036416",  # Департамент Ф53
        "78638",  # Т-Банк
        "2748",  # Ростелеком
        "2180",  # Ozon
        "3529",  # СБЕР
    ]

    # Загрузка вакансий
    hh_api = HeadHunterAPI(employer_id=employer_id)
    hh_api.load_companies_and_vacancies()
    vacancies = hh_api.vacancies

    # Создание базы данных, таблиц и заполнение таблиц данными
    params = config()
    postgresql_db = PostgreSQL(params=params)
    postgresql_db.create_db()
    postgresql_db.create_tables_in_db()
    postgresql_db.save_data_to_db_tables(vacancies)


if __name__ == '__main__':
    main()

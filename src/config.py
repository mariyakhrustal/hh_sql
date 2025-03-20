from configparser import ConfigParser

# ID работодателей, от которых вы будете получать данные о вакансиях по API
employer_id = [
    '41862',  # Контур
    '9764865',  # Роскосмос
    '638950',  # Ресурс Групп
    '816144',  # ВкусВилл
    '23186',  # Группа Компаний РУСАГРО
    "3036416",  # Департамент Ф53
    "78638",  # Т-Банк
    "2748",  # Ростелеком
    "2180",  # Ozon
    "3529",  # СБЕР
]


def config(filename: str = "database.ini", section: str = "postgresql") -> dict:
    """Функция читает конфигурационный файл и извлекает параметры для подключения к базе данных"""
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db
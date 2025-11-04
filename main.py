import json

from config import config
from src.classAPI import HH
from src.db_manager import DBManager
from src.employer_id import get_employer_id, save_data_to_database


def main() -> None:
    """ Основная функция """
    # Получаем параметры подключения из database.ini
    params = config()
    

    # Создаем экземпляр DBManager с именем базы данных
    db_manager = DBManager("hh_vacancy")

    db_manager.create_database(params)
    print("База данных hh_vacancy успешно подключена")
    companies = set()
    company_name = [
        "Яндекс",
        "Сбер",
        "Газпром",
        "Роснефть",
        "Ozon",
        "Альфа-Банк",
        "Мегафон",
        "Т-Банк",
        "буше",
        "МТС",
    ]

    vacancy_all = []
    for company in company_name:
        company_id = get_employer_id(company)
        hh_API = HH()
        vacancies_data = hh_API.load_vacancies([company_id])
        companies.add((company, company_id))
        for item in vacancies_data:
            try:
                description_items = {}
                if item.get("name", {}):
                    description_items["name"] = item["name"]
                description_items["company"] = company
                description_items["company_id"] = company_id
                if item.get("salary", {}):
                    description_items["salary"] = item["salary"]["from"]
                else:
                    description_items["salary"] = None
                if item.get("alternate_url", {}):
                    description_items["url"] = item["alternate_url"]
                if item.get("snippet", {}):
                    description_items["description"] = item["snippet"]["requirement"]
                vacancy_all.append(description_items)
            except ValueError as e:
                print(f"Ошибка при обработке вакансии: {e}")
    with open("json/vacancy.json", "w") as f:
        json.dump(vacancy_all, f, ensure_ascii=False, indent=4)
    save_data_to_database(vacancy_all, "hh_vacancy", params, companies)

    print('Данные по вакансиям сохранены в базе данных и сводка представлена в json файлах')
    db_manager.get_companies_and_vacancies_count(params)
    db_manager.get_all_vacancies(params)
    print(f'Cреднее значение зарплаты: {db_manager.get_avg_salary(params)}')
    db_manager.get_vacancies_with_higher_salary(params)
    db_manager.get_vacancies_with_keyword(params, "python")


if __name__ == "__main__":
    main()

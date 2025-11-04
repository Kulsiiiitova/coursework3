import psycopg2
import requests
import json


def get_employer_id(company_name: str) -> str:
    """Находит ID работодателя по названию компании"""
    url = "https://api.hh.ru/employers"
    params = {"text": company_name, "only_with_vacancies": True}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        items = response.json().get("items", [])
        if items:
            return items[0]["id"]
    return None


def save_data_to_database(
    data: list[dict], database_name: str, params: dict, companies
):
    """Сохранение данных о вакансиях в базу данных."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:

        for company_name, company_id in companies:
            cur.execute(
                """
                INSERT INTO company (company_id, company_name)
                VALUES (%s, %s)
                ON CONFLICT (company_id) DO NOTHING
                """,
                (company_id, company_name),
            )
        for item in data:
            cur.execute(
                """
                INSERT INTO vacancy (company_name, company_id, name, salary, url_vacancy, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    item["company"],
                    item["company_id"],
                    item["name"],
                    item["salary"],
                    item["url"],
                    item.get("description"),
                ),
            )

        conn.commit()
        conn.close()


def get_json(file_name, data):
    """ Функция, которая сохраняет данные в json-файл"""
    with open(file_name, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
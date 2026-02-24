import psycopg2

from src.employer_id import get_json


class DBManager:
    """Класс для работы с БД postgre"""

    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def create_database(self, params: dict) -> None:
        """ Метод, который создает базу данных"""
        conn = psycopg2.connect(dbname="postgres", **params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"DROP DATABASE {self.db_name}")
        cur.execute(f"CREATE DATABASE {self.db_name}")

        conn = psycopg2.connect(dbname=f"{self.db_name}", **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE company (
                    company_id int PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL UNIQUE
                )
            """
            )

        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE vacancy (
                    vacancy_id SERIAL PRIMARY KEY ,
                    company_name VARCHAR,
                    company_id INT REFERENCES company(company_id),
                    name VARCHAR NOT NULL,
                    salary int,
                    url_vacancy text,
                    description text
                )
            """
            )
        cur.close()
        conn.commit()
        conn.close()

    def get_companies_and_vacancies_count(self, params: dict) -> None:
        """ Метод, который получает список всех компаний и количество вакансий у каждой компании."""
        conn = psycopg2.connect(dbname=self.db_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT company.company_name, COUNT(*) FROM vacancy JOIN company USING (company_id)
                GROUP BY company.company_name
                """
            )
            result = cur.fetchall()
        conn.close()
        get_json('json/companies_and_vacancies_count.json', result)

    def get_all_vacancies(self, params: dict) -> None:
        """ Метод, который получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию."""
        conn = psycopg2.connect(dbname=self.db_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT company.company_name, name, salary, url_vacancy FROM vacancy JOIN company USING (company_id)
                """
            )
            result = cur.fetchall()
        conn.close()
        get_json('json/all_vacancies.json', result)

    def get_avg_salary(self, params: dict) -> float:
        """ Метод, который получает среднюю зарплату по вакансиям."""
        conn = psycopg2.connect(dbname=self.db_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG(salary) FROM vacancy
                """
            )
            result = cur.fetchone()[0]
        conn.close()
        return float(result)

    def get_vacancies_with_higher_salary(self, params: dict) -> None:
        """ Метод, который получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        conn = psycopg2.connect(dbname=self.db_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name FROM vacancy
                WHERE SALARY > (SELECT AVG(salary) FROM vacancy)
                """
            )
            result = cur.fetchall()
        conn.close()
        get_json('json/vacancies_with_higher_salary.json', result)

    def get_vacancies_with_keyword(self, params: dict, key: str) -> None:
        """ Метод, который получает список всех вакансий, в названии которых содержатся переданные в метод слова,
        например python."""
        conn = psycopg2.connect(dbname=self.db_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, description FROM vacancy
                WHERE LOWER(name) LIKE LOWER(%s)
                   OR LOWER(description) LIKE LOWER(%s)
                """,
                (f"%{key}%", f"%{key}%"),
            )
            result = cur.fetchall()
        conn.close()
        get_json('json/vacancies_with_keyword.json', result)

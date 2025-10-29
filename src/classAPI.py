import requests


class HH:
    """
    Класс для работы с API HeadHunter
    Получение данных о вакансиях
    """

    def __init__(self) -> None:
        self.url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"employer_id": "", "page": 0, "per_page": 100}

    def load_vacancies(self, employers: list) -> list:
        """Загружает вакансии по ключевому слову из API HeadHunter"""
        vacanties = []
        for employer_id in employers:
            self.params["employer_id"] = employer_id
            response = requests.get(self.url, headers=self.headers, params=self.params)
            vacanties.extend(response.json().get("items", []))
        return vacanties

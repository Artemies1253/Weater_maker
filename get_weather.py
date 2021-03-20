import requests
from bs4 import BeautifulSoup
import re

temperature_day_pattern = re.compile(r'([\+\-]?\d*°)')
structured_day_info_pattern = re.compile(r'(\S\w+)')
day_pattern = re.compile(r'\d+')
month_pattern = re.compile(r'\w{3}')
CONVERT_NAME_MONTH_IN_NUMBER = {'Авг': '08', 'Апр': '04', 'Дек': '12', 'Июл': '07', 'Июн': '06', 'Май': '05',
                                'Мар': '03', 'Ноя': '11', 'Окт': '10', 'Сен': '09', 'Фев': '02', 'Янв': '01'}
YEAR_UPDAIT = "2021"


class WeatherMaker:
    """Парсит сайт погоды маил.ру, возвращает информацию за запрашиваемые месяц,
     месяц спрашивается форматом ХХ числом, например 4 или 11"""

    def __init__(self, number_month):
        self.number_month = str(number_month)
        self.corected_number_month()
        self.weather_on_month = dict()
        self.url_months_of_year = dict()
        self.updait_url_month_of_year()

    def run(self):
        self.give_info_of_month(self.number_month)
        return self.weather_on_month

    def updait_url_month_of_year(self, year_url=f'https://pogoda.mail.ru/prognoz/voronezh/february-{YEAR_UPDAIT}/'):
        """Обновление url месяцов за год"""
        response = requests.get(url=year_url)
        if response.status_code == 200:
            html_doc = BeautifulSoup(response.content, features="html.parser")
            months_info = html_doc.find_all('div', {'class': "month-menu__month"})
            for month_info in months_info:
                teg_a = month_info.find('a')
                url = 'https://pogoda.mail.ru' + teg_a.get('href')
                month_name = re.findall(month_pattern, month_info.text)[0]
                self.url_months_of_year[CONVERT_NAME_MONTH_IN_NUMBER[month_name]] = url

    def give_info_of_month(self, number_month):
        """Возвращает информацию за месяц"""
        self.weather_on_month = dict()
        month_url = self.url_months_of_year[number_month]
        response = requests.get(url=month_url)
        if response.status_code == 200:
            html_doc = BeautifulSoup(response.content, features="html.parser")
            days_gone_by_info = html_doc.find_all('div', {'class': "day day_calendar"})
            self.extract_information(days_gone_by_info)
            future_days_info = html_doc.find_all('div', {'class': "day day_calendar day_current"})
            self.extract_information(future_days_info)
            return self.weather_on_month

    def extract_information(self, days_info):
        """Извлекает и возвращает информацию за определенное количество дней"""
        for day_info in days_info:
            structured_day_info = dict()
            data = day_info.find('div', {'class': 'day__date'})
            day = re.findall(day_pattern, data.text)[0]
            temperature_day = day_info.find('div', {'class': 'day__temperature'})
            temperature_day = re.findall(temperature_day_pattern, temperature_day.text)[0]
            temperature_night = day_info.find('span', {'class': 'day__temperature__night'})
            structured_day_info['temperature_day'] = temperature_day
            structured_day_info['temperature_night'] = temperature_night.text
            day_description = day_info.find('div', {'class': 'day__description'})
            if day_description:
                day_description = re.findall(structured_day_info_pattern, day_description.text)[0]
            else:
                day_description = "Не определенно"
            structured_day_info["day_description"] = day_description
            self.weather_on_month[day] = structured_day_info

    def corected_number_month(self):
        """Превращает число в вид ХХ если оно вида 1-9"""
        if len(self.number_month) == 1:
            self.number_month = "0" + str(self.number_month)


if __name__ == "__main__":
    weather_maker = WeatherMaker("2")
    weather_maker.run()

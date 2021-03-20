from get_weather import WeatherMaker
from _datetime import date, timedelta
from pony.orm import db_session
import handlers
from models import Weather
import calendar
from draw_weather import DrawWeather


class UserInterface:
    """Класс отвечающий за взаимодействие с пользователем"""

    def __init__(self, user_answer=None):
        self.weather_on_months = dict()
        self.user_answer = user_answer
        self.today = date.today()
        self.next_week = self.today + timedelta(days=7)
        self.update_bd_on_1_week()

    def update_bd_on_1_week(self):
        """Обновление базы данных на одну неделю, вызывается при запуске класса"""
        date_from = self.today
        date_to = self.next_week
        dates = {"date_from": date_from, "date_to": date_to}
        self.get_weather_of_data(dates)
        self.update_bd(
            data_from=dates["date_from"],
            data_to=dates["date_to"]
        )

    def run(self):
        """Выбор сценария пользователя"""
        print('Вы можете:'
              '\n1. Обновить базу данных'
              '\n2. Посмотреть прогноз погоды в консольной строке'
              '\n3. Посмотреть прогноз погоды в открытке')
        self.user_answer = str(input())
        self.update_bd_on_1_week()
        if self.user_answer == "1":
            self.scenario_update_bd()
        if self.user_answer == "2":
            self.scenario_write_from_bd_to_console()
        if self.user_answer == "3":
            self.scenario_draw_weather()

    def scenario_update_bd(self):
        """Обновляет базу данных за запрашиваемый промежуток времени"""
        dates_of_user = self.give_dates_of_user()
        self.get_weather_of_data(dates_of_user)
        self.update_bd(
            data_from=dates_of_user["date_from"],
            data_to=dates_of_user["date_to"]
        )

    def scenario_write_from_bd_to_console(self):
        """Пишет на консоль с базы данных прогноз погоды за запрашиваемый промежуток времени"""
        dates_of_user = self.give_dates_of_user()
        self.write_to_console_period(
            data_from=dates_of_user["date_from"],
            data_to=dates_of_user["date_to"]
        )

    def scenario_draw_weather(self):
        """Рисует прогноз погоды в виде открытки с базы данных прогноз погоды за запрашиваемый промежуток времени"""
        dates_of_user = self.give_dates_of_user()
        draw_weather = DrawWeather(
            data_from=dates_of_user["date_from"],
            data_to=dates_of_user["date_to"]
        )
        draw_weather.run()

    def give_dates_of_user(self):
        """Спрашивает пользователя дату, возвращает словарь с 2 элементов
        date_from - объекта date начало диапазона, date_to объекта date конец диапазона"""
        dates_of_user = None
        while not dates_of_user:
            message_for_user = 'Введите диапозон дат, данные которых в хотите получить из базы данных\n' \
                               "Формат ввода должен быть вида dd-mm:dd-mm\n" \
                               "Например 18-02:25-02\n"
            print(message_for_user)
            self.user_answer = str(input())
            dates_of_user = handlers.handler_date_of_user(user_answer=self.user_answer)
            return dates_of_user

    def get_weather_of_data(self, dates_of_user):
        """Заполняет словать weather_on_months, добавляет в него всю погоду за запрашиваемые месяца"""
        self.weather_on_months = dict()
        data_from = dates_of_user["date_from"]
        data_to = dates_of_user["date_to"]
        month_from = data_from.month
        month_to = data_to.month
        if month_from == month_to:
            weather_maker = WeatherMaker(month_from)
            weather_on_month = weather_maker.run()
            self.weather_on_months[str(month_from)] = weather_on_month
        elif month_to - month_from == 1:
            weather_maker = WeatherMaker(month_from)
            weather_on_month = weather_maker.run()
            self.weather_on_months[str(month_from)] = weather_on_month
            weather_maker = WeatherMaker(month_to)
            weather_on_month = weather_maker.run()
            self.weather_on_months[str(month_to)] = weather_on_month
        else:
            for number_month in range(month_from, month_to + 1, 1):
                weather_maker = WeatherMaker(number_month)
                weather_on_month = weather_maker.run()
                self.weather_on_months[str(number_month)] = weather_on_month

    def update_bd(self, data_from, data_to):
        """Обновляет базу данных за диапазон от data_from до data_to"""
        self.remove_extra_days(data_from, data_to)
        numbers_months = self.weather_on_months.keys()
        for number_month in numbers_months:
            self.wtite_month_in_bd(number_month, self.weather_on_months[number_month])

    def remove_extra_days(self, data_from, data_to):
        """Удаляет лишние дни в месяце(месяцах), которые не входят в диапазон"""
        day_from = data_from.day
        month_from = data_from.month
        day_to = data_to.day
        month_to = data_to.month
        keys_month_from = self.weather_on_months[str(month_from)].keys()
        keys_month_to = self.weather_on_months[str(month_to)].keys()
        keys_for_dalete = list()
        for key_month_from in keys_month_from:
            if int(key_month_from) < day_from:
                keys_for_dalete.append(key_month_from)
        for key_for_dalete in keys_for_dalete:
            self.weather_on_months[str(month_from)].pop(key_for_dalete)
        keys_for_dalete = list()
        for key_month_to in keys_month_to:
            if int(key_month_to) > day_to:
                keys_for_dalete.append(key_month_to)
        for key_for_dalete in keys_for_dalete:
            self.weather_on_months[str(month_to)].pop(key_for_dalete)

    @db_session
    def wtite_month_in_bd(self, number_month, weather_on_month):
        """Записывает в базу данных погоду месяца number_month"""
        if len(number_month) == 1:
            number_month = "0" + number_month
        days = weather_on_month.keys()
        for day in days:
            date = day + "-" + number_month
            temperature_day = weather_on_month[day]['temperature_day']
            temperature_night = weather_on_month[day]['temperature_night']
            day_description = weather_on_month[day]['day_description']
            day_info = Weather.get(date=date)
            if day_info:
                day_info.delete()
            Weather(date=date, temperature_day=temperature_day,
                    temperature_night=temperature_night, day_description=day_description)

    def write_to_console_period(self, data_from, data_to):
        """Выводит на консол погоду с базы данных от data_from до data_to"""
        write_first_line_to_console()
        self.weather_on_months = dict()
        day_from = data_from.day
        day_to = data_to.day
        month_from = data_from.month
        month_to = data_to.month
        max_day_month_from = calendar.monthrange(month=month_from, year=2021)[1]
        if month_from == month_to:
            write_month(day_from, day_to, month_from)
        elif month_to - month_from == 1:
            write_month(day_from, max_day_month_from, month_from)
            write_month(1, day_to, month_to)
        else:
            for number_month in range(month_from, month_to + 1, 1):
                max_day = calendar.monthrange(month=number_month, year=2021)[1]
                if number_month == month_from:
                    write_month(day_from, max_day, number_month)
                elif number_month != month_to:
                    write_month(1, max_day, number_month)
                else:
                    write_month(1, day_to, number_month)


@db_session
def write_month(start_day, end_day, number_month):
    """Пишет на консоль погоду с баззы данных месяца number_month от start_day до end_day"""
    for day in range(start_day, end_day + 1, 1):
        if len(str(number_month)) == 1:
            number_month = "0" + str(number_month)
        date = str(day) + "-" + str(number_month)
        weater_one_day = Weather.get(date=date)
        write_to_console_1_day(weater_one_day, date)


def write_to_console_1_day(weater_one_day, date):
    """Пишет на консоль 1 день"""
    if not weater_one_day:
        print(f'|{"Нет данных за":>35} : {date:<30} {" " * 3}|')
        print('-' * 73)
        return
    print(f'|{" " * 17}|{" " * 17}|{" " * 17}|{" " * 17}|')
    print(f'|{weater_one_day.date:^17}|{weater_one_day.temperature_day:^17}'
          f'|{weater_one_day.temperature_night:^17}|{weater_one_day.day_description:^17}|')
    print(f'|{" " * 17}|{" " * 17}|{" " * 17}|{" " * 17}|')
    print('-' * 73)


def write_first_line_to_console():
    """Пишет на консоль начало таблицы"""
    print('_' * 73)
    print(f'|{" " * 17}|{" " * 17}|{" " * 17}|{" " * 17}|')
    print(f'|{"date":^17}|{"temperature_day":^17}|{"temperature_night":^17}|{"day_description":^17}|')
    print(f'|{" " * 17}|{" " * 17}|{" " * 17}|{" " * 17}|')
    print('-' * 73)


if __name__ == "__main__":
    interface = UserInterface()
    interface.run()

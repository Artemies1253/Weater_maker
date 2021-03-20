from _datetime import date
import re


def handler_date_of_user(user_answer):
    """Проверяет корректность веденных данных пользователем и возвращает словарь из 2 элементов
    date_from - объекта date начало диапазона, date_to объекта date конец диапазона"""
    try:
        date_from, date_to = re.split(r':', user_answer)
        day_date_from, month_date_from = re.split(r'-', date_from)
        day_date_to, month_date_to = re.split(r'-', date_to)
        date_from = date(day=int(day_date_from), month=int(month_date_from), year=2021)
        date_to = date(day=int(day_date_to), month=int(month_date_to), year=2021)
        user_answer = {'date_from': date_from, 'date_to': date_to}
        return user_answer
    except Exception():
        print(f'{user_answer}, дата не соответствует виду dd-mm')


if __name__ == "__main__":
    user_answer = '18-02:25-02'
    result = handler_date_of_user(user_answer=user_answer)
    print(result)

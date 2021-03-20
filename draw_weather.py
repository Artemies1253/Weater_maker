import calendar
from models import Weather
from pony.orm import db_session
import cv2

WHITE = (255, 255, 255)
BLUE = (250, 12, 0)
LIGHT_BLUE = (224, 150, 0)
YELLOW = (0, 255, 255)
GREY = (112, 112, 112)
FONT_ON_DAY = "weather_img/font_on_day.jpg"
FONT_ON_WEEK = "weather_img/font_on_week.jpg"
ICON_CLOUD = "weather_img/cloud.jpg"
ICON_RAIN = "weather_img/rain.jpg"
ICON_SNOW = "weather_img/snow.jpg"
ICON_SUN = "weather_img/sun.jpg"


class DrawWeather:
    """Рисует открытку прогноза погоды на неделю"""

    def __init__(self, data_from, data_to):
        self.data_from = data_from
        self.data_to = data_to
        self.image_day = None
        self.drawn_week = list()

    def run(self):
        try:
            self.draw_weather_on_one_week()
            image_week = draw_wether_week(self.drawn_week)
            viewImage(image_week, "week")
        except IndexError:
            print("Данных в базе данных нет за эти числа, обновите пожалуйста базу данных")

    def draw_weather_on_one_week(self):
        """Рисует прогноз погоды на неделю"""
        day_from = self.data_from.day
        day_to = self.data_to.day
        month_from = self.data_from.month
        month_to = self.data_to.month
        max_day_month_from = calendar.monthrange(month=month_from, year=2021)[1]
        if month_from == month_to:
            self.draw_one_week_to_the_list(day_from, day_to, month_from)
        else:
            self.draw_one_week_to_the_list(day_from, max_day_month_from, month_from)
            self.draw_one_week_to_the_list(1, day_to, month_to)

    @db_session
    def draw_one_week_to_the_list(self, start_day, end_day, number_month):
        """Заполняет пустой список, состоящий из 7 изображений, соответствующий 7 дням"""
        for day in range(start_day, end_day + 1, 1):
            if len(self.drawn_week) == 7:
                return
            if len(str(number_month)) == 1:
                number_month = "0" + str(number_month)
            date = str(day) + "-" + str(number_month)
            weater_one_day = Weather.get(date=date)
            if weater_one_day:
                self.image_day = None
                self.draw_one_day(weater_one_day, date)
                self.drawn_week.append(self.image_day)

    def draw_wether_week(self):
        """Рисуется неделя из списка 7 дней"""
        image_week = cv2.imread(FONT_ON_WEEK)
        left_pixcel = int(1)
        right_pixcel = int(269)
        top_pixcel = int(1)
        dawn_pixcel = int(253)
        pixcel_x_day = 0
        for image_day in self.drawn_week:
            for x in range(left_pixcel, right_pixcel - 1, 1):
                pixcel_y_day = -1
                pixcel_x_day += 1
                for y in range(dawn_pixcel, top_pixcel - 1, 1):
                    pixcel_y_day += 1
                    image_week[x, y] = image_day[pixcel_x_day, pixcel_y_day]

    def draw_one_day(self, weater_one_day, date):
        """Рисуется 1 день"""
        day_description = weater_one_day.day_description
        temperature_day = "temperature_day" + weater_one_day.temperature_day
        temperature_night = "temperature_night" + weater_one_day.temperature_night
        self.make_background_day(day_description=day_description)
        cv2.putText(self.image_day, date, (60, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0))
        cv2.putText(self.image_day, temperature_day[:-1], (20, 195), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0))
        cv2.putText(self.image_day, temperature_night[:-1], (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0))

    def make_background_day(self, day_description):
        """Заполняет background дня согласно погоде"""
        if day_description:
            if day_description == "ясно":
                self.make_background(icon=ICON_SUN, color_left=YELLOW)
            elif day_description == "снег" or day_description == "метель":
                self.make_background(icon=ICON_SNOW, color_left=LIGHT_BLUE)
            elif day_description == "облачно":
                self.make_background(icon=ICON_CLOUD, color_left=GREY)
            elif day_description == "дождь":
                self.make_background(icon=ICON_RAIN, color_left=BLUE)

    def make_background(self, icon, color_left):
        """Заполняет background, в центр дня помещает icon, цвет color_left слева переходит в белый"""
        self.image_day = cv2.imread(FONT_ON_DAY)
        image_icon = cv2.imread(icon)
        make_gradient(self.image_day, color_left, WHITE)
        paste_image(self.image_day, image_icon)


def viewImage(image, name_of_window):
    """Выводит изображение на экран в виде окна"""
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def make_gradient(image, left_side, right_side):
    """Заполняет градиент"""
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            koef_conversion = y / image.shape[1]
            image[x, y] = (left_side[0] - (left_side[0] - right_side[0]) * koef_conversion,
                           left_side[1] - (left_side[1] - right_side[1]) * koef_conversion,
                           left_side[2] - (left_side[2] - right_side[2]) * koef_conversion)


def paste_image(image_big, image_small):
    """Вставляет в центр image_big картинку image_small"""
    left_pixcel = int(image_big.shape[0] / 2 - image_small.shape[0] / 2)
    right_pixcel = int(image_big.shape[0] / 2 + image_small.shape[0] / 2)
    top_pixcel = int(image_big.shape[1] / 2 + image_small.shape[1] / 2)
    dawn_pixcel = int(image_big.shape[1] / 2 - image_small.shape[1] / 2)
    pixcel_x_small = 0
    for x in range(left_pixcel, right_pixcel - 1, 1):
        pixcel_y_small = -1
        pixcel_x_small += 1
        for y in range(dawn_pixcel, top_pixcel - 1, 1):
            pixcel_y_small += 1
            image_big[x, y] = image_small[pixcel_x_small, pixcel_y_small]


def draw_wether_week(week):
    """Рисует неделю из списка week, возвращая изображение недели"""
    image_week = cv2.imread(FONT_ON_WEEK)
    image_day = week[0]
    width_image_day = int(image_day.shape[1])
    height_image_day = int(image_day.shape[0])
    dawn_pixcel = int(0)
    top_pixcel = width_image_day
    rigth_pixcel = height_image_day
    left_pixcel = int(0)
    pixcel_y_day = -1
    for image_day in week:
        for y in range(dawn_pixcel, top_pixcel - 1, 1):
            pixcel_x_day = 0
            pixcel_y_day += 1
            for x in range(left_pixcel, rigth_pixcel - 1, 1):
                image_week[x, y] = image_day[pixcel_x_day, pixcel_y_day]
                pixcel_x_day += 1
        dawn_pixcel += width_image_day
        top_pixcel += width_image_day
        pixcel_y_day = -1
    return image_week

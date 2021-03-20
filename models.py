from pony.orm import Database, Required

db = Database()
db.bind(
    provider="sqlite",
    filename="weather.db",
    create_db=True
)


class Weather(db.Entity):
    """Погода"""
    date = Required(str)
    temperature_day = Required(str)
    temperature_night = Required(str)
    day_description = Required(str)


db.generate_mapping(create_tables=True)

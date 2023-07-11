import json


class Settings:
    def __init__(self, path: str) -> None:
        with open(path, "rt") as f:
            obj = json.load(f)
            self.MAX_CURRENCY_LEN = obj["MAX_CURRENCY_LEN"]
            self.LOGGER_FORMAT = obj["LOGGER_FORMAT"]
            self.APP_LOG_LEVEL = obj["log_level"]["app"]
            self.TELEBOT_LOG_LEVEL = obj["log_level"].get("telebot", "warning")
            self.SQLALCHEMY_ENGINE_LOG_LEVEL = obj["log_level"].get(
                "sqlalchemy.engine", "warning"
            )
            self.BOT_TOKEN = obj["BOT_TOKEN"]
            self.CHANGE_CREDIT_PATTERN = obj["CHANGE_CREDIT_PATTERN"]
            self.SUPER_ADMIN_ID = int(obj["SUPER_ADMIN_ID"])
            self.SQLALCHEMY_DATABASE_URI = obj["SQLALCHEMY_DATABASE_URI"]
            self.MAX_BALLS_ROWS = int(obj["MAX_BALLS_ROWS"])
            self.POINTS_REFILL_RATE = self.__parse_refill_rate(obj)
            self.POINTS_BURST_SIZE = int(obj["POINTS_BURST_SIZE"])

    def __parse_refill_rate(self, obj) -> float:
        tup = tuple(map(float, obj["POINTS_REFILL_RATE"].split("/", 2)))
        return tup[0] / tup[1]


settings = Settings("app.json")

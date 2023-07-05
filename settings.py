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
            self.DELTA_LIMIT = int(obj["DELTA_LIMIT"])
            self.SQLALCHEMY_DATABASE_URI = obj["SQLALCHEMY_DATABASE_URI"]
            self.MAX_BALLS_ROWS = int(obj["MAX_BALLS_ROWS"])


settings = Settings("app.json")

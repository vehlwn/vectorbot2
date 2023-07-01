import dotenv
import os

dotenv.load_dotenv()

MAX_CURRENCY_LEN = int(os.environ["MAX_CURRENCY_LEN"])
LOGGER_FORMAT = os.environ["LOGGER_FORMAT"]
LOG_LEVEL = os.environ["LOG_LEVEL"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANGE_CREDIT_PATTERN = os.environ["CHANGE_CREDIT_PATTERN"]
SUPER_ADMIN_ID = int(os.environ["SUPER_ADMIN_ID"])
DELTA_LIMIT = int(os.environ["DELTA_LIMIT"])
SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]

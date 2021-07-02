import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(".env")

VIBER_TOKEN = os.environ.get("VIBER_TOKEN")
WIT_TOKEN = os.environ.get("WIT_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")


class Configuration(object):
    DEBUG = os.environ.get('DEBUG', default=1)
    HOST = os.environ.get('HOST', default='0.0.0.0')
    PORT = os.environ.get('PORT', default=443)
    SERVER_NAME = f"{HOST}:{PORT}"

from dotenv import load_dotenv
import os

load_dotenv()


VERIFIED_USERS = set(map(int, os.getenv('VERIFIED_USERS').split(",")))
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_ID = int(TELEGRAM_BOT_TOKEN.split(":")[0])
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

event_handler = set()
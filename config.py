import logging
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

BOT_TOKEN = "7658302656:AAE7eVURsYVSrDxil0GdJFOwFWwdb6gLiZ8"
BOT_OWNER = "@YourUsernameHere"
BOT_USERNAME = None
BOT_ID = None

CLEANUP_DELAY = 9999999999999999999989999999999
ALLOWED_TYPES = ['group', 'supergroup']

bot = TeleBot(BOT_TOKEN, state_storage=StateMemoryStorage())

logger = logging.getLogger('BotLogger')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
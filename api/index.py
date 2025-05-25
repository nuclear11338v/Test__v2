import os
from flask import Flask, request
import telebot

API_TOKEN = os.getenv('BOT_TOKEN')  # Ensure this environment variable is set in Vercel
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/', methods=['GET'])
def index():
    return 'Bot is alive', 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('VERCEL_URL')}/")
    app.run(host="0.0.0.0", port=8080)

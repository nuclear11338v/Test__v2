from flask import Flask, request
import os
import sys
import importlib

# Add root directory to path so we can import main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import bot  # Import your bot instance from main.py

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = bot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/', methods=['GET'])
def index():
    return 'Bot is alive', 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('VERCEL_URL')}/")
    app.run(host="0.0.0.0", port=8080)

from config import bot, logger
from kick import disabled
import telebot
import json
import os
import time
from functools import wraps
from ban_sticker_pack.ban_sticker_pack import is_allowed, is_admin
from kick import disabled
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group
SETTINGS_FILE = 'cleancommand.json'

if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump({}, f)

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")


@bot.message_handler(regexp=r'^[\/!](cleancommandtypes)(?:\s|$|@)')
@disabled
@is_admin
@is_allowed
def command_cleancommandtype(message):
    types = "Available types for /cleancommand and /keepcommand:\n- admin\n- user\n- all"
    bot.reply_to(message, types)

@bot.message_handler(regexp=r'^[\/!](cleancommand)(?:\s|$|@)')
@disabled
@is_admin
@is_allowed
def command_cleancommand(message):
    chat_id = str(message.chat.id)
    
    try:
        command_type = message.text.split()[1].lower() if len(message.text.split()) > 1 else None
        
        if command_type not in ['admin', 'user', 'all']:
            bot.reply_to(message, "Invalid type. Use: /cleancommand [admin|user|all]")
            return
        
        settings = load_settings()
        
        if chat_id not in settings or not isinstance(settings[chat_id], dict):
            settings[chat_id] = {}
        
        settings[chat_id]['cleancommand'] = command_type
        save_settings(settings)
        
        bot.reply_to(message, f"Set /cleancommand to delete {command_type} command messages.")
    
    except IndexError:
        bot.reply_to(message, "Please specify a type: /cleancommand [admin|user|all]")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(regexp=r'^[\/!](keepcommand)(?:\s|$|@)')
@disabled
@is_admin
@is_allowed
def command_keepcommand(message):
    chat_id = str(message.chat.id)
    
    try:
        command_type = message.text.split()[1].lower() if len(message.text.split()) > 1 else None
        
        if command_type not in ['admin', 'user', 'all']:
            bot.reply_to(message, "Invalid type. Use: /keepcommand [admin|user|all]")
            return
        
        settings = load_settings()
        
        if chat_id not in settings or not isinstance(settings[chat_id], dict):
            settings[chat_id] = {}
        
        settings[chat_id]['keepcommand'] = command_type
        save_settings(settings)
        
        bot.reply_to(message, f"Set /keepcommand to keep {command_type} command messages.")
    
    except IndexError:
        bot.reply_to(message, "Please specify a type: /keepcommand [admin|user|all]")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

import json
import time
from datetime import datetime, timedelta
from functools import wraps
import re
from telebot.types import Message
from kick import disabled
from config import bot
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group

MAX_WARN = 3
DATA_FILE = 'warnings.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

data = load_data()

def parse_time(time_str):
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'mo': 2592000, 'y': 31536000}
    match = re.match(r'^(\d+)([smhdw]|mo|y)$', time_str)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    return value * time_units[unit]

def get_user(message: Message):
    try:
        if message.reply_to_message:
            return message.reply_to_message.from_user
        text = message.text.split()
        if len(text) < 2:
            return None
        target = text[1]
        try:
            if target.startswith('@'):
                try:
                    with open('data/data.json', 'r') as file:
                        users = json.load(file)
                    username = target[1:].lower()
                    for user in users:
                        if user.get('username', '').lower() == username:
                            return bot.get_chat_member(message.chat.id, int(user['user_id'])).user
                    bot.reply_to(message, "User not found. Please use /warn [reply] or /warn [user_id]")
                    return None
                except FileNotFoundError:
                    bot.reply_to(message, "User data file not found. Please use /warn [reply] or /warn [user_id]")
                    return None
                except json.JSONDecodeError:
                    bot.reply_to(message, "Error reading user data. Please use /warn [reply] or /warn [user_id]")
                    return None
            return bot.get_chat_member(message.chat.id, int(target)).user
        except ValueError:
            bot.reply_to(message, "Invalid user ID or username format!")
            return None
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(message.chat.id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return None
            raise
    except Exception as e:
        bot.reply_to(message, f"Error getting user: {str(e)}")
        return None

def init_chat_data(chat_id):
    chat_id = str(chat_id)
    if chat_id not in data:
        data[chat_id] = {
            'warnings': {},
            'settings': {
                'warn_limit': MAX_WARN,
                'warn_mode': 'mute',
                'warn_time': 86400
            }
        }
        save_data(data)

def warn_user(message, chat_id, user_id, reason, silent=False, delete=False):
    init_chat_data(chat_id)
    chat_id, user_id = str(chat_id), str(user_id)
    user_data = data[chat_id]['warnings'].setdefault(user_id, {'count': 0, 'reasons': [], 'expires': None})
    
    user_data['count'] += 1
    user_data['reasons'].append(reason or "No reason provided")
    
    warn_time = data[chat_id]['settings']['warn_time']
    if warn_time:
        user_data['expires'] = (datetime.now() + timedelta(seconds=warn_time)).timestamp()
    
    try:
        user = bot.get_chat_member(chat_id, user_id).user
        user_mention = f"[{user.first_name}](tg://user?id={user_id})"
    except:
        user_mention = f"User ID {user_id}"
    
    if not silent:
        bot.reply_to(message, f"User {user_mention} warned ({user_data['count']}/{data[chat_id]['settings']['warn_limit']}): {reason or 'No reason provided'}", parse_mode='Markdown')
    
    save_data(data)
    
    if user_data['count'] >= data[chat_id]['settings']['warn_limit']:
        mode = data[chat_id]['settings']['warn_mode']
        
        if mode == 'ban':
            bot.ban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"{user_mention} banned due to reaching warn limit", parse_mode='Markdown')
        elif mode == 'kick':
            bot.ban_chat_member(chat_id, user_id)
            bot.unban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"{user_mention} kicked due to reaching warn limit", parse_mode='Markdown')
        elif mode == 'mute':
            bot.restrict_chat_member(chat_id, user_id, 
                                  until_date=int(time.time() + warn_time),
                                  can_send_messages=False)
            bot.send_message(chat_id, f"{user_mention} muted due to reaching warn limit", parse_mode='Markdown')
        
        user_data['count'] = 0
        user_data['reasons'] = []
        user_data['expires'] = None
        save_data(data)

@bot.message_handler(regexp=r'^[\/!](warn)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_warn(message: Message):
    user = get_user(message)
    if not user:
        bot.reply_to(message, "Please reply to a message or provide a user ID/username (e.g., /warn @username [reason] or /warn 123456 [reason])")
        return
    text = message.text.split()
    reason = None
    if message.reply_to_message:
        reason = ' '.join(text[1:]) if len(text) > 1 else None
    elif len(text) > 2:
        reason = ' '.join(text[2:])
    warn_user(message, message.chat.id, user.id, reason)

@bot.message_handler(regexp=r'^[\/!](swarn)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_swarn(message: Message):
    user = get_user(message)
    if not user:
        bot.reply_to(message, "Please reply to a message or provide a user ID/username (e.g., /swarn @username [reason] or /swarn 123456 [reason])")
        return
    text = message.text.split()
    reason = None
    if message.reply_to_message:
        reason = ' '.join(text[1:]) if len(text) > 1 else None
    elif len(text) > 2:
        reason = ' '.join(text[2:])
    warn_user(message, message.chat.id, user.id, reason, silent=True)
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(regexp=r'^[\/!](dwarn)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_dwarn(message: Message):
    user = get_user(message)
    if not user:
        bot.reply_to(message, "Please reply to a message or provide a user ID/username (e.g., /dwarn @username [reason] or /dwarn 123456 [reason])")
        return
    text = message.text.split()
    reason = None
    if message.reply_to_message:
        reason = ' '.join(text[1:]) if len(text) > 1 else None
    elif len(text) > 2:
        reason = ' '.join(text[2:])
    if message.reply_to_message:
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)
    warn_user(message, message.chat.id, user.id, reason, delete=True)

@bot.message_handler(regexp=r'^[\/!](rmwarn)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def remove_warn_command(message: Message):
    user = get_user(message)
    if not user:
        bot.reply_to(message, "Please reply to a message or provide a user ID/username (e.g., /rmwarn @username or /rmwarn 123456)")
        return
    chat_id, user_id = str(message.chat.id), str(user.id)
    init_chat_data(chat_id)
    
    if user_id in data[chat_id]['warnings'] and data[chat_id]['warnings'][user_id]['count'] > 0:
        data[chat_id]['warnings'][user_id]['count'] -= 1
        data[chat_id]['warnings'][user_id]['reasons'].pop()
        save_data(data)
        bot.reply_to(message, f"Removed one warning from user")
    else:
        bot.reply_to(message, "User has no warnings")

@bot.message_handler(regexp=r'^[\/!](resetwarn)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_resetwarn(message: Message):
    user = get_user(message)
    if not user:
        bot.reply_to(message, "Please reply to a message or provide a user ID/username (e.g., /resetwarn @username or /resetwarn 123456)")
        return
    chat_id, user_id = str(message.chat.id), str(user.id)
    init_chat_data(chat_id)
    
    if user_id in data[chat_id]['warnings']:
        data[chat_id]['warnings'][user_id] = {'count': 0, 'reasons': [], 'expires': None}
        save_data(data)
        bot.reply_to(message, "User warnings reset")

@bot.message_handler(regexp=r'^[\/!](resetallwarnings)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_resetallwarnings(message: Message):
    chat_id = str(message.chat.id)
    init_chat_data(chat_id)
    data[chat_id]['warnings'] = {}
    save_data(data)
    bot.reply_to(message, "All warnings reset for this chat")

@bot.message_handler(regexp=r'^[\/!](warnings)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_warnings(message: Message):
    chat_id = str(message.chat.id)
    init_chat_data(chat_id)
    settings = data[chat_id]['settings']
    response = (f"Warning Settings:\n"
                f"Warn Limit: {settings['warn_limit']}\n"
                f"Warn Mode: {settings['warn_mode']}\n"
                f"Warn Time: {settings['warn_time']//86400}d")
    bot.reply_to(message, response)

@bot.message_handler(regexp=r'^[\/!](warningmode)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_warningmode(message: Message):
    modes = ['ban', 'mute', 'kick']
    mode = message.text.split()[1].lower() if len(message.text.split()) > 1 else None
    if mode not in modes:
        bot.reply_to(message, f"Invalid mode. Use: {', '.join(modes)}")
        return
    chat_id = str(message.chat.id)
    init_chat_data(chat_id)
    data[chat_id]['settings']['warn_mode'] = mode
    save_data(data)
    bot.reply_to(message, f"Warning mode set to {mode}")

@bot.message_handler(regexp=r'^[\/!](warnlimit)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_warnlimit(message: Message):
    try:
        limit = int(message.text.split()[1])
        if limit < 1:
            raise ValueError
    except:
        bot.reply_to(message, "Please provide a valid number")
        return
    chat_id = str(message.chat.id)
    init_chat_data(chat_id)
    data[chat_id]['settings']['warn_limit'] = limit
    save_data(data)
    bot.reply_to(message, f"Warn limit set to {limit}")

@bot.message_handler(regexp=r'^[\/!](warntime)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_warntime(message: Message):
    chat_id = str(message.chat.id)
    init_chat_data(chat_id)
    
    if len(message.text.split()) == 1:
        current_time = data[chat_id]['settings']['warn_time']
        bot.reply_to(message, f"Current warn time: {current_time//86400}d")
        return
    
    time_str = message.text.split()[1]
    seconds = parse_time(time_str)
    if not seconds:
        bot.reply_to(message, "Invalid time format. Use: 1s, 2m, 3h, 4d, 5w, 6mo, 7y")
        return
    
    data[chat_id]['settings']['warn_time'] = seconds
    save_data(data)
    bot.reply_to(message, f"Warn time set to {time_str}")

def cleanup_expired_warnings():
    while True:
        current_time = datetime.now().timestamp()
        for chat_id in data:
            for user_id in list(data[chat_id]['warnings']):
                if data[chat_id]['warnings'][user_id].get('expires') and current_time > data[chat_id]['warnings'][user_id]['expires']:
                    data[chat_id]['warnings'][user_id] = {'count': 0, 'reasons': [], 'expires': None}
        save_data(data)
        time.sleep(3600)

import threading
threading.Thread(target=cleanup_expired_warnings, daemon=True).start()
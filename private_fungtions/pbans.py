import telebot
from telebot import types
import json
from functools import wraps
from typing import Optional, Union
import re
import time
from datetime import datetime
from config import bot

def load_connections():
    try:
        with open('connections.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def is_private(func):
    @wraps(func)
    def wrapper(message: types.Message, *args, **kwargs):
        if message.chat.type != 'private':
            bot.reply_to(message, "This command can only be used in private chats (bot DMs).")
            return
        return func(message, *args, **kwargs)
    return wrapper

def has_connections(func):
    @wraps(func)
    def wrapper(message: types.Message, *args, **kwargs):
        user_id = str(message.from_user.id)
        connections = load_connections()
        if user_id not in connections or not connections[user_id]:
            bot.reply_to(message, "You have no connected groups. Use /connect to connect a group.")
            return
        return func(message, *args, **kwargs)
    return wrapper

def is_user_admin(chat_id: int, user_id: int) -> bool:
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except telebot.apihelper.ApiTelegramException:
        return False

def is_bot_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.user.is_bot
    except telebot.apihelper.ApiTelegramException:
        return False

def get_user_mention(user_id: int, chat_id: int) -> str:
    try:
        user = bot.get_chat_member(chat_id, user_id).user
        first_name = user.first_name or "Unknown"
        return f"[{first_name}](tg://user?id={user_id})"
    except telebot.apihelper.ApiTelegramException:
        return f"[User {user_id}](tg://user?id={user_id})"

def get_admin_mention(message: types.Message) -> str:
    admin_id = message.from_user.id
    first_name = message.from_user.first_name or "Unknown"
    return f"[{first_name}](tg://user?id={admin_id})"

def parse_duration(duration_str: str) -> Optional[int]:
    try:
        match = re.match(r'^(\d+)([smhdw])$', duration_str.lower())
        if not match:
            return None
        
        value, unit = int(match.group(1)), match.group(2)
        if value == 0:
            return None
            
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        elif unit == 'w':
            return value * 604800
        return None
    except Exception:
        return None

def format_ban_response(target_user_id, admin_user, chat_id, reason=None, duration=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_mention = get_user_mention(target_user_id, chat_id)
    admin_mention = get_admin_mention(admin_user)
    
    response = (
        f"✅ User Banned\n"
        f"By: {admin_mention}\n"
        f"User: {target_mention}\n"
        f"On {date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"
    if duration:
        duration_str = duration if isinstance(duration, str) else f"{duration // 86400}d" if duration >= 86400 else f"{duration // 3600}h" if duration >= 3600 else f"{duration // 60}m"
        response += f"\nDuration: {duration_str}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Unban",
        callback_data=f"unban_{target_user_id}_{chat_id}"
    ))
    return response, markup

def format_unban_response(target_user_id, admin_user, chat_id, reason=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_mention = get_user_mention(target_user_id, chat_id)
    admin_mention = get_admin_mention(admin_user)
    
    response = (
        f"✅ User Unbanned\n"
        f"By: {admin_mention}\n"
        f"User: {target_mention}\n"
        f"On {date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Ban",
        callback_data=f"ban_{target_user_id}_{chat_id}"
    ))
    return response, markup

@bot.message_handler(commands=['pban'])
@is_private
@has_connections
def command_ban(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Please provide a user ID (e.g., /ban 123456 [reason])")
            return
        
        user_id = args[1]
        reason = ' '.join(args[2:]) if len(args) > 2 else None
        
        if not user_id.isdigit():
            bot.reply_to(message, "Invalid user ID. Please provide a numeric user ID.")
            return
        
        user_id = int(user_id)
        connections = load_connections()
        user_connections = connections.get(str(message.from_user.id), [])
        
        if len(user_connections) == 1:
            chat_id = int(user_connections[0])
            perform_ban(message, user_id, chat_id, reason, silent=False)
        else:
            markup = types.InlineKeyboardMarkup()
            for group_id in user_connections:
                try:
                    group = bot.get_chat(group_id)
                    group_title = group.title or "Unknown Group"
                    markup.add(types.InlineKeyboardButton(
                        text=group_title,
                        callback_data=f"ban_{user_id}_{group_id}_{reason or ''}"
                    ))
                except telebot.apihelper.ApiTelegramException:
                    continue
            bot.reply_to(message, "Choose a group to ban the user from:", reply_markup=markup)
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['psban'])
@is_private
@has_connections
def command_psban(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Please provide a user ID (e.g., /psban 123456 [reason])")
            return
        
        user_id = args[1]
        reason = ' '.join(args[2:]) if len(args) > 2 else None
        
        if not user_id.isdigit():
            bot.reply_to(message, "Invalid user ID. Please provide a numeric user ID.")
            return
        
        user_id = int(user_id)
        connections = load_connections()
        user_connections = connections.get(str(message.from_user.id), [])
        
        if len(user_connections) == 1:
            chat_id = int(user_connections[0])
            perform_ban(message, user_id, chat_id, reason, silent=True)
        else:
            markup = types.InlineKeyboardMarkup()
            for group_id in user_connections:
                try:
                    group = bot.get_chat(group_id)
                    group_title = group.title or "Unknown Group"
                    markup.add(types.InlineKeyboardButton(
                        text=group_title,
                        callback_data=f"sban_{user_id}_{group_id}_{reason or ''}"
                    ))
                except telebot.apihelper.ApiTelegramException:
                    continue
            bot.reply_to(message, "Choose a group to silently ban the user from:", reply_markup=markup)
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['ptban'])
@is_private
@has_connections
def command_ptban(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "Usage: /ptban <user_id> [reason] <duration> (e.g., /ptban 123456 spam 1h)")
            return
        
        user_id = args[1]
        duration_str = args[-1]
        reason = ' '.join(args[2:-1]) if len(args) > 3 else None
        
        if not user_id.isdigit():
            bot.reply_to(message, "Invalid user ID. Please provide a numeric user ID.")
            return
        
        user_id = int(user_id)
        duration = parse_duration(duration_str)
        if not duration:
            bot.reply_to(message, "Invalid duration format! Use <number>[s|m|h|d|w] (e.g., 1h, 30m, 2d)")
            return
        
        if duration > 31622400:
            bot.reply_to(message, "Duration cannot exceed 366 days!")
            return
        
        connections = load_connections()
        user_connections = connections.get(str(message.from_user.id), [])
        
        if len(user_connections) == 1:
            chat_id = int(user_connections[0])
            perform_ban(message, user_id, chat_id, reason, silent=False, duration=duration, duration_str=duration_str)
        else:
            markup = types.InlineKeyboardMarkup()
            for group_id in user_connections:
                try:
                    group = bot.get_chat(group_id)
                    group_title = group.title or "Unknown Group"
                    markup.add(types.InlineKeyboardButton(
                        text=group_title,
                        callback_data=f"tban_{user_id}_{group_id}_{reason or ''}_{duration_str}"
                    ))
                except telebot.apihelper.ApiTelegramException:
                    continue
            bot.reply_to(message, "Choose a group to temporarily ban the user from:", reply_markup=markup)
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['punban'])
@is_private
@has_connections
def command_unban(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Please provide a user ID (e.g., /unban 123456 [reason])")
            return
        
        user_id = args[1]
        reason = ' '.join(args[2:]) if len(args) > 2 else None
        
        if not user_id.isdigit():
            bot.reply_to(message, "Invalid user ID. Please provide a numeric user ID.")
            return
        
        user_id = int(user_id)
        connections = load_connections()
        user_connections = connections.get(str(message.from_user.id), [])
        
        if len(user_connections) == 1:
            chat_id = int(user_connections[0])
            perform_unban(message, user_id, chat_id, reason)
        else:
            markup = types.InlineKeyboardMarkup()
            for group_id in user_connections:
                try:
                    group = bot.get_chat(group_id)
                    group_title = group.title or "Unknown Group"
                    markup.add(types.InlineKeyboardButton(
                        text=group_title,
                        callback_data=f"unban_{user_id}_{group_id}_{reason or ''}"
                    ))
                except telebot.apihelper.ApiTelegramException:
                    continue
            bot.reply_to(message, "Choose a group to unban the user from:", reply_markup=markup)
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

def perform_ban(message: types.Message, user_id: int, chat_id: int, reason: Optional[str], silent: bool = False, duration: Optional[int] = None, duration_str: Optional[str] = None):
    try:
        if not is_user_admin(chat_id, message.from_user.id):
            bot.reply_to(message, "You are no longer an admin in this group.")
            return
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Cannot ban an admin or creator!")
            return
        
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "Cannot ban a bot!")
            return
        
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "User is already banned!")
                return
        except telebot.apihelper.ApiTelegramException:
            pass
        
        if duration:
            until_date = int(time.time() + duration)
            bot.ban_chat_member(chat_id, user_id, until_date=until_date)
        else:
            bot.ban_chat_member(chat_id, user_id)
        
        response, markup = format_ban_response(user_id, message, chat_id, reason, duration_str or duration)
        if silent:
            bot.send_message(message.from_user.id, response, reply_markup=markup, parse_mode="Markdown")
        else:
            bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users in this group! Please check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Cannot ban an admin!")
        else:
            bot.reply_to(message, f"Error banning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

def perform_unban(message: types.Message, user_id: int, chat_id: int, reason: Optional[str]):
    try:
        if not is_user_admin(chat_id, message.from_user.id):
            bot.reply_to(message, "You are no longer an admin in this group.")
            return
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Cannot unban an admin or creator!")
            return
        
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "Cannot unban a bot!")
            return
        
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status != 'kicked':
                bot.reply_to(message, "User is not banned!")
                return
        except telebot.apihelper.ApiTelegramException:
            pass
        
        bot.unban_chat_member(chat_id, user_id)
        
        response, markup = format_unban_response(user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to unban users in this group! Please check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Cannot unban an admin!")
        else:
            bot.reply_to(message, f"Error unbanning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        data = call.data.split('_')
        action = data[0]
        user_id = int(data[1])
        chat_id = int(data[2])
        reason = '_'.join(data[3:]) if len(data) > 3 else None
        duration_str = None
        
        if action == 'tban':
            duration_str = data[-1]
            reason = '_'.join(data[3:-1]) if len(data) > 4 else None
            duration = parse_duration(duration_str)
            if not duration:
                bot.answer_callback_query(call.id, "Invalid duration format!", show_alert=True)
                return
            if duration > 31622400:
                bot.answer_callback_query(call.id, "Duration cannot exceed 366 days!", show_alert=True)
                return
        
        if reason == '':
            reason = None
        
        if action == 'ban':
            perform_ban(call.message, user_id, chat_id, reason, silent=False)
        elif action == 'sban':
            perform_ban(call.message, user_id, chat_id, reason, silent=True)
        elif action == 'tban':
            perform_ban(call.message, user_id, chat_id, reason, silent=False, duration=duration, duration_str=duration_str)
        elif action == 'unban':
            perform_unban(call.message, user_id, chat_id, reason)
        
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    
    except telebot.apihelper.ApiTelegramException as e:
        bot.answer_callback_query(call.id, f"Error: {e}", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Unexpected error: {e}", show_alert=True)
import telebot
from telebot import types
import time
from datetime import datetime, timedelta
import random
import re
from functools import wraps
from typing import Optional, Union
import json
import os
from config import bot
from kick import disabled
from user_logs.user_logs import log_action
from ban_sticker_pack.ban_sticker_pack import is_allowed, is_group


temp_bans = {}

def is_user_admin(chat_id, user_id, message=None):
    """Check if user is admin or anonymous admin"""
    try:
        if message and message.sender_chat and message.sender_chat.id == chat_id:
            return True
        
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False

def is_admin(func):
    @wraps(func)
    def wrapper(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        try:
            if is_user_admin(chat_id, user_id, message):
                return func(message)
            else:
                bot.reply_to(message, "Soo sad, You need to be an admin to do this.")
        except Exception as e:
            bot.reply_to(message, f"Error checking admin status: {str(e)}")
    return wrapper

def is_bot_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.user.is_bot
    except:
        return False

def get_user_id(message: types.Message) -> Optional[Union[int, str]]:
    try:
        if message.reply_to_message:
            return message.reply_to_message.from_user.id
        elif len(message.text.split()) > 1:
            identifier = message.text.split()[1]
            if identifier.startswith('@'):
                try:
                    with open('data/data.json', 'r') as file:
                        users = json.load(file)
                    username = identifier[1:].lower()
                    for user in users:
                        if user.get('username', '').lower() == username:
                            return int(user['user_id'])
                    bot.reply_to(message, "User not found. Please ban with /ban [reply] or /ban [user_id]")
                    return None
                except FileNotFoundError:
                    bot.reply_to(message, "User data file not found. Please ban with /ban [reply] or /ban [user_id]")
                    return None
                except json.JSONDecodeError:
                    bot.reply_to(message, "Error reading user data. Please ban with /ban [reply] or /ban [user_id]")
                    return None
            elif identifier.isdigit():
                return int(identifier)
            else:
                bot.reply_to(message, "Invalid user ID or username format!")
                return None
        return None
    except Exception as e:
        bot.reply_to(message, f"Error extracting user ID: {e}")
        return None

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

def get_reason(args, start_index):
    return ' '.join(args[start_index:]) if len(args) > start_index else None

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

def format_ban_response(target_user_id, admin_message, chat_id, reason=None, duration=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_mention = get_user_mention(target_user_id, chat_id)
    
    if admin_message.sender_chat and admin_message.sender_chat.id == chat_id:
        admin_mention = "Anonymous Admin"
    else:
        admin_id = admin_message.from_user.id
        first_name = admin_message.from_user.first_name or "Unknown"
        admin_mention = f"[{first_name}](tg://user?id={admin_id})"
    
    response = (
        f"Shh... bzzzt! Another rulebreaker banned {target_mention}\n\n"
        f"Moderator: {admin_mention}\n"
        f"{date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"
    if duration:
        duration_str = duration if isinstance(duration, str) else f"{duration // 86400}d" if duration >= 86400 else f"{duration // 3600}h" if duration >= 3600 else f"{duration // 60}m"
        response += f"\nDuration: {duration_str}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Unban",
        callback_data=f"unban_"
    ))
    return response, markup

def format_unban_response(target_user_id, admin_message, chat_id, reason=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_mention = get_user_mention(target_user_id, chat_id)
    
    if admin_message.sender_chat and admin_message.sender_chat.id == chat_id:
        admin_mention = "Anonymous Admin"
    else:
        admin_id = admin_message.from_user.id
        first_name = admin_message.from_user.first_name or "Unknown"
        admin_mention = f"[{first_name}](tg://user?id={admin_id})"
    
    response = (
        f"Unbanned {target_mention}\n"
        f"Moderator: {admin_mention}\n\n"
        f"{date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Ban",
        callback_data=f"ban_{target_user_id}"
    ))
    return response, markup

@bot.message_handler(regexp=r'^[\/!](ban)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_ban(message: types.Message):
    try:
        args = message.text.split()
        user_id = get_user_id(message)
        reason = None

        if message.reply_to_message:
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            bot.reply_to(message, "Reply to a message or provide a user ID/username (e.g., /ban @username or /ban 123456 [reason])!")
            return

        if not user_id:
            return

        chat_id = message.chat.id
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Are you crazy? I can't ban an moderator.")
            return
            
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "can't act on bot's.")
            return
            
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "Ahm 🤦, user is already banned.")
                return
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(chat_id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return
            raise

        bot.ban_chat_member(chat_id, user_id)
        target_user = bot.get_chat_member(chat_id, user_id).user
        
        log_action(
            chat_id=chat_id,
            action="ban",
            executor=message.from_user,
            target=target_user,
            details={"type": "permanent", "reason": reason}
        )
        
        response, markup = format_ban_response(user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users. Check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Are you crazy? I can't ban an moderator.")
        else:
            bot.reply_to(message, f"Error banning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(regexp=r'^[\/!](sban)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_sban(message: types.Message):
    try:
        args = message.text.split()
        user_id = get_user_id(message)
        reason = None

        if message.reply_to_message:
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            bot.reply_to(message, "Reply to a message or provide a user ID/username (e.g., /sban @username or /sban 123456 [reason])!")
            return

        if not user_id:
            return

        chat_id = message.chat.id
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
            return
            
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "First remove admin rights from that bot.")
            return
            
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "Ahm 🤦, user is already banned")
                return
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(chat_id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return
            raise

        bot.ban_chat_member(chat_id, user_id)
        target_user = bot.get_chat_member(chat_id, user_id).user
        
        log_action(
            chat_id=chat_id,
            action="sban",
            executor=message.from_user,
            target=target_user,
            details={"type": "silent", "reason": reason}
        )
        
        if message.reply_to_message:
            try:
                bot.delete_message(chat_id, message.reply_to_message.message_id)
            except telebot.apihelper.ApiTelegramException:
                pass
        try:
            bot.delete_message(chat_id, message.message_id)
        except telebot.apihelper.ApiTelegramException:
            pass
        
        response, markup = format_ban_response(user_id, message, chat_id, reason)
        bot.send_message(chat_id, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users. Check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
        else:
            bot.reply_to(message, f"Error banning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(regexp=r'^[\/!](tban)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_tban(message: types.Message):
    try:
        args = message.text.split()
        user_id = get_user_id(message)
        reason = None
        duration_str = None

        if message.reply_to_message:
            if len(args) < 2:
                bot.reply_to(message, "Usage: /tban <user_id/reply> [reason] <duration> (e.g., /tban spam 1h)")
                return
            duration_str = args[-1]
            reason = ' '.join(args[1:-1]) if len(args) > 2 else None
        elif len(args) > 1:
            if len(args) < 3:
                bot.reply_to(message, "Usage: /tban <user_id/username> [reason] <duration> (e.g., /tban @username spam 1h or /tban 123456 spam 1h)")
                return
            duration_str = args[-1]
            reason = ' '.join(args[2:-1]) if len(args) > 3 else None
        else:
            bot.reply_to(message, "Reply to a message or provide a user ID/username (e.g., /tban @username [reason] 1h or /tban 123456 [reason] 1h).")
            return

        if not user_id:
            return

        chat_id = message.chat.id
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
            return
            
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "First remove admin rights from that bot")
            return
            
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "Ahm 🤦, user is already banned")
                return
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(chat_id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return
            raise

        duration = parse_duration(duration_str)
        if not duration:
            bot.reply_to(message, "Invalid duration format! Use <number>[s|m|h|d|w] (e.g., 1h, 30m, 2d)")
            return

        if duration > 31622400:
            bot.reply_to(message, "Duration cannot exceed 366 days!")
            return

        until_date = int(time.time() + duration)
        bot.ban_chat_member(chat_id, user_id, until_date=until_date)
        temp_bans[(chat_id, user_id)] = until_date
        target_user = bot.get_chat_member(chat_id, user_id).user
        
        log_action(
            chat_id=chat_id,
            action="tban",
            executor=message.from_user,
            target=target_user,
            details={"type": "temporary", "duration": duration_str, "reason": reason}
        )
        
        response, markup = format_ban_response(user_id, message, chat_id, reason, duration_str)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users. Check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
        else:
            bot.reply_to(message, f"Error temporarily banning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(regexp=r'^[\/!](dban)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_dban(message: types.Message):
    try:
        args = message.text.split()
        user_id = None
        reason = None

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = get_reason(args, 1) if len(args) > 1 else None
        else:
            bot.reply_to(message, "Reply to a message to use /dban (e.g., /dban [reason])!")
            return

        chat_id = message.chat.id
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
            return
            
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "First remove admin rights from that bot")
            return
            
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "Ahm 🤦, user is already banned")
                return
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(chat_id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return
            raise
            
        bot.ban_chat_member(chat_id, user_id)
        target_user = bot.get_chat_member(chat_id, user_id).user
        
        log_action(
            chat_id=chat_id,
            action="dban",
            executor=message.from_user,
            target=target_user,
            details={"type": "delete", "reason": reason}
        )
        
        try:
            bot.delete_message(chat_id, message.reply_to_message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            bot.reply_to(message, f"User banned but failed to delete message: {e}")
            
        response, markup = format_ban_response(user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users. Check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
        else:
            bot.reply_to(message, f"Error banning and deleting message: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(regexp=r'^[\/!](rban)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_rban(message: types.Message):
    try:
        args = message.text.split()
        user_id = get_user_id(message)
        reason = None

        if message.reply_to_message:
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            bot.reply_to(message, "Reply to a message or provide a user ID/username (e.g., /rban @username or /rban 123456 [reason]).")
            return

        if not user_id:
            return

        chat_id = message.chat.id
        
        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
            return
            
        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "First remove admin rights from that bot")
            return
            
        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "Ahm 🤦, user is already banned")
                return
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(chat_id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return
            raise

        random_duration = random.randint(60, 604800)
        until_date = int(time.time() + random_duration)
        
        if random_duration < 3600:
            duration_str = f"{random_duration // 60}m"
        elif random_duration < 86400:
            duration_str = f"{random_duration // 3600}h"
        else:
            duration_str = f"{random_duration // 86400}d"

        bot.ban_chat_member(chat_id, user_id, until_date=until_date)
        temp_bans[(chat_id, user_id)] = until_date
        target_user = bot.get_chat_member(chat_id, user_id).user
        
        log_action(
            chat_id=chat_id,
            action="rban",
            executor=message.from_user,
            target=target_user,
            details={"type": "random", "duration": duration_str, "reason": reason}
        )
        
        response, markup = format_ban_response(user_id, message, chat_id, reason, duration_str)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users. Check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Are you crazy? I can't ban an moderator")
        else:
            bot.reply_to(message, f"Error randomly banning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(regexp=r'^[\/!](unban)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_unban(message: types.Message):
    try:
        args = message.text.split()
        user_id = get_user_id(message)
        reason = None

        if message.reply_to_message:
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            bot.reply_to(message, "Reply to a message or provide a user ID/username (e.g., /unban @username or /unban 123456 [reason])!")
            return

        if not user_id:
            return

        chat_id = message.chat.id

        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Are you crazy?")
            return

        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "Cannot unban a bot!")
            return

        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status != 'kicked':
                bot.reply_to(message, "Ahm 🤦, user is not banned.")
                return
        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                group_name = bot.get_chat(chat_id).title or "this group"
                bot.reply_to(message, f"User not found in {group_name}")
                return
            raise

        bot.unban_chat_member(chat_id, user_id)
        
        target_user = bot.get_chat_member(chat_id, user_id).user
        log_action(
            chat_id=chat_id,
            action="unban",
            executor=message.from_user,
            target=target_user,
            details={"reason": reason}
        )
        
        temp_bans_key = (chat_id, user_id)
        if temp_bans_key in temp_bans:
            del temp_bans[temp_bans_key]

        response, markup = format_unban_response(user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to unban users. Check my admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Are you crazy?.")
        else:
            bot.reply_to(message, f"Error unbanning user: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(regexp=r'^[\/!](banme)(?:\s|$|@)')
@is_group
@disabled
def command_banme(message: types.Message):
    try:
        args = message.text.split()
        user_id = message.from_user.id
        chat_id = message.chat.id
        reason = get_reason(args, 1) if len(args) > 1 else None

        if is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Admins cannot ban themselves!")
            return

        if is_bot_user(chat_id, user_id):
            bot.reply_to(message, "Bots cannot ban themselves!")
            return

        try:
            chat_member = bot.get_chat_member(chat_id, user_id)
            if chat_member.status == 'kicked':
                bot.reply_to(message, "You are already banned!")
                return
        except telebot.apihelper.ApiTelegramException:
            pass

        bot.ban_chat_member(chat_id, user_id)
        
        log_action(
            chat_id=chat_id,
            action="banme",
            executor=message.from_user,
            target=message.from_user,
            details={"type": "self-ban", "reason": reason}
        )
        
        response, markup = format_ban_response(user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to ban users. Check my admin rights.")
        else:
            bot.reply_to(message, f"Error banning yourself: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")
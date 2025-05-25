import telebot
import random
from functools import wraps
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot, logger
import time
from telebot import types
from datetime import datetime
from user_logs.user_logs import log_action
import traceback
import json
import os
from ban_sticker_pack.ban_sticker_pack import is_group
from kick import disabled
from telebot.types import ChatPermissions
from datetime import datetime, timedelta
from telebot.apihelper import ApiException


MUTE_DURATION_MINUTES = 1440

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

def is_user_admin(chat_id: int, user_id: int) -> bool:
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except:
        return False

def is_bot_user(chat_id: int, user_id: int) -> bool:
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.user.is_bot
    except:
        return False

def is_admin(func):
    @wraps(func)
    def wrapper(message):
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "This command works only in groups")
            return

        try:
            if message.sender_chat and message.sender_chat.id == message.chat.id:
                return func(message)

            admins = bot.get_chat_administrators(message.chat.id)
            if any(admin.user.id == message.from_user.id for admin in admins):
                return func(message)
            
            bot.reply_to(message, "Soo sad, You need to be an admin to do this.")
        except Exception as e:
            bot.reply_to(message, f"Error checking admin status: {str(e)}")
    return wrapper

def bot_is_admin(func):
    def wrapper(message):
        if message.chat.type not in ['group', 'supergroup']:
            return
        try:
            bot_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
            if bot_member.status == 'administrator':
                return func(message)
            bot.reply_to(message, "I need to be an admin to perform this action")
        except Exception as e:
            bot.reply_to(message, f"Error checking bot admin status: {str(e)}")
    return wrapper
    
def is_anonymous(func):
    """Decorator to check for anonymous admin support"""
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "This command can only be used in groups.")
            return

        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if not is_user_admin(chat_id, user_id):
            bot.reply_to(message, "Only admins can use this command.")
            return

        return func(message, *args, **kwargs)
    return wrapped

def extract_user(message):
    try:
        if message.reply_to_message:
            return message.reply_to_message.from_user
        elif len(message.text.split()) > 1:
            text = message.text.split()[1]
            if text.startswith('@'):
                try:
                    with open('data/data.json', 'r') as file:
                        users = json.load(file)
                    username = text[1:].lower()
                    for user in users:
                        if user.get('username', '').lower() == username:
                            member = bot.get_chat_member(message.chat.id, int(user['user_id']))
                            return member.user
                    bot.reply_to(message, "User not found. Please mute with /mute [reply] or /mute [user_id]")
                    return None
                except FileNotFoundError:
                    bot.reply_to(message, "User data file not found. Please mute with /mute [reply] or /mute [user_id]")
                    return None
                except json.JSONDecodeError:
                    bot.reply_to(message, "Error reading user data. Please mute with /mute [reply] or /mute [user_id]")
                    return None
            elif text.isdigit():
                member = bot.get_chat_member(message.chat.id, int(text))
                return member.user
            else:
                bot.reply_to(message, "Invalid user ID or username format!")
                return None
        return None
    except Exception as e:
        bot.reply_to(message, f"Error extracting user: {str(e)}")
        return None

def format_datetime():
    now = datetime.now()
    return {
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%I:%M:%S %p")
    }

def create_action_buttons(user_id, action):
    markup = types.InlineKeyboardMarkup()
    if action == 'mute':
        buttons = [
            types.InlineKeyboardButton("Kick ( admin only )", callback_data=f"kick_{user_id}"),
            types.InlineKeyboardButton("Ban ( admin only )", callback_data=f"ban_{user_id}"),
            types.InlineKeyboardButton("Unmute ( admin only )", callback_data=f"unmute_{user_id}")
        ]
    else:
        buttons = [
            types.InlineKeyboardButton("Kick ( admin only )", callback_data=f"kick_{user_id}"),
            types.InlineKeyboardButton("Ban ( admin only )", callback_data=f"ban_{user_id}"),
            types.InlineKeyboardButton("Mute ( admin only )", callback_data=f"mute_{user_id}")
        ]
    markup.row(buttons[0], buttons[1])
    markup.row(buttons[2])
    return markup
    
def get_target_user(message):
    try:
        if message.reply_to_message:
            return message.reply_to_message.from_user
        args = message.text.split()
        if len(args) < 2:
            return None
        target = args[1]
        if target.startswith('@'):
            try:
                with open('data/data.json', 'r') as file:
                    users = json.load(file)
                username = target[1:].lower()
                for user in users:
                    if user.get('username', '').lower() == username:
                        member = bot.get_chat_member(message.chat.id, int(user['user_id']))
                        return member.user
                bot.reply_to(message, "User not found. Please mute with /mute [reply] or /mute [user_id]")
                return None
            except FileNotFoundError:
                bot.reply_to(message, "User data file not found. Please mute with /mute [reply] or /mute [user_id]")
                return None
            except json.JSONDecodeError:
                bot.reply_to(message, "Error reading user data. Please mute with /mute [reply] or /mute [user_id]")
                return None
        try:
            user_id = int(target)
            chat_member = bot.get_chat_member(message.chat.id, user_id)
            return chat_member.user
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
        logger.error(f"Error getting target user: {str(e)}")
        return None

def get_reason(args, start_index):
    return ' '.join(args[start_index:]) if len(args) > start_index else None

def parse_duration(duration_str):
    try:
        if not duration_str:
            return None
        unit = duration_str[-1].lower()
        value = int(duration_str[:-1])
        if value <= 0:
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
        elif unit == 'y':
            return value * 31536000
        return None
    except (ValueError, IndexError):
        return None

def format_mute_response(target_user, admin_user, reason=None, duration=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_link = f"tg://user?id={target_user.id}"
    admin_link = f"tg://user?id={admin_user.id}"
    
    response = (
        f"User Muted\n"
        f"By: [{admin_user.first_name}]({admin_link})\n"
        f"User: [{target_user.first_name}]({target_link})\n\n"
        f"On {date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"
    if duration:
        unmute_time = datetime.fromtimestamp(current_time.timestamp() + duration)
        unmute_date = unmute_time.strftime("%d/%m/%y")
        unmute_time_str = unmute_time.strftime("%I:%M:%S %p")
        response += f"\nUnmute on: Date {unmute_date} Time {unmute_time_str}"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="Unmute ( admin only )",
        callback_data=f"unmute_{target_user.id}"
    ))
    return response, markup

def format_unmute_response(target_user, admin_user, reason=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_link = f"tg://user?id={target_user.id}"
    admin_link = f"tg://user?id={admin_user.id}"
    
    response = (
        f"User Unmuted\n"
        f"By: [{admin_user.first_name}]({admin_link})\n"
        f"User: [{target_user.first_name}]({target_link})\n\n"
        f"On {date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="Mute ( admin only )",
        callback_data=f"mute_{target_user.id}"
    ))
    return response, markup

def can_mute(chat_id, user_id):
    try:
        bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
        if not bot_member.can_restrict_members:
            return False, "restrict members"
        return True, None
    except Exception as e:
        logger.error(f"Error checking bot permissions: {str(e)}")
        return False, "check permissions"

def validate_target(chat_id, target_user, admin_user):
    if not target_user:
        return False, "Reply to a message or provide a user ID."
    if target_user.id == admin_user.id:
        return False, "You can't mute yourself."
    if target_user.is_bot:
        return False, "You can't mute bots."
    try:
        target_member = bot.get_chat_member(chat_id, target_user.id)
        if target_member.status in ['administrator', 'creator']:
            return False, "You can't mute moderator"
        return True, None
    except Exception as e:
        logger.error(f"Error validating target: {str(e)}")
        return False, "validate user status"

def handle_action(chat_id, target_user_id, admin_user_id, action, is_anonymous=False, reason=None):
    try:
        admin_name = "Anonymous Admin"
        admin_user = None
        
        if not is_anonymous:
            try:
                admin_member = bot.get_chat_member(chat_id, admin_user_id)
                if admin_member.status not in ['administrator', 'creator']:
                    return None, "Soo sad, You need to be an admin to do this."
                admin_user = admin_member.user
                admin_name = f"[{admin_user.first_name}](tg://user?id={admin_user_id})"
            except:
                return None, "Admin not found in this chat"

        bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
        if bot_member.status != 'administrator':
            return None, "I'm not an admin anymore."
        if not getattr(bot_member, 'can_restrict_members', False):
            return None, "I need Restrict Members permission."

        try:
            target_member = bot.get_chat_member(chat_id, target_user_id)
            target_user = target_member.user
        except Exception as e:
            return None, f"User not found: {str(e)}"

        if target_user.is_bot:
            return None, "Can't act on bots."
        if target_member.status in ['administrator', 'creator']:
            return None, "Can't act on moderator."

        if action == 'unmute' and target_member.can_send_messages is not False:
            return None, "This user is not muted."

        if action == 'mute':
            permissions = types.ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            bot.restrict_chat_member(chat_id, target_user_id, permissions)
            
        elif action == 'unmute':
            permissions = types.ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            bot.restrict_chat_member(chat_id, target_user_id, permissions)
            
        elif action == 'kick':
            bot.kick_chat_member(chat_id, target_user_id)
            bot.unban_chat_member(chat_id, target_user_id)
            
        elif action == 'ban':
            bot.ban_chat_member(chat_id, target_user_id)

        datetime_info = format_datetime()
        target_link = f"[{target_user.first_name}](tg://user?id={target_user.id})"
        
        action_text = {
            'mute': 'Muted',
            'unmute': 'Unmuted',
            'kick': 'Kicked',
            'ban': 'Banned'
        }[action]

        response = (
            f"User {action_text}\n"
            f"By: {admin_name}\n"
            f"User: {target_link}\n\n"
            f"On {datetime_info['date']} at {datetime_info['time']}"
        )
        
        if reason:
            response += f"\nReason: {reason}"
            
        return response, create_action_buttons(target_user_id, action)
        
    except Exception as e:
        return None, f"Error: {str(e)}"

@bot.message_handler(regexp=r'^[\/!](mute)(?:\s|$|@)')
@is_group
@bot_is_admin
@is_admin
def command_mute(message):
    try:
        args = message.text.split()
        user = None
        reason = None

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            user = get_target_user(message)
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            return bot.reply_to(message, "Reply to a user or provide a user ID/username (e.g., /mute @username or /mute 123456 [reason])")

        if not user:
            return

        is_anonymous = bool(message.sender_chat and message.sender_chat.id == message.chat.id)
        
        response, markup = handle_action(
            message.chat.id,
            user.id,
            message.from_user.id if not is_anonymous else message.sender_chat.id,
            'mute',
            is_anonymous=is_anonymous,
            reason=reason
        )
        
        if response:
            bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.reply_to(message, markup)

    except Exception as e:
        bot.reply_to(message, f"Mute failed: {str(e)}")

@bot.message_handler(commands=['unmute'])
@is_group
@is_admin
@bot_is_admin
def unmute_user(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()

    try:
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            reason = get_reason(args, 1)
        else:
            if len(args) < 2:
                bot.reply_to(message, "Reply to a user or provide a user ID/username (e.g., /unmute @username or /unmute 123456 [reason])")
                return
            target_user = get_target_user(message)
            reason = get_reason(args, 2) if len(args) > 2 else None

        if not target_user:
            return

        if target_user.is_bot:
            bot.reply_to(message, "I cannot unmute bots.")
            return

        permissions = telebot.types.ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )

        bot.restrict_chat_member(chat_id, target_user.id, permissions=permissions)

        user_mention = get_user_mention(target_user.id, chat_id)
        admin_mention = get_admin_mention(message)
        reason_text = f"\nReason: {reason}" if reason else ""

        bot.send_message(
            chat_id,
            f"{user_mention}\nHas been unmuted by {admin_mention}.\n{reason_text}",
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.reply_to(message, f"Something went wrong while unmuting: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](tmute)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@bot_is_admin
def command_tmute(message):
    try:
        args = message.text.split()
        user = None
        reason = None
        duration_str = None

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            if len(args) > 1:
                duration_str = args[-1]
                reason = ' '.join(args[1:-1]) if len(args) > 2 else None
        elif len(args) > 1:
            user = get_target_user(message)
            duration_str = args[-1]
            reason = ' '.join(args[2:-1]) if len(args) > 3 else None
        else:
            return bot.reply_to(message, "Usage: /tmute <user_id/reply/username> [reason] <duration> (e.g., /tmute @username spam 1h or /tmute 123456 spam 1h)")

        if not user:
            return

        duration = parse_duration(duration_str)
        if not duration:
            return bot.reply_to(message, "Invalid duration. Use formats like 1h, 30m, 2d")

        valid, error = validate_target(message.chat.id, user, message.from_user)
        if not valid:
            return bot.reply_to(message, f"{error}")

        can_mute_result, permission = can_mute(message.chat.id, user.id)
        if not can_mute_result:
            return bot.reply_to(message, f"I need the '{permission}' right!")

        until_date = int(time.time() + duration)
        permissions = types.ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        
        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=permissions,
            until_date=until_date
        )
        log_action(
            chat_id=message.chat.id,
            action="tmute",
            executor=message.from_user,
            target=user,
            details={"duration": duration, "reason": reason}
        )

        response, markup = format_mute_response(user, message.from_user, reason, duration)
        bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"Temporary mute failed: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](rmute)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@bot_is_admin
def command_rmute(message):
    try:
        args = message.text.split()
        user = None
        reason = None

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            user = get_target_user(message)
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            return bot.reply_to(message, "Reply to a user or provide a user ID/username (e.g., /rmute @username or /rmute 123456 [reason])")

        if not user:
            return

        duration = random.randint(60, 604800)

        valid, error = validate_target(message.chat.id, user, message.from_user)
        if not valid:
            return bot.reply_to(message, f"{error}")

        can_mute_result, permission = can_mute(message.chat.id, user.id)
        if not can_mute_result:
            return bot.reply_to(message, f"I need the '{permission}' right!")

        until_date = int(time.time() + duration)
        permissions = types.ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            permissions=permissions,
            until_date=until_date
        )
        log_action(
            chat_id=message.chat.id,
            action="rmute",
            executor=message.from_user,
            target=user,
            details={"duration": duration, "reason": reason}
        )

        response, markup = format_mute_response(user, message.from_user, reason, duration)
        bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"Random mute failed: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](smute)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@bot_is_admin
def command_smute(message):
    try:
        args = message.text.split()
        user = None
        reason = None

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            user = get_target_user(message)
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            return bot.reply_to(message, "Reply to a user or provide a user ID/username (e.g., /smute @username or /smute 123456 [reason])")

        if not user:
            return

        valid, error = validate_target(message.chat.id, user, message.from_user)
        if not valid:
            bot.reply_to(message, f"{error}")
            return

        can_mute_result, permission = can_mute(message.chat.id, user.id)
        if not can_mute_result:
            bot.reply_to(message, f"I need the '{permission}' right!")
            return

        bot.delete_message(message.chat.id, message.message_id)

        response, markup = handle_action(message.chat.id, user.id, message.from_user.id, 'mute', reason=reason)
        if response:
            bot.send_message(
                message.chat.id,
                response,
                parse_mode='Markdown',
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, markup)

    except Exception as e:
        logger.error(f"Error in /smute: {str(e)}")
        bot.reply_to(message, f"Silent mute failed: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](dmute)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@bot_is_admin
def command_dmute(message):
    try:
        args = message.text.split()
        user = None
        reason = None

        if message.reply_to_message:
            user = message.reply_to_message.from_user
            reason = get_reason(args, 1) if len(args) > 1 else None
        elif len(args) > 1:
            user = get_target_user(message)
            reason = get_reason(args, 2) if len(args) > 2 else None
        else:
            return bot.reply_to(message, "Reply to a user or provide a user ID/username (e.g., /dmute @username or /dmute 123456 [reason])")

        if not user:
            return

        valid, error = validate_target(message.chat.id, user, message.from_user)
        if not valid:
            return bot.reply_to(message, f"{error}")

        can_mute_result, permission = can_mute(message.chat.id, user.id)
        if not can_mute_result:
            return bot.reply_to(message, f"I need the '{permission}' right!")

        if message.reply_to_message:
            bot.delete_message(message.chat.id, message.reply_to_message.message_id)

        response, markup = handle_action(message.chat.id, user.id, message.from_user.id, 'mute', reason=reason)
        if response:
            bot.reply_to(message, response, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.reply_to(message, markup)

    except Exception as e:
        logger.error(f"Error in /dmute: {str(e)}")
        bot.reply_to(message, f"Delete mute failed: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](checkmute)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_checkmute(message):
    try:
        target_user = get_target_user(message)
        if not target_user:
            return

        chat_member = bot.get_chat_member(message.chat.id, target_user.id)
        if chat_member.can_send_messages is False:
            bot.reply_to(message, f"User {target_user.first_name} (ID: {target_user.id}) is muted.")
        else:
            bot.reply_to(message, f"User {target_user.first_name} (ID: {target_user.id}) is not muted.")
    except Exception as e:
        logger.error(f"Error in /checkmute: {str(e)}\n{traceback.format_exc()}")
        bot.reply_to(message, f"Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('auth_'))
def handle_auth(call):
    try:
        data = call.data.split('_')
        action = data[1]
        target_user_id = int(data[2])
        admin_user_id = int(data[3])

        if call.from_user.id != admin_user_id:
            bot.answer_callback_query(call.id, f"Under development.", show_alert=True)
            return

        response, markup = handle_action(
            call.message.chat.id,
            target_user_id,
            admin_user_id,
            action,
            is_anonymous=True
        )

        if response:
            log_action(
                chat_id=call.message.chat.id,
                action=action,
                executor=call.from_user,
                target=bot.get_chat_member(call.message.chat.id, target_user_id).user,
                details={"via": "auth_callback"}
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=response,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, f"{action.capitalize()} done.")
        else:
            bot.answer_callback_query(call.id, markup, show_alert=True)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('mute_', 'unmute_', 'kick_', 'ban_')))
def handle_action_buttons(call):
    try:
        action_part, user_id_part = call.data.split('_', 1)
        target_user_id = int(user_id_part)
        
        bot.answer_callback_query(call.id, f"processing...", show_alert=True)
        
        response, markup = handle_action(
            call.message.chat.id,
            target_user_id,
            call.from_user.id,
            action_part,
            getattr(bot.get_chat_member(call.message.chat.id, call.from_user.id), 'is_anonymous', False)
        )

        if response:
            bot.edit_message_text(
                response,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id, f"{action_part.capitalize()} success!")
        else:
            bot.answer_callback_query(call.id, markup, show_alert=True)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)
        
@bot.message_handler(regexp=r'^[\/!](muteme)(?:\s|$|@)')
@is_group
@disabled
@bot_is_admin
def command_muteme(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "This command can only be used in group chats.")
        return

    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status in ['administrator', 'creator']:
            bot.reply_to(message, "You can't mute yourself if you're an admin or the group owner.")
            return

        until_date = datetime.now() + timedelta(minutes=MUTE_DURATION_MINUTES)
        bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        bot.reply_to(message, "You have been muted for 1 day.")
    except ApiException as api_err:
        logger.error(f"Telegram API error while muting user {message.from_user.id} in chat {message.chat.id}: {api_err}")
        bot.reply_to(message, "Sorry, I couldn't mute you due to a permissions issue or API error.")
    except Exception as e:
        logger.exception(f"Unexpected error in /muteme command for user {message.from_user.id}")
        bot.reply_to(message, "Something went wrong while processing your request. Please try again later.")
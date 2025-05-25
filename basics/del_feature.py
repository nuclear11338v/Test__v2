import telebot
from telebot import types
from functools import wraps
import logging
import time
from config import bot, logger
from kick import disabled

def is_admin(func):
    @wraps(func)
    def wrapper(message):
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            admins = bot.get_chat_administrators(chat_id)
            admin_ids = [admin.user.id for admin in admins]
            if user_id not in admin_ids:
                bot.reply_to(message, "You must be an admin to use this command.")
                return
            return func(message)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Error checking admin status: {e}")
            bot.reply_to(message, "An error occurred while checking admin status.")
    return wrapper

def delete_user_messages(chat_id, user_id, target_user_id):
    try:
        messages_to_delete = []

        for i in range(1000):
            try:
                messages = bot.get_chat_history(chat_id, limit=1000, offset=i*1000)
                for msg in messages:
                    if msg.from_user.id == target_user_id:
                        messages_to_delete.append(msg.message_id)
            except Exception as e:
                logger.warning(f"Error fetching messages: {e}")
                break

        for msg_id in messages_to_delete:
            try:
                bot.delete_message(chat_id, msg_id)
            except telebot.apihelper.ApiTelegramException:
                continue
    except Exception as e:
        logger.error(f"Error deleting user messages: {e}")

def format_response(firstname, user_id, action):
    user_link = f"tg://user?id={user_id}"
    return f"deleted message\n[{firstname}]({user_link})\nBye -"

@bot.message_handler(commands=['fban'])
@is_admin
def fban_command(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Please reply to a user's message to use this command.")
            return

        chat_id = message.chat.id
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        firstname = target_user.first_name
        reason = ' '.join(message.text.split()[1:]) if len(message.text.split()) > 1 else "No reason provided"

        delete_user_messages(chat_id, message.from_user.id, target_user_id)

        bot.ban_chat_member(chat_id, target_user_id)

        bot.reply_to(message, format_response(firstname, target_user_id, "banned"), parse_mode="Markdown")
        logger.info(f"User {target_user_id} banned from {chat_id}. Reason: {reason}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error in fban: {e}")
        bot.reply_to(message, "Failed to ban the user. Check bot permissions.")
    except Exception as e:
        logger.error(f"Unexpected error in fban: {e}")
        bot.reply_to(message, "An unexpected error occurred.")

@bot.message_handler(commands=['fkick'])
@is_admin
def fkick_command(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Please reply to a user's message to use this command.")
            return

        chat_id = message.chat.id
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        firstname = target_user.first_name
        reason = ' '.join(message.text.split()[1:]) if len(message.text.split()) > 1 else "No reason provided"

        delete_user_messages(chat_id, message.from_user.id, target_user_id)

        bot.ban_chat_member(chat_id, target_user_id)
        bot.unban_chat_member(chat_id, target_user_id)

        bot.reply_to(message, format_response(firstname, target_user_id, "kicked"), parse_mode="Markdown")
        logger.info(f"User {target_user_id} kicked from {chat_id}. Reason: {reason}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error in fkick: {e}")
        bot.reply_to(message, "Failed to kick the user. Check bot permissions.")
    except Exception as e:
        logger.error(f"Unexpected error in fkick: {e}")
        bot.reply_to(message, "An unexpected error occurred.")

@bot.message_handler(commands=['fmute'])
@is_admin
def fmute_command(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Please reply to a user's message to use this command.")
            return

        chat_id = message.chat.id
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        firstname = target_user.first_name
        reason = ' '.join(message.text.split()[1:]) if len(message.text.split()) > 1 else "No reason provided"

        delete_user_messages(chat_id, message.from_user.id, target_user_id)
        bot.restrict_chat_member(chat_id, target_user_id, permissions=types.ChatPermissions(can_send_messages=False))

        bot.reply_to(message, format_response(firstname, target_user_id, "muted"), parse_mode="Markdown")
        logger.info(f"User {target_user_id} muted in {chat_id}. Reason: {reason}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error in fmute: {e}")
        bot.reply_to(message, "Failed to mute the user. Check bot permissions.")
    except Exception as e:
        logger.error(f"Unexpected error in fmute: {e}")
        bot.reply_to(message, "An unexpected error occurred.")
        
@bot.message_handler(commands=['fdel'])
@is_admin
def fdel_command(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Please reply to a user's message to use this command.")
            return

        chat_id = message.chat.id
        target_user = message.reply_to_message.from_user
        target_user_id = target_user.id
        firstname = target_user.first_name
        reason = ' '.join(message.text.split()[1:]) if len(message.text.split()) > 1 else "No reason provided"

        delete_user_messages(chat_id, message.from_user.id, target_user_id)

        bot.reply_to(message, format_response(firstname, target_user_id, "messages deleted"), parse_mode="Markdown")
        logger.info(f"Messages of user {target_user_id} deleted in {chat_id}. Reason: {reason}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error in fdel: {e}")
        bot.reply_to(message, "Failed to delete messages. Check bot permissions.")
    except Exception as e:
        logger.error(f"Unexpected error in fdel: {e}")
        bot.reply_to(message, "An unexpected error occurred.")
        
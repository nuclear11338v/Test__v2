import telebot
import json
import os
from functools import wraps
from telebot.types import Message
from telebot import apihelper
from config import bot, logger
from kick import disabled
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group
from datetime import datetime, timedelta
import time

DATA_FILE = 'purge.json'
MAX_MESSAGES = 100  # Telegram API limit for bulk deletion
MESSAGE_AGE_LIMIT = timedelta(hours=48)  # Telegram's 48-hour limit for bot message deletion

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to parse purge.json. Starting with empty data.")
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save purge.json: {str(e)}")

data = load_data()

def safe_delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
        return True
    except apihelper.ApiTelegramException as e:
        logger.debug(f"Failed to delete message {message_id} in chat {chat_id}: {str(e)}")
        return False

def check_message_age(message: Message):
    """Check if the message is within the 48-hour deletion window."""
    message_time = message.date
    current_time = datetime.utcfromtimestamp(time.time())
    message_datetime = datetime.utcfromtimestamp(message_time)
    return current_time - message_datetime <= MESSAGE_AGE_LIMIT

@bot.message_handler(regexp=r'^[\/!](purge)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_purge_messages(message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a message to start purging from.")
        return

    if not check_message_age(message.reply_to_message):
        bot.reply_to(message, "Cannot purge messages older than 48 hours.")
        return

    start_message_id = message.reply_to_message.message_id
    end_message_id = message.message_id

    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        count = min(int(args[1]), MAX_MESSAGES)  # Cap at 100 messages
        end_message_id = start_message_id + count
    else:
        end_message_id += 1

    if end_message_id - start_message_id > MAX_MESSAGES:
        bot.reply_to(message, f"Cannot purge more than {MAX_MESSAGES} messages at once.")
        return

    deleted_count = 0
    for msg_id in range(start_message_id, end_message_id):
        if safe_delete_message(chat_id, msg_id):
            deleted_count += 1
        time.sleep(0.05)  # Rate limiting to avoid API flood

    bot.send_message(chat_id, f"Purged {deleted_count} messages from {start_message_id} to {end_message_id - 1}")
    safe_delete_message(chat_id, message.message_id)  # Clean up command message

@bot.message_handler(regexp=r'^[\/!](spurge)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_spurge(message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a message to start purging from!")
        return

    if not check_message_age(message.reply_to_message):
        return  # Silently fail for old messages

    start_message_id = message.reply_to_message.message_id
    end_message_id = message.message_id + 1

    if end_message_id - start_message_id > MAX_MESSAGES:
        return  # Silently fail for too many messages

    deleted_count = 0
    for msg_id in range(start_message_id, end_message_id):
        if safe_delete_message(chat_id, msg_id):
            deleted_count += 1
        time.sleep(0.05)  # Rate limiting

    safe_delete_message(chat_id, message.message_id)  # Clean up command message

@bot.message_handler(regexp=r'^[\/!](del)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_del(message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a message to delete it!")
        return

    if not check_message_age(message.reply_to_message):
        return  # Silently fail for old messages

    if safe_delete_message(chat_id, message.reply_to_message.message_id):
        safe_delete_message(chat_id, message.message_id)  # Clean up command message

@bot.message_handler(regexp=r'^[\/!](purgefrom)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_purge_from(message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a message to mark as purge start.")
        return

    if not check_message_age(message.reply_to_message):
        bot.reply_to(message, "Cannot mark messages older than 48 hours as purge start.")
        return

    if chat_id not in data:
        data[chat_id] = {}
    data[chat_id]['purge_from'] = message.reply_to_message.message_id
    save_data(data)
    bot.reply_to(message, "Purge start marked. Now use /purgeto to mark the end.")
    safe_delete_message(chat_id, message.message_id)  # Clean up command message

@bot.message_handler(regexp=r'^[\/!](purgeto)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_purge_to(message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a message to mark as purge end!")
        return

    if chat_id not in data or 'purge_from' not in data[chat_id]:
        bot.reply_to(message, "No purge start marked! Use /purgefrom first.")
        return

    start_message_id = data[chat_id]['purge_from']
    end_message_id = message.reply_to_message.message_id + 1

    if end_message_id <= start_message_id:
        bot.reply_to(message, "End message must be after the start message!")
        return

    if end_message_id - start_message_id > MAX_MESSAGES:
        bot.reply_to(message, f"Cannot purge more than {MAX_MESSAGES} messages at once.")
        return

    if not check_message_age(message.reply_to_message):
        bot.reply_to(message, "Cannot purge messages older than 48 hours.")
        return

    deleted_count = 0
    for msg_id in range(start_message_id, end_message_id):
        if safe_delete_message(chat_id, msg_id):
            deleted_count += 1
        time.sleep(0.05)  # Rate limiting

    bot.send_message(chat_id, f"Purged {deleted_count} messages from {start_message_id} to {end_message_id - 1}")
    del data[chat_id]['purge_from']
    save_data(data)
    safe_delete_message(chat_id, message.message_id)  # Clean up command message
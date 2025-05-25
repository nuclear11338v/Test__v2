import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
import os
from functools import wraps
import logging
from telebot import types, util
from config import bot, logger

ADMIN_ID = 6177259495

# File to store user IDs
USER_IDS_FILE = 'broadcasting/user_ids.json'

# Load user IDs from file
def load_user_ids():
    if os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save user IDs to file
def save_user_ids(user_data):
    with open(USER_IDS_FILE, 'w') as f:
        json.dump(user_data, f, indent=4)

# Decorator to record user ID
def record_user_id(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user = message.from_user
        user_id = str(user.id)
        user_data = load_user_ids()
        
        # Save user info
        user_data[user_id] = {
            'first_name': user.first_name or '',
            'user_id': user_id,
            'username': user.username or ''
        }
        save_user_ids(user_data)
        
        return func(message, *args, **kwargs)
    return wrapper

# Check if user is admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Users command (admin only)
@bot.message_handler(commands=['users'])
@record_user_id
def users_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    user_data = load_user_ids()
    if not user_data:
        bot.reply_to(message, "No users found.")
        return

    # Prepare user list
    user_list = []
    for user_id, info in user_data.items():
        user_text = (
            f"{len(user_list) + 1}. {info['first_name']}\n"
            f"User ID: {info['user_id']}\n"
            f"Username: {info['username'] or 'N/A'}\n"
        )
        user_list.append(user_text)

    # Split message if it exceeds 4000 characters
    max_text_limit = 4000
    messages = []
    current_message = ""
    
    for user_text in user_list:
        if len(current_message) + len(user_text) < max_text_limit:
            current_message += user_text + "\n"
        else:
            messages.append(current_message)
            current_message = user_text + "\n"
    
    if current_message:
        messages.append(current_message)

    # Send messages
    for msg in messages:
        bot.send_message(message.chat.id, msg)

# Broadcast command (admin only)
@bot.message_handler(commands=['broadcast'])
@record_user_id
def broadcast_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    # Check if there's a message or replied message
    if message.reply_to_message:
        content = message.reply_to_message
        text = content.caption or content.text or ""
    else:
        text = message.text[len('/broadcast '):] if message.text.startswith('/broadcast ') else ""
        content = message

    if not text and not content:
        bot.reply_to(message, "Please provide a message to broadcast or reply to a message.")
        return

    user_data = load_user_ids()
    total_users = len(user_data)
    if total_users == 0:
        bot.reply_to(message, "No users to broadcast to.")
        return

    # Initialize counters
    complete = 0
    failed = 0
    processing = total_users

    # Send initial processing message
    status_message = bot.reply_to(message, "Processing...")

    # Wait 0.2 seconds and update
    time.sleep(0.2)
    bot.edit_message_text(
        f"Broadcasting\nComplete - {complete}\nFailed - {failed}\nProcessing - {processing}",
        chat_id=status_message.chat.id,
        message_id=status_message.message_id
    )

    # Prepare inline buttons if any
    markup = None
    if content.reply_markup:
        markup = content.reply_markup

    # Broadcast to all users
    for user_id in user_data.keys():
        try:
            # Handle different content types
            if content.photo:
                bot.send_photo(
                    user_id,
                    content.photo[-1].file_id,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            elif content.video:
                bot.send_video(
                    user_id,
                    content.video.file_id,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            elif content.audio:
                bot.send_audio(
                    user_id,
                    content.audio.file_id,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            elif content.document:
                bot.send_document(
                    user_id,
                    content.document.file_id,
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    user_id,
                    text,
                    parse_mode='Markdown',
                    reply_markup=markup,
                    disable_web_page_preview=False
                )
            complete += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed += 1
        
        processing -= 1

        # Update status every second
        time.sleep(1)
        bot.edit_message_text(
            f"Broadcasting\nComplete - {complete}\nFailed - {failed}\nProcessing - {processing}",
            chat_id=status_message.chat.id,
            message_id=status_message.message_id
        )

    # Final status update
    bot.edit_message_text(
        f"Broadcasting\nComplete - {complete}\nFailed - {failed}\nProcessing - {processing}",
        chat_id=status_message.chat.id,
        message_id=status_message.message_id
    )
    
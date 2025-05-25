import telebot
import json
import os
import logging
from functools import wraps
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot, logger
from kick import disabled 

REPORTS_FILE = "reports.json"

def load_report_settings():
    """Load report settings from reports.json."""
    try:
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading reports.json: {e}")
        return {}

def save_report_settings(settings):
    """Save report settings to reports.json."""
    try:
        with open(REPORTS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving reports.json: {e}")

group_report_settings = load_report_settings()

def is_admin(func):
    """Decorator to restrict commands to group admins."""
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        if message.chat.type not in ['group', 'supergroup']:
            bot.reply_to(message, "This command can only be used in groups.")
            return
        try:
            chat_admins = bot.get_chat_administrators(message.chat.id)
            if any(admin.user.id == message.from_user.id for admin in chat_admins):
                return func(message, *args, **kwargs)
            else:
                bot.reply_to(message, "You need to.be an admin..")
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Error checking admin status: {e}")
            bot.reply_to(message, "Error: Unable to verify admin status. Please ensure the bot has admin privileges.")
    return wrapped

def get_admin_names(chat_id):
    """Fetch names of group admins."""
    try:
        admins = bot.get_chat_administrators(chat_id)
        return [admin.user.first_name for admin in admins]
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error fetching admin names for chat {chat_id}: {e}")
        return ["Admin"]

@bot.message_handler(regexp=r'^[\/!](reports)(?:\s|$|@)')
@disabled
@is_admin
def command_toggle_reports(message):
    """Toggle report settings for a group."""
    chat_id = str(message.chat.id)
    command = message.text.lower().split()

    if len(command) < 2:
        bot.reply_to(message, "Usage: /reports <on/off/yes/no/true/false>")
        return

    state = command[1]
    if state in ['on', 'yes', 'true']:
        group_report_settings[chat_id] = True
        save_report_settings(group_report_settings)
        bot.reply_to(message, "Reports are now enabled for this group.")
    elif state in ['off', 'no', 'false']:
        group_report_settings[chat_id] = False
        save_report_settings(group_report_settings)
        bot.reply_to(message, "Reports are now disabled for this group.")
    else:
        bot.reply_to(message, "Invalid option. Use on/off/yes/no/true/false.")

def notify_admins(chat_id, reporter_name, group_name, reported_user=None, message_text=None, message_link=None):
    """Notify group admins about a report."""
    try:
        chat_admins = bot.get_chat_administrators(chat_id)
        for admin in chat_admins:
            try:
                if message_link:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("View Message", url=message_link))
                    bot.send_message(
                        admin.user.id,
                        f"New report from {reporter_name}:\n"
                        f"Reported user: {reported_user or 'None'}\n"
                        f"Group: {group_name}\n"
                        f"Message: {message_text or 'No text'}",
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                else:
                    bot.send_message(
                        admin.user.id,
                        f"New report from {reporter_name}:\n"
                        f"Group: {group_name}\n"
                        f"No specific message reported.",
                        parse_mode='Markdown'
                    )
            except telebot.apihelper.ApiTelegramException as e:
                logger.warning(f"Failed to notify admin {admin.user.id}: {e}")
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error fetching admins for notification: {e}")

def handle_report(message, is_admin_mention=False):
    """Handle /report and @admin commands."""
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "This command can only be used in groups.")
        return

    chat_id = str(message.chat.id)
    if chat_id in group_report_settings and not group_report_settings[chat_id]:
        bot.reply_to(message, "Reporting is currently disabled in this group.")
        return

    try:
        chat_admins = bot.get_chat_administrators(message.chat.id)
        if any(admin.user.id == message.from_user.id for admin in chat_admins):
            return
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error checking admin status: {e}")
        bot.reply_to(message, "Error: Unable to verify admin status.")
        return
    admin_names = get_admin_names(message.chat.id)
    admin_name = ", ".join(admin_names) if admin_names else "Admin"

    if message.reply_to_message:
        reported_user = message.reply_to_message.from_user
        if any(admin.user.id == reported_user.id for admin in chat_admins):
            bot.reply_to(message, "Are you sure to report an admin?")
            return

        reported_message_link = f"https://t.me/c/{str(message.chat.id)[4:]}/{message.reply_to_message.message_id}"
        response = f"Reported [{reported_user.first_name}]({reported_message_link}) to {admin_name}"
        
        notify_admins(
            chat_id=message.chat.id,
            reporter_name=message.from_user.first_name,
            group_name=message.chat.title,
            reported_user=reported_user.first_name,
            message_text=message.reply_to_message.text,
            message_link=reported_message_link
        )
    else:
        response = f"Reported to {admin_name}"
        notify_admins(
            chat_id=message.chat.id,
            reporter_name=message.from_user.first_name,
            group_name=message.chat.title
        )

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(regexp=r'^[\/!](report)(?:\s|$|@)')
@disabled
def command_report_message(message):
    """Handle /report command."""
    handle_report(message)

@bot.message_handler(regexp='@admin')
@disabled
def command_admin_mention(message):
    """Handle @admin mention."""
    handle_report(message, is_admin_mention=True)
    
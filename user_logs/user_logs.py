import json
import os
import logging
from datetime import datetime
import telebot
from telebot import types
from functools import wraps
from config import bot, logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import time

LOGS_DIR = "logs"
SCHEDULE_FILE = os.path.join(LOGS_DIR, "schedule.json")
os.makedirs(LOGS_DIR, exist_ok=True)

scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()

def is_group(func):
    @wraps(func)
    def wrapper(message):
        if message.chat.type in ['group', 'supergroup']:
            return func(message)
        return
    return wrapper
    
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

def admin_required(func):
    @wraps(func)
    def wrapper(message):
        try:
            chat_id = message.chat.id
            user_id = message.from_user.id
            if not is_admin(chat_id, user_id):
                bot.reply_to(message, "You must be an admin to use this command!")
                logger.warning(f"Unauthorized access attempt by user {user_id} in chat {chat_id}")
                return
            return func(message)
        except telebot.apihelper.ApiTelegramException as e:
            bot.reply_to(message, "Error checking admin status.")
            logger.error(f"Telegram API error while checking admin: {e}")
        except Exception as e:
            bot.reply_to(message, "An unexpected error occurred.")
            logger.error(f"Unexpected error in admin_required: {e}")
    return wrapper

def get_log_file(chat_id):
    return os.path.join(LOGS_DIR, f"chat_{chat_id}.json")

def get_archive_log_file(chat_id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOGS_DIR, f"chat_{chat_id}_archive_{timestamp}.json")

def log_action(chat_id, action, executor, target, details=None):
    try:
        log_entry = {
            "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "action": action,
            "executor": {
                "id": executor.id,
                "first_name": executor.first_name,
                "username": executor.username
            },
            "target": {
                "id": target.id,
                "title": getattr(target, "title", None),
                "first_name": getattr(target, "first_name", None),
                "username": getattr(target, "username", None)
            },
            "details": details or {}
        }
        log_file = get_log_file(chat_id)
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Corrupted JSON in {log_file}, starting fresh")
        logs.append(log_entry)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
        if os.path.getsize(log_file) > 10 * 1024 * 1024:
            os.rename(log_file, get_archive_log_file(chat_id))
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    except Exception as e:
        logger.error(f"Error logging action for chat {chat_id}: {e}")

def parse_duration(duration_str):
    try:
        if not duration_str:
            return None
        unit = duration_str[-2:].lower() if duration_str[-2:].lower() == 'mo' else duration_str[-1].lower()
        value = int(duration_str[:-2 if unit == 'mo' else -1])
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
        elif unit == 'mo':
            return value * 2592000
        elif unit == 'y':
            return value * 31536000
        return None
    except (ValueError, IndexError):
        return None

def clear_logs(chat_id):
    log_file = get_log_file(chat_id)
    try:
        if os.path.exists(log_file):
            os.remove(log_file)
            logger.info(f"Logs cleared for chat {chat_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error clearing logs for chat {chat_id}: {e}")
        return False

def schedule_log_clearing(chat_id, duration):
    try:
        run_time = time.time() + duration
        job = scheduler.add_job(
            clear_logs,
            trigger=DateTrigger(run_date=datetime.fromtimestamp(run_time)),
            args=[chat_id],
            id=f"clear_logs_{chat_id}"
        )
        schedules = {}
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                schedules = json.load(f)
        schedules[str(chat_id)] = {
            "duration": duration,
            "run_time": run_time
        }
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=4)
        logger.info(f"Scheduled log clearing for chat {chat_id} in {duration} seconds")
    except Exception as e:
        logger.error(f"Error scheduling log clearing for chat {chat_id}: {e}")

def cancel_log_clearing(chat_id):
    try:
        scheduler.remove_job(f"clear_logs_{chat_id}")
        schedules = {}
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                schedules = json.load(f)
        if str(chat_id) in schedules:
            del schedules[str(chat_id)]
            with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
                json.dump(schedules, f, ensure_ascii=False, indent=4)
            logger.info(f"Cancelled scheduled log clearing for chat {chat_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error cancelling log clearing for chat {chat_id}: {e}")
        return False

def format_log_entry(entry):
    executor = entry["executor"]["first_name"] or entry["executor"]["username"] or f"ID {entry['executor']['id']}"
    if entry["target"]["title"]:
        target = entry["target"]["title"]
    else:
        target = entry["target"]["first_name"] or entry["target"]["username"] or f"ID {entry['target']['id']}"
    details = ", ".join(f"{k}: {v}" for k, v in entry["details"].items()) if entry["details"] else "None"
    return (f"[{entry['timestamp']}] {entry['action'].upper()}\n"
            f"By: {executor}\n"
            f"Target: {target}\n"
            f"Details: {details}\n")

@bot.message_handler(commands=['logs'])
@is_group
@admin_required
def command_logs(message):
    try:
        args = message.text.split()
        if len(args) > 1 and args[1].lower() in ['txt', 'json']:
            if args[1].lower() == 'txt':
                command_logs_txt(message)
            else:
                command_logs_json(message)
            return
        log_file = get_log_file(message.chat.id)
        if not os.path.exists(log_file):
            bot.reply_to(message, "No logs found for this group.")
            return
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        if not logs:
            bot.reply_to(message, "No logs found for this group.")
            return
        response = "Recent Logs:\n\n"
        for entry in logs[-10:]:
            response += format_log_entry(entry) + "\n"
        bot.reply_to(message, response)
    except FileNotFoundError:
        bot.reply_to(message, "No logs found for this group.")
        logger.error(f"Log file not found for chat {message.chat.id}")
    except json.JSONDecodeError:
        bot.reply_to(message, "Error: Corrupted log file.")
        logger.error(f"Corrupted JSON in log file for chat {message.chat.id}")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error sending logs due to Telegram API limits.")
        logger.error(f"Telegram API error in /logs: {e}")
    except Exception as e:
        bot.reply_to(message, "Error retrieving logs.")
        logger.error(f"Unexpected error in /logs for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['logs txt'])
@is_group
@admin_required
def command_logs_txt(message):
    try:
        bot.reply_to(message, "Collecting logs, please wait, this may take a while...")
        log_file = get_log_file(message.chat.id)
        if not os.path.exists(log_file):
            bot.reply_to(message, "No logs found for this group.")
            return
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        if not logs:
            bot.reply_to(message, "No logs found for this group.")
            return
        txt_content = "Group Logs\n\n"
        for entry in logs:
            txt_content += format_log_entry(entry) + "\n"
        txt_file = f"logs_{message.chat.id}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        with open(txt_file, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="Group Logs (TXT)")
        os.remove(txt_file)
        if os.path.getsize(log_file) > 5 * 1024 * 1024:
            os.rename(log_file, get_archive_log_file(message.chat.id))
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    except FileNotFoundError:
        bot.reply_to(message, "No logs found for this group.")
        logger.error(f"Log file not found for chat {message.chat.id}")
    except json.JSONDecodeError:
        bot.reply_to(message, "Error: Corrupted log file.")
        logger.error(f"Corrupted JSON in log file for chat {message.chat.id}")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error sending text logs due to Telegram API limits.")
        logger.error(f"Telegram API error in /logs txt: {e}")
    except Exception as e:
        bot.reply_to(message, "Error exporting logs to text.")
        logger.error(f"Unexpected error in /logs txt for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['logs json'])
@is_group
@admin_required
def command_logs_json(message):
    try:
        bot.reply_to(message, "Collecting logs, please wait, this may take a while...")
        log_file = get_log_file(message.chat.id)
        if not os.path.exists(log_file):
            bot.reply_to(message, "No logs found for this group.")
            return
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        if not logs:
            bot.reply_to(message, "No logs found for this group.")
            return
        json_file = f"logs_{message.chat.id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
        with open(json_file, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="Group Logs (JSON)")
        os.remove(json_file)
        if os.path.getsize(log_file) > 5 * 1024 * 1024:
            os.rename(log_file, get_archive_log_file(message.chat.id))
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    except FileNotFoundError:
        bot.reply_to(message, "No logs found for this group.")
        logger.error(f"Log file not found for chat {message.chat.id}")
    except json.JSONDecodeError:
        bot.reply_to(message, "Error: Corrupted log file.")
        logger.error(f"Corrupted JSON in log file for chat {message.chat.id}")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error sending JSON logs due to Telegram API limits.")
        logger.error(f"Telegram API error in /logs json: {e}")
    except Exception as e:
        bot.reply_to(message, "Error exporting logs to JSON.")
        logger.error(f"Unexpected error in /logs json for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['clearlogs'])
@is_group
@admin_required
def command_clearlogs(message):
    try:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            duration_str = args[1]
            duration = parse_duration(duration_str)
            if not duration:
                bot.reply_to(message, "Invalid duration. Use formats like 1s, 30m, 2h, 1d, 1w, 1mo, 1y.")
                return
            schedule_log_clearing(message.chat.id, duration)
            bot.reply_to(message, f"Scheduled log clearing in {duration_str}.")
        else:
            if clear_logs(message.chat.id):
                bot.reply_to(message, "Logs cleared successfully!")
            else:
                bot.reply_to(message, "No logs found to clear.")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error interacting with Telegram API.")
        logger.error(f"Telegram API error in /clearlogs: {e}")
    except Exception as e:
        bot.reply_to(message, "Error clearing logs.")
        logger.error(f"Unexpected error in /clearlogs for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['txtlogs'])
@is_group
@admin_required
def command_txtlogs(message):
    try:
        bot.reply_to(message, "Collecting logs, please wait, this may take a while...")
        log_file = get_log_file(message.chat.id)
        if not os.path.exists(log_file):
            bot.reply_to(message, "No logs found for this group.")
            return
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        if not logs:
            bot.reply_to(message, "No logs found for this group.")
            return
        txt_content = "Group Logs\n\n"
        for entry in logs:
            txt_content += format_log_entry(entry) + "\n"
        txt_file = f"logs_{message.chat.id}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        with open(txt_file, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="Group Logs")
        os.remove(txt_file)
        if os.path.getsize(log_file) > 5 * 1024 * 1024:
            os.rename(log_file, get_archive_log_file(message.chat.id))
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    except FileNotFoundError:
        bot.reply_to(message, "No logs found for this group.")
        logger.error(f"Log file not found for chat {message.chat.id}")
    except json.JSONDecodeError:
        bot.reply_to(message, "Error: Corrupted log file.")
        logger.error(f"Corrupted JSON in log file for chat {message.chat.id}")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error sending text logs due to Telegram API limits.")
        logger.error(f"Telegram API error in /txtlogs: {e}")
    except Exception as e:
        bot.reply_to(message, "Error exporting logs.")
        logger.error(f"Unexpected error in /txtlogs for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['helplogs'])
@is_group
@admin_required
def command_helplogs(message):
    try:
        help_text = (
            "📜 Log Commands Help\n\n"
            "/logs - View recent group logs (last 10 entries).\n"
            "/logs txt - Export group logs as a text file.\n"
            "/logs json - Export group logs as a JSON file.\n"
            "/clearlogs - Clear all group logs immediately.\n"
            "/clearlogs <duration> - Schedule log clearing (e.g., 1d, 1w, 1mo).\n"
            "/cancelclear - Cancel scheduled log clearing.\n"
            "/txtlogs - Export group logs as a text file (legacy).\n"
            "/logsummary - Show a summary of group actions.\n"
            "/helplogs - Show this help message.\n\n"
            "Durations: s (seconds), m (minutes), h (hours), d (days), w (weeks), mo (months), y (years)."
        )
        bot.reply_to(message, help_text)
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error sending help message.")
        logger.error(f"Telegram API error in /helplogs: {e}")
    except Exception as e:
        bot.reply_to(message, "Error displaying help.")
        logger.error(f"Unexpected error in /helplogs for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['cancelclear'])
@is_group
@admin_required
def command_cancelclear(message):
    try:
        if cancel_log_clearing(message.chat.id):
            bot.reply_to(message, "Scheduled log clearing cancelled.")
        else:
            bot.reply_to(message, "No scheduled log clearing found.")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error interacting with Telegram API.")
        logger.error(f"Telegram API error in /cancelclear: {e}")
    except Exception as e:
        bot.reply_to(message, "Error cancelling log clearing.")
        logger.error(f"Unexpected error in /cancelclear for chat {message.chat.id}: {e}")

@bot.message_handler(commands=['logsummary'])
@is_group
@admin_required
def command_logsummary(message):
    try:
        bot.reply_to(message, "Collecting log summary, please wait...")
        log_file = get_log_file(message.chat.id)
        if not os.path.exists(log_file):
            bot.reply_to(message, "No logs found for this group.")
            return
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        if not logs:
            bot.reply_to(message, "No logs found for this group.")
            return
        action_counts = {}
        for entry in logs:
            action = entry["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        response = "Log Summary:\n\n"
        for action, count in action_counts.items():
            response += f"{action.upper()}: {count}\n"
        
        lines = response.splitlines()
        if len(lines) > 4000:
            part = 1
            current_part = []
            current_count = 0
            for line in lines:
                current_part.append(line)
                current_count += 1
                if current_count >= 4000:
                    bot.send_message(message.chat.id, f"Log Summary Part {part}:\n\n" + "\n".join(current_part))
                    part += 1
                    current_part = []
                    current_count = 0
            if current_part:
                bot.send_message(message.chat.id, f"Log Summary Part {part}:\n\n" + "\n".join(current_part))
        else:
            bot.reply_to(message, response)
    except FileNotFoundError:
        bot.reply_to(message, "No logs found for this group.")
        logger.error(f"Log file not found for chat {message.chat.id}")
    except json.JSONDecodeError:
        bot.reply_to(message, "Error: Corrupted log file.")
        logger.error(f"Corrupted JSON in log file for chat {message.chat.id}")
    except telebot.apihelper.ApiTelegramException as e:
        bot.reply_to(message, "Error sending log summary due to Telegram API limits.")
        logger.error(f"Telegram API error in /logsummary: {e}")
    except Exception as e:
        bot.reply_to(message, "Error generating log summary.")
        logger.error(f"Unexpected error in /logsummary for chat {message.chat.id}: {e}")

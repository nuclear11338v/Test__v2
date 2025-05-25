import logging
from datetime import datetime
from telebot import TeleBot, types
from telebot.util import quick_markup
import re
import telebot
import json
import os
from telebot.types import Message
from functools import wraps
from telebot.types import ChatPermissions
from config import bot, logger
from kick import disabled
import time
from typing import List, Dict, Optional, Any
from threading import Lock
from datetime import datetime, timedelta
from user_logs.user_logs import log_action
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from functools import wraps
import html
from admins import is_group
from telebot.util import quick_markup
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group, is_user_admin
from datetime import datetime, timedelta



LOCKS_FILE = "locks.json"
SETTINGS_FILE = "chat_settings.json"
BLOCKLIST_FILE = "blocklist.json"
file_lock = Lock()

default_settings = {
    "flood_limit": 0,
    "timed_flood": {"count": 0, "duration": 0},
    "flood_mode": "mute",
    "clear_flood": False,
}

def load_blocklist():
    try:
        with file_lock:
            with open(BLOCKLIST_FILE, "r") as f:
                data = json.load(f)
                for chat_id in data.get("settings", {}):
                    data["settings"][chat_id] = {**default_settings, **data["settings"][chat_id]}
                return data
    except FileNotFoundError:
        return {"settings": {}, "users": {}}
    except json.JSONDecodeError:
        print("Error: blocklist.json is corrupted. Initializing new blocklist.")
        return {"settings": {}, "users": {}}
    except Exception as e:
        print(f"Error loading blocklist: {e}")
        return {"settings": {}, "users": {}}

def save_blocklist(data):
    try:
        with file_lock:
            with open(BLOCKLIST_FILE, "w") as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving blocklist: {e}")

blocklist = load_blocklist()

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode settings JSON: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

def load_locks():
    try:
        if os.path.exists(LOCKS_FILE):
            with open(LOCKS_FILE, "r") as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode locks JSON: {e}")
        return {}
    except Exception as e:
        logger.error(f"Error loading locks: {e}")
        return {}

def save_locks(locks):
    try:
        with open(LOCKS_FILE, "w") as f:
            json.dump(locks, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving locks: {e}")

def init_chat_locks(chat_id):
    locks = load_locks()
    chat_id = str(chat_id)
    
    default_locks = {
        "all": False,
        "album": False,
        "invitelink": False,
        "anonchannel": False,
        "audio": False,
        "bot": False,
        "botlink": False,
        "button": False,
        "commands": False,
        "comment": False,
        "contact": False,
        "document": False,
        "email": False,
        "emoji": False,
        "emojicustom": False,
        "emojigame": False,
        "externalreply": False,
        "game": False,
        "gif": False,
        "inline": False,
        "location": False,
        "phone": False,
        "photo": False,
        "poll": False,
        "spoiler": False,
        "text": False,
        "url": False,
        "video": False,
        "videonote": False,
        "voice": False,
        "sticker": False
    }
    
    if chat_id not in locks:
        locks[chat_id] = default_locks
    else:
        locks[chat_id] = {**default_locks, **locks[chat_id]}
    
    save_locks(locks)
    return locks

URL_PATTERN = re.compile(
    r'(?i)'
    r'(?:'
    r'https?://[\w\-\.]+(?:\.[\w\-]+)+[\w\-\._~:/?#[\]@!$&\'()*+,;=]*|'
    r'@[\w_]+|'
    r'[\w\-\.]+\.(?:com|online|org|net|edu|gov|io|co|biz|info|me|tv|us|uk|ca|au|de|fr|in|cn|jp|ru|br|it|es|nl|se|no|fi|dk|ch|at|be|pl|hu|cz|ro|gr|tr|mx|ar|cl|co|pe|ve|za|ng|eg|sa|ae|il|sg|my|th|vn|ph|id|kr|tw|hk|nz|ie|pt|sk|si|hr|rs|bg|lt|lv|ee|ua|by|kz|bd|lk|np|pk|ir|iq|sy|jo|lb|kw|qa|om|bh|ye|tn|dz|ma|ly|sd|et|ke|ug|gh|ci|cm|cd|zm|zw|ao|mz|bw|na|rw|tz|mg|mw|ls|sz|bj|bf|bi|cv|cf|td|km|dj|ga|gm|gn|gw|lr|ml|mr|ne|sn|sl|tg|mu|re|sc|st|yt|fk|gl|pn|sh|tk|to|tv|wf|ws|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bl|bm|bn|bo|bq|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cw|cx|cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mf|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tr|tt|tv|tw|tz|ua|ug|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw)(?:/[\w\-\._~:/?#[\]@!$&\'()*+,;=]*)?)'
)

@bot.message_handler(regexp=r'^[\/!](lock)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_lock(message):
    chat_id = str(message.chat.id)
    locks = init_chat_locks(chat_id)
    args = message.text.split()

    if len(args) < 2:
        valid_types = [
            "all", "album", "invitelink", "anonchannel", "audio", "bot", "botlink", "button",
            "commands", "comment", "contact", "document", "email", "emoji", "emojicustom",
            "emojigame", "externalreply", "game", "gif", "inline", "location", "phone",
            "photo", "poll", "spoiler", "text", "url", "video", "videonote", "voice"
        ]
        bot.reply_to(message, f"Usage: /lock <type> ({', '.join(valid_types)})")
        return

    lock_type = args[1].lower()
    valid_types = [
        "all", "album", "invitelink", "anonchannel", "audio", "bot", "botlink", "button",
        "commands", "comment", "contact", "document", "email", "emoji", "emojicustom",
        "emojigame", "externalreply", "game", "gif", "inline", "location", "phone",
        "photo", "poll", "spoiler", "text", "url", "video", "videonote", "voice"
    ]

    if lock_type not in valid_types:
        bot.reply_to(message, f"Invalid lock type! Valid types: {', '.join(valid_types)}")
        return

    locks[chat_id][lock_type] = True
    save_locks(locks)

    if lock_type == "all":
        try:
            bot.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_invite_users=False
                )
            )
            log_action(
                chat_id=message.chat.id,
                action="lock",
                executor=message.from_user,
                target=message.chat,
                details={"type": lock_type}
            )
            bot.reply_to(message, "Chat is now locked for all members.")
        except telebot.apihelper.ApiTelegramException as e:
            bot.reply_to(message, f"Error setting permissions: {e}")
    else:
        log_action(
            chat_id=message.chat.id,
            action="lock",
            executor=message.from_user,
            target=message.chat,
            details={"type": lock_type}
        )
        bot.reply_to(message, f"{lock_type.capitalize()} messages are now locked!")
        
@bot.message_handler(regexp=r'^[\/!](unlock)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_unlock(message):
    chat_id = str(message.chat.id)
    locks = init_chat_locks(chat_id)
    args = message.text.split()

    if len(args) < 2:
        valid_types = [
            "all", "album", "invitelink", "anonchannel", "audio", "bot", "botlink", "button",
            "commands", "comment", "contact", "document", "email", "emoji", "emojicustom",
            "emojigame", "externalreply", "game", "gif", "inline", "location", "phone",
            "photo", "poll", "spoiler", "text", "url", "video", "videonote", "voice"
        ]
        bot.reply_to(message, f"Usage: /unlock <type> ({', '.join(valid_types)})")
        return

    lock_type = args[1].lower()
    valid_types = [
        "all", "album", "invitelink", "anonchannel", "audio", "bot", "botlink", "button",
        "commands", "comment", "contact", "document", "email", "emoji", "emojicustom",
        "emojigame", "externalreply", "game", "gif", "inline", "location", "phone",
        "photo", "poll", "spoiler", "text", "url", "video", "videonote", "voice"
    ]

    if lock_type not in valid_types:
        bot.reply_to(message, f"Invalid lock type! Valid types: {', '.join(valid_types)}")
        return

    locks[chat_id][lock_type] = False
    save_locks(locks)

    if lock_type == "all":
        try:
            bot.set_chat_permissions(
                chat_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True
                )
            )
            log_action(
                chat_id=message.chat.id,
                action="unlock",
                executor=message.from_user,
                target=message.chat,
                details={"type": lock_type}
            )
            bot.reply_to(message, "Chat is now unlocked for all members!")
        except telebot.apihelper.ApiTelegramException as e:
            bot.reply_to(message, f"Error setting permissions: {e}")
    else:
        log_action(
            chat_id=message.chat.id,
            action="unlock",
            executor=message.from_user,
            target=message.chat,
            details={"type": lock_type}
        )
        bot.reply_to(message, f"{lock_type.capitalize()} messages are now unlocked!")

@bot.message_handler(regexp=r'^[\/!](pinned)(?:\s|$|@)')
@is_group
@disabled
def command_get_pinned(message):
    try:
        chat = bot.get_chat(message.chat.id)
        if chat.pinned_message:
            chat_id = str(message.chat.id)
            if chat_id.startswith('-100'):
                chat_id = chat_id[4:]
            message_id = chat.pinned_message.message_id
            pinned_link = f"https://t.me/c/{chat_id}/{message_id}"
            bot.reply_to(message, f"[Click here to view the pinned message.]({pinned_link})", parse_mode='Markdown')
        else:
            bot.reply_to(message, "No pinned message.")
    except telebot.apihelper.ApiTelegramException as e:
        if "chat not found" in str(e).lower():
            bot.reply_to(message, "Error: Chat not found.")
        elif "not enough rights" in str(e).lower():
            bot.reply_to(message, "Error: Bot lacks permission to access chat info.")
        else:
            bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](pin)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_pin_message(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "reply to a message to pin it!")
            return
        
        notify = 'notify' in message.text.lower() or 'loud' in message.text.lower()
        bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id,
            disable_notification=not notify
        )
        log_action(
            chat_id=message.chat.id,
            action="pin",
            executor=message.from_user,
            target=message.chat,
            details={"notify": notify}
        )
        bot.reply_to(message, "Message pinned successfully.")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights to pin" in str(e).lower() or "can_pin_messages" in str(e).lower():
            bot.reply_to(message, "Error: Bot lacks permission to pin messages.")
        elif "message to pin not found" in str(e).lower():
            bot.reply_to(message, "Error: The message to pin no longer exists.")
        elif "chat not found" in str(e).lower():
            bot.reply_to(message, "Error: Chat not found.")
        else:
            bot.reply_to(message, f"Error pinning message: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](permapin)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_perma_pin(message):
    try:
        text = message.text.replace('/permapin', '').strip()
        if not text:
            bot.reply_to(message, "provide text to pin.\n\n/permpin hello")
            return
        
        sent_message = bot.send_message(message.chat.id, text, parse_mode='Markdown')
        bot.pin_chat_message(
            chat_id=message.chat.id,
            message_id=sent_message.message_id,
            disable_notification=True
        )
        log_action(
            chat_id=message.chat.id,
            action="permapin",
            executor=message.from_user,
            target=message.chat,
            details={"type": "custom"}
        )
        bot.reply_to(message, "message pinned successfully.")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights to pin" in str(e).lower() or "can_pin_messages" in str(e).lower():
            bot.reply_to(message, "Error: Bot lacks permission to pin messages.\n- can_pin_messages")
        elif "chat not found" in str(e).lower():
            bot.reply_to(message, "Error: Chat not found.")
        elif "message too long" in str(e).lower():
            bot.reply_to(message, "Error: The provided text is too long.")
        else:
            bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](unpin)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_unpin_message(message):
    try:
        if message.reply_to_message:
            bot.unpin_chat_message(
                chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )
            log_action(
                chat_id=message.chat.id,
                action="unpin",
                executor=message.from_user,
                target=message.chat,
                details={"scope": "specific"}
            )
            bot.reply_to(message, "Message unpinned successfully.")
        else:
            bot.unpin_chat_message(message.chat.id)
            log_action(
                chat_id=message.chat.id,
                action="unpin",
                executor=message.from_user,
                target=message.chat,
                details={"scope": "current"}
            )
            bot.reply_to(message, "Pinned message removed!")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower() or "can_pin_messages" in str(e).lower():
            bot.reply_to(message, "Bot lacks permission to unpin messages.\n- can_pin_messages")
        elif "message to unpin not found" in str(e).lower():
            bot.reply_to(message, "No pinned message found.")
        elif "chat not found" in str(e).lower():
            bot.reply_to(message, "Error: Chat not found.")
        else:
            bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](unpinall)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_unpin_all(message):
    try:
        bot.unpin_all_chat_messages(message.chat.id)
        log_action(
            chat_id=message.chat.id,
            action="unpinall",
            executor=message.from_user,
            target=message.chat,
            details={"scope": "all"}
        )
        bot.reply_to(message, "All pinned messages removed!")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower() or "can_pin_messages" in str(e).lower():
            bot.reply_to(message, "Bot lacks permission to unpin messages.\n- can_pin_messages")
        elif "chat not found" in str(e).lower():
            bot.reply_to(message, "Chat not found.")
        else:
            bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](antichannelpin)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_antichannelpin(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.lower().replace('/antichannelpin', '').strip()
        settings = load_settings()

        if chat_id not in settings:
            settings[chat_id] = {'antichannelpin': False, 'cleanlinked': False}

        if not args:
            status = "on" if settings[chat_id]['antichannelpin'] else "off"
            bot.reply_to(message, f"Anti-channel pin is currently {status}.")
            return

        if args in ['yes', 'on']:
            settings[chat_id]['antichannelpin'] = True
            operation = "enable"
            bot.reply_to(message, "Anti-channel pin enabled.")
        elif args in ['no', 'off']:
            settings[chat_id]['antichannelpin'] = False
            operation = "disable"
            bot.reply_to(message, "Anti-channel pin disabled.")
        else:
            bot.reply_to(message, "Invalid argument. Use yes/no/on/off.")
            return

        save_settings(settings)
        log_action(
            chat_id=message.chat.id,
            action="antichannelpin",
            executor=message.from_user,
            target=message.chat,
            details={"operation": operation}
        )
    except telebot.apihelper.ApiTelegramException as e:
        if "chat not found" in str(e).lower():
            bot.reply_to(message, "Chat not found.")
        else:
            bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](cleanlinked)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_cleanlinked(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.lower().replace('/cleanlinked', '').strip()
        settings = load_settings()

        if chat_id not in settings:
            settings[chat_id] = {'antichannelpin': False, 'cleanlinked': False}

        if not args:
            status = "on" if settings[chat_id]['cleanlinked'] else "off"
            bot.reply_to(message, f"Clean linked channel messages is currently {status}.")
            return

        if args in ['yes', 'on']:
            settings[chat_id]['cleanlinked'] = True
            operation = "enable"
            bot.reply_to(message, "Clean linked channel messages enabled.")
        elif args in ['no', 'off']:
            settings[chat_id]['cleanlinked'] = False
            operation = "disable"
            bot.reply_to(message, "Clean linked channel messages disabled.")
        else:
            bot.reply_to(message, "Invalid argument. Use yes/no/on/off.")
            return

        save_settings(settings)
        log_action(
            chat_id=message.chat.id,
            action="cleanlinked",
            executor=message.from_user,
            target=message.chat,
            details={"operation": operation}
        )
    except telebot.apihelper.ApiTelegramException as e:
        if "chat not found" in str(e).lower():
            bot.reply_to(message, "Chat not found.")
        else:
            bot.reply_to(message, f"Error: {str(e)}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {str(e)}")

def parse_duration(duration_str):
    try:
        if not duration_str:
            return 0
        match = re.match(r"^(\d+)([smhd])$", duration_str.lower())
        if not match:
            return None
        value, unit = int(match.group(1)), match.group(2)
        if unit == "s":
            return value
        elif unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        elif unit == "d":
            return value * 86400
    except Exception:
        return None
    return 0

def apply_action(chat_id, user_id, action, duration=None):
    try:
        if action == "ban":
            bot.ban_chat_member(chat_id, user_id)
            return "banned"
        elif action == "mute":
            bot.restrict_chat_member(chat_id, user_id, permissions=telebot.types.ChatPermissions(can_send_messages=False))
            return "muted"
        elif action == "kick":
            bot.ban_chat_member(chat_id, user_id)
            bot.unban_chat_member(chat_id, user_id)
            return "kicked"
        elif action == "tban" and duration:
            until_date = int(time.time()) + duration
            bot.ban_chat_member(chat_id, user_id, until_date=until_date)
            return f"temporarily banned for {duration} seconds"
        elif action == "tmute" and duration:
            until_date = int(time.time()) + duration
            bot.restrict_chat_member(chat_id, user_id, permissions=telebot.types.ChatPermissions(can_send_messages=False), until_date=until_date)
            return f"temporarily muted for {duration} seconds"
        else:
            return None
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error applying action: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error applying action: {e}")
        return None

@bot.message_handler(regexp=r'^[\/!](flood)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_flood_settings(message):
    try:
        chat_id = str(message.chat.id)
        settings = blocklist["settings"].get(chat_id, default_settings)
        flood_limit = settings["flood_limit"]
        timed_flood = settings["timed_flood"]
        flood_mode = settings["flood_mode"]
        clear_flood = settings["clear_flood"]

        response = (
            f"*Antiflood Settings*\n"
            f"Consecutive Messages Limit: {flood_limit if flood_limit > 0 else 'Disabled'}\n"
            f"Timed Flood: {timed_flood['count']} messages in {timed_flood['duration']}s {'(Disabled)' if timed_flood['count'] == 0 else ''}\n"
            f"Action: {flood_mode}\n"
            f"Delete Flood Messages: {'Yes' if clear_flood else 'No'}"
        )
        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Error retrieving settings: {e}")

@bot.message_handler(regexp=r'^[\/!](setflood)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_set_flood(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "Usage: /setflood <number/off>")
            return

        value = args[0].lower()
        if value in ["off", "no", "0"]:
            blocklist["settings"][chat_id]["flood_limit"] = 0
            log_action(
                chat_id=message.chat.id,
                action="setflood",
                executor=message.from_user,
                target=message.chat,
                details={"limit": "disabled"}
            )
            bot.reply_to(message, "Antiflood disabled.")
        else:
            try:
                limit = int(value)
                if limit < 0:
                    bot.reply_to(message, "Limit must be a non-negative number.")
                    return
                blocklist["settings"][chat_id]["flood_limit"] = limit
                log_action(
                    chat_id=message.chat.id,
                    action="setflood",
                    executor=message.from_user,
                    target=message.chat,
                    details={"limit": limit}
                )
                bot.reply_to(message, f"Antiflood set to trigger after {limit} consecutive messages.")
            except ValueError:
                bot.reply_to(message, "Please provide a valid number or 'off'.")
                return
        save_blocklist(blocklist)
    except Exception as e:
        bot.reply_to(message, f"Error setting flood limit: {e}")

@bot.message_handler(regexp=r'^[\/!](setfloodtimer)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_set_flood_timer(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "Usage: /setfloodtimer <count> <duration> or /setfloodtimer off")
            return

        if chat_id not in blocklist["settings"]:
            blocklist["settings"][chat_id] = default_settings.copy()

        if args[0].lower() in ["off", "no"]:
            blocklist["settings"][chat_id]["timed_flood"] = {"count": 0, "duration": 0}
            log_action(
                chat_id=message.chat.id,
                action="setfloodtimer",
                executor=message.from_user,
                target=message.chat,
                details={"operation": "disable"}
            )
            bot.reply_to(message, "Timed antiflood disabled.")
            save_blocklist(blocklist)
            return

        if len(args) < 2:
            bot.reply_to(message, "Usage: /setfloodtimer <count> <duration>")
            return

        try:
            count = int(args[0])
            duration = parse_duration(args[1])
            if count <= 0 or duration is None:
                bot.reply_to(message, "Invalid count or duration. Duration format: e.g., 30s, 5m, 3d")
                return
            blocklist["settings"][chat_id]["timed_flood"] = {"count": count, "duration": duration}
            log_action(
                chat_id=message.chat.id,
                action="setfloodtimer",
                executor=message.from_user,
                target=message.chat,
                details={"count": count, "duration": duration}
            )
            bot.reply_to(message, f"Timed antiflood set to {count} messages in {duration} seconds.")
            save_blocklist(blocklist)
        except ValueError:
            bot.reply_to(message, "Please provide a valid number for count.")
    except Exception as e:
        logger.error(f"Error setting flood timer for chat {chat_id}: {e}")
        bot.reply_to(message, "An error occurred while setting the flood timer. Please try again.")

@bot.message_handler(regexp=r'^[\/!](floodmode)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_set_flood_mode(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "Usage: /floodmode <ban/mute/kick/tban/tmute> [duration for tban/tmute]")
            return

        action = args[0].lower()
        duration = parse_duration(args[1]) if len(args) > 1 and action in ["tban", "tmute"] else None
        if action in ["tban", "tmute"] and duration is None:
            bot.reply_to(message, f"Duration required for {action}. Format: e.g., 3d, 30s")
            return
        if action not in ["ban", "mute", "kick", "tban", "tmute"]:
            bot.reply_to(message, "Invalid action. Choose: ban, mute, kick, tban, tmute")
            return

        blocklist["settings"][chat_id]["flood_mode"] = action
        blocklist["settings"][chat_id]["flood_mode_duration"] = duration if duration else 0
        log_action(
            chat_id=message.chat.id,
            action="floodmode",
            executor=message.from_user,
            target=message.chat,
            details={"action": action, "duration": duration if duration else 0}
        )
        bot.reply_to(message, f"Flood action set to {action}" + (f" with duration {duration}s" if duration else ""))
        save_blocklist(blocklist)
    except Exception as e:
        bot.reply_to(message, f"Error setting flood mode: {e}")

@bot.message_handler(regexp=r'^[\/!](clearflood)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_set_clear_flood(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.split()[1:]
        if not args:
            bot.reply_to(message, "Usage: /clearflood <yes/no/on/off>")
            return

        value = args[0].lower()
        if value in ["yes", "on"]:
            blocklist["settings"][chat_id]["clear_flood"] = True
            operation = "enable"
            bot.reply_to(message, "Flood messages will be deleted.")
        elif value in ["no", "off"]:
            blocklist["settings"][chat_id]["clear_flood"] = False
            operation = "disable"
            bot.reply_to(message, "Flood messages will not be deleted.")
        else:
            bot.reply_to(message, "Invalid option. Use yes/no/on/off")
            return
        save_blocklist(blocklist)
        log_action(
            chat_id=message.chat.id,
            action="clearflood",
            executor=message.from_user,
            target=message.chat,
            details={"operation": operation}
        )
    except Exception as e:
        bot.reply_to(message, f"Error setting clear flood: {e}")

SLOWMODE_FILE = "slowmode.json"
slowmode_lock = Lock()
last_message_times = {}

def load_slowmode():
    try:
        with slowmode_lock:
            if os.path.exists(SLOWMODE_FILE):
                with open(SLOWMODE_FILE, 'r') as f:
                    return json.load(f)
            return {}
    except Exception as e:
        print(f"Error loading slowmode: {e}")
        return {}

def save_slowmode(data):
    try:
        with slowmode_lock:
            with open(SLOWMODE_FILE, 'w') as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving slowmode: {e}")

def parse_duration(duration_str):
    try:
        if not duration_str:
            return 0
        match = re.match(r"^(\d+)(s|m|h|d|w|mo|y)$", duration_str.lower())
        if not match:
            return None
            
        value, unit = int(match.group(1)), match.group(2)
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
            'mo': 2592000,
            'y': 31536000
        }
        return value * multipliers[unit]
    except Exception as e:
        logger.error(f"Duration parse error: {e}")
        return None

@bot.message_handler(regexp=r'^[\/!](slowmode)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def set_slowmode(message):
    chat_id = str(message.chat.id)
    args = message.text.split()
    
    if len(args) < 2:
        bot.reply_to(message, "Usage: /slowmode <off/False/1s/1m/1h/1d/1w/1mo/1y>")
        return
    
    mode = args[1].lower()
    slowmode_data = load_slowmode()
    
    if mode in ['off', 'false', '0']:
        slowmode_data[chat_id] = 0
        log_action(
            chat_id=message.chat.id,
            action="slowmode",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "disable"}
        )
        bot.reply_to(message, "Slow mode has been disabled.")
    else:
        duration = parse_duration(mode)
        if not duration or duration < 1:
            bot.reply_to(message, "Invalid duration format! Examples: 30s, 5m, 3h, 1d, 1w")
            return
        slowmode_data[chat_id] = duration
        log_action(
            chat_id=message.chat.id,
            action="slowmode",
            executor=message.from_user,
            target=message.chat,
            details={"duration": duration}
        )
        bot.reply_to(message, f"Slow mode set to {duration} seconds. Users must wait between messages.")
    
    save_slowmode(slowmode_data)
        
STORAGE_DIR = "custom_command"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

RESERVED_COMMANDS = {'help', 'promote', 'demote', 'admincache', 'adminerror', 'anonadmin', 'adminlist', 'mute', 'tmute', 'dmute', 'smute', 'rmute', 'unmute', 'checkmute', 'ban', 'rban', 'tban', 'sban', 'dban', 'unban', 'kick', 'skick', 'dkick', 'kickme', 'blocklist', 'blocklistmode', 'addblocklist', 'approve', 'lock', 'unlock', 'pin', 'unpin', 'unpinall', 'cleanlinked', 'antichannelpin', 'permapin', 'flood', 'setflood', 'clearflood', 'floodmode', 'setfloodtimer', 'disable', 'disableadmin', 'adddescription', 'renamegroup', 'save', 'privatenotes', 'clearall', 'clear', 'saved', 'notes', 'get', 'purge', 'spurge', 'purgeto', 'purgefrom', 'del', 'rules', 'setrules', 'resetrulesbutton', 'setrulesbutton', 'resetrules', 'privaterules', 'deletetopic', 'reopentopic', 'closetopic', 'renametopic', 'newtopic', 'warn', 'warntime', 'warnlimit', 'warningmode', 'warnings', 'resetallwarnings', 'rmwarn', 'swarn', 'dwarn', 'twarn', 'welcome', 'goodbye', 'setwelcome', 'setgoodbye', 'cleanwelcome', 'resetgoodbye', 'resetwelcome', 'autoantiraid', 'raidactiontime', 'raidtime', 'antiraid', 'filter', 'filters', 'stop', 'stopall', 'nocleanservice', 'cleanservicetypes', 'keepservice', 'cleanservice', 'cleancommand', 'keepcommand', 'id', 'info', 'me', 'privacy', 'connection', 'reconnect', 'disconnectall', 'connect', 'logsummary', 'cancelclear', 'helplogs', 'clearlogs', 'logs', 'abansticker', 'cleansticker', 'bansticker', 'tbansticker', 'unbansticker', 'wbansticker', 'banstickermode', 'ban_asticker', 'allowadmins', 'wbanstickermode', 'wbanstickerlimit', 'helpsticker', 'banstickerstatus', 'slowmode', 'addcommand', 'rcommand', 'ucommand', 'add_media_command', 'remove', 'commands', 'ban_forward_action', 'tban_forward', 'ban_forward'}

MARKDOWNV2_SPECIAL_CHARS = r'_[]()~`>#+-=|{}.!'
    
def escape_markdownv2(text):
    """Escape special MarkdownV2 characters, handling emojis safely."""
    if not text:
        return text
    for char in MARKDOWNV2_SPECIAL_CHARS:
        text = text.replace(char, f'\\{char}')
    return text

def get_chat_file(chat_id):
    return os.path.join(STORAGE_DIR, f"chat_{chat_id}.json")

def load_commands(chat_id):
    chat_file = get_chat_file(chat_id)
    if os.path.exists(chat_file):
        with open(chat_file, 'r') as f:
            return json.load(f)
    return {}

def save_commands(chat_id, commands):
    chat_file = get_chat_file(chat_id)
    with open(chat_file, 'w') as f:
        json.dump(commands, f, indent=4)

def replace_placeholders(message, response):
    """Replace placeholders with escaped values."""
    placeholders = {
        '{username}': message.from_user.username or '',
        '{first_name}': message.from_user.first_name or '',
        '{last_name}': message.from_user.last_name or '',
        '{first}': message.from_user.first_name or '',
        '{last}': message.from_user.last_name or '',
        '{group}': message.chat.title or '',
        '{group_name}': message.chat.title or '',
        '{id}': str(message.from_user.id)
    }
    for placeholder, value in placeholders.items():
        response = response.replace(placeholder, escape_markdownv2(value))
    return response

def parse_command_buttons(button_data):
    """Parse button data into inline keyboard, supporting [text](buttonurl://url) and text|url formats."""
    if not button_data:
        return None
    buttons = []
    button_matches = re.findall(r'\[([^\]]+)\]\(buttonurl://([^\)]+)\)', button_data)
    for text, url in button_matches:
        buttons.append(types.InlineKeyboardButton(text=text.strip(), url=url.strip()))
    for btn in button_data.split(';'):
        if '|' in btn and not re.match(r'\[.*\]\(buttonurl://.*\)', btn):
            text, url = btn.split('|', 1)
            buttons.append(types.InlineKeyboardButton(text=text.strip(), url=url.strip()))
    return types.InlineKeyboardMarkup([buttons]) if buttons else None

def extract_response_and_buttons(raw_input):
    """Extract response and button data, handling both :: and [text](buttonurl://url) formats."""
    parts = raw_input.split('::', 1)
    response = parts[0].strip()
    buttons = parts[1].strip() if len(parts) > 1 else ''
    
    button_matches = re.findall(r'(\[([^\]]+)\]\(buttonurl://([^\)]+)\))', raw_input)
    if button_matches:
        for full_match, text, url in button_matches:
            buttons += f"{text}|{url};" if buttons else f"{text}|{url}"
            response = response.replace(full_match, '').strip()
    
    return response, buttons

@bot.message_handler(regexp=r'^[\/!](addcommand)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def add_command(message):
    try:
        chat_id = message.chat.id
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "Usage: /add_command [command] [response]::[button_text|button_url;...] or [response with [text](buttonurl://url)]", parse_mode='HTML')
            return

        command = args[1].lstrip('/').lower()
        raw_response = args[2]
        response, buttons = extract_response_and_buttons(raw_response)

        if command in RESERVED_COMMANDS:
            bot.reply_to(message, f"Command /{command} is reserved and cannot be added.", parse_mode='HTML')
            return

        commands = load_commands(chat_id)
        if 'commands' not in commands:
            commands['commands'] = {}

        commands['commands'][command] = {
            'response': response,
            'added_on': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'chat_title': message.chat.title,
            'type': 'all',
            'buttons': buttons if buttons else None
        }

        save_commands(chat_id, commands)
        bot.reply_to(message, f"Command /{command} added successfully.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in add_command: {e}")
        bot.reply_to(message, "An error occurred while adding the command. Ensure the response and button format are correct.", parse_mode='Markdown')

@bot.message_handler(regexp=r'^[\/!](rcommand)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def add_restricted_command(message):
    try:
        chat_id = message.chat.id
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "Usage: /rcommand [command] [response]::[button_text|button_url;...] or [response with [text](buttonurl://url)]", parse_mode='HTML')
            return

        command = args[1].lstrip('/').lower()
        raw_response = args[2]
        response, buttons = extract_response_and_buttons(raw_response)

        if command in RESERVED_COMMANDS:
            bot.reply_to(message, f"Command `/{command}` is reserved and cannot be added.", parse_mode='HTML')
            return

        commands = load_commands(chat_id)
        if 'commands' not in commands:
            commands['commands'] = {}

        commands['commands'][command] = {
            'response': response,
            'added_on': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'chat_title': message.chat.title,
            'type': 'admin',
            'buttons': buttons if buttons else None
        }

        save_commands(chat_id, commands)
        bot.reply_to(message, f"Admin-only command /{command} added successfully.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in rcommand: {e}")
        bot.reply_to(message, "An error occurred while adding the admin command. Ensure the response and button format are correct.", parse_mode='Markdown')

@bot.message_handler(regexp=r'^[\/!](ucommand)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def add_user_command(message):
    try:
        chat_id = message.chat.id
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "Usage: /ucommand [command] [response]::[button_text|button_url;...] or [response with [text](buttonurl://url)]", parse_mode='HTML')
            return

        command = args[1].lstrip('/').lower()
        raw_response = args[2]
        response, buttons = extract_response_and_buttons(raw_response)

        if command in RESERVED_COMMANDS:
            bot.reply_to(message, f"Command /{command} is reserved and cannot be added.", parse_mode='Markdown')
            return

        commands = load_commands(chat_id)
        if 'commands' not in commands:
            commands['commands'] = {}

        commands['commands'][command] = {
            'response': response,
            'added_on': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'chat_title': message.chat.title,
            'type': 'user',
            'buttons': buttons if buttons else None
        }

        save_commands(chat_id, commands)
        bot.reply_to(message, f"User-only command /{command} added successfully.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in ucommand: {e}")
        bot.reply_to(message, "An error occurred while adding the user command. Ensure the response and button format are correct.", parse_mode='Markdown')

@bot.message_handler(commands=['add_media_command'])
@disabled
@is_admin
@is_group
def add_media_command(message):
    try:
        chat_id = message.chat.id
        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            bot.reply_to(message, "Usage: /add_media_command [command] [photo|video] [media_url]::[caption]::[button_text|button_url;...] or [caption with [text](buttonurl://url)]", parse_mode='HTML')
            return

        command = args[1].lstrip('/').lower()
        media_type = args[2].lower()
        data = args[3].split('::', 2)
        media_url = data[0].strip()
        caption = data[1].strip() if len(data) > 1 else ''
        buttons = data[2].strip() if len(data) > 2 else ''

        if caption:
            caption, extracted_buttons = extract_response_and_buttons(caption)
            buttons = extracted_buttons if extracted_buttons else buttons

        if media_type not in ['photo', 'video']:
            bot.reply_to(message, "Media type must be 'photo' or 'video'.", parse_mode='Markdown')
            return

        if command in RESERVED_COMMANDS:
            bot.reply_to(message, f"Command /{command} is reserved and cannot be added.", parse_mode='HTML')
            return

        commands = load_commands(chat_id)
        if 'commands' not in commands:
            commands['commands'] = {}

        commands['commands'][command] = {
            'media_type': media_type,
            'media_url': media_url,
            'caption': caption if caption else None,
            'added_on': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'chat_title': message.chat.title,
            'type': 'all',
            'buttons': buttons if buttons else None
        }

        save_commands(chat_id, commands)
        bot.reply_to(message, f"Media command `/{command}` added successfully.", parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in add_media_command: {e}")
        bot.reply_to(message, "An error occurred while adding the media command.", parse_mode='Markdown')

@bot.message_handler(regexp=r'^[\/!](remove)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def remove_command(message):
    try:
        chat_id = message.chat.id
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Usage: /remove [command]", parse_mode='HTML')
            return

        command = args[1].lstrip('/').lower()
        commands = load_commands(chat_id)

        if 'commands' not in commands or command not in commands['commands']:
            bot.reply_to(message, f"Command /{command} not found.", parse_mode='HTML')
            return

        del commands['commands'][command]
        save_commands(chat_id, commands)
        bot.reply_to(message, f"Command /{command} removed successfully.", parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in remove_command: {e}")
        bot.reply_to(message, "An error occurred while removing the command.", parse_mode='HTML')

@bot.message_handler(regexp=r'^[\/!](commands)(?:\s|$|@)')
@disabled
@is_group
def list_commands(message):
    try:
        chat_id = message.chat.id
        commands = load_commands(chat_id)

        if 'commands' not in commands or not commands['commands']:
            bot.reply_to(message, "No custom commands found for this group.", parse_mode='Markdown')
            return

        response = f"*Custom Commands ({len(commands['commands'])})*\n\n"
        for cmd, data in commands['commands'].items():
            if 'media_type' in data:
                response += f"`/{cmd}` - {data['media_type'].capitalize()} (URL: {data['media_url']})\n"
                response += f"Caption: {data['caption'] or 'None'}\n"
            else:
                response += f"`/{cmd}` - {data['response']}\n"
            response += f"Added on: {data['added_on']}\n"
            response += f"Type: {data['type'].capitalize()}\n"
            if data.get('buttons'):
                response += f"Buttons: {data['buttons']}\n"
            response += "\n"

        bot.reply_to(message, response, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in list_commands: {e}")
        bot.reply_to(message, "An error occurred while listing commands.", parse_mode='Markdown')
        
def handle_custom_command(message):
    try:
        chat_id = message.chat.id
        command = message.text.split()[0][1:].lower()
        commands = load_commands(chat_id)

        if 'commands' not in commands or command not in commands['commands']:
            return

        cmd_data = commands['commands'][command]
        cmd_type = cmd_data['type']
        user_id = message.from_user.id
        member = bot.get_chat_member(chat_id, user_id)
        is_admin_user = member.status in ['administrator', 'creator']

        if cmd_type == 'admin' and not is_admin_user:
            return
        if cmd_type == 'user' and is_admin_user:
            return  
        keyboard = parse_command_buttons(cmd_data['buttons']) if cmd_data.get('buttons') else None

        if 'media_type' in cmd_data:
            caption = replace_placeholders(message, cmd_data['caption']) if cmd_data.get('caption') else None
            if caption:
                caption = escape_markdownv2(caption)
            if cmd_data['media_type'] == 'photo':
                bot.send_photo(
                    chat_id,
                    cmd_data['media_url'],
                    caption=caption,
                    parse_mode='MarkdownV2' if caption else None,
                    reply_to_message_id=message.message_id,
                    reply_markup=keyboard
                )
            elif cmd_data['media_type'] == 'video':
                bot.send_video(
                    chat_id,
                    cmd_data['media_url'],
                    caption=caption,
                    parse_mode='MarkdownV2' if caption else None,
                    reply_to_message_id=message.message_id,
                    reply_markup=keyboard
                )
        else:
            response = replace_placeholders(message, cmd_data['response'])
            response = escape_markdownv2(response)
            bot.reply_to(
                message,
                response,
                parse_mode='MarkdownV2',
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Error in handle_custom_command: {e}")
        bot.reply_to(message, "An error occurred while processing the command.", parse_mode='Markdown')
        
DATA_FILE = "filters.json"
MAX_MESSAGE_LENGTH = 4000

def escape_html(text: str) -> str:
    """
    Escapes HTML special characters to prevent injection and ensure safe rendering.
    """
    return html.escape(text)

def safe_send_message(chat_id, text, reply_to_message_id=None, reply_markup=None):
    """
    Sends a message with HTML, falling back to plain text if it fails.
    """
    try:
        if reply_to_message_id:
            bot.send_message(
                chat_id,
                text,
                parse_mode='HTML',
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup
            )
        else:
            bot.send_message(
                chat_id,
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"HTML parsing failed: {e}. Sending as plain text.")
        
        plain_text = html.unescape(text)
        if reply_to_message_id:
            bot.send_message(
                chat_id,
                plain_text,
                parse_mode=None,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup
            )
        else:
            bot.send_message(
                chat_id,
                plain_text,
                parse_mode=None,
                reply_markup=reply_markup
            )

def load_data() -> Dict:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {}

def save_data(data: Dict) -> None:
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

filters_data = load_data()

def parse_buttons(response: str) -> tuple[str, InlineKeyboardMarkup | None]:
    markup = InlineKeyboardMarkup()
    buttons = []
    button_pattern = r'\[([^\]]+)\]\((buttonurl://[^)]+)\)'
    matches = re.findall(button_pattern, response)
    
    for text, url in matches:
        buttons.append(InlineKeyboardButton(text=text, url=url.replace("buttonurl://", "")))
        response = response.replace(f"[{text}]({url})", "")
    
    if buttons:
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i+2])
        return response.strip(), markup
    return response.strip(), None

@bot.message_handler(regexp=r'^[\/!](filter)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_addfilter(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.split(maxsplit=2)
        
        if len(args) < 3:
            safe_send_message(
                message.chat.id,
                "Usage: /filter &lt;trigger(s)&gt; &lt;response&gt",
                reply_to_message_id=message.message_id
            )
            return
        
        triggers_input = args[1].strip('"').lower()
        response = args[2]
        
        if not triggers_input or not response:
            safe_send_message(
                message.chat.id,
                "Triggers and response cannot be empty!",
                reply_to_message_id=message.message_id
            )
            return
        
        triggers = [t.strip() for t in triggers_input.split('"') if t.strip()] or [triggers_input]
        
        if chat_id not in filters_data:
            filters_data[chat_id] = {}
        
        for trigger in triggers:
            if trigger:
                filters_data[chat_id][trigger] = response
                logger.info(f"Added trigger: {trigger} for chat: {chat_id}")
        
        save_data(filters_data)
        escaped_triggers = [escape_html(t) for t in triggers]
        log_action(
            chat_id=message.chat.id,
            action="filter",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "add", "triggers": triggers}
        )
        safe_send_message(
            message.chat.id,
            f"Filter(s) added for trigger(s): <b>{', '.join(escaped_triggers)}</b>",
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Error in add_filter: {e}")
        safe_send_message(
            message.chat.id,
            "An error occurred while adding the filter.",
            reply_to_message_id=message.message_id
        )
        
@bot.message_handler(regexp=r'^[\/!](filters)(?:\s|$|@)')
@is_group
@disabled
def command_list_filters(message):
    try:
        chat_id = str(message.chat.id)
        if chat_id not in filters_data or not filters_data[chat_id]:
            safe_send_message(
                message.chat.id,
                "No filters set in this group.",
                reply_to_message_id=message.message_id
            )
            return
        
        response = "<b>Filters in this group:</b>\n"
        for i, trigger in enumerate(filters_data[chat_id], 1):
            response += f"{i}. {escape_html(trigger)}\n"
        
        safe_send_message(
            message.chat.id,
            response,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Error in list_filters: {e}")
        safe_send_message(
            message.chat.id,
            "An error occurred while listing filters.",
            reply_to_message_id=message.message_id
        )

@bot.message_handler(regexp=r'^[\/!](stop)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_stop_filter(message):
    try:
        chat_id = str(message.chat.id)
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            safe_send_message(
                message.chat.id,
                "Usage: /stop &lt;trigger&gt;",
                reply_to_message_id=message.message_id
            )
            return
        
        trigger = args[1].lower().strip('"')
        
        if chat_id not in filters_data or trigger not in filters_data[chat_id]:
            safe_send_message(
                message.chat.id,
                "No filters found!",
                reply_to_message_id=message.message_id
            )
            return
        
        del filters_data[chat_id][trigger]
        if not filters_data[chat_id]:
            del filters_data[chat_id]
        save_data(filters_data)
        log_action(
            chat_id=message.chat.id,
            action="stop_filter",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "remove", "trigger": trigger}
        )
        safe_send_message(
            message.chat.id,
            f"Filter <b>{escape_html(trigger)}</b> removed.",
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Error in stop_filter: {e}")
        safe_send_message(
            message.chat.id,
            "An error occurred while removing the filter.",
            reply_to_message_id=message.message_id
        )

@bot.message_handler(regexp=r'^[\/!](stopall)(?:\s|$|@)')
@is_group
@disabled
@is_admin
def command_stop_all_filters(message):
    try:
        chat_id = str(message.chat.id)
        
        if chat_id not in filters_data:
            safe_send_message(
                message.chat.id,
                "No filters to remove in this group.",
                reply_to_message_id=message.message_id
            )
            return
        
        del filters_data[chat_id]
        save_data(filters_data)
        log_action(
            chat_id=message.chat.id,
            action="stop_all_filters",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "remove_all"}
        )
        safe_send_message(
            message.chat.id,
            "All filters removed from this group.",
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Error in stop_all_filters: {e}")
        safe_send_message(
            message.chat.id,
            "An error occurred while removing all filters.",
            reply_to_message_id=message.message_id
        )


FORWARD_SETTINGS_FILE = "ban_forward/forwarded.json"
FORWARD_LOG_FILE = "ban_forward/forward.json"

file_lock = Lock()

default_forward_settings = {
    "ban_forward": False,
    "tban_forward": False,
    "ban_forward_action": "mute",
    "tban_duration": 86400
}

def load_forward_settings():
    """Load forward settings from forwarded.json."""
    try:
        with file_lock:
            if os.path.exists(FORWARD_SETTINGS_FILE):
                with open(FORWARD_SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            return {}
    except Exception as e:
        logger.error(f"Error loading forward settings: {e}")
        return {}

def save_forward_settings(settings):
    """Save forward settings to forwarded.json."""
    try:
        with file_lock:
            with open(FORWARD_SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving forward settings: {e}")

def load_forward_log():
    """Load forward log from forward.json."""
    try:
        with file_lock:
            if os.path.exists(FORWARD_LOG_FILE):
                with open(FORWARD_LOG_FILE, 'r') as f:
                    return json.load(f)
            return []
    except Exception as e:
        logger.error(f"Error loading forward log: {e}")
        return []

def save_forward_log(log_data):
    """Save forward log to forward.json."""
    try:
        with file_lock:
            with open(FORWARD_LOG_FILE, 'w') as f:
                json.dump(log_data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving forward log: {e}")

def apply_action(chat_id, user_id, action, duration=None):
    """Apply the specified action (ban, kick, mute, tban, tmute) to a user."""
    try:
        if action == "ban":
            bot.ban_chat_member(chat_id, user_id)
            return "banned"
        elif action == "kick":
            bot.ban_chat_member(chat_id, user_id)
            bot.unban_chat_member(chat_id, user_id)
            return "kicked"
        elif action == "mute":
            bot.restrict_chat_member(chat_id, user_id, permissions=telebot.types.ChatPermissions(can_send_messages=False))
            return "muted"
        elif action == "tban" and duration:
            until_date = int(time.time()) + duration
            bot.ban_chat_member(chat_id, user_id, until_date=until_date)
            return f"temporarily banned for {duration} seconds"
        elif action == "tmute" and duration:
            until_date = int(time.time()) + duration
            bot.restrict_chat_member(chat_id, user_id, permissions=telebot.types.ChatPermissions(can_send_messages=False), until_date=until_date)
            return f"temporarily muted for {duration} seconds"
        return None
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Error applying action: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error applying action: {e}")
        return None

@bot.message_handler(regexp=r'^[\/!](ban_forward)(?:\s|$|@)')
@is_group
@is_admin
def command_ban_forward(message):
    """Handle /ban_forward <on/off/True/False/yes/no> command."""
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        settings = load_forward_settings()
        status = settings.get(chat_id, default_forward_settings)['ban_forward']
        bot.reply_to(message, f"Forward ban is currently {'on' if status else 'off'}.")
        return

    value = args[1].lower()
    settings = load_forward_settings()
    
    if chat_id not in settings:
        settings[chat_id] = default_forward_settings.copy()
    
    if value in ['on', 'true', 'yes']:
        settings[chat_id]['ban_forward'] = True
        operation = "enable"
        bot.reply_to(message, "Forward ban enabled.")
    elif value in ['off', 'false', 'no']:
        settings[chat_id]['ban_forward'] = False
        operation = "disable"
        bot.reply_to(message, "Forward ban disabled.")
    else:
        bot.reply_to(message, "Invalid argument. Use on/off/True/False/yes/no.")
        return
    
    save_forward_settings(settings)
    log_action(
        chat_id=message.chat.id,
        action="ban_forward",
        executor=message.from_user,
        target=message.chat,
        details={"operation": operation}
    )

@bot.message_handler(regexp=r'^[\/!](tban_forward)(?:\s|$|@)')
@is_group
@is_admin
def command_tban_forward(message):
    """Handle /tban_forward <on/off/True/False/yes/no> command."""
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        settings = load_forward_settings()
        status = settings.get(chat_id, default_forward_settings)['tban_forward']
        bot.reply_to(message, f"Temporary forward ban is currently {'on' if status else 'off'}.")
        return

    value = args[1].lower()
    settings = load_forward_settings()
    
    if chat_id not in settings:
        settings[chat_id] = default_forward_settings.copy()
    
    if value in ['on', 'true', 'yes']:
        settings[chat_id]['tban_forward'] = True
        operation = "enable"
        bot.reply_to(message, "Temporary forward ban enabled.")
    elif value in ['off', 'false', 'no']:
        settings[chat_id]['tban_forward'] = False
        operation = "disable"
        bot.reply_to(message, "Temporary forward ban disabled.")
    else:
        bot.reply_to(message, "Invalid argument. Use on/off/True/False/yes/no.")
        return
    
    save_forward_settings(settings)
    log_action(
        chat_id=message.chat.id,
        action="tban_forward",
        executor=message.from_user,
        target=message.chat,
        details={"operation": operation}
    )

@bot.message_handler(regexp=r'^[\/!](ban_forward_action)(?:\s|$|@)')
@is_group
@is_admin
def command_ban_forward_action(message):
    """Handle /ban_forward_action <ban/kick/mute> command."""
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        settings = load_forward_settings()
        action = settings.get(chat_id, default_forward_settings)['ban_forward_action']
        bot.reply_to(message, f"Forward ban action is currently set to: {action}.")
        return

    action = args[1].lower()
    if action not in ['ban', 'kick', 'mute']:
        bot.reply_to(message, "Invalid action. Choose: ban, kick, mute.")
        return
    
    settings = load_forward_settings()
    if chat_id not in settings:
        settings[chat_id] = default_forward_settings.copy()
    
    settings[chat_id]['ban_forward_action'] = action
    save_forward_settings(settings)
    bot.reply_to(message, f"Forward ban action set to: {action}.")
    log_action(
        chat_id=message.chat.id,
        action="ban_forward_action",
        executor=message.from_user,
        target=message.chat,
        details={"action": action}
    )
    
FILTER_FILE = 'block.json'

def load_block():
    if os.path.exists(FILTER_FILE):
        with open(FILTER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_block(filter_data):
    with open(FILTER_FILE, 'w') as f:
        json.dump(filter_data, f, indent=4)

def initialize_chat_filter(chat_id):
    filter_data = load_block()
    chat_id_str = str(chat_id)
    if chat_id_str not in filter_data:
        filter_data[chat_id_str] = {
            'triggers': {},
            'mode': 'nothing',
            'delete_messages': True,
            'default_reason': 'Blocked content detected'
        }
        save_block(filter_data)
    return filter_data

def pattern_to_regex(pattern):
    pattern = re.escape(pattern)
    pattern = pattern.replace(r'\*\*', r'.*')
    pattern = pattern.replace(r'\*', r'[^\s]*')
    pattern = pattern.replace(r'\?', r'[^\s]')
    return f'^{pattern}$'

def check_filter(message):
    chat_id = str(message.chat.id)
    filter_data = load_block().get(chat_id, {})
    triggers = filter_data.get('triggers', {})
    text = message.text or message.caption or ''
    
    for trigger, reason in triggers.items():
        regex = pattern_to_regex(trigger)
        if re.match(regex, text, re.IGNORECASE):
            return True, reason or filter_data.get('default_reason', 'Blocked content detected'), filter_data.get('mode', 'nothing'), filter_data.get('delete_messages', True)
    return False, None, None, None

def handle_filter_action(chat_id, user_id, mode, message, reason):
    try:
        if mode == 'ban':
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"User banned for: {reason}")
        elif mode == 'mute':
            bot.restrict_chat_member(chat_id, user_id, permissions=telebot.types.ChatPermissions(can_send_messages=False))
            bot.reply_to(message, f"User muted for: {reason}")
        elif mode == 'kick':
            bot.ban_chat_member(chat_id, user_id)
            bot.unban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"User kicked for: {reason}")
        elif mode == 'warn':
            bot.reply_to(message, f"Warning: {reason}")
        elif mode == 'tban':
            until_date = datetime.now() + timedelta(hours=24)
            bot.ban_chat_member(chat_id, user_id, until_date=until_date)
            bot.reply_to(message, f"User temporarily banned for 24h: {reason}")
        elif mode == 'tmute':
            until_date = datetime.now() + timedelta(hours=24)
            bot.restrict_chat_member(chat_id, user_id, permissions=telebot.types.ChatPermissions(can_send_messages=False), until_date=until_date)
            bot.reply_to(message, f"User temporarily muted for 24h: {reason}")
    except Exception as e:
        bot.reply_to(message, f"Error performing action: {str(e)}")

@bot.message_handler(commands=['addblocklist'])
@is_admin
def add_filter(message):
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=2)[1:]
    if len(args) < 2:
        bot.reply_to(message, "Usage: /addblocklist <trigger> <reason>")
        return
    trigger, reason = args
    if trigger.startswith('"') and trigger.endswith('"'):
        trigger = trigger[1:-1]
    filter_data = initialize_chat_filter(chat_id)
    filter_data[chat_id]['triggers'][trigger] = reason
    save_block(filter_data)
    bot.reply_to(message, f"Added blocklist trigger: {trigger} with reason: {reason}")

@bot.message_handler(commands=['rmblocklist'])
@is_admin
def remove_filter(message):
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /rmblocklist <blocklist>")
        return
    trigger = args[1]
    filter_data = load_block()
    if chat_id in filter_data and trigger in filter_data[chat_id]['triggers']:
        del filter_data[chat_id]['triggers'][trigger]
        save_block(filter_data)
        bot.reply_to(message, f"Removed  blocklist: {trigger}")
    else:
        bot.reply_to(message, "blocklist not found.")

@bot.message_handler(commands=['unblocklistall'])
@is_admin
def unfilter_all(message):
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
    member = bot.get_chat_member(chat_id, user_id)
    if member.status != 'creator':
        bot.reply_to(message, "Only the chat creator can use this command.")
        return
    filter_data = load_block()
    if chat_id in filter_data:
        filter_data[chat_id]['triggers'] = {}
        save_block(filter_data)
        bot.reply_to(message, "All blocklist removed.")
    else:
        bot.reply_to(message, "No  blocklist found.")

@bot.message_handler(commands=['blocklist'])
@is_admin
def list_filter(message):
    chat_id = str(message.chat.id)
    filter_data = load_block().get(chat_id, {})
    triggers = filter_data.get('triggers', {})
    if not triggers:
        bot.reply_to(message, "No blocklist triggers set.")
        return
    response = "blocklist triggers:\n"
    for trigger, reason in triggers.items():
        response += f"- {trigger}: {reason}\n"
    response += f"Mode: {filter_data.get('mode', 'nothing')}\n"
    response += f"Delete messages: {filter_data.get('delete_messages', True)}\n"
    response += f"Default reason: {filter_data.get('default_reason', 'Blocked content detected')}"
    bot.reply_to(message, response)

@bot.message_handler(commands=['blocklistmode'])
@is_admin
def set_filter_mode(message):
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    valid_modes = ['nothing', 'ban', 'mute', 'kick', 'warn', 'tban', 'tmute']
    if len(args) < 2 or args[1] not in valid_modes:
        bot.reply_to(message, f"Usage: /blocklistmode <mode>\nAvailable modes: {', '.join(valid_modes)}")
        return
    mode = args[1]
    filter_data = initialize_chat_filter(chat_id)
    filter_data[chat_id]['mode'] = mode
    save_block(filter_data)
    bot.reply_to(message, f"blocklist mode set to: {mode}")

@bot.message_handler(commands=['blocklistdelete'])
@is_admin
def set_filter_delete(message):
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1].lower() not in ['yes', 'no', 'on', 'off']:
        bot.reply_to(message, "Usage: /blocklistdelete <yes/no/on/off>")
        return
    delete = args[1].lower() in ['yes', 'on']
    filter_data = initialize_chat_filter(chat_id)
    filter_data[chat_id]['delete_messages'] = delete
    save_block(filter_data)
    bot.reply_to(message, f"blocklist message deletion set to: {delete}")

@bot.message_handler(commands=['setblocklistreason'])
@is_admin
def set_filter_reason(message):
    chat_id = str(message.chat.id)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /setblocklistreason <reason>")
        return
    reason = args[1]
    filter_data = initialize_chat_filter(chat_id)
    filter_data[chat_id]['default_reason'] = reason
    save_block(filter_data)
    bot.reply_to(message, f"Default blocklist reason set to: {reason}")

@bot.message_handler(commands=['resetblocklistreason'])
@is_admin
def reset_filter_reason(message):
    chat_id = str(message.chat.id)
    filter_data = initialize_chat_filter(chat_id)
    filter_data[chat_id]['default_reason'] = 'Blocked content detected'
    save_block(filter_data)
    bot.reply_to(message, "Default blocklist reason reset to default.\n- Blocked content detected")

USER_DATA_FILE = "data/data.json"
file_lock = Lock()

if not os.path.exists("data"):
    os.makedirs("data")

def load_user_data():
    try:
        with file_lock:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, 'r') as f:
                    return json.load(f)
            return []
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return []

def save_user_data(data):
    try:
        with file_lock:
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
                   
@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def handle_messages(message):
    if message.chat.type not in ['group', 'supergroup']:
        return
        
    chat_id = str(message.chat.id)
    user_id = message.from_user.id

    user_data = load_user_data()
    user_info = {
        "user_id": user_id,
        "username": message.from_user.username or "",
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or ""
    }
    
    if not any(user["user_id"] == user_id for user in user_data):
        user_data.append(user_info)
        save_user_data(user_data)
        logger.info(f"Added user {user_id} to {USER_DATA_FILE}")
    else:
        logger.debug(f"User {user_id} already exists in {USER_DATA_FILE}")
        
        
    is_blocked, reason, mode, delete_messages = check_filter(message)
    if is_blocked:
        if delete_messages:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                bot.send_message(message.chat.id, f"Error deleting message: {str(e)}")
        if mode != 'nothing':
            handle_filter_action(message.chat.id, message.from_user.id, mode, message, reason)

        return
    is_admin_user = False
    try:
        member = bot.get_chat_member(chat_id, user_id)
        is_admin_user = member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return
        
    settings = load_forward_settings()
    chat_settings = settings.get(chat_id, default_forward_settings)
    if (chat_settings['ban_forward'] or chat_settings['tban_forward']) and \
       (message.forward_from or message.forward_from_chat or message.forward_sender_name):
        forward_info = {
            "message_id": message.message_id,
            "chat_id": chat_id,
            "original_user_id": user_id,
            "forwarded_user_id": None,
            "forwarded_chat_id": None,
            "forward_type": None,
            "forward_name": None,
            "action": None,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if message.forward_from:
            forward_info["forward_type"] = "user"
            forward_info["forwarded_user_id"] = message.forward_from.id
            forward_info["forward_name"] = message.forward_from.username or message.forward_from.first_name
        elif message.forward_from_chat:
            forward_info["forward_type"] = message.forward_from_chat.type
            forward_info["forwarded_chat_id"] = message.forward_from_chat.id
            forward_info["forward_name"] = message.forward_from_chat.title or message.forward_from_chat.username
        elif message.forward_sender_name:
            forward_info["forward_type"] = "anonymous"
            forward_info["forward_name"] = message.forward_sender_name

        action = chat_settings['ban_forward_action']
        action_taken = None
        try:
            if chat_settings['ban_forward']:
                action_taken = apply_action(chat_id, user_id, action)
            elif chat_settings['tban_forward']:
                if action == "ban":
                    action = "tban"
                elif action == "mute":
                    action = "tmute"
                action_taken = apply_action(chat_id, user_id, action, chat_settings['tban_duration'])

            if action_taken:
                forward_info["action"] = action_taken
                bot.delete_message(chat_id, message.message_id)
                username = message.from_user.username or message.from_user.first_name
                bot.send_message(chat_id, f"User {username} has been {action_taken} for forwarding messages.")

            forward_log = load_forward_log()
            forward_log.append(forward_info)
            save_forward_log(forward_log)

            log_action(
                chat_id=message.chat.id,
                action="forward_restriction",
                executor=None,
                target=message.from_user,
                details=forward_info
            )
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Error handling forwarded message: {e}")
            forward_info["action"] = f"error: {str(e)}"
            forward_log = load_forward_log()
            forward_log.append(forward_info)
            save_forward_log(forward_log)
        except Exception as e:
            logger.error(f"Unexpected error handling forwarded message: {e}")
    
    if chat_id in filters_data:
        if message.text:
            text = message.text.lower().strip()
            if len(text) > MAX_MESSAGE_LENGTH:
                logger.info(f"Ignoring long message: {text[:50]}...")
            else:
                for trigger, response in filters_data[chat_id].items():
                    logger.debug(f"Checking trigger '{trigger}' against text '{text}'")
                    if text == trigger or f" {trigger} " in f" {text} ":
                        logger.info(f"Trigger '{trigger}' matched for chat {chat_id}")
                        response_text, markup = parse_buttons(response)
                        safe_send_message(
                            message.chat.id,
                            response_text,
                            reply_to_message_id=message.message_id,
                            reply_markup=markup
                        )

    if message.text and message.text.startswith('/'):
        handle_custom_command(message)

        return

    if message.text:
        text = message.text.lower().strip()
        if 'kira' in text or 'mrskira' in text:
            first_name = escape_html(message.from_user.first_name or "User")
            user_link = f"tg://user?id={user_id}"
            response = f'<a href="{user_link}">{first_name}</a>, thanks mujhe yaad karne k liye\nbaas bolo kya karna hai 🔥'
            safe_send_message(
                message.chat.id,
                response,
                reply_to_message_id=message.message_id
            )
            
    chat_id = str(message.chat.id)
    user_id = message.from_user.id
   
    slowmode_data = load_slowmode()
    cooldown = slowmode_data.get(chat_id, 0)
    
    if cooldown > 0 and not is_user_admin(chat_id, user_id, message):
        current_time = time.time()
        last_time = last_message_times.get(chat_id, {}).get(user_id, 0)
        
        if current_time - last_time < cooldown:
            try:
                bot.delete_message(chat_id, message.message_id)
                return
            except Exception as e:
                logger.error(f"Slowmode delete error: {e}")
                return
        else:
            if chat_id not in last_message_times:
                last_message_times[chat_id] = {}
            last_message_times[chat_id][user_id] = current_time

    locks = init_chat_locks(chat_id)
    if not is_user_admin(message.chat.id, message.from_user.id, message):
        if locks[chat_id]["all"]:
            try:
                bot.delete_message(chat_id, message.message_id)
            except Exception:
                pass
            return
        
    chat_id = str(message.chat.id)
    
    locks = init_chat_locks(chat_id)
    if not is_user_admin(message.chat.id, message.from_user.id, message):
        if locks[chat_id]["all"]:
            try:
                bot.delete_message(chat_id, message.message_id)
            except Exception:
                pass
            return
        if locks[chat_id]["album"] and message.media_group_id:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["invitelink"] and message.entities and any(e.type == "text_link" and "t.me/joinchat/" in e.url for e in message.entities):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["anonchannel"] and message.sender_chat and message.sender_chat.type == "channel":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["audio"] and message.content_type == "audio":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["bot"] and message.from_user.is_bot:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["botlink"] and message.entities and any(e.type == "mention" and e.user and e.user.is_bot for e in message.entities):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["button"] and message.reply_markup and message.reply_markup.inline_keyboard:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["commands"] and message.text and message.text.startswith('/'):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["comment"] and message.is_topic_message:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["contact"] and message.content_type == "contact":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["document"] and message.content_type == "document":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["email"] and message.entities and any(e.type == "email" for e in message.entities):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["emoji"] and message.text and any(0x1F300 <= ord(c) <= 0x1F9FF for c in message.text):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["emojicustom"] and message.sticker and message.sticker.is_animated:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["emojigame"] and message.game:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["externalreply"] and message.reply_to_message and message.reply_to_message.forward_from:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["game"] and message.content_type == "game":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["gif"] and message.content_type == "animation":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["inline"] and message.via_bot:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["location"] and message.content_type == "location":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["phone"] and message.entities and any(e.type == "phone_number" for e in message.entities):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["photo"] and message.content_type == "photo":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["poll"] and message.content_type == "poll":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["spoiler"] and message.has_media_spoiler:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["text"] and message.content_type == "text" and not message.entities:
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["url"] and message.text and URL_PATTERN.search(message.text):
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["video"] and message.content_type == "video":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["videonote"] and message.content_type == "video_note":
            bot.delete_message(chat_id, message.message_id)
            return
        if locks[chat_id]["voice"] and message.content_type == "voice":
            bot.delete_message(chat_id, message.message_id)
            return

    settings = load_settings()
    if chat_id in settings:
        try:
            if message.sender_chat and message.sender_chat.type == 'channel' and settings[chat_id].get('cleanlinked', False):
                try:
                    bot.delete_message(chat_id, message.message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    if "not enough rights" in str(e).lower() or "can_delete_messages" in str(e).lower():
                        logger.warning(f"Cannot delete message due to insufficient rights: {e}")
                    elif "message to delete not found" in str(e).lower():
                        logger.warning(f"Message to delete not found: {e}")
                return

            if settings[chat_id].get('antichannelpin', False) and message.pinned_message and message.pinned_message.sender_chat and message.pinned_message.sender_chat.type == 'channel':
                try:
                    bot.unpin_chat_message(chat_id, message.pinned_message.message_id)
                except telebot.apihelper.ApiTelegramException as e:
                    if "not enough rights" in str(e).lower() or "can_pin_messages" in str(e).lower():
                        logger.warning(f"Cannot unpin message due to insufficient rights: {e}")
                    elif "message to unpin not found" in str(e).lower():
                        logger.warning(f"Message to unpin not found: {e}")
        except Exception as e:
            logger.error(f"Error in handle_messages (anti-channel): {e}")

    if not is_user_admin(message.chat.id, message.from_user.id, message):
        try:
            user_id = str(message.from_user.id)
            current_time = time.time()

            if chat_id not in blocklist["settings"]:
                blocklist["settings"][chat_id] = default_settings.copy()
                save_blocklist(blocklist)

            antiflood_settings = blocklist["settings"][chat_id]
            if antiflood_settings["flood_limit"] == 0 and antiflood_settings["timed_flood"]["count"] == 0:
                return

            if chat_id not in blocklist["users"]:
                blocklist["users"][chat_id] = {}
            if user_id not in blocklist["users"][chat_id]:
                blocklist["users"][chat_id][user_id] = {"count": 0, "last_message_time": 0, "message_times": []}

            user_data = blocklist["users"][chat_id][user_id]
            user_data["count"] += 1
            user_data["message_times"].append(current_time)
            user_data["last_message_time"] = current_time

            timed_flood = antiflood_settings["timed_flood"]
            if timed_flood["count"] > 0 and timed_flood["duration"] > 0:
                user_data["message_times"] = [t for t in user_data["message_times"] if current_time - t <= timed_flood["duration"]]

            action_taken = None
            duration = antiflood_settings.get("flood_mode_duration", 0)
            if antiflood_settings["flood_limit"] > 0 and user_data["count"] >= antiflood_settings["flood_limit"]:
                action_taken = apply_action(message.chat.id, message.from_user.id, antiflood_settings["flood_mode"], duration)
                user_data["count"] = 0
            elif timed_flood["count"] > 0 and len(user_data["message_times"]) >= timed_flood["count"]:
                action_taken = apply_action(message.chat.id, message.from_user.id, antiflood_settings["flood_mode"], duration)
                user_data["message_times"] = []

            if action_taken:
                username = message.from_user.username or message.from_user.first_name
                bot.send_message(message.chat.id, f"User {username} has been {action_taken} for flooding.")
                if antiflood_settings["clear_flood"]:
                    try:
                        bot.delete_message(message.chat.id, message.message_id)
                    except telebot.apihelper.ApiTelegramException:
                        pass
                save_blocklist(blocklist)
            elif user_data["count"] > 1 and user_data["last_message_time"] - user_data["message_times"][-2] > 10:
                user_data["count"] = 1
            save_blocklist(blocklist)
        except Exception as e:
            logger.error(f"Error in handle_messages (antiflood): {e}")
    chat_id = str(message.chat.id)
    
    settings = load_settings()
    chat_settings = settings.get(chat_id, {})
    clean_type = chat_settings.get('cleancommand')
    keep_type = chat_settings.get('keepcommand')
    
    if not clean_type or not message.text.startswith('/'):
        return
    
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = {admin.user.id for admin in admins}
        
        admin = message.from_user.id in admin_ids
        
        should_clean = (
            (clean_type == 'all') or
            (clean_type == 'admin' and is_admin) or
            (clean_type == 'user' and not is_admin)
        )
        
        should_keep = False
        if keep_type:
            should_keep = (
                (keep_type == 'all') or
                (keep_type == 'admin' and is_admin) or
                (keep_type == 'user' and not is_admin)
            )
        
        if should_clean and not should_keep:
            try:
                bot.delete_message(chat_id, message.message_id)
            except Exception:
                pass
    
    except Exception:
        pass

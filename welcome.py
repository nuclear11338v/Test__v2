from config import bot, logger
from utilities.utils import ALLOWED_TYPES, CLEANUP_DELAY, SETTINGS_FILE
from welcomesettings import get_group_settings, save_settings, settings
from telebot import types
from functools import wraps
import time
import logging
import re
import os
import json
from datetime import datetime, timedelta
from threading import Thread
from kick import disabled
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group


ADMIN_IDS = [6177259495, 987654321]
SUPPORT_CONTACT = "@KiraChatGroup"
BAN_FILE = "banned_groups.json"

def load_banned_groups():
    if os.path.exists(BAN_FILE):
        with open(BAN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_banned_groups(banned_groups):
    with open(BAN_FILE, "w") as f:
        json.dump(banned_groups, f, indent=4)

banned_groups = load_banned_groups()

def is_bot_admin(user_id):
    return user_id in ADMIN_IDS

def resolve_group_id(identifier):
    try:
        if identifier.startswith("@"):
            chat = bot.get_chat(identifier)
            return str(chat.id), chat.username
        return str(identifier), None
    except Exception as e:
        logger.error(f"Error resolving group ID {identifier}: {e}")
        return None, None

def check_banned_group(chat_id, message=None):
    chat_id_str = str(chat_id)
    if chat_id_str in banned_groups:
        reason = banned_groups[chat_id_str].get("reason", "No reason provided")
        leave_message = (
            f"Your group has been banned from this bot.\n"
            f"Contact support - {SUPPORT_CONTACT}\n"
            f"Reason - {reason}"
        )
        try:
            if message:
                bot.send_message(
                    chat_id,
                    leave_message,
                    disable_web_page_preview=True
                )
            bot.leave_chat(chat_id)
        except Exception as e:
            logger.error(f"Error leaving banned group {chat_id}: {e}")
        return True
    return False

def parse_buttons_and_text(text):
    if not text:
        return "Default message", None

    markup = types.InlineKeyboardMarkup()
    buttons = []
    message_lines = text.split('\n')
    message_text = []

    button_pattern = r'\[(.*?)\]\(buttonurl://(.*?)(?::same)?(?:\)|$|\s)'
    for line in message_lines:
        button_match = re.search(button_pattern, line)
        if button_match:
            button_text = button_match.group(1).strip()
            url = button_match.group(2).strip()
            same_line = ":same" in line
            if button_text and url and url.startswith('http'):
                buttons.append((types.InlineKeyboardButton(text=button_text, url=url), same_line))
            else:
                logging.warning(f"Invalid button syntax: {line}")
                message_text.append(line)
        else:
            message_text.append(line)

    final_message = '\n'.join(message_text).strip() or "Default message"
    if buttons:
        for i, (button, same) in enumerate(buttons):
            if same and i + 1 < len(buttons) and buttons[i + 1][1]:
                markup.row(button, buttons[i + 1][0])
                i += 1
            else:
                markup.add(button)

    return final_message, markup if buttons else None

def format_message(template, user, group):
    try:
        username = f"@{user.username}" if user.username else user.first_name
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        return template.format(
            first_name=user.first_name or "User",
            username=username,
            mention=mention,
            group=group or "Group",
            id=str(user.id)
        )
    except Exception as e:
        logging.error(f"Message formatting error: {str(e)}")
        return template

def send_media(chat_id, media, text=None, markup=None):
    try:
        if text and len(text) > 1024:
            text = text[:1024]
            logging.warning("Caption truncated to 1024 characters")

        if media and "type" in media and "file_id" in media:
            media_type = media["type"]
            if media_type == "photo":
                return bot.send_photo(chat_id, media["file_id"], caption=text, reply_markup=markup, parse_mode="Markdown")
            elif media_type == "video":
                return bot.send_video(chat_id, media["file_id"], caption=text, reply_markup=markup, parse_mode="Markdown")
            elif media_type == "audio":
                return bot.send_audio(chat_id, media["file_id"], caption=text, reply_markup=markup, parse_mode="Markdown")
            elif media_type == "document":
                return bot.send_document(chat_id, media["file_id"], caption=text, reply_markup=markup, parse_mode="Markdown")
            else:
                logging.error(f"Unknown media type: {media_type}")
        return bot.send_message(chat_id, text or "No message provided!", reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        error_msg = "Invalid Markdown syntax in text or caption. Ensure buttons ([text](buttonurl://url)) and Markdown (*bold*, _italic_) are correctly formatted." if "can't parse entities" in str(e).lower() else f"Error sending media: {str(e)}"
        logging.error(error_msg)
        return bot.send_message(chat_id, error_msg, parse_mode="Markdown")

def parse_time(duration_str):
    try:
        if duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith('d'):
            return int(duration_str[:-1]) * 86400
        return int(duration_str) * 3600
    except ValueError:
        return None

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_members(message):
    chat_id = str(message.chat.id)
    
    if check_banned_group(message.chat.id, message):
        logger.info(f"Bot left banned group {message.chat.id}")
        return

    current_time = time.time()

    join_times.setdefault(chat_id, []).append(current_time)

    banned_users = []
    group_settings = get_group_settings(message.chat.id)
    try:
        if group_settings.get('antiraid_enabled', False):
            for new_member in message.new_chat_members:
                if new_member.id != bot.get_me().id:
                    ban_duration = group_settings.get('raid_action_time', 3600)
                    until_date = datetime.utcnow() + timedelta(seconds=ban_duration)
                    try:
                        bot.ban_chat_member(chat_id=message.chat.id, user_id=new_member.id, until_date=until_date)
                        bot.send_message(chat_id, f"User {new_member.first_name} has been temporarily banned due to active AntiRaid.")
                        banned_users.append(new_member.id)
                    except Exception as e:
                        logging.error(f"Failed to ban user {new_member.id}: {str(e)}")
    except Exception as e:
        logging.error(f"AntiRaid error: {str(e)}")

    try:
        auto_threshold = group_settings.get('autoantiraid', 0)
        if auto_threshold > 0:
            recent_joins = len([t for t in join_times[chat_id] if current_time - t < 60])
            if recent_joins >= auto_threshold and not group_settings.get('antiraid_enabled', False):
                group_settings['antiraid_enabled'] = True
                group_settings['antiraid_end'] = current_time + group_settings.get('raid_time', 21600)
                save_settings(settings)
                bot.send_message(chat_id, f"AutoAntiRaid triggered! {recent_joins} users joined in the last minute. AntiRaid enabled for {group_settings['raid_time']//3600} hours.")
    except Exception as e:
        logging.error(f"AutoAntiRaid error: {str(e)}")

    if message.chat.type not in ALLOWED_TYPES or not group_settings["welcome"]:
        return

    for user in message.new_chat_members:
        if user.id in banned_users:
            continue
        try:
            msg_text, markup = parse_buttons_and_text(group_settings["welcome_msg"])
            formatted_text = format_message(msg_text, user, message.chat.title)

            if group_settings["clean_welcome"] and group_settings["last_welcome_id"]:
                try:
                    bot.delete_message(message.chat.id, group_settings["last_welcome_id"])
                except:
                    pass

            sent_msg = send_media(message.chat.id, group_settings["welcome_media"], formatted_text, markup)
            group_settings["last_welcome_id"] = sent_msg.message_id

            if group_settings["clean_welcome"]:
                time.sleep(CLEANUP_DELAY)
                try:
                    bot.delete_message(message.chat.id, sent_msg.message_id)
                    group_settings["last_welcome_id"] = None
                except:
                    pass

            save_settings(settings)
            logging.info(f"Welcome sent for user {user.id} in chat {message.chat.id}")
        except Exception as e:
            error_msg = f"Error in welcome message: {str(e)}"
            bot.reply_to(message, error_msg)
            logging.error(error_msg)

@bot.message_handler(content_types=['left_chat_member'])
def handle_left_members(message):
    if message.chat.type not in ALLOWED_TYPES or not get_group_settings(message.chat.id).get("goodbye", False):
        return

    try:
        group_settings = get_group_settings(message.chat.id)
        msg_text, markup = parse_buttons_and_text(group_settings["goodbye_msg"])
        formatted_text = format_message(msg_text, message.left_chat_member, message.chat.title)
        send_media(message.chat.id, group_settings["goodbye_media"], formatted_text, markup)
        logging.info(f"Goodbye sent for user {message.left_chat_member.id} in chat {message.chat.id}")
    except Exception as e:
        error_msg = f"Error in goodbye message: {str(e)}"
        bot.reply_to(message, error_msg)
        logging.error(error_msg)

@bot.message_handler(regexp=r'^[\/!](welcome)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_welcome(message):
    group_settings = get_group_settings(message.chat.id)
    try:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            param = args[1].lower()
            if param in ['yes', 'on']:
                group_settings["welcome"] = True
                bot.reply_to(message, "Welcome messages enabled!")
            elif param in ['no', 'off']:
                group_settings["welcome"] = False
                bot.reply_to(message, "Welcome messages disabled!")
            else:
                raise ValueError("Invalid parameter")
        else:
            status = "enabled" if group_settings["welcome"] else "disabled"
            preview, markup = parse_buttons_and_text(group_settings["welcome_msg"])
            preview_text = f"Current welcome message:\n{preview}"
            if group_settings["welcome_media"]:
                preview_text += f"\nWith attached media: {group_settings['welcome_media']['type']}"
            send_media(message.chat.id, group_settings["welcome_media"], preview_text, markup)
            bot.reply_to(message, f"Welcome messages are {status}")
        save_settings(settings)
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /welcome <yes/no/on/off> or /welcome to check current settings")
        logging.error(f"Welcome command error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](goodbye)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_goodbye(message):
    group_settings = get_group_settings(message.chat.id)
    try:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            param = args[1].lower()
            if param in ['yes', 'on']:
                group_settings["goodbye"] = True
                bot.reply_to(message, "Goodbye messages enabled!")
            elif param in ['no', 'off']:
                group_settings["goodbye"] = False
                bot.reply_to(message, "Goodbye messages disabled!")
            else:
                raise ValueError("Invalid parameter")
        else:
            status = "enabled" if group_settings["goodbye"] else "disabled"
            preview, markup = parse_buttons_and_text(group_settings["goodbye_msg"])
            preview_text = f"Current goodbye message:\n{preview}"
            if group_settings["goodbye_media"]:
                preview_text += f"\nWith attached media: {group_settings['goodbye_media']['type']}"
            send_media(message.chat.id, group_settings["goodbye_media"], preview_text, markup)
            bot.reply_to(message, f"Goodbye messages are {status}")
        save_settings(settings)
        logging.info(f"Goodbye setting changed in {message.chat.id}")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}\nUsage: /goodbye <yes/no/on/off> or /goodbye to check current settings")
        logging.error(f"Goodbye command error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](setwelcome)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_set_welcome_msg(message):
    group_settings = get_group_settings(message.chat.id)
    content = message.reply_to_message if message.reply_to_message else message
    try:
        msg_text = content.caption or (content.text.split(maxsplit=1)[1] if content.text.startswith('/setwelcome') and len(content.text.split()) > 1 else content.text)
        if not msg_text and not (content.photo or content.video or content.audio or content.document):
            bot.reply_to(message, "Please provide text/caption or reply to a message with text/media!")
            return

        formatted_text, markup = parse_buttons_and_text(msg_text or "")
        group_settings["welcome_msg"] = msg_text or "Hey {username} welcome to {group}. Please follow the group rules"

        media = None
        if content.photo:
            media = {"type": "photo", "file_id": content.photo[-1].file_id}
        elif content.video:
            media = {"type": "video", "file_id": content.video.file_id}
        elif content.audio:
            media = {"type": "audio", "file_id": content.audio.file_id}
        elif content.document:
            media = {"type": "document", "file_id": content.document.file_id}

        group_settings["welcome_media"] = media
        save_settings(settings)

        preview_text = f"Welcome set to:\n{formatted_text}"
        if media:
            preview_text += f"\nWith attached media: {media['type']}"
        send_media(message.chat.id, media, preview_text, markup)
        bot.reply_to(message, "Welcome message updated successfully!")
        logging.info(f"Welcome message updated in {message.chat.id}")
    except Exception as e:
        error_msg = "Invalid Markdown syntax in text or caption. Ensure buttons ([text](buttonurl://url)) and Markdown (*bold*, _italic_) are correctly formatted." if "can't parse entities" in str(e).lower() else f"Error setting welcome: {str(e)}"
        bot.reply_to(message, error_msg)
        logging.error(f"Setwelcome error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](resetwelcome)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_reset_welcome(message):
    group_settings = get_group_settings(message.chat.id)
    try:
        group_settings["welcome_msg"] = "Hey {username} welcome to {group}. Please follow the group rules"
        group_settings["welcome_media"] = None
        group_settings["last_welcome_id"] = None
        save_settings(settings)
        bot.reply_to(message, "Welcome message reset to default!")
        logging.info(f"Welcome reset in {message.chat.id}")
    except Exception as e:
        bot.reply_to(message, f"Error resetting welcome: {str(e)}")
        logging.error(f"Resetwelcome error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](setgoodbye)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_set_goodbye_msg(message):
    group_settings = get_group_settings(message.chat.id)
    content = message.reply_to_message if message.reply_to_message else message
    try:
        msg_text = content.caption or (content.text.split(maxsplit=1)[1] if content.text.startswith('/setgoodbye') and len(content.text.split()) > 1 else content.text)
        if not msg_text and not (content.photo or content.video or content.audio or content.document):
            bot.reply_to(message, "Please provide text/caption or reply to a message with text/media!")
            return

        formatted_text, markup = parse_buttons_and_text(msg_text or "")
        group_settings["goodbye_msg"] = msg_text or "Goodbye {username} we miss you"

        media = None
        if content.photo:
            media = {"type": "photo", "file_id": content.photo[-1].file_id}
        elif content.video:
            media = {"type": "video", "file_id": content.video.file_id}
        elif content.audio:
            media = {"type": "audio", "file_id": content.audio.file_id}
        elif content.document:
            media = {"type": "document", "file_id": content.document.file_id}

        group_settings["goodbye_media"] = media
        save_settings(settings)

        preview_text = f"Goodbye set to:\n{formatted_text}"
        if media:
            preview_text += f"\nWith attached media: {media['type']}"
        send_media(message.chat.id, media, preview_text, markup)
        bot.reply_to(message, "Goodbye message updated successfully!")
        logging.info(f"Goodbye message updated in {message.chat.id}")
    except Exception as e:
        error_msg = "Invalid Markdown syntax in text or caption. Ensure buttons ([text](buttonurl://url)) and Markdown (*bold*, _italic_) are correctly formatted." if "can't parse entities" in str(e).lower() else f"Error setting goodbye: {str(e)}"
        bot.reply_to(message, error_msg)
        logging.error(f"Setgoodbye error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](resetgoodbye)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_reset_goodbye(message):
    group_settings = get_group_settings(message.chat.id)
    try:
        group_settings["goodbye_msg"] = "Goodbye {username} we miss you"
        group_settings["goodbye_media"] = None
        save_settings(settings)
        bot.reply_to(message, "Goodbye message reset to default!")
        logging.info(f"Goodbye reset in {message.chat.id}")
    except Exception as e:
        bot.reply_to(message, f"Error resetting goodbye: {str(e)}")
        logging.error(f"Resetgoodbye error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](cleanwelcome)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_set_clean_welcome(message):
    group_settings = get_group_settings(message.chat.id)
    try:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            param = args[1].lower()
            if param in ['yes', 'on']:
                group_settings["clean_welcome"] = True
                bot.reply_to(message, "Welcome message cleanup enabled! Messages will be deleted after 5 minutes.")
            elif param in ['no', 'off']:
                group_settings["clean_welcome"] = False
                bot.reply_to(message, "Welcome message cleanup disabled!")
            else:
                raise ValueError("Invalid parameter")
        else:
            status = "enabled" if group_settings["clean_welcome"] else "disabled"
            bot.reply_to(message, f"Welcome message cleanup is {status}.\nUsage: /cleanwelcome <yes/no/on/off>")
        save_settings(settings)
        logging.info(f"Cleanwelcome set to {param} in {message.chat.id}")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")
        logging.error(f"Cleanwelcome error: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](antiraid)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_antiraid(message):
    chat_id = str(message.chat.id)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    group_settings = get_group_settings(chat_id)

    if not args:
        group_settings['antiraid_enabled'] = not group_settings.get('antiraid_enabled', False)
        if group_settings['antiraid_enabled']:
            raid_time = group_settings.get('raid_time', 21600)
            group_settings['antiraid_end'] = time.time() + raid_time
            bot.reply_to(message, f"AntiRaid enabled for {raid_time//3600} hours.")
        else:
            group_settings.pop('antiraid_end', None)
            bot.reply_to(message, "AntiRaid has been disabled.")
    elif args[0].lower() in ['off', 'no']:
        group_settings['antiraid_enabled'] = False
        group_settings.pop('antiraid_end', None)
        bot.reply_to(message, "AntiRaid has been disabled.")
    else:
        duration = parse_time(args[0])
        if duration is None:
            bot.reply_to(message, "Invalid time format. Use formats like '3h', '30m', or '1d'.")
            return
        group_settings['antiraid_enabled'] = True
        group_settings['antiraid_end'] = time.time() + duration
        bot.reply_to(message, f"AntiRaid enabled for {duration//3600} hours.")
    save_settings(settings)

@bot.message_handler(regexp=r'^[\/!](raidtime)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_raidtime(message):
    chat_id = str(message.chat.id)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    group_settings = get_group_settings(chat_id)

    if not args:
        raid_time = group_settings.get('raid_time', 21600)
        bot.reply_to(message, f"Current AntiRaid duration: {raid_time//3600} hours.")
    else:
        duration = parse_time(args[0])
        if duration is None:
            bot.reply_to(message, "Invalid time format. Use formats like '3h', '30m', or '1d'.")
            return
        group_settings['raid_time'] = duration
        save_settings(settings)
        bot.reply_to(message, f"AntiRaid duration set to {duration//3600} hours.")

@bot.message_handler(regexp=r'^[\/!](raidactiontime)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_raidaction(message):
    chat_id = str(message.chat.id)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    group_settings = get_group_settings(chat_id)

    if not args:
        action_time = group_settings.get('raid_action_time', 3600)
        bot.reply_to(message, f"Current AntiRaid ban duration: {action_time//3600} hours.")
    else:
        duration = parse_time(args[0])
        if duration is None:
            bot.reply_to(message, "Invalid time format. Use formats like '3h', '30m', or '1d'.")
            return
        group_settings['raid_action_time'] = duration
        save_settings(settings)
        bot.reply_to(message, f"AntiRaid ban duration set to {duration//3600} hours.")

@bot.message_handler(regexp=r'^[\/!](autoantiraid)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_autoantiraid(message):
    chat_id = str(message.chat.id)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    group_settings = get_group_settings(chat_id)

    if not args:
        threshold = group_settings.get('autoantiraid', 0)
        bot.reply_to(message, f"AutoAntiRaid {'is disabled' if threshold == 0 else f'triggers after {threshold} joins per minute'}.")
    elif args[0].lower() in ['off', 'no', '0']:
        group_settings['autoantiraid'] = 0
        save_settings(settings)
        bot.reply_to(message, "AutoAntiRaid has been disabled.")
    else:
        try:
            threshold = int(args[0])
            if threshold < 0:
                raise ValueError
            group_settings['autoantiraid'] = threshold
            save_settings(settings)
            bot.reply_to(message, f"AutoAntiRaid set to trigger after {threshold} joins per minute.")
        except ValueError:
            bot.reply_to(message, "Please provide a valid number or 'off'.")

@bot.message_handler(regexp=r'^[\/!](gban)(?:\s|$|@)')
def gban_command(message):
    if not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "Usage: /gban <group_id/username> <reason>")
            return

        identifier, reason = args[1], args[2]
        group_id, username = resolve_group_id(identifier)

        if not group_id:
            bot.reply_to(message, "Invalid group ID or username.")
            return

        if group_id in banned_groups:
            bot.reply_to(message, "This group is already banned.")
            return

        banned_groups[group_id] = {
            "username": username,
            "reason": reason,
            "banned_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_banned_groups(banned_groups)

        try:
            bot.send_message(
                group_id,
                f"Your group has been banned from this bot.\n"
                f"Contact support - {SUPPORT_CONTACT}\n"
                f"Reason - {reason}",
                disable_web_page_preview=True
            )
            bot.leave_chat(group_id)
        except Exception as e:
            logger.warning(f"Could not leave group {group_id}: {e}")

        bot.reply_to(message, f"Group {identifier} has been banned.")
        logger.info(f"Group {group_id} banned by {message.from_user.id}. Reason: {reason}")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please try again.")
        logger.error(f"Error in /gban: {e}")

@bot.message_handler(regexp=r'^[\/!](gunban)(?:\s|$|@)')
def gunban_command(message):
    if not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Usage: /gunban <group_id/username>")
            return

        identifier = args[1]
        group_id, _ = resolve_group_id(identifier)

        if not group_id:
            bot.reply_to(message, "Invalid group ID or username.")
            return

        if group_id not in banned_groups:
            bot.reply_to(message, "This group is not banned.")
            return

        del banned_groups[group_id]
        save_banned_groups(banned_groups)

        bot.reply_to(message, f"Group {identifier} has been unbanned.")
        logger.info(f"Group {group_id} unbanned by {message.from_user.id}")
    except Exception as e:
        bot.reply_to(message, "An error occurred. Please try again.")
        logger.error(f"Error in /gunban: {e}")

@bot.message_handler(regexp=r'^[\/!](gbanned)(?:\s|$|@)')
def gbanned_command(message):
    if not is_bot_admin(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    if not banned_groups:
        bot.reply_to(message, "No groups are currently banned.")
        return

    response = "Banned Groups:\n\n"
    for group_id, info in banned_groups.items():
        username = info.get("username", "N/A")
        reason = info.get("reason", "No reason provided")
        banned_at = info.get("banned_at", "Unknown")
        response += (
            f"ID: {group_id}\n"
            f"Username: {username}\n"
            f"Reason: {reason}\n"
            f"Banned At: {banned_at}\n\n"
        )

    bot.reply_to(message, response)
    logger.info(f"Banned groups list requested by {message.from_user.id}")

@bot.message_handler(regexp=r'^[\/!](support)(?:\s|$|@)')
def support_command(message):
    bot.reply_to(
        message,
        f"For support, please contact {SUPPORT_CONTACT}",
        disable_web_page_preview=True
    )

join_times = {}

def clean_join_times():
    while True:
        current_time = time.time()
        for chat_id in list(join_times.keys()):
            join_times[chat_id] = [t for t in join_times[chat_id] if current_time - t < 60]
            if not join_times[chat_id]:
                del join_times[chat_id]
        time.sleep(60)

def check_antiraid_expiry():
    while True:
        current_time = time.time()
        for chat_id in list(settings.keys()):
            if settings[chat_id].get('antiraid_enabled', False) and current_time >= settings[chat_id].get('antiraid_end', 0):
                settings[chat_id]['antiraid_enabled'] = False
                settings[chat_id].pop('antiraid_end', None)
                save_settings(settings)
                bot.send_message(chat_id, "AntiRaid has been automatically disabled as the duration has expired.")
        time.sleep(60)

join_times = {}

def clean_join_times():
    while True:
        current_time = time.time()
        for chat_id in list(join_times.keys()):
            join_times[chat_id] = [t for t in join_times[chat_id] if current_time - t < 60]
            if not join_times[chat_id]:
                del join_times[chat_id]
        time.sleep(60)

def check_antiraid_expiry():
    while True:
        current_time = time.time()
        for chat_id in list(settings.keys()):
            if settings[chat_id].get('antiraid_enabled', False) and current_time >= settings[chat_id].get('antiraid_end', 0):
                settings[chat_id]['antiraid_enabled'] = False
                settings[chat_id].pop('antiraid_end', None)
                save_settings(settings)
                bot.send_message(chat_id, "AntiRaid has been automatically disabled as the duration has expired.")
        time.sleep(60)

Thread(target=clean_join_times, daemon=True).start()
Thread(target=check_antiraid_expiry, daemon=True).start()
import telebot
import json
import os
import re
import time
from functools import wraps
from datetime import datetime, timedelta
from config import bot
from user_logs.user_logs import log_action
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


SETTINGS_FILE = "ban_sticker_pack/settings.json"
STICKERS_FILE = "ban_sticker_pack/stickers.json"
BANNED_FILE = "ban_sticker_pack/banned_stickers.json"
DETAILS_FILE = "ban_sticker_pack/sticker_details.json"
WARNINGS_FILE = "ban_sticker_pack/warnings.json"

os.makedirs("ban_sticker_pack", exist_ok=True)

def load_json(file):
    try:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({}, f)
        with open(file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON {file}: {e}")
        return {}

def save_json(file, data):
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving JSON {file}: {e}")

settings_data = load_json(SETTINGS_FILE)
stickers_data = load_json(STICKERS_FILE)
banned_data = load_json(BANNED_FILE)
details_data = load_json(DETAILS_FILE)
warnings_data = load_json(WARNINGS_FILE)

def create_sticker_pack_target(set_name):
    """Create a pseudo-target object for a sticker pack."""
    return type('StickerPack', (), {
        'id': set_name,
        'title': set_name,
        'first_name': None,
        'username': None
    })()

def extract_sticker_pack_name(input_str, reply_message=None):
    """
    Extracts sticker pack name from reply, name, or URL.
    Returns (pack_name, error_message) tuple.
    """
    if reply_message and reply_message.sticker and reply_message.sticker.set_name:
        return reply_message.sticker.set_name, None
    
    url_pattern = r'https?://t\.me/addstickers/([A-Za-z0-9_-]+)'
    url_match = re.match(url_pattern, input_str.strip())
    if url_match:
        return url_match.group(1), None
    
    pack_name = input_str.strip()
    if pack_name and re.match(r'^[A-Za-z0-9_-]+$', pack_name):
        return pack_name, None
    
    return None, "Invalid input. Provide a sticker reply, pack name, or URL (e.g., https://t.me/addstickers/PackName)."

def is_user_admin(chat_id, user_id, message=None):
    """Check if user is admin or anonymous admin"""
    try:
        if message and message.sender_chat and message.sender_chat.id == chat_id:
            return True
        
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False    

def is_group(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.chat.type in ['group', 'supergroup']:
            return func(message, *args, **kwargs)
        else:
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            
            help_button = InlineKeyboardButton(
                text="Help",
                url="https://t.me/MrsKiraBot?start=help"
            )
            add_to_group_button = InlineKeyboardButton(
                text="Add me to group",
                url="https://t.me/MrsKiraBot?startgroup=true&admin=change_info+post_messages+edit_messages+delete_messages+invite_users+restrict_members+pin_messages+promote_members+manage_chat"
            )
            
            markup.add(help_button, add_to_group_button)
            
            command = message.text.split()[0][1:] if message.text.startswith('/') else message.text
            
            bot.reply_to(
                message,
                f"<b>Command</b>\n<code>- {command}</code>\n<i>This command can only be used in groups</i>",
                parse_mode="HTML",
                reply_markup=markup
            )
        return
    return wrapper

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

def is_owner(func):
    @wraps(func)
    def wrapper(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        try:
            if message.sender_chat and message.sender_chat.id == chat_id:
                return func(message)
                
            admins = bot.get_chat_administrators(chat_id)
            owner = next((admin for admin in admins if admin.status == 'creator'), None)
            if not owner or owner.user.id != user_id:
                bot.reply_to(message, "Only the group owner can use this command.")
                return
            return func(message)
        except Exception as e:
            bot.reply_to(message, "Error checking owner status.")
            print(f"Owner check error: {e}")
            return
    return wrapper

def is_allowed(func):
    @wraps(func)
    def wrapper(message):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        try:
            
            if message.sender_chat and message.sender_chat.id == message.chat.id:
                return func(message)
                
            admins = bot.get_chat_administrators(message.chat.id)
            owner = next((admin for admin in admins if admin.status == 'creator'), None)
            is_admin = any(admin.user.id == user_id for admin in admins)
            
            if not is_admin:
                bot.reply_to(message, "You need to be an admin to do this.")
                return
            
            if owner and owner.user.id == user_id:
                return func(message)
            
            if settings_data.get(chat_id, {}).get('allow_admins', False):
                return func(message)
            
            bot.reply_to(message, "Admins are not allowed to use this command.\n\nAsk owner to enable with: */allowadmins on* ( owner only )")
            return
        except Exception as e:
            bot.reply_to(message, "Error checking permissions.")
            print(f"Permission check error: {e}")
            return
    return wrapper


def init_group_settings(chat_id):
    chat_id = str(chat_id)
    if chat_id not in settings_data:
        settings_data[chat_id] = {
            'ban_mode': 'delete',
            'warn_enabled': False,
            'warn_limit': 3,
            'warn_mode': 'ban',
            'allow_admins': False,
            'ban_target': 'all',
            'ban_animated_stickers': False,
            'ban_all_stickers': False
        }
        save_json(SETTINGS_FILE, settings_data)
        
def is_user_affected(message, chat_id):
    ban_target = settings_data[chat_id].get('ban_target', 'all')
    user_id = message.from_user.id
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        is_admin = any(admin.user.id == user_id for admin in admins)
        
        if is_admin:
            return False
        
        if ban_target == 'all':
            return True
        elif ban_target == 'user':
            return not is_admin
        elif ban_target == 'admin':
            return False
        return False
    except Exception as e:
        print(f"Error checking user status: {e}")
        return True

def perform_action(message, action):
    """Perform the specified action (mute, ban, kick) on the user."""
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        if action == 'mute':
            bot.restrict_chat_member(chat_id, user_id, until_date=int(time.time()) + 3600)
            bot.send_message(chat_id, f"User {message.from_user.first_name} has been muted for 1 hour.")
        elif action == 'ban':
            bot.ban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"User {message.from_user.first_name} has been banned.")
        elif action == 'kick':
            bot.ban_chat_member(chat_id, user_id)
            bot.unban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"User {message.from_user.first_name} has been kicked.")
    except Exception as e:
        print(f"Error performing action {action}: {e}")

@bot.message_handler(content_types=["sticker"])
@is_group
def handle_sticker(message):
    try:
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        
        sticker = message.sticker
        set_name = sticker.set_name or "Unknown"
        
        stickers_data[set_name] = {
            "file_id": sticker.file_id,
            "emoji": sticker.emoji,
            "is_animated": sticker.is_animated,
            "is_video": sticker.is_video,
            "is_premium": getattr(sticker, 'is_premium', False)
        }
        save_json(STICKERS_FILE, stickers_data)

        user = message.from_user
        details_data[str(message.message_id)] = {
            "set_name": set_name,
            "user_id": user.id,
            "username": f"@{user.username}" if user.username else "NoUsername",
            "first_name": user.first_name,
            "last_name": user.last_name or "",
            "chat_id": chat_id,
            "banned": set_name in banned_data,
            "is_animated": sticker.is_animated,
            "is_premium": getattr(sticker, 'is_premium', False),
            "timestamp": datetime.now().isoformat(),
            "pack_url": f"https://t.me/addstickers/{set_name}" if set_name != "Unknown" else "N/A"
        }
        save_json(DETAILS_FILE, details_data)
        
        is_all_banned = settings_data[chat_id].get('ban_all_stickers', False)
        is_animated_banned = settings_data[chat_id].get('ban_animated_stickers', False) and sticker.is_animated
        is_premium = getattr(sticker, 'is_premium', False)
        
        if is_all_banned or set_name in banned_data or is_animated_banned:
            try:
                bot.delete_message(message.chat.id, message.message_id)
                
                if is_user_affected(message, chat_id):
                    if is_all_banned:
                        reason = "all stickers banned"
                    elif is_animated_banned:
                        reason = "animated sticker"
                    else:
                        reason = "banned sticker pack"
                    if is_premium:
                        reason += " (premium)"
                    
                    if settings_data[chat_id]['warn_enabled']:
                        handle_warning(message, set_name, reason)
                    elif settings_data[chat_id]['ban_mode'] != 'delete':
                        action = settings_data[chat_id]['ban_mode']
                        perform_action(message, action)
                        log_action(
                            chat_id=message.chat.id,
                            action=f"sticker_{action}",
                            executor=bot.get_me(),
                            target=message.from_user,
                            details={
                                "sticker_pack": set_name,
                                "action": action,
                                "reason": reason,
                                "is_animated": sticker.is_animated,
                                "is_premium": is_premium,
                                "pack_url": f"https://t.me/addstickers/{set_name}" if set_name != "Unknown" else "N/A"
                            }
                        )
            except Exception as e:
                print(f"Failed to handle banned sticker: {e}")
    except Exception as e:
        bot.reply_to(message, "An error occurred while processing the sticker.")
        print(f"Sticker handler error: {e}")

def handle_warning(message, set_name, reason="banned sticker pack"):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        if any(admin.user.id == message.from_user.id for admin in admins):
            return
    except Exception as e:
        print(f"Error checking admin status in warning: {e}")
        return
    
    if chat_id not in warnings_data:
        warnings_data[chat_id] = {}
    if user_id not in warnings_data[chat_id]:
        warnings_data[chat_id][user_id] = 0
    
    warnings_data[chat_id][user_id] += 1
    warn_count = warnings_data[chat_id][user_id]
    warn_limit = settings_data[chat_id]['warn_limit']
    
    save_json(WARNINGS_FILE, warnings_data)
    
    bot.send_message(message.chat.id, f"{username}: Warning {warn_count}/{warn_limit}\nReason: {reason} '{set_name}'.")
    
    log_action(
        chat_id=message.chat.id,
        action="sticker_warning",
        executor=bot.get_me(),
        target=message.from_user,
        details={
            "sticker_pack": set_name,
            "warn_count": warn_count,
            "warn_limit": warn_limit,
            "reason": reason,
            "pack_url": f"https://t.me/addstickers/{set_name}" if set_name != "Unknown" else "N/A"
        }
    )
    
    if warn_count >= warn_limit:
        action = settings_data[chat_id]['warn_mode']
        perform_action( message, action)
        warnings_data[chat_id][set_name] = 0
        save_json(WARNINGS_FILE, warnings_data)
        log_action(
            chat_id=message.chat.id,
        action=f"sticker_{action}",
        executor=bot.get_me(),
        target=message.from_user,
        details={
            "sticker_pack": set_name,
            "action": action,
            "reason": f"Reached warning limit ({reason})",
            "pack_url": f"https://t.me/addstickers/{set_name}" if set_name != "Unknown" else "N/A"
        }
    )

@bot.message_handler(regexp=r'^[\/!](cleansticker)(?:\s|$|@)')
@is_group
@is_owner
def clean_sticker_settings(message):
    try:
        chat_id = str(message.chat.id)
        
        settings_data[chat_id] = {
            'ban_mode': 'delete',
            'warn_enabled': False,
            'warn_limit': 3,
            'warn_mode': 'ban',
            'allow_admins': False,
            'ban_target': 'all',
            'ban_animated_stickers': False,
            'ban_all_stickers': False
        }
        save_json(SETTINGS_FILE, settings_data)
        
        banned_data.clear()
        save_json(BANNED_FILE, banned_data)
        
        if chat_id in warnings_data:
            del warnings_data[chat_id]
            save_json(WARNINGS_FILE, warnings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="cleansticker",
            executor=message.from_user,
            target=message.chat,
            details={
                "reason": "Reset all sticker settings and bans"
            }
        )
        
        bot.reply_to(message, "All sticker settings have been reset to default, banned sticker packs cleared, and user warnings reset.\ntry */helpsticker*.")
    except Exception as e:
        bot.reply_to(message, "Error resetting sticker settings.")
        print(f"Clean sticker error: {e}")
    
@bot.message_handler(regexp=r'^[\/!](abansticker)(?:\s|$|@)')
@is_group
@is_allowed
def ban_all_stickers(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /abansticker <on/off> [reason]\ntry */helpsticker*.")

        state = args[1].lower() in ['on', 'true', 'yes']
        reason = args[2] if len(args) > 2 else "ㅤ"
        
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        settings_data[chat_id]['ban_all_stickers'] = state
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_abansticker",
            executor=message.from_user,
            target=message.chat,
            details={
                "state": "enabled" if state else "disabled",
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"All stickers ban {'enabled' if state else 'disabled'}\nReason: {reason}\ntry */helpsticker*.")
    except Exception as e:
        bot.reply_to(message, "Error setting all stickers ban.")
        print(f"Set all stickers ban error: {e}")
        
@bot.message_handler(regexp=r'^[\/!](bansticker)(?:\s|$|@)')
@is_group
@is_allowed
def ban_sticker(message):
    try:
        args = message.text.split(maxsplit=2)
        has_reply = message.reply_to_message is not None
        input_str = args[1] if len(args) > 1 else ""
        reason = args[2] if len(args) > 2 else ("ㅤ" if has_reply or input_str else input_str)
        
        set_name, error = extract_sticker_pack_name(input_str, message.reply_to_message)
        if error:
            return bot.reply_to(message, error)
        
        if not set_name:
            return bot.reply_to(message, "No sticker pack specified.\nReply to a sticker, provide a pack name, or URL\ntry */helpsticker*.")

        if set_name in banned_data:
            return bot.reply_to(message, f"Sticker pack '{set_name}' is already banned.")

        is_premium = False
        is_animated = False
        if message.reply_to_message and message.reply_to_message.sticker:
            is_premium = getattr(message.reply_to_message.sticker, 'is_premium', False)
            is_animated = message.reply_to_message.sticker.is_animated

        banned_data[set_name] = {
            "banned_by": message.from_user.id,
            "username": f"@{message.from_user.username}" if message.from_user.username else "NoUsername",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "is_premium": is_premium,
            "is_animated": is_animated
        }
        save_json(BANNED_FILE, banned_data)
        
        log_action(
            chat_id=message.chat.id,
            action="bansticker",
            executor=message.from_user,
            target=create_sticker_pack_target(set_name),
            details={
                "reason": reason,
                "is_premium": is_premium,
                "is_animated": is_animated,
                "pack_url": f"https://t.me/addstickers/{set_name}"
            }
        )
        
        sticker_type = "Premium" if is_premium else "Animated" if is_animated else "Regular"
        bot.reply_to(message, f"Banned sticker pack: {set_name} ({sticker_type})\nReason: {reason}\nLink: https://t.me/addstickers/{set_name}.")
    except Exception as e:
        bot.reply_to(message, "Error banning sticker pack.")
        print(f"Ban sticker error: {e}")

@bot.message_handler(regexp=r'^[\/!](tbansticker)(?:\s|$|@)')
@is_group
@is_allowed
def temp_ban_sticker(message):
    try:
        args = message.text.split(maxsplit=3)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /tbansticker <sticker_pack_name/URL/reply> [duration] [reason]\nExample: /tbansticker PackName 1h Spamming\ntry */helpsticker*.")

        input_str = args[1]
        duration = args[2] if len(args) > 2 else None
        reason = args[3] if len(args) > 3 else "ㅤ"
        
        set_name, error = extract_sticker_pack_name(input_str, message.reply_to_message)
        if error:
            return bot.reply_to(message, error)
        
        if not set_name:
            return bot.reply_to(message, "No sticker pack specified. Reply to a sticker, provide a pack name, or URL\ntry */helpsticker*..")
        
        if not duration:
            return bot.reply_to(message, "Duration is required. Use format: 1m/1h/1d.\n\nargs - [sticker] [duration] ( optional [reason] )\ntry */helpsticker*.")

        time_units = {'m': 60, 'h': 3600, 'd': 86400}
        if not (duration[-1] in time_units and duration[:-1].isdigit()):
            return bot.reply_to(message, "Invalid duration format. Use 1m/1h/1d.\ntry */helpsticker*.")

        seconds = int(duration[:-1]) * time_units[duration[-1]]
        expiry = datetime.now() + timedelta(seconds=seconds)

        if set_name in banned_data:
            return bot.reply_to(message, f"Sticker pack '{set_name}' is already banned.\ntry */helpsticker*.")

        is_premium = False
        is_animated = False
        if message.reply_to_message and message.reply_to_message.sticker:
            is_premium = getattr(message.reply_to_message.sticker, 'is_premium', False)
            is_animated = message.reply_to_message.sticker.is_animated

        banned_data[set_name] = {
            "banned_by": message.from_user.id,
            "username": f"@{message.from_user.username}" if message.from_user.username else "NoUsername",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "expiry": expiry.isoformat(),
            "is_premium": is_premium,
            "is_animated": is_animated
        }
        save_json(BANNED_FILE, banned_data)
        
        log_action(
            chat_id=message.chat.id,
            action="tbansticker",
            executor=message.from_user,
            target=create_sticker_pack_target(set_name),
            details={
                "reason": reason,
                "duration": duration,
                "expiry": expiry.isoformat(),
                "is_premium": is_premium,
                "is_animated": is_animated,
                "pack_url": f"https://t.me/addstickers/{set_name}"
            }
        )
        
        sticker_type = "Premium" if is_premium else "Animated" if is_animated else "Regular"
        bot.reply_to(message, f"Temporarily banned sticker pack: {set_name} ({sticker_type})\nDuration: {duration}\nReason: {reason}\nLink: https://t.me/addstickers/{set_name}")
    except Exception as e:
        bot.reply_to(message, "Error setting temporary ban.")
        print(f"Temp ban error: {e}")

@bot.message_handler(regexp=r'^[\/!](unbansticker)(?:\s|$|@)')
@is_group
@is_allowed
def unban_sticker(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /unbansticker <sticker_pack_name/URL> ( optional [reason] )\ntry */helpsticker*.")

        input_str = args[1]
        reason = args[2] if len(args) > 2 else "ㅤ"
        
        set_name, error = extract_sticker_pack_name(input_str)
        if error:
            return bot.reply_to(message, error)
        
        if not set_name:
            return bot.reply_to(message, "No sticker pack specified. Provide a pack name or URL.\ntry */helpsticker*.")

        if set_name in banned_data:
            is_premium = banned_data[set_name].get('is_premium', False)
            is_animated = banned_data[set_name].get('is_animated', False)
            del banned_data[set_name]
            save_json(BANNED_FILE, banned_data)
            
            log_action(
                chat_id=message.chat.id,
                action="unbansticker",
                executor=message.from_user,
                target=create_sticker_pack_target(set_name),
                details={
                    "reason": reason,
                    "is_premium": is_premium,
                    "is_animated": is_animated,
                    "pack_url": f"https://t.me/addstickers/{set_name}"
                }
            )
            
            sticker_type = "Premium" if is_premium else "Animated" if is_animated else "Regular"
            bot.reply_to(message, f"Unbanned sticker pack: {set_name} ({sticker_type})\nReason: {reason}")
        else:
            bot.reply_to(message, f"Sticker pack '{set_name}' is not in the banned list.")
    except Exception as e:
        bot.reply_to(message, "Error unbanning sticker pack.\ntry */helpsticker*.")
        print(f"Unban sticker error: {e}")

@bot.message_handler(regexp=r'^[\/!](ban_asticker)(?:\s|$|@)')
@is_group
@is_allowed
def ban_animated_sticker(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /ban_asticker <on/off> [reason]\ntry */helpsticker*.")

        state = args[1].lower() in ['on', 'true', 'yes']
        reason = args[2] if len(args) > 2 else "ㅤ"
        
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        settings_data[chat_id]['ban_animated_stickers'] = state
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_ban_asticker",
            executor=message.from_user,
            target=message.chat,
            details={
                "state": "enabled" if state else "disabled",
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"Animated sticker ban {'enabled' if state else 'disabled'}\nReason: {reason}")
    except Exception as e:
        bot.reply_to(message, "Error setting animated sticker ban.")
        print(f"Set animated sticker ban error: {e}")

@bot.message_handler(regexp=r'^[\/!](banstickermode)(?:\s|$|@)')
@is_group
@is_allowed
def set_ban_mode(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /banstickermode <mute/ban/kick/delete> [reason]\ntry */helpsticker*.")

        mode = args[1].lower()
        reason = args[2] if len(args) > 2 else "No reason provided"
        
        if mode not in ['mute', 'ban', 'kick', 'delete']:
            return bot.reply_to(message, "Invalid mode. Use mute/ban/kick/delete.")

        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        settings_data[chat_id]['ban_mode'] = mode
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_banstickermode",
            executor=message.from_user,
            target=message.chat,
            details={
                "mode": mode,
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"Sticker ban mode set to: {mode}\nReason: {reason}")
    except Exception as e:
        bot.reply_to(message, "Error setting ban mode.")
        print(f"Set ban mode error: {e}")

@bot.message_handler(regexp=r'^[\/!](wbansticker)(?:\s|$|@)')
@is_group
@is_allowed
def set_warn_mode(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /wbansticker <on/off> [reason]\ntry */helpsticker*.")

        state = args[1].lower() in ['on', 'true', 'yes']
        reason = args[2] if len(args) > 2 else "ㅤ"
        
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        settings_data[chat_id]['warn_enabled'] = state
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_wbansticker",
            executor=message.from_user,
            target=message.chat,
            details={
                "state": "enabled" if state else "disabled",
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"Sticker warning system {'enabled' if state else 'disabled'}\nReason: {reason}")
    except Exception as e:
        bot.reply_to(message, "Error setting warning mode.")
        print(f"Set warn mode error: {e}")

@bot.message_handler(regexp=r'^[\/!](wbanstickerlimit)(?:\s|$|@)')
@is_group
@is_allowed
def set_warn_limit(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /wbanstickerlimit <number/default> [reason]\ntry */helpsticker*.")

        limit = args[1].lower()
        reason = args[2] if len(args) > 2 else "No reason provided"
        
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        
        if limit == 'default':
            limit = 3
        elif limit.isdigit():
            limit = int(limit)
            if limit < 1 or limit > 100:
                return bot.reply_to(message, "Limit must be between 1 and 100.")
        else:
            return bot.reply_to(message, "Invalid limit. Use a number or 'default'.")

        settings_data[chat_id]['warn_limit'] = limit
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_wbanstickerlimit",
            executor=message.from_user,
            target=message.chat,
            details={
                "limit": limit,
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"Warning limit set to: {limit}\nReason: {reason}")
    except Exception as e:
        bot.reply_to(message, "Error setting warning limit.")
        print(f"Set warn limit error: {e}")

@bot.message_handler(regexp=r'^[\/!](wbanstickermode)(?:\s|$|@)')
@is_group
@is_allowed
def set_warn_action(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /wbanstickermode <ban/kick/mute> [reason]\ntry */helpsticker*.")

        mode = args[1].lower()
        reason = args[2] if len(args) > 2 else "No reason provided"
        
        if mode not in ['ban', 'kick', 'mute']:
            return bot.reply_to(message, "Invalid mode. Use ban/kick/mute.")

        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        settings_data[chat_id]['warn_mode'] = mode
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_wbanstickermode",
            executor=message.from_user,
            target=message.chat,
            details={
                "mode": mode,
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"Warning action set to: {mode}\nReason: {reason}")
    except Exception as e:
        bot.reply_to(message, "Error setting warning action.")
        print(f"Set warn action error: {e}")
        
@bot.message_handler(regexp=r'^[\/!](allowadmins)(?:\s|$|@)')
@is_group
@is_owner
def set_allow_admins(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            return bot.reply_to(message, "Usage: /allowadmins <on/off> [reason]\ntry */helpsticker*.")

        state = args[1].lower() in ['on', 'true', 'yes']
        reason = args[2] if len(args) > 2 else "ㅤ"
        
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        settings_data[chat_id]['allow_admins'] = state
        save_json(SETTINGS_FILE, settings_data)
        
        log_action(
            chat_id=message.chat.id,
            action="set_allowadmins",
            executor=message.from_user,
            target=message.chat,
            details={
                "state": "enabled" if state else "disabled",
                "reason": reason
            }
        )
        
        bot.reply_to(message, f"Admin permissions {'enabled' if state else 'disabled'}\nReason: {reason}")
    except Exception as e:
        bot.reply_to(message, "Error setting admin permissions.")
        print(f"Set allow admins error: {e}")

@bot.message_handler(regexp=r'^[\/!](banstickerstatus)(?:\s|$|@)')
@is_group
@is_allowed
def ban_sticker_status(message):
    try:
        chat_id = str(message.chat.id)
        init_group_settings(chat_id)
        
        settings = settings_data.get(chat_id, {})
        ban_mode = settings.get('ban_mode', 'delete')
        warn_enabled = settings.get('warn_enabled', False)
        warn_limit = settings.get('warn_limit', 3)
        warn_mode = settings.get('warn_mode', 'ban')
        allow_admins = settings.get('allow_admins', False)
        ban_target = settings.get('ban_target', 'all')
        
        banned_packs = []
        for set_name, data in banned_data.items():
            reason = data.get('reason', 'ㅤ')
            expiry = data.get('expiry', None)
            status = f"{set_name} (Reason: {reason})"
            if expiry:
                expiry_date = datetime.fromisoformat(expiry).strftime("%Y-%m-%d %H:%M:%S")
                status += f" [Expires: {expiry_date}]"
            banned_packs.append(status)
        
        banned_list = "\n- ".join(banned_packs) if banned_packs else "None"
        target_text = {"all": "All users", "user": "Non-admin users", "admin": "Admins"}[ban_target]
        response = (
            f"📊 *Sticker Ban Status for {message.chat.title}*\n\n"
            f"🛠 *Ban Mode*: {ban_mode.capitalize()}\n"
            f"⚠️ *Warnings Enabled*: {'Yes' if warn_enabled else 'No'}\n"
            f"🔢 *Warning Limit*: {warn_limit}\n"
            f"🚨 *Warning Action*: {warn_mode.capitalize()}\n"
            f"👮 *Admins Allowed*: {'Yes' if allow_admins else 'No'}\n"
            f"🎯 *Ban Target*: {target_text}\n"
            f"\n📌 *Banned Sticker Packs*:\n- {banned_list}"
        )
        
        bot.reply_to(message, response, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "Error retrieving ban status.")
        print(f"Ban sticker status error: {e}")
        

@bot.message_handler(regexp=r'^[\/!](helpsticker)(?:\s|$|@)')
@is_group
def help_sticker(message):
    help_text = (
        "📖 *Sticker Management Help*\n\n"
        "This commands helps group admins manage sticker packs by banning, unbanning, and setting rules for their use.\n\n"
        "🔧 *General Commands*\n"
        "1. */bansticker <pack_name/URL/reply> [reason]*\n"
        "   - Bans a sticker pack permanently.\n"
        "   - *How to specify pack:*\n"
        "     - Reply to a sticker to ban its pack.\n"
        "     - Provide the pack name (e.g., `PackName`).\n"
        "     - Use a URL (e.g., `https://t.me/addstickers/PackName`).\n"
        "   - *Example:* `/bansticker PackName Spamming`\n"
        "   - *Note:* Reason is optional.\n\n"
        "2. */tbansticker <pack_name/URL/reply> <duration> [reason]*\n"
        "   - Temporarily bans a sticker pack.\n"
        "   - *Duration format:* `1m` (minutes), `1h` (hours), `1d` (days).\n"
        "   - *Example:* `/tbansticker PackName 1h Spamming`\n"
        "   - *Note:* Duration is required; reason is optional.\n\n"
        "3. */unbansticker <pack_name/URL> [reason]*\n"
        "   - Unbans a sticker pack.\n"
        "   - *Example:* `/unbansticker PackName No longer needed`\n"
        "   - *Note:* Reason is optional.\n\n"
        "⚙️ *Settings Commands*\n"
        "4. */banstickermode <mute/ban/kick/delete> [reason]*\n"
        "   - Sets the action for banned sticker use.\n"
        "   - *Options:* `mute`, `ban`, `kick`, `delete` (default).\n"
        "   - *Example:* `/banstickermode ban Inappropriate content`\n"
        "   - *Note:* Reason is optional.\n\n"
        "5. */wbansticker <on/off> [reason]*\n"
        "   - Enables/disables warnings for banned stickers.\n"
        "   - *Example:* `/wbansticker on Enable warnings`\n"
        "   - *Note:* Reason is optional.\n\n"
        "6. */wbanstickerlimit <number/default> [reason]*\n"
        "   - Sets warning limit before action.\n"
        "   - *Range:* 1 to 100; `default` = 3.\n"
        "   - *Example:* `/wbanstickerlimit 5 Strict enforcement`\n"
        "   - *Note:* Reason is optional.\n\n"
        "7. */wbanstickermode <ban/kick/mute> [reason]*\n"
        "   - Sets action after warning limit.\n"
        "   - *Example:* `/wbanstickermode mute Reduce disruptions`\n"
        "   - *Note:* Reason is optional.\n\n"
        "8. */allowadmins <on/off> [reason]*\n"
        "   - Allows/restricts admins from using commands.\n"
        "   - *Only for group owner.*\n"
        "   - *Example:* `/allowadmins on Admins trusted`\n"
        "   - *Note:* Reason is optional.\n\n"
        "9. */banstickeron <all/user/admin> [reason]*\n"
        "   - Sets who is affected by bans.\n"
        "   - *Options:* `all` (default), `user` (non-admins), `admin`.\n"
        "   - *Example:* `/banstickeron user Protect admins`\n"
        "   - *Note:* Reason is optional.\n\n"
        "📊 *Status Command*\n"
        "10. */banstickerstatus*\n"
        "    - Shows current settings and banned packs.\n"
        "    - *Example:* `/banstickerstatus`\n\n"
        "💡 *Tips*\n"
        "- Use letters, numbers, underscores, or hyphens for pack names.\n"
        "- Reply to stickers for easy banning.\n"
        "- Check settings with `/banstickerstatus`.\n"
        "- All actions are logged."
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")
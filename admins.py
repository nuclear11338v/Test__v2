import telebot
import time
import re
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
from config import bot
from functools import wraps
from kick import disabled
from user_logs.user_logs import log_action
from ban_sticker_pack.ban_sticker_pack import is_allowed, is_group

DATA_FILE = "bot_data.json"

def read_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {"admin_cache": {}, "temp_admins": [], "group_settings": {}}
    except Exception as e:
        print(f"Error reading data: {e}")
        return {"admin_cache": {}, "temp_admins": [], "group_settings": {}}

def write_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error writing data: {e}")

def parse_title_and_duration(args):
    custom_title = None
    duration = None
    if args:
        last_arg = args[-1]
        if re.match(r"^\d+[mhd]$", last_arg):
            duration_val = int(last_arg[:-1])
            unit = last_arg[-1]
            if unit == 'm':
                duration = duration_val * 60
            elif unit == 'h':
                duration = duration_val * 3600
            elif unit == 'd':
                duration = duration_val * 86400
            args = args[:-1]
        custom_title = " ".join(args) if args else None
    return custom_title, duration

def format_duration(seconds):
    if seconds < 3600:
        return f"{seconds // 60} minutes"
    elif seconds < 86400:
        return f"{seconds // 3600} hours"
    else:
        return f"{seconds // 86400} days"

def get_user_mention(user):
    return f"[{user.first_name}](tg://user?id={user.id})"

def is_admin(chat_id, user_id, message=None):
    """Check if user is admin or anonymous admin"""
    try:
        if message and message.sender_chat and message.sender_chat.id == chat_id:
            return True
        
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception:
        return False

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
                bot.reply_to(message, "User not found. Please use /promote [reply] or /promote [user_id]")
                return None
            except FileNotFoundError:
                bot.reply_to(message, "User data file not found. Please use /promote [reply] or /promote [user_id]")
                return None
            except json.JSONDecodeError:
                bot.reply_to(message, "Error reading user data. Please use /promote [reply] or /promote [user_id]")
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
        bot.reply_to(message, f"Error getting target user: {str(e)}")
        return None

def update_admin_cache(chat_id):
    try:
        data = read_data()
        admins = bot.get_chat_administrators(chat_id)
        admin_list = [
            {"user_id": admin.user.id, "status": admin.status}
            for admin in admins
        ]
        data["admin_cache"][str(chat_id)] = admin_list
        write_data(data)
    except Exception as e:
        print(f"Error updating admin cache: {e}")

def get_group_setting(chat_id, setting):
    data = read_data()
    return data.get("group_settings", {}).get(str(chat_id), {}).get(setting, False)

def update_group_setting(chat_id, setting, value):
    data = read_data()
    if str(chat_id) not in data["group_settings"]:
        data["group_settings"][str(chat_id)] = {}
    data["group_settings"][str(chat_id)][setting] = value
    write_data(data)

def check_temp_admins():
    data = read_data()
    current_time = int(time.time())
    expired = []
    for temp_admin in data["temp_admins"]:
        if temp_admin["expiry"] <= current_time:
            try:
                bot.promote_chat_member(
                    chat_id=temp_admin["chat_id"],
                    user_id=temp_admin["user_id"],
                    can_change_info=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_video_chats=False
                )
                update_admin_cache(temp_admin["chat_id"])
                expired.append(temp_admin)
            except Exception as e:
                print(f"Error demoting temp admin {temp_admin['user_id']}: {e}")
    data["temp_admins"] = [ta for ta in data["temp_admins"] if ta not in expired]
    write_data(data)

def admin_required(func):
    @wraps(func)
    def wrapper(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        try:
            if is_admin(chat_id, user_id, message):
                return func(message)
            else:
                bot.reply_to(message, "Soo sad, You need to be an admin to do this.")
        except Exception as e:
            bot.reply_to(message, f"Error checking admin status: {str(e)}")
    return wrapper

def rights(func):
    @wraps(func)
    def wrapper(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if message.sender_chat and message.sender_chat.id == chat_id:
            return func(message)
            
        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == 'creator':
                return func(message)
            elif member.status == 'administrator' and member.can_promote_members:
                return func(message)
            else:
                bot.reply_to(message, "You don't have sufficient permissions to perform this action.")
        except Exception as e:
            bot.reply_to(message, f"Error checking permissions: {str(e)}")
    return wrapper

@bot.message_handler(regexp=r'^[\/!](promote)(?:\s|$|@)')
@disabled
@admin_required
@rights
def command_promote(message):
    try:
        chat_id = message.chat.id
        is_anonymous = message.sender_chat and message.sender_chat.id == chat_id
        target_user = None
        custom_title = None
        duration = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            args_after_command = message.text.split()[1:]
            custom_title, duration = parse_title_and_duration(args_after_command)
            args_to_check = args_after_command
        else:
            args_after_command = message.text.split()[1:]
            if not args_after_command:
                bot.reply_to(message, "Usᴀɢᴇ → /promote [ᴜsᴇʀ_ɪᴅ|username] [title] [duration]\nExample: /promote @username Moderator 1d or /promote 123456 Moderator 1d\nOr reply to a user: /promote [title] [duration]")
                return
            target_user = get_target_user(message)
            if not target_user:
                return
            remaining_args = args_after_command[1:]
            custom_title, duration = parse_title_and_duration(remaining_args)
            args_to_check = remaining_args

        if duration is None and args_to_check:
            last_arg = args_to_check[-1]
            if re.match(r"^\d+[a-zA-Z]$", last_arg):
                bot.reply_to(message, f"Invalid duration format: {last_arg}. Use m, h, or d (e.g., 30m, 2h, 1d).")
                return

        if duration is not None and duration <= 0:
            bot.reply_to(message, "Dᴜʀᴀᴛɪᴏɴ Mᴜsᴛ Bᴇ ᴀ Pᴏsɪᴛɪᴠᴇ Vᴀʟᴜᴇ.")
            return

        if custom_title and len(custom_title) > 16:
            bot.reply_to(message, "Tɪᴛʟᴇ Mᴜsᴛ Bᴇ 16 Cʜᴀʀᴀᴄᴛᴇʀs Oʀ Lᴇss!")
            return

        if is_admin(chat_id, target_user.id):
            bot.reply_to(message, f"{get_user_mention(target_user)} Is Aʟʀᴇᴀᴅʏ Aɴ Aᴅᴍɪɴ.")
            return

        bot.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            can_change_info=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_promote_members=False,
            can_manage_video_chats=True
        )

        if custom_title:
            bot.set_chat_administrator_custom_title(
                chat_id=chat_id,
                user_id=target_user.id,
                custom_title=custom_title
            )

        if duration:
            expiry_time = int(time.time()) + duration
            data = read_data()
            data["temp_admins"].append({
                "chat_id": chat_id,
                "user_id": target_user.id,
                "expiry": expiry_time,
                "custom_title": custom_title
            })
            write_data(data)

        details = {
            "custom_title": custom_title,
            "duration": format_duration(duration) if duration else None,
            "permissions": {
                "can_change_info": True,
                "can_delete_messages": True,
                "can_restrict_members": True,
                "can_invite_users": True,
                "can_pin_messages": True,
                "can_promote_members": False,
                "can_manage_video_chats": True
            }
        }
        log_action(
            chat_id=chat_id,
            action="promote",
            executor=message.from_user,
            target=target_user,
            details=details
        )

        update_admin_cache(chat_id)
        admin_name = "Anonymous Admin" if is_anonymous else get_user_mention(message.from_user)
        response_msg = f"Successfully promoted {get_user_mention(target_user)}\nBye - {admin_name}\n\nPermissions:\n- Change info: True\n- Delete messages: True\n- Restrict members: True\n- Invite users: True\n- Pin messages: True\n- Promote members: False\n- Manage video chats: True"
        if custom_title:
            response_msg += f"\n\nTɪᴛʟᴇ Sᴇᴛ: {custom_title}"
        if duration:
            formatted_dur = format_duration(duration)
            response_msg += f"\nDᴜʀᴀᴛɪᴏɴ : {formatted_dur}"
        bot.reply_to(message, response_msg, parse_mode='Markdown')

    except Exception as e:
        error_message = f"Promotion failed: {str(e)}"
        if "not enough rights" in str(e).lower():
            error_message = "I Dᴏɴ'ᴛ Hᴀᴠᴇ Pᴇʀᴍɪssɪᴏɴ Tᴏ Pʀᴏᴍᴏᴛᴇ Usᴇʀs."
        elif "ADMINS_TOO_MUCH" in str(e):
            error_message = "Tᴏᴏ Mᴀɴʏ Aᴅᴍɪɴs! Mᴀxɪᴍᴜᴍ Is 50."
        elif "user is not a member" in str(e).lower():
            error_message = "Usᴇʀ Is Nᴏᴛ ᴀ Mᴇᴍʙᴇʀ Oғ Tʜɪs Cʜᴀᴛ."
        bot.reply_to(message, error_message)

@bot.message_handler(regexp=r'^[\/!](demote)(?:\s|$|@)')
@disabled
@admin_required
@rights
def command_demote(message):
    try:
        chat_id = message.chat.id
        target_user = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        else:
            args = message.text.split()[1:]
            if not args:
                bot.reply_to(message, "Usᴀɢᴇ → /demote [ᴜsᴇʀ_ɪᴅ|username]\nExample: /demote @username or /demote 123456\nOr reply to a user: /demote")
                return
            target_user = get_target_user(message)
            if not target_user:
                return

        target_member = bot.get_chat_member(chat_id, target_user.id)
        if target_member.status == 'creator':
            bot.reply_to(message, "Yᴏᴜ Cᴀɴ'ᴛ Dᴇᴍᴏᴛᴇ Tʜᴇ Gʀᴏᴜᴘ Oᴡɴᴇʀ.")
            return

        if target_member.status != 'administrator':
            bot.reply_to(message, f"{get_user_mention(target_user)} Is Nᴏᴛ Aɴ Aᴅᴍɪɴ.")
            return

        bot.promote_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            can_change_info=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False
        )

        data = read_data()
        data["temp_admins"] = [
            ta for ta in data["temp_admins"]
            if not (ta["chat_id"] == chat_id and ta["user_id"] == target_user.id)
        ]
        write_data(data)

        details = {
            "permissions": {
                "can_change_info": False,
                "can_delete_messages": False,
                "can_restrict_members": False,
                "can_invite_users": False,
                "can_pin_messages": False,
                "can_promote_members": False,
                "can_manage_video_chats": False
            }
        }
        log_action(
            chat_id=chat_id,
            action="demote",
            executor=message.from_user,
            target=target_user,
            details=details
        )

        update_admin_cache(chat_id)
        bot.reply_to(message,
                   f"successfully demoted {get_user_mention(target_user)}\n\nPermissions:\n- Change info: False\n- Delete messages: False\n- Restrict members: False\n- Invite users: False\n- Pin messages: False\n- Promote members: False\n- Manage video chats: False",
                   parse_mode='Markdown')

    except Exception as e:
        error_message = f"Demotion failed: {str(e)}"
        if "not enough rights" in str(e).lower():
            error_message = "I Dᴏɴ'ᴛ Hᴀᴠᴇ Pᴇʀᴍɪssɪᴏɴ Tᴏ Dᴇᴍᴏᴛᴇ Usᴇʀs!"
        elif "user is not a member" in str(e).lower():
            error_message = "Usᴇʀ Is Nᴏᴛ ᴀ Mᴇᴍʙᴇʀ Oғ Tʜɪs Cʜᴀᴛ."
        bot.reply_to(message, error_message)

@bot.message_handler(regexp=r'^[\/!](adminlist)(?:\s|$|@)')
@disabled
def command_adminlist(message):
    chat_id = message.chat.id
    try:
        update_admin_cache(chat_id)
        data = read_data()
        admins = data["admin_cache"].get(str(chat_id), [])
        
        if not admins:
            bot.reply_to(message, "Nᴏ Aᴅᴍɪɴs Fᴏᴜɴᴅ.")
            return

        admin_list = []
        for admin in admins:
            user = bot.get_chat_member(chat_id, admin["user_id"]).user
            admin_type = "Owner" if admin["status"] == 'creator' else "Admin"
            admin_list.append(f"{admin_type}: {get_user_mention(user)}")
        
        response = f"Admins in {message.chat.title}\n" + "\n".join(admin_list)
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"Failed to retrieve admin list: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](admincache)(?:\s|$|@)')
@disabled
@admin_required
def command_admincache(message):
    try:
        update_admin_cache(message.chat.id)
        bot.reply_to(message, "Aᴅᴍɪɴ Cᴀᴄʜᴇ Rᴇғʀᴇsʜᴇᴅ Sᴜᴄᴄᴇssғᴜʟʟʏ.")
    except Exception as e:
        bot.reply_to(message, f"Cᴀᴄʜᴇ Rᴇғʀᴇsʜ Fᴀɪʟᴇᴅ {str(e)}")

@bot.message_handler(regexp=r'^[\/!](anonadmin)(?:\s|$|@)')
@disabled
@admin_required
def command_anonadmin(message):
    try:
        chat_id = message.chat.id
        args = message.text.split()[1:]
        if not args:
            current = get_group_setting(chat_id, "anonadmin")
            status = "enabled" if current else "disabled"
            bot.reply_to(message, f"Aɴᴏɴʏᴍᴏᴜs Aᴅᴍɪɴ Mᴏᴅᴇ Is Cᴜʀʀᴇɴᴛʟʏ. {status}")
            return

        value = args[0].lower()
        new_value = value in ['yes', 'on', 'true', '1']
        update_group_setting(chat_id, "anonadmin", new_value)
        bot.reply_to(message, f"Aɴᴏɴʏᴍᴏᴜs Aᴅᴍɪɴ Mᴏᴅᴇ {'enabled' if new_value else 'disabled'}!")

    except Exception as e:
        bot.reply_to(message, f"Failed to update settings: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](adminerror)(?:\s|$|@)')
@admin_required
@disabled
def command_adminerror(message):
    try:
        chat_id = message.chat.id
        args = message.text.split()[1:]
        if not args:
            current = get_group_setting(chat_id, "adminerror")
            status = "enabled" if current else "disabled"
            bot.reply_to(message, f"Aᴅᴍɪɴ Eʀʀᴏʀ Mᴇssᴀɢᴇs Aʀᴇ Cᴜʀʀᴇɴᴛʟʏ. {status}")
            return

        value = args[0].lower()
        new_value = value in ['yes', 'on', 'true', '1']
        update_group_setting(chat_id, "adminerror", new_value)
        bot.reply_to(message, f"Aᴅᴍɪɴ Eʀʀᴏʀ Mᴇssᴀɢᴇs {'enabled' if new_value else 'disabled'}!")

    except Exception as e:
        bot.reply_to(message, f"Failed to update settings: {str(e)}")

def start_admin_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_temp_admins, 'interval', seconds=60)
    scheduler.start()
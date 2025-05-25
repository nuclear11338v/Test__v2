import telebot
from telebot import types
from functools import wraps
from telebot.util import user_link
from config import bot
import os
import json
from user_logs.user_logs import log_action
from datetime import datetime
from ban_sticker_pack.ban_sticker_pack import is_allowed, is_admin, is_group

SETTINGS_FILE = 'mix.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            try:
                data = json.load(f)
                for chat_id in data:
                    data[chat_id] = {
                        'disable': data[chat_id].get('disable', False),
                        'disabledel': data[chat_id].get('disabledel', False),
                        'disableadmin': data[chat_id].get('disableadmin', False),
                        'disabled_commands': data[chat_id].get('disabled_commands', [])
                    }
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

group_settings = load_settings()

def get_target_user_id(message):
    try:
        if message.reply_to_message:
            return message.reply_to_message.from_user.id
        elif len(message.text.split()) > 1:
            identifier = message.text.split()[1]
            if identifier.startswith('@'):
                try:
                    with open('data/data.json', 'r') as file:
                        users = json.load(file)
                    username = identifier[1:].lower()
                    for user in users:
                        if user.get('username', '').lower() == username:
                            return int(user['user_id'])
                    bot.reply_to(message, "User not found. Please kick with /kick [reply] or /kick [user_id]")
                    return None
                except FileNotFoundError:
                    bot.reply_to(message, "User data file not found. Please kick with /kick [reply] or /kick [user_id]")
                    return None
                except json.JSONDecodeError:
                    bot.reply_to(message, "Error reading user data. Please kick with /kick [reply] or /kick [user_id]")
                    return None
            elif identifier.isdigit():
                user_id = int(identifier)
                try:
                    bot.get_chat_member(message.chat.id, user_id)  # Verify user exists in chat
                    return user_id
                except telebot.apihelper.ApiTelegramException as e:
                    if "PARTICIPANT_ID_INVALID" in str(e):
                        group_name = bot.get_chat(message.chat.id).title or "this group"
                        bot.reply_to(message, f"User not found in {group_name}")
                        return None
                    raise
            else:
                bot.reply_to(message, "Invalid user ID or username format!")
                return None
        return None
    except Exception as e:
        bot.reply_to(message, f"Error extracting user ID: {str(e)}")
        return None

def is_user_admin(chat_id, user_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except telebot.apihelper.ApiTelegramException:
        return False

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

def get_reason(args, start_index):
    return ' '.join(args[start_index:]) if len(args) > start_index else None

def format_kick_response(target_user_id, admin_user, chat_id, reason=None):
    current_time = datetime.now()
    date_str = current_time.strftime("%d/%m/%y")
    time_str = current_time.strftime("%I:%M:%S %p")
    target_mention = get_user_mention(target_user_id, chat_id)
    admin_mention = get_admin_mention(admin_user)
    
    response = (
        f"Whoosh! Troublemaker kicked away, {target_mention}.\n"
        f"Moderator: {admin_mention}\n"
        f"{date_str} at {time_str}"
    )
    if reason:
        response += f"\nReason: {reason}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="Ban ( admin only )", callback_data=f"ban_{target_user_id}"),
        types.InlineKeyboardButton(text="Mute ( admin only )", callback_data=f"mute_{target_user_id}")
    )
    return response, markup

def disabled(func):
    @wraps(func)
    def wrapper(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        settings = group_settings.get(str(chat_id), {
            'disable': False,
            'disabledel': False,
            'disableadmin': False,
            'disabled_commands': []
        })
        
        if str(chat_id) not in group_settings:
            group_settings[str(chat_id)] = settings
            save_settings(group_settings)

        command_name = func.__name__.replace('_user', '') if func.__name__.endswith('_user') else message.text.split()[0][1:].lower()

        is_command_disabled = (
            (command_name == 'kickme' and settings['disable']) or
            command_name in settings['disabled_commands']
        )

        if is_command_disabled:
            if settings['disableadmin']:
                try:
                    if settings['disabledel']:
                        bot.delete_message(chat_id, message.message_id)
                    return
                except telebot.apihelper.ApiTelegramException:
                    return
            else:
                try:
                    chat_member = bot.get_chat_member(chat_id, user_id)
                    if chat_member.status in ['administrator', 'creator']:
                        return func(message)
                    else:
                        if settings['disabledel']:
                            bot.delete_message(chat_id, message.message_id)
                        return
                except telebot.apihelper.ApiTelegramException:
                    return
        return func(message)
    return wrapper

@bot.message_handler(regexp=r'^[\/!](disable)(?:\s|$|@)')
@is_group
@is_admin
@is_allowed
def disable_command(message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /disable <command>|all|on|off|yes|no\nExample: /disable kick, /disable all")
        return

    command = args[1].lower()
    settings = group_settings.setdefault(str(chat_id), {
        'disable': False,
        'disabledel': False,
        'disableadmin': False,
        'disabled_commands': []
    })

    if command in ['on', 'off', 'yes', 'no']:
        is_disabled = command in ['on', 'yes']
        settings['disable'] = is_disabled
        save_settings(group_settings)
        log_action(
            chat_id=message.chat.id,
            action="disable",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "kickme", "state": "disabled" if is_disabled else "enabled"}
        )
        status = "disabled" if is_disabled else "enabled"
        bot.reply_to(message, f"disabling is now {status} in this group.")
        return

    valid_commands = [
        'kick', 'promote', 'mute', 'skick', 'dkick', 'kickme', 'all', 'demote', 'admincache', 
        'adminerror', 'anonadmin', 'adminlist', 'tmute', 'smute', 'dmute', 'rmute', 'unmute', 
        'ban', 'rban', 'tban', 'sban', 'dban', 'unban', 'blocklist', 'blocklistmode', 
        'addblocklist', 'approve', 'lock', 'unlock', 'pin', 'unpin', 'unpinall', 'cleanlinked', 
        'antichannelpin', 'permapin', 'flood', 'setflood', 'clearflood', 'floodmode', 
        'setfloodtimer', 'disable', 'disableadmin', 'checkmute', 'adddescription', 'renamegroup', 
        'save', 'privatenotes', 'clearall', 'clear', 'saved', 'notes', 'get', 'purge', 'spurge', 
        'purgeto', 'purgefrom', 'del', 'rules', 'setrules', 'resetrulesbutton', 'setrulesbutton', 
        'resetrules', 'privaterules', 'deletetopic', 'reopentopic', 'closetopic', 'renametopic', 
        'newtopic', 'warn', 'warntime', 'warnlimit', 'warningmode', 'warnings', 
        'resetallwarnings', 'rmwarn', 'swarn', 'dwarn', 'twarn', 'welcome', 'goodbye', 
        'setwelcome', 'setgoodbye', 'cleanwelcome', 'resetgoodbye', 'resetwelcome', 
        'autoantiraid', 'raidactiontime', 'raidtime', 'antiraid', 'filter', 'filters', 'stop', 
        'stopall', 'nocleanservice', 'cleanservicetypes', 'keepservice', 'cleanservice', 
        'cleancommand', 'keepcommand', 'start'
    ]
    if command not in valid_commands:
        bot.reply_to(message, f"Invalid command. Valid options: {', '.join(valid_commands)}")
        return

    if command == 'all':
        settings['disabled_commands'] = valid_commands
        settings['disable'] = True
        log_details = {"operation": "all", "commands": valid_commands}
    else:
        if command not in settings['disabled_commands']:
            settings['disabled_commands'].append(command)
        if command == 'kickme':
            settings['disable'] = True
        log_details = {"operation": "command", "command": command}

    save_settings(group_settings)
    log_action(
        chat_id=message.chat.id,
        action="disable",
        executor=message.from_user,
        target=message.chat,
        details=log_details
    )
    bot.reply_to(message, f"Command /{command} is now disabled in this group.")

@bot.message_handler(regexp=r'^[\/!](enable)(?:\s|$|@)')
@is_group
@is_admin
@is_allowed
def enable_command(message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /enable <command>\nExample: /enable kick.")
        return

    command = args[1].lower()
    settings = group_settings.setdefault(str(chat_id), {
        'disable': False,
        'disabledel': False,
        'disableadmin': False,
        'disabled_commands': []
    })

    valid_commands = [
        'kick', 'promote', 'mute', 'skick', 'dkick', 'kickme', 'all', 'demote', 'admincache', 
        'adminerror', 'anonadmin', 'adminlist', 'tmute', 'smute', 'dmute', 'rmute', 'unmute', 
        'ban', 'rban', 'tban', 'sban', 'dban', 'unban', 'blocklist', 'blocklistmode', 
        'addblocklist', 'approve', 'lock', 'unlock', 'pin', 'unpin', 'unpinall', 'cleanlinked', 
        'antichannelpin', 'permapin', 'flood', 'setflood', 'clearflood', 'floodmode', 
        'setfloodtimer', 'disable', 'disableadmin', 'checkmute', 'adddescription', 'renamegroup', 
        'save', 'privatenotes', 'clearall', 'clear', 'saved', 'notes', 'get', 'purge', 'spurge', 
        'purgeto', 'purgefrom', 'del', 'rules', 'setrules', 'resetrulesbutton', 'setrulesbutton', 
        'resetrules', 'privaterules', 'deletetopic', 'reopentopic', 'closetopic', 'renametopic', 
        'newtopic', 'warn', 'warntime', 'warnlimit', 'warningmode', 'warnings', 
        'resetallwarnings', 'rmwarn', 'swarn', 'dwarn', 'twarn', 'welcome', 'goodbye', 
        'setwelcome', 'setgoodbye', 'cleanwelcome', 'resetgoodbye', 'resetwelcome', 
        'autoantiraid', 'raidactiontime', 'raidtime', 'antiraid', 'filter', 'filters', 'stop', 
        'stopall', 'nocleanservice', 'cleanservicetypes', 'keepservice', 'cleanservice', 
        'cleancommand', 'keepcommand'
    ]
    if command not in valid_commands:
        bot.reply_to(message, f"Invalid command. Valid options: {', '.join(valid_commands)}")
        return

    if command == 'all':
        settings['disabled_commands'] = []
        settings['disable'] = False
        log_details = {"operation": "all", "commands": valid_commands}
    else:
        if command in settings['disabled_commands']:
            settings['disabled_commands'].remove(command)
        if command == 'kickme':
            settings['disable'] = False
        log_details = {"operation": "command", "command": command}

    save_settings(group_settings)
    log_action(
        chat_id=message.chat.id,
        action="enable",
        executor=message.from_user,
        target=message.chat,
        details=log_details
    )
    bot.reply_to(message, f"✅ Command /{command} is now enabled in this group.")

@bot.message_handler(regexp=r'^[\/!](disabledel)(?:\s|$|@)')
@is_group
@is_admin
@is_allowed
def disabledel_command(message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /disabledel on|off|yes|no")
        return

    state = args[1].lower()
    if state not in ['on', 'off', 'yes', 'no']:
        bot.reply_to(message, "Invalid argument. Use on|off|yes|no.")
        return

    is_enabled = state in ['on', 'yes']
    group_settings.setdefault(str(chat_id), {
        'disable': False,
        'disabledel': False,
        'disableadmin': False,
        'disabled_commands': []
    })
    group_settings[str(chat_id)]['disabledel'] = is_enabled
    save_settings(group_settings)
    log_action(
        chat_id=message.chat.id,
        action="disabledel",
        executor=message.from_user,
        target=message.chat,
        details={"operation": "enable" if is_enabled else "disable"}
    )
    status = "enabled" if is_enabled else "disabled"
    bot.reply_to(message, f"Deleting disabled commands for non-admins is now {status} in this group.")

@bot.message_handler(regexp=r'^[\/!](disableadmin)(?:\s|$|@)')
@is_group
@is_admin
@is_allowed
def disableadmin_command(message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /disableadmin on|off|yes|no")
        return

    state = args[1].lower()
    if state not in ['on', 'off', 'yes', 'no']:
        bot.reply_to(message, "Invalid argument. Use on|off|yes|no.")
        return

    is_enabled = state in ['on', 'yes']
    group_settings.setdefault(str(chat_id), {
        'disable': False,
        'disabledel': False,
        'disableadmin': False,
        'disabled_commands': []
    })
    group_settings[str(chat_id)]['disableadmin'] = is_enabled
    save_settings(group_settings)
    log_action(
        chat_id=message.chat.id,
        action="disableadmin",
        executor=message.from_user,
        target=message.chat,
        details={"operation": "enable" if is_enabled else "disable"}
    )
    status = "enabled" if is_enabled else "disabled"
    bot.reply_to(message, f"Restricting admins from using disabled commands is now {status} in this group.")

@bot.message_handler(regexp=r'^[\/!](kick)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@is_allowed
def command_kick(message):
    chat_id = message.chat.id
    args = message.text.split()
    target_user_id = get_target_user_id(message)
    reason = None

    if message.reply_to_message:
        reason = get_reason(args, 1) if len(args) > 1 else None
    elif len(args) > 1:
        reason = get_reason(args, 2) if len(args) > 2 else None
    else:
        bot.reply_to(message, "Reply to a user's message or provide a valid user ID/username (e.g., /kick @username or /kick 123456 [reason])")
        return
    
    if not target_user_id:
        return
    
    if target_user_id == message.from_user.id:
        bot.reply_to(message, "You cannot kick yourself!")
        return
    
    if target_user_id == bot.get_me().id:
        bot.reply_to(message, "Are you crazy?, I cannot kick myself!")
        return
    
    if is_user_admin(chat_id, target_user_id):
        bot.reply_to(message, "hmmm 🤷, I cannot kick an moderator.")
        return
    
    try:
        bot.kick_chat_member(chat_id, target_user_id)
        bot.unban_chat_member(chat_id, target_user_id)
        target_user = bot.get_chat_member(chat_id, target_user_id).user
        log_action(
            chat_id=message.chat.id,
            action="kick",
            executor=message.from_user,
            target=target_user,
            details={"type": "normal", "reason": reason}
        )
        response, markup = format_kick_response(target_user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to kick users. grant me admin rights with ban permissions.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "hmm 🤷, I cannot kick an moderator.")
        else:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(regexp=r'^[\/!](skick)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@is_allowed
def silent_kick_user(message):
    chat_id = message.chat.id
    args = message.text.split()
    target_user_id = get_target_user_id(message)
    reason = None

    if message.reply_to_message:
        reason = get_reason(args, 1) if len(args) > 1 else None
    elif len(args) > 1:
        reason = get_reason(args, 2) if len(args) > 2 else None
    else:
        bot.reply_to(message, "Reply to a user's message or provide a valid user ID/username (e.g., /skick @username or /skick 123456 [reason])")
        return
    
    if not target_user_id:
        return
    
    if target_user_id == message.from_user.id:
        bot.reply_to(message, "Hmm 🧐, You cannot kick yourself.")
        return
    
    if target_user_id == bot.get_me().id:
        bot.reply_to(message, "🤦, I cannot kick myself!")
        return
    
    if is_user_admin(chat_id, target_user_id):
        bot.reply_to(message, "hmm 🤦, I cannot kick an admin!")
        return
    
    try:
        bot.kick_chat_member(chat_id, target_user_id)
        bot.unban_chat_member(chat_id, target_user_id)
        target_user = bot.get_chat_member(chat_id, target_user_id).user
        log_action(
            chat_id=message.chat.id,
            action="skick",
            executor=message.from_user,
            target=target_user,
            details={"type": "silent", "reason": reason}
        )
        bot.delete_message(chat_id, message.message_id)
        response, markup = format_kick_response(target_user_id, message, chat_id, reason)
        bot.send_message(chat_id, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to kick users or delete messages. Please grant me admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "🤦, I cannot kick an moderator.")
        else:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(regexp=r'^[\/!](dkick)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@is_allowed
def delete_and_kick_user(message):
    chat_id = message.chat.id
    args = message.text.split()
    reason = None

    if not message.reply_to_message:
        bot.reply_to(message, "reply to the user's message you want to delete and kick (e.g., /dkick [reason]).")
        return
    
    target_user_id = message.reply_to_message.from_user.id
    reason = get_reason(args, 1) if len(args) > 1 else None
    
    if target_user_id == message.from_user.id:
        bot.reply_to(message, "🤷, You cannot kick yourself!")
        return
    
    if target_user_id == bot.get_me().id:
        bot.reply_to(message, "shhhh, I cannot kick myself!")
        return
    
    if is_user_admin(chat_id, target_user_id):
        bot.reply_to(message, "shhh, I cannot kick an moderator.")
        return
    
    try:
        bot.delete_message(chat_id, message.reply_to_message.message_id)
        bot.kick_chat_member(chat_id, target_user_id)
        bot.unban_chat_member(chat_id, target_user_id)
        target_user = bot.get_chat_member(chat_id, target_user_id).user
        log_action(
            chat_id=message.chat.id,
            action="dkick",
            executor=message.from_user,
            target=target_user,
            details={"type": "delete", "reason": reason}
        )
        response, markup = format_kick_response(target_user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to delete messages or kick users. Please grant me admin rights.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "shh I cannot kick an moderator.")
        else:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(regexp=r'^[\/!](kickme)(?:\s|$|@)')
@is_group
@disabled
def kickme(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    args = message.text.split()
    reason = get_reason(args, 1) if len(args) > 1 else None
    
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            bot.reply_to(message, "Admins cannot kick themselves!")
            return
        
        bot.kick_chat_member(chat_id, user_id)
        bot.unban_chat_member(chat_id, user_id)
        log_action(
            chat_id=message.chat.id,
            action="kickme",
            executor=message.from_user,
            target=message.from_user,
            details={"type": "self", "reason": reason}
        )
        response, markup = format_kick_response(user_id, message, chat_id, reason)
        bot.reply_to(message, response, reply_markup=markup, parse_mode="Markdown")
    except telebot.apihelper.ApiTelegramException as e:
        if "not enough rights" in str(e).lower():
            bot.reply_to(message, "I don't have permission to kick users. Please grant me admin rights with ban permissions.")
        elif "user is an administrator" in str(e).lower():
            bot.reply_to(message, "Admins cannot be kicked!")
        else:
            bot.reply_to(message, f"Error: {e}")
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")
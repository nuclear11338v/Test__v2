import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import json
import os
from config import bot, logger
from kick import disabled
from user_logs.user_logs import log_action
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group

SETTINGS_fiilee = 'cleanservice.json'

SERVICE_TYPES = {
    'all': 'All service messages',
    'other': 'Miscellaneous (boosts, payments, etc.)',
    'photo': 'Chat photo/background changes',
    'pin': 'Message pinning',
    'title': 'Chat/topic title changes',
    'videochat': 'Video chat actions'
}

def load_settings():
    if os.path.exists(SETTINGS_fiilee):
        with open(SETTINGS_fiilee, 'r') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_fiilee, 'w') as f:
        json.dump(settings, f)


def init_group_settings(chat_id):
    settings = load_settings()
    chat_id = str(chat_id)
    if chat_id not in settings:
        settings[chat_id] = {'clean_service': []}
        save_settings(settings)
    return settings

@bot.message_handler(content_types=['new_chat_photo', 'delete_chat_photo', 
                                  'new_chat_title', 'pinned_message',
                                  'group_chat_created', 'supergroup_chat_created',
                                  'channel_chat_created', 'migrate_to_chat_id',
                                  'migrate_from_chat_id', 'video_chat_scheduled',
                                  'video_chat_started', 'video_chat_ended',
                                  'video_chat_participants_invited', 
                                  'successful_payment', 'proximity_alert_triggered',
                                  'message_auto_delete_timer_changed',
                                  'web_app_data'])
def handle_service_messages(message):
    chat_id = str(message.chat.id)
    settings = load_settings()
    
    if chat_id not in settings:
        return

    clean_types = settings[chat_id]['clean_service']
    
    if 'all' in clean_types:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return

    message_type = None
    if message.new_chat_photo or message.delete_chat_photo:
        message_type = 'photo'
    elif message.new_chat_title:
        message_type = 'title'
    elif message.pinned_message:
        message_type = 'pin'
    elif (message.video_chat_scheduled or message.video_chat_started or 
          message.video_chat_ended or message.video_chat_participants_invited):
        message_type = 'videochat'
    else:
        message_type = 'other'

    if message_type in clean_types:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

@bot.message_handler(regexp=r'^[\/!](cleanservice)(?:\s|$|@)')
@disabled
@is_admin
def command_cleanservice(message):
    chat_id = str(message.chat.id)
    init_group_settings(chat_id)
    
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        bot.reply_to(message, "Please specify a service type or on/off. Use /cleanservicetypes to see available types.")
        return
    
    settings = load_settings()
    param = args[0].lower()
    
    if param in ['yes', 'on']:
        settings[chat_id]['clean_service'] = list(SERVICE_TYPES.keys())
        save_settings(settings)
        log_action(
            chat_id=message.chat.id,
            action="cleanservice",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "enable_all"}
        )
        bot.reply_to(message, "All service messages will now be deleted.")
    elif param in ['no', 'off']:
        settings[chat_id]['clean_service'] = []
        save_settings(settings)
        log_action(
            chat_id=message.chat.id,
            action="cleanservice",
            executor=message.from_user,
            target=message.chat,
            details={"operation": "disable_all"}
        )
        bot.reply_to(message, "Service message deletion disabled.")
    elif param in SERVICE_TYPES:
        if param not in settings[chat_id]['clean_service']:
            settings[chat_id]['clean_service'].append(param)
            save_settings(settings)
            log_action(
                chat_id=message.chat.id,
                action="cleanservice",
                executor=message.from_user,
                target=message.chat,
                details={"operation": "add_type", "type": param}
            )
            bot.reply_to(message, f"Now deleting {param} service messages.")
        else:
            bot.reply_to(message, f"{param} service messages are already being deleted.")
    else:
        bot.reply_to(message, "Invalid service type. Use /cleanservicetypes to see available types.")

@bot.message_handler(commands=['keepservice', 'nocleanservice'])
@disabled
@is_admin
def command_keepservice(message):
    chat_id = str(message.chat.id)
    init_group_settings(chat_id)
    
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        bot.reply_to(message, "Please specify a service type. Use /cleanservicetypes to see available types.")
        return
    
    settings = load_settings()
    param = args[0].lower()
    
    if param in SERVICE_TYPES:
        if param in settings[chat_id]['clean_service']:
            settings[chat_id]['clean_service'].remove(param)
            save_settings(settings)
            log_action(
                chat_id=message.chat.id,
                action="keepservice",
                executor=message.from_user,
                target=message.chat,
                details={"operation": "remove_type", "type": param}
            )
            bot.reply_to(message, f"Stopped deleting {param} service messages.")
        else:
            bot.reply_to(message, f"{param} service messages were not being deleted.")
    else:
        bot.reply_to(message, "Invalid service type. Use /cleanservicetypes to see available types.")

@bot.message_handler(regexp=r'^[\/!](cleanservicetypes)(?:\s|$|@)')
@disabled
@is_admin
def command_cleanservicetypes(message):
    response = "Available service message types:\n\n"
    for type_name, description in SERVICE_TYPES.items():
        response += f"• {type_name}: {description}\n"
    bot.reply_to(message, response)
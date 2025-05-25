import telebot
from telebot import types
from functools import wraps
import logging
from config import bot, logger
from kick import disabled
from user_logs.user_logs import log_action
from ban_sticker_pack.ban_sticker_pack import is_allowed, is_admin, is_group



@bot.message_handler(regexp=r'^[\/!](regroup)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@is_allowed
def command_rename_group(message):
    try:
        new_name = message.text.split(maxsplit=1)
        if len(new_name) < 2:
            bot.reply_to(message, "Provide a new group name: /regroup <new_name>")
            return
        
        new_name = new_name[1]
        
        if len(new_name) > 255:
            bot.reply_to(message, "Group name is too long (max 255 characters).")
            return
        
        bot.set_chat_title(message.chat.id, new_name)
        log_action(
            chat_id=message.chat.id,
            action="renamegroup",
            executor=message.from_user,
            target=message.chat,
            details={"new_name": new_name}
        )
        bot.reply_to(message, f"Group name changed to: {new_name}")
        logger.info(f"group {message.chat.id} renamed to {new_name} by user {message.from_user.id}")
        
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 400:
            bot.reply_to(message, "Invalid group name or bot lacks permission to change it.")
        elif e.error_code == 403:
            bot.reply_to(message, "Bot needs admin privileges to change group name!")
        else:
            bot.reply_to(message, "Failed to change group name.")
        logger.error(f"telegram api error in rename_group: {e}")
    except Exception as e:
        bot.reply_to(message, "An unexpected error occurred.")
        logger.error(f"unexpected error in rename_group: {e}")

@bot.message_handler(regexp=r'^[\/!](add_dis)(?:\s|$|@)')
@is_group
@disabled
@is_admin
@is_allowed
def command_add_description(message):
    try:
        description = message.text.split(maxsplit=1)
        if len(description) < 2:
            bot.reply_to(message, "provide a description: /add_dis <description>")
            return
        
        description = description[1]
        
        if len(description) > 255:
            bot.reply_to(message, "Description is too long (max 255 characters).")
            return
        
        bot.set_chat_description(message.chat.id, description)
        log_action(
            chat_id=message.chat.id,
            action="adddescription",
            executor=message.from_user,
            target=message.chat,
            details={"description": description}
        )
        bot.reply_to(message, "Group description updated successfully!")
        logger.info(f"description updated for group {message.chat.id} by user {message.from_user.id}")
        
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 400:
            bot.reply_to(message, "Invalid description or bot lacks permission to change it.")
        elif e.error_code == 403:
            bot.reply_to(message, "Bot needs admin privileges to change description!")
        else:
            bot.reply_to(message, "Failed to change group description.")
        logger.error(f"telegram api error in add_description: {e}")
    except Exception as e:
        bot.reply_to(message, "An unexpected error occurred.")
        logger.error(f"unexpected error in add_description: {e}")
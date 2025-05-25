import telebot
import json
import os
from functools import wraps
from telebot.types import Message
from config import bot
from kick import disabled
from ban_sticker_pack.ban_sticker_pack import is_admin, is_group

TOPICS_FILE = 'topics.json'

def load_topics():
    if os.path.exists(TOPICS_FILE):
        with open(TOPICS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_topics(topics):
    with open(TOPICS_FILE, 'w') as f:
        json.dump(topics, f, indent=4)

topics = load_topics()


def ensure_group_settings(chat_id: str):
    if chat_id not in topics:
        topics[chat_id] = {
            'action_topic': None,
            'topics': {}
        }
        save_topics(topics)

@bot.message_handler(regexp=r'^[\/!](actiontopic)(?:\s|$|@)')
@disabled
@is_group
def command_action_topic(message: Message):
    chat_id = str(message.chat.id)
    ensure_group_settings(chat_id)
    
    action_topic = topics[chat_id].get('action_topic', None)
    if action_topic:
        bot.reply_to(message, f"The action topic is: {action_topic}")
    else:
        bot.reply_to(message, "No action topic set for this group.")


@bot.message_handler(regexp=r'^[\/!](setactiontopic)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_set_action_topic(message: Message):
    chat_id = str(message.chat.id)
    topic_id = message.message_thread_id
    ensure_group_settings(chat_id)
    
    if topic_id:
        topics[chat_id]['action_topic'] = topic_id
        save_topics(topics)
        bot.reply_to(message, f"Current topic set as the default action topic.")
    else:
        bot.reply_to(message, "This command must be used in a topic.")

@bot.message_handler(regexp=r'^[\/!](newtopic)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_new_topic(message: Message):
    chat_id = str(message.chat.id)
    ensure_group_settings(chat_id)
    
    try:
        topic_name = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Please provide a topic name: /newtopic <name>")
        return
    
    try:
        new_topic = bot.create_forum_topic(chat_id, topic_name)
        topic_id = new_topic.message_thread_id
        topics[chat_id]['topics'][str(topic_id)] = {'name': topic_name, 'closed': False}
        save_topics(topics)
        bot.reply_to(message, f"Topic '{topic_name}' created successfully!")
    except Exception as e:
        bot.reply_to(message, f"Error creating topic: {str(e)}")

@bot.message_handler(regexp=r'^[\/!](renametopic)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_rename_topic(message: Message):
    chat_id = str(message.chat.id)
    topic_id = str(message.message_thread_id)
    ensure_group_settings(chat_id)
    
    try:
        new_name = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Please provide a new topic name: /renametopic <name>")
        return
    
    if topic_id in topics[chat_id]['topics']:
        try:
            bot.edit_forum_topic(chat_id, topic_id, name=new_name)
            topics[chat_id]['topics'][topic_id]['name'] = new_name
            save_topics(topics)
            bot.reply_to(message, f"Topic renamed to '{new_name}'.")
        except Exception as e:
            bot.reply_to(message, f"Error renaming topic: {str(e)}")
    else:
        bot.reply_to(message, "This topic does not exist.")

@bot.message_handler(regexp=r'^[\/!](closetopic)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_close_topic(message: Message):
    chat_id = str(message.chat.id)
    topic_id = str(message.message_thread_id)
    ensure_group_settings(chat_id)
    
    if topic_id in topics[chat_id]['topics']:
        try:
            bot.close_forum_topic(chat_id, topic_id)
            topics[chat_id]['topics'][topic_id]['closed'] = True
            save_topics(topics)
            bot.reply_to(message, "Topic closed successfully.")
        except Exception as e:
            bot.reply_to(message, f"Error closing topic: {str(e)}")
    else:
        bot.reply_to(message, "This topic does not exist.")

@bot.message_handler(regexp=r'^[\/!](reopentopic)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_reopen_topic(message: Message):
    chat_id = str(message.chat.id)
    topic_id = str(message.message_thread_id)
    ensure_group_settings(chat_id)
    
    if topic_id in topics[chat_id]['topics']:
        try:
            bot.reopen_forum_topic(chat_id, topic_id)
            topics[chat_id]['topics'][topic_id]['closed'] = False
            save_topics(topics)
            bot.reply_to(message, "Topic reopened successfully.")
        except Exception as e:
            bot.reply_to(message, f"Error reopening topic: {str(e)}")
    else:
        bot.reply_to(message, "This topic does not exist.")

@bot.message_handler(regexp=r'^[\/!](deletetopic)(?:\s|$|@)')
@disabled
@is_admin
@is_group
def command_delete_topic(message: Message):
    chat_id = str(message.chat.id)
    topic_id = str(message.message_thread_id)
    ensure_group_settings(chat_id)
    
    if topic_id in topics[chat_id]['topics']:
        try:
            bot.delete_forum_topic(chat_id, topic_id)
            del topics[chat_id]['topics'][topic_id]
            if topics[chat_id]['action_topic'] == topic_id:
                topics[chat_id]['action_topic'] = None
            save_topics(topics)
            bot.reply_to(message, "Topic deleted successfully.")
        except Exception as e:
            bot.reply_to(message, f"Error deleting topic: {str(e)}")
    else:
        bot.reply_to(message, "This topic does not exist.")

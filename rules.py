import telebot
import json
import os
from functools import wraps
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot
from kick import disabled

RULES_FILE = "rules.json"


def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)

def is_admin(func):
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        chat_id = str(message.chat.id)
        user_id = message.from_user.id
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status not in ["administrator", "creator"]:
            bot.reply_to(message, "You need to be an admin to use this command!")
            return
        return func(message, *args, **kwargs)
    return wrapped

def initialize_chat(chat_id):
    rules_data = load_rules()
    chat_id = str(chat_id)
    if chat_id not in rules_data:
        rules_data[chat_id] = {
            "rules": "",
            "private_rules": False,
            "rules_button": "Rules",
            "buttons": []
        }
        save_rules(rules_data)
    return rules_data

def parse_buttons(rules_text):
    buttons = []
    pattern = r'\[([^\]]+)\]\(buttonurl://([^\)]+)\)'
    matches = re.findall(pattern, rules_text)
    cleaned_text = re.sub(pattern, '', rules_text).strip()
    
    for text, url in matches:
        buttons.append({"text": text, "url": url})
    
    return cleaned_text, buttons

def create_inline_keyboard(buttons):
    markup = InlineKeyboardMarkup()
    for button in buttons:
        markup.add(InlineKeyboardButton(text=button["text"], url=button["url"]))
    return markup

def display_rules(chat_id, user_id, message=None, noformat=False, is_private=False):
    chat_id = str(chat_id)
    rules_data = load_rules()
    
    if chat_id not in rules_data:
        if message:
            bot.reply_to(message, "No rules set for this chat.")
        else:
            bot.send_message(user_id, "No rules set for this chat.")
        return

    rules_text = rules_data[chat_id]["rules"]
    private_rules = rules_data[chat_id]["private_rules"]
    button_name = rules_data[chat_id]["rules_button"]
    buttons = rules_data[chat_id]["buttons"]

    if not rules_text:
        if message:
            bot.reply_to(message, "No rules set for this chat.")
        else:
            bot.send_message(user_id, "No rules set for this chat.")
        return

    if noformat:
        raw_text, _ = parse_buttons(rules_text)
        if message:
            bot.reply_to(message, raw_text or rules_text)
        else:
            bot.send_message(user_id, raw_text or rules_text)
        return

    display_text, parsed_buttons = parse_buttons(rules_text)
    display_text = display_text or rules_text
    markup = create_inline_keyboard(buttons + parsed_buttons) if (buttons + parsed_buttons) else None

    if private_rules and not is_private:
        private_markup = InlineKeyboardMarkup()
        deep_link = f"t.me/{bot.get_me().username}?start=rules_{chat_id}"
        private_markup.add(InlineKeyboardButton(button_name, url=deep_link))
        if message:
            bot.reply_to(message, "Click the button below to view the rules:", reply_markup=private_markup)
        else:
            bot.send_message(user_id, "Click the button below to view the rules:", reply_markup=private_markup)
    else:
        if message:
            bot.reply_to(message, display_text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)
        else:
            bot.send_message(user_id, display_text, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)

@bot.message_handler(regexp=r'^[\/!](rules)(?:\s|$|@)')
@disabled
def command_rules(message):
    chat_id = str(message.chat.id)
    args = message.text.split()
    noformat = len(args) > 1 and args[1].lower() == "noformat"
    display_rules(chat_id, message.from_user.id, message, noformat)

@bot.message_handler(regexp=r'^[\/!](setrules)(?:\s|$|@)')
@disabled
@is_admin
def command_set_rules(message):
    chat_id = str(message.chat.id)
    rules_data = initialize_chat(chat_id)
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Please provide the rules text. Usage: /setrules <text>")
        return

    rules_text = args[1]
    _, buttons = parse_buttons(rules_text)
    rules_data[chat_id]["rules"] = rules_text
    rules_data[chat_id]["buttons"] = buttons
    save_rules(rules_data)
    deep_link = f"t.me/{bot.get_me().username}?start=rules_{chat_id}"
    bot.reply_to(message, f"Rules updated successfully! Share rules with this deep link: {deep_link}")

@bot.message_handler(regexp=r'^[\/!](privaterules)(?:\s|$|@)')
@disabled
@is_admin
def command_private_rules(message):
    chat_id = str(message.chat.id)
    rules_data = initialize_chat(chat_id)
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1].lower() not in ["yes", "no", "on", "off"]:
        bot.reply_to(message, "Usage: /privaterules <yes/no/on/off>")
        return

    private = args[1].lower() in ["yes", "on"]
    rules_data[chat_id]["private_rules"] = private
    save_rules(rules_data)
    status = "enabled" if private else "disabled"
    bot.reply_to(message, f"Private rules {status}.")

@bot.message_handler(regexp=r'^[\/!](resetrules)(?:\s|$|@)')
@disabled
@is_admin
def command_reset_rules(message):
    chat_id = str(message.chat.id)
    rules_data = initialize_chat(chat_id)
    
    rules_data[chat_id]["rules"] = ""
    rules_data[chat_id]["buttons"] = []
    save_rules(rules_data)
    bot.reply_to(message, "Rules reset to default.")

@bot.message_handler(regexp=r'^[\/!](setrulesbutton)(?:\s|$|@)')
@disabled
@is_admin
def command_set_rules_button(message):
    chat_id = str(message.chat.id)
    rules_data = initialize_chat(chat_id)
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Please provide the button name. Usage: /setrulesbutton <name>")
        return

    button_name = args[1]
    rules_data[chat_id]["rules_button"] = button_name
    save_rules(rules_data)
    bot.reply_to(message, f"Rules button name set to: {button_name}")

@bot.message_handler(regexp=r'^[\/!](resetrulesbutton)(?:\s|$|@)')
@disabled
@is_admin
def command_reset_rules_button(message):
    chat_id = str(message.chat.id)
    rules_data = initialize_chat(chat_id)
    
    rules_data[chat_id]["rules_button"] = "Rules"
    save_rules(rules_data)
    bot.reply_to(message, "Rules button name reset to default.")

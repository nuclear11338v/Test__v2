import telebot
from telebot import types
import json
from functools import wraps
from config import bot

def load_connections():
    try:
        with open('connections.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_connections(connections):
    try:
        with open('connections.json', 'w') as f:
            json.dump(connections, f, indent=4)
    except Exception as e:
        print(f"Error saving connections: {e}")

def is_private(func):
    @wraps(func)
    def wrapper(message: types.Message, *args, **kwargs):
        if message.chat.type != 'private':
            bot.reply_to(message, "This command can only be used in private chats (bot DMs).")
            return
        return func(message, *args, **kwargs)
    return wrapper

def is_user_admin(chat_id: int, user_id: int) -> bool:
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except telebot.apihelper.ApiTelegramException:
        return False

@bot.message_handler(commands=['connect'])
@is_private
def command_connect(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /connect <group_id> (e.g., /connect -100123456789)")
            return
        
        user_id = str(message.from_user.id)
        group_ids = args[1:]
        connections = load_connections()
        
        if user_id not in connections:
            connections[user_id] = []
        
        connected_groups = []
        failed_groups = []
        
        for group_id in group_ids:
            try:
                group_id = group_id.strip()
                if not group_id.startswith('-'):
                    failed_groups.append(group_id)
                    continue
                
                chat_id = int(group_id)
                if not is_user_admin(chat_id, message.from_user.id):
                    failed_groups.append(group_id)
                    continue
                
                if str(chat_id) in connections[user_id]:
                    failed_groups.append(group_id)
                    continue
                
                bot.get_chat(chat_id)
                connections[user_id].append(str(chat_id))
                connected_groups.append(group_id)
            
            except telebot.apihelper.ApiTelegramException as e:
                failed_groups.append(group_id)
            except ValueError:
                failed_groups.append(group_id)
        
        save_connections(connections)
        
        response = ""
        if connected_groups:
            response += f"Successfully connected to: {', '.join(connected_groups)}\n"
        if failed_groups:
            response += f"Failed to connect to: {', '.join(failed_groups)} (check if you are an admin or if the group ID is valid)"
        
        bot.reply_to(message, response.strip() or "No groups connected.")
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['disconnect'])
@is_private
def command_disconnect(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /disconnect <group_id> (e.g., /disconnect -100123456789)")
            return
        
        user_id = str(message.from_user.id)
        group_id = args[1].strip()
        connections = load_connections()
        
        if user_id not in connections or not connections[user_id]:
            bot.reply_to(message, "You have no connected groups.")
            return
        
        if group_id not in connections[user_id]:
            bot.reply_to(message, f"Group {group_id} is not connected.")
            return
        
        connections[user_id].remove(group_id)
        if not connections[user_id]:
            del connections[user_id]
        
        save_connections(connections)
        bot.reply_to(message, f"Successfully disconnected from group {group_id}.")
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['disconnectall'])
@is_private
def command_disconnectall(message: types.Message):
    try:
        user_id = str(message.from_user.id)
        connections = load_connections()
        
        if user_id not in connections or not connections[user_id]:
            bot.reply_to(message, "You have no connected groups.")
            return
        
        del connections[user_id]
        save_connections(connections)
        bot.reply_to(message, "Successfully disconnected from all groups.")
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['reconnect'])
@is_private
def command_reconnect(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /reconnect <group_id> (e.g., /reconnect -100123456789)")
            return
        
        user_id = str(message.from_user.id)
        group_id = args[1].strip()
        connections = load_connections()
        
        if user_id not in connections or not connections[user_id]:
            bot.reply_to(message, "You have no connected groups.")
            return
        
        if group_id not in connections[user_id]:
            bot.reply_to(message, f"Group {group_id} is not connected.")
            return
        
        if not is_user_admin(int(group_id), message.from_user.id):
            connections[user_id].remove(group_id)
            if not connections[user_id]:
                del connections[user_id]
            save_connections(connections)
            bot.reply_to(message, f"Cannot reconnect to {group_id}. You are no longer an admin.")
            return
        
        try:
            bot.get_chat(group_id)
            bot.reply_to(message, f"Successfully reconnected to group {group_id}.")
        except telebot.apihelper.ApiTelegramException:
            connections[user_id].remove(group_id)
            if not connections[user_id]:
                del connections[user_id]
            save_connections(connections)
            bot.reply_to(message, f"Group {group_id} no longer exists or is inaccessible.")
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")

@bot.message_handler(commands=['connection'])
@is_private
def command_connection(message: types.Message):
    try:
        user_id = str(message.from_user.id)
        connections = load_connections()
        
        if user_id not in connections or not connections[user_id]:
            bot.reply_to(message, "You have no connected groups.")
            return
        
        response = "Connected groups:\n"
        for group_id in connections[user_id]:
            try:
                group = bot.get_chat(group_id)
                group_title = group.title or "Unknown Group"
                response += f"- {group_title} ({group_id})\n"
            except telebot.apihelper.ApiTelegramException:
                response += f"- {group_id} (inaccessible)\n"
        
        bot.reply_to(message, response.strip())
    
    except Exception as e:
        bot.reply_to(message, f"Unexpected error: {e}")
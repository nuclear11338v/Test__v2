from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_connection_help():
    """Generate main help menu content"""
    help_menu = """
            📜 <b>Connection Help</b>

     <i>This module allows you to manage your Telegram groups directly from the bot's private messages (PM).</i>
     
<i>Use the following commands to connect, disconnect, and manage your groups. All commands must be used in the bot's private chat.</i>

<b>Available Commands:</b>
<code>/connect [group_id]</code> - <b>Connects the bot to a group where you are an admin.</b>
<blockquote>Example: /connect -100123456789</blockquote>

You can provide multiple group IDs separated by spaces.

<b>Note:</b>
<i>The group ID must start with - (e.g., -100123456789), and you must be an admin in the group./disconnect [group_id] Disconnects the bot from a specific group.</i>

<pre>Example: /disconnect -100123456789</pre> <b>- The group must already be connected.</b>

<code>/disconnectall</code> <b>- Disconnects the bot from all connected groups.</b>

<b>Example:</b>
<code>/disconnectall</code>
<code>/reconnect [group_id]</code>
<b>Reconnects the bot to a group to verify access.</b>

<pre>Example: /reconnect -100123456789</pre> - <b>Checks if the group is still accessible and if you are an admin.</b>
Disconnects if the group is inaccessible or you are no longer an admin.

<code>/connectionLists</code> -<b> all groups currently connected to your account.</b>

<pre>Example: /connection</pre> <b>- Displays group titles and IDs, or notes if a group is inaccessible.</b>

<b>Important Notes:</b>
<i>All commands work only in private chats with the bot.You must be an admin in the group to connect or reconnect.</i>

Group IDs can be found by adding this bot to the group and type /id.
    """
    
    buttons = [
        ("Close", "connection_close"),
        ("Back", "connection_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('connection_'))
def handle_help_callback(call):
    try:
        if call.data == 'connection_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'connection_back':
            text, markup = create_english_help()
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML',
                reply_markup=markup
            )
            return

        bot.answer_callback_query(call.id, "⏳ Section under development!", show_alert=True)

    except Exception as e:
        logger.error(f"Callback error: {str(e)}\n{traceback.format_exc()}")
        try:
            bot.answer_callback_query(call.id, f"Error in Callback.\nPlease try again.", show_alert=True)
        except Exception as e:
            logger.error(f"Failed to answer callback: {str(e)}")
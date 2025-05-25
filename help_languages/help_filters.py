from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_filters_help():
    """Generate main help menu content"""
    help_menu = """
<b>Filters Module Help</b>

<i>The Filters module allows admins to set triggers that automatically respond with predefined messages or media when specific words or phrases are detected in chats.</i>

<b>Available Commands</b>
<code>/filter [trigger(s)] [response]</code>
<b>Purpose:</b> Adds one or more triggers with a response.
 
<b>Usage:</b> <code>/filter [trigger] [response]</code> <b>Triggers can be single words or quoted phrases.</b>
<i>Multiple triggers can be separated by spaces or quotes.</i>
 
<blockquote>Responses support HTML.</blockquote>
 
<b>Example:</b>
<code>/filter hello Hi there!</code> - <b>Responds to "hello" with "Hi there!".</b>
<code>/filter "good morning" Good day! [Visit](buttonurl://https://google.com)</code> - <b>Responds to "good morning" with a button.</b>
 
<blockquote>/filters</blockquote>
<b>Purpose:</b> Lists all active filters in the group.

<blockquote>/stop</blockquote>
<b>Purpose:</b> Removes a specific filter trigger.
<b>Usage:</b> <code>/stop</code>
<b>Example:</b>
<code>/stop hello</code> - <b>Removes the "hello" filter.</b>

<blockquote>/stopall</blockquote>
<b>Purpose:</b> Removes all filters in the group.
<b>Usage:</b> <code>/stopall</code>
<b>Example:</b>
<code>/stopall</code> - <b>Clears all filters.</b>


<b>Example Workflow</b>
<b>Add filter:</b> <code>/filter hello 👋</code> - <b>Sets response for "hello".</b>
<b>List filters:</b> <code>/filters</code> - <b>Shows all triggers.</b>
<b>Remove filter:</b> <code>/stop hello</code> - <b>Removes "hello" filter.</b>
<b>Clear all:</b> <code>/stopall</code> - <b>Removes all filters.</b>
    """
    
    buttons = [
        ("Close", "filters_close"),
        ("Back", "filters_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('filters_'))
def handle_help_callback(call):
    try:
        if call.data == 'filters_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'filters_back':
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
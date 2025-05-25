from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_cleanservice_help():
    """Generate main help menu content"""
    help_menu = """
            📜 <b>Cleanservice Help</b>

<code>/cleanservice</code> [service]
<code>/cleanservicetypes</code> <b>check the service types</b>
<code>/keepservice</code> [service]
<b>Available service message types:</b>

• <b>all:</b> <i>All service messages</i>
• <b>other:</b> <i>Miscellaneous (boosts, payments, etc.)</i>
• <b>photo:</b> <i>Chat photo/background changes</i>
• <b>pin:</b> <i>Message pinning</i>
• <b>title:</b> <i>Chat/topic title changes</i>
• <b>videochat:</b> <i>Video chat actions</i>
    """
    
    buttons = [
        ("Close", "cleanservice_close"),
        ("Back", "cleanservice_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('cleanservice_'))
def handle_help_callback(call):
    try:
        if call.data == 'cleanservice_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'cleanservice_back':
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
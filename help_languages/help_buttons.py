from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_buttons_help():
    """Generate main help menu content"""
    help_menu = """
    <b>📚 Hᴇʟᴘ Mᴇɴᴜ</b>

    ├── 🔹 Hey im MrsKira
    │   │
    │   ├ 𝘾𝙃𝙊𝙊𝙎𝙀 𝙊𝙋𝙏𝙄𝙊𝙉𝙎
    │   ├ 𝙁𝙄𝙍𝙎𝙏 𝙐 𝙉𝙀𝙀𝘿 𝙏𝙊 𝘼𝘿𝘿 𝙈𝙀 𝙏𝙊 𝘼 𝙂𝙍𝙊𝙐𝙋
    │   └ 𝙄𝙉𝙅𝙊𝙔 𝘽𝘼𝘽𝙔 𝙐𝙎𝙄𝙉𝙂 𝙏𝙃𝙄𝙎 𝘽𝙊𝙏 :)
    │
    ├── 🔹Sᴜᴘᴘᴏʀᴛ
    │   ├ /help - Sнow Tнιs Mᴇɴu
    │   ├ /ping - Cнᴇcκ Sʏsтᴇм
    │   └ /start - Sтᴀʀт Tнᴇ Boт
    └──
    """
    
    buttons = [
        ("˹ 𝗰ʟ𝗼𝘀ᴇ ✘ ˼", "buttons_close"),
        ("Back", "buttons_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('buttons_'))
def handle_help_callback(call):
    try:
        if call.data == 'buttons_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'buttons_back':
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
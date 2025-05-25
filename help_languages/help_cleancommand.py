from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_cleancommand_help():
    """Generate main help menu content"""
    help_menu = """
<b>Cleancommand Module Help</b>

<i>The Cleancommand module allows admins to configure automatic deletion or retention of command messages in chats based on the sender's status (admin, user, or all).</i>

<b>Available Commands</b>
<blockquote>/cleancommandtypes</blockquote>

<b>Purpose:</b> <i>Lists valid types for /cleancommand and /keepcommand.</i>
<b>Usage:</b> <code>/cleancommandtypes</code>

<blockquote>/cleancommand [admin|user|all]</blockquote>
<b>Purpose:</b> Sets the type of command messages to delete automatically.
<b>Usage:</b> <code>/cleancommand [admin|user|all]</code>

<b>- admin:</b> <i>Deletes commands sent by admins.</i>
<b>- user:</b> <i>Deletes commands sent by non-admins.</i>
<b>- all:</b> <i>Deletes all command messages.</i>

<b>Example:</b>
<code>/cleancommand user</code> - <b>Deletes non-admin command messages.</b>
<code>/cleancommand all</code> - <b>Deletes all command messages.</b>

<blockquote>/keepcommand [admin|user|all]</blockquote>
<b>Purpose:</b> <i>Sets the type of command messages to keep (overrides /cleancommand).</i>
<b>Usage:</b> <code>/keepcommand [admin|user|all]</code>

<b>Example:</b>
<code>/keepcommand admin</code> - <b>Keeps admin command messages.</b>
<code>/keepcommand all</code> - <b>Keeps all command messages.</b>

<b>Important Notes</b>
<b>Enforcement:</b>
Command messages (starting with /) are checked for deletion.
<code>/cleancommand</code> <b>sets which messages to delete; /keepcommand sets exceptions.</b>
<b>Example:</b> If <code>/cleancommand all</code> and <code>/keepcommand admin</code>, all commands are deleted except those from admins.

<b>Example Workflow</b>
<b>List types:</b> <code>/cleancommandtypes</code> - <b>Shows valid options.</b>
<b>Set deletion:</b> <code>/cleancommand user</code> - <b>Deletes non-admin commands.</b>
<b>Set retention:</b> <code>/keepcommand admin</code> - <b>Keeps admin commands.</b>
<b>Adjust settings:</b> <code>/cleancommand all</code> - <b>Deletes all commands, but admin commands remain due to <code>/keepcommand</code>.</b>
    """
    
    buttons = [
        ("Close", "cleancommand_close"),
        ("Back", "cleancommand_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('cleancommand_'))
def handle_help_callback(call):
    try:
        if call.data == 'cleancommand_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'cleancommand_back':
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
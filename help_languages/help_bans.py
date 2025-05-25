from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_bans_help():
    """Generate main help menu content"""
    help_menu = """
<b>Bans Module Help</b>

<i>The Bans module enables admins to manage user bans in chats, including permanent, temporary, silent, and random-duration bans, as well as unbanning and self-banning.</i>

<b>Available Commands</b>
<code>/ban [user_id | reply] [reason]</code>
<b>Purpose:</b> Permanently bans a user from the group.

<b>Example:</b>
<code>/ban 27736544 Spam</code> - <b>Bans user with reason.</b>
<code>/ban (reply)</code> - <b>Bans replied user.</b>

<code>/sban [user_id | reply] [reason]</code>
<b>Purpose:</b> <i>Silently bans a user and deletes the command and replied messages.</i>

<b>Example:</b>
<code>/sban 1727365</code> - <b>Silently bans user.</b>
<code>/sban (reply) Spam</code> - <b>Bans and deletes messages.</b>

<code>/tban [user_id | reply] [reason]</code>
<b>Purpose:</b> <i>Temporarily bans a user for a specified duration.</i>
<b>Usage:</b> <code>/tban [user_id | reply] [reason]</code>
<b>Duration format:</b> [number][s|m|h|d|w] (seconds, minutes, hours, days, weeks).
<b>Max duration:</b> 366 days.

<b>Example:</b>
<code>/tban 272636 Spam 1h</code> - <b>Bans for 1 hour.</b>
<code>/tban (reply) 30m</code> - <b>Bans for 30 minutes.</b>

<blockquote>/dban [reply] [reason]</blockquote>
<b>Purpose:</b> <i>Bans a user and deletes their replied message.</i>
<b>Usage:</b> <code>/dban [reply] [reason]</code>

<b>Example:</b>
<code>/dban (reply) Spam</code> - <b>Bans and deletes message.</b>

<blockquote>/rban [user_id | reply] [reason]</blockquote>
<b>Purpose:</b> <i>Bans a user for a random duration (1 minute to 1 week).</i>
<b>Usage:</b> <code>/rban [user_id | reply] [reason]</code>

<b>Example:</b>
<code>/rban 34543223</code> - <b>Bans for random duration.</b>
<code>/rban (reply) Spam</code> - <b>Bans with reason.</b>

<blockquote>/unban [user_id | reply] [reason]</blockquote>
<b>Purpose:</b> <i>Unbans a user from the group.</i>
<b>Usage:</b> <code>/unban [user_id | reply] [reason]</code>
Example:
<code>/unban 2726383 Mistake</code> - <b>Unbans with reason.</b>
<code>/unban 123456</code> - <b>Unbans user.</b>

<blockquote>/banme [reason]</blockquote>
<b>Purpose:</b> Allows a user to ban themselves from the group.
<b>Usage:</b> <code>/banme [reason]</code>
<b>Example:</b>
<code>/banme I need a break</code> - <b>Self-bans with reason.</b>

<b>Example Workflow</b>
<b>Ban user:</b> <code>/ban 12345678 Spam</code> - <b>Permanently bans with reason.</b>
<b>Silent ban:</b> <code>/sban</code> (reply) - <b>Bans and deletes messages discreetly.</b>
<b>Temp ban:</b> <code>/tban 1734637 Flood 2h</code> - <b>Bans for 2 hours.</b>
<b>Delete and ban:</b> <code>/dban</code> (reply) - <b>Bans and deletes replied message.</b>
<b>Random ban:</b> <code>/rban 1733636</code> - <b>Bans for random duration.</b>
<b>Unban user:</b> <code>/unban 7272636 Mistake</code> - <b>Unbans with reason.</b>
<b>Self-ban:</b> <code>/banme Taking a break</code> - <b>User bans themselves.</b>
    """
    
    buttons = [
        ("Close", "bans_close"),
        ("Back", "bans_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('bans_'))
def handle_help_callback(call):
    try:
        if call.data == 'bans_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'bans_back':
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
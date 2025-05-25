from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_warns_help():
    """Generate main help menu content"""
    help_menu = """
<b>Warns Module Help</b>

<i>The Warns module enables admins to manage user warnings in chats, with configurable limits, modes, and durations.</i>

<b>Available Commands</b>
<code>/warn [user_id | @username | reply] [reason]</code>
<b>Purpose:</b> Issues a warning to a user with an optional reason.
<b>Usage:</b> <code>/warn [user_id | @username | reply] [reason]</code>

<b>Example:</b>
<code>/warn @username Spam</code> - <b>Warns user with reason.</b>
<code>/warn (reply) Flooding</code> - <b>Warns replied user.</b>

<code>/swarn [user_id | @username | reply] [reason]</code>
<b>Purpose:</b> Silently issues a warning and deletes the command message.
<b>Usage:</b> <code>/swarn [user_id | @username | reply] [reason]</code>

<b>Example:</b>
<code>/swarn @username Spam</code> - <b>Silently warns user.</b>
<code>/swarn</code> (reply) - <b>Silently warns replied user.</b>

<code>/dwarn [user_id | @username | reply] [reason]</code>
<b>Purpose:</b> Issues a warning and deletes the replied message (if applicable).
<b>Usage:</b> <code>/dwarn [user_id | @username | reply] [reason]</code>

<b>Example:</b>
<code>/dwarn <b>(reply)</b> Spam</code> - <b>Warns and deletes replied message.</b>
<code>/dwarn @username Flood</code> - <b>Warns user.</b>

<code>/rmwarn [user_id | @username | reply]</code>
<b>Purpose:</b> <i>Removes one warning from a user.</i>
<b>Usage:</b> <code>/rmwarn [user_id | @username | reply]</code>

<b>Example:</b>
<code>/rmwarn @username</code> - <b>Removes one warning.</b>
<code>/rmwarn <b>(reply)</b></code> - <b>Removes one warning from replied user.</b>

<code>/resetwarn [user_id | @username | reply]</code>
<b>Purpose:</b> <i>Resets all warnings for a user.</i>
<b>Usage:</b> <code>/resetwarn [user_id | @username | reply]</code>

<b>Example:</b>
<code>/resetwarn @username</code> - <b>Clears all warnings.</b>
<code>/resetwarn <b>(reply)</b></code> - <b>Clears warnings for replied user.</b>

<blockquote>/resetallwarnings</blockquote>
<b>Purpose:</b> <i>Resets all warnings for all users in the chat.</i>
<b>Usage:</b> <code>/resetallwarnings</code>

<b>Example:</b>
<code>/resetallwarnings</code> - <b>Clears all warnings in the group.</b>

<blockquote>/warnings</blockquote>
<b>Purpose:</b> <i>Displays current warning settings (limit, mode, time).</i>

<blockquote>/warningmode [ban|mute|kick]</blockquote>
<b>Purpose:</b> <i>Sets the action when the warn limit is reached.</i>
<b>Usage:</b> <code>/warningmode [ban|mute|kick]</code>
<b>ban:</b> Permanently bans the user.
<b>mute:</b> Mutes for the warn time duration.
<b>kick:</b> Kicks (bans then unbans).

<b>Example:</b>
<code>/warningmode ban</code> - <b>Sets ban as the action.</b>

<blockquote>/warnlimit</blockquote>
<b>Purpose:</b> Sets the maximum number of warnings before action.
<b>Usage:</b> <code>/warnlimit</code>

<b>Example:</b>
<code>/warnlimit 5</code> - <b>Sets warn limit to 5.</b>

<code>/warntime [time]</code>
<b>Purpose:</b> Sets the duration for warnings and mute actions.
<b>Usage:</b> <code>/warntime [time]</code>
<b>Time format:</b> [number][s|m|h|d|w|mo|y] (seconds, minutes, hours, days, weeks, months, years).

<b>Example:</b>
<code>/warntime 2h</code> - <b>Sets warn/mute duration to 2 hours.</b>
<code>/warntime</code> - <b>Shows current warn time.</b>

<b>Example Workflow</b>
<b>Configure settings:</b> <code>/warnlimit 4</code>, <code>/warningmode ban</code>, <code>/warntime 1d</code> - <b>Sets limit to 4, action to ban, duration to 1 day.</b>

<b>Warn user:</b> <code>/warn @username Spam</code> - <b>Issues warning (1/4).</b>
<b>Silent warn:</b> <code>/swarn (reply) Flood</code> - <b>Warns silently, deletes command.</b>
<b>Delete and warn:</b> <code>/dwarn (reply)</code> - <b>Warns and deletes message.</b>
<b>Remove warning:</b> <code>/rmwarn @username</code> - <b>Reduces count to 0/4.</b>
<b>Reset warnings:</b> <code>/resetwarn @username</code> - <b>Clears all warnings.</b>
<b>Reset all:</b> <code>/resetallwarnings</code> - <b>Clears all warnings in chat.</b>
<b>Check settings:</b> <code>/warnings</code> - <b>Shows current configuration.</b>
    """
    
    buttons = [
        ("Close", "warns_close"),
        ("Back", "warns_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('warns_'))
def handle_help_callback(call):
    try:
        if call.data == 'warns_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'warns_back':
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
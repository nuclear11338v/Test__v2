from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_admins_help():
    """Generate main help menu content"""
    help_menu = """
<b>Admins Module Help</b>

<i>This module help group--admins to Promote/Demote users</i>

<b>Available Commands</b>
<code>/promote [user_id|reply] [title] [duration]</code>
<b>Purpose:</b> <i>Promotes a user to admin with specified permissions and optional title/duration.</i>
<b>Usage:</b> <code>/promote [user_id|reply] [title] [duration]</code>
<i>User can be specified by ID, username, or replying to their message.</i>

<b>Title:</b> Optional custom admin title (max 16 characters).
<b>Duration:</b> Optional temporary promotion (e.g., 30m, 2h, 1d).

<b>Example:</b>
<code>/promote 123456 Moderator 1d</code> - <b>Promotes user with title for 1 day.</b>
<code>/promote (reply)</code> - <b>Promotes replied user.</b>

<code>/demote [user_id|reply]</code>
<b>Purpose:</b> <i>Demotes an admin, removing all admin permissions.</i>
<b>Usage:</b> <code>/demote [user_id|reply]</code>
<i>User can be specified by ID, username, or replying to their message.</i>

<b>Example:</b>
<code>/demote 1234561</code> - <b>Demotes replied user.</b>

<blockquote>/adminlist</blockquote>
<b>Purpose:</b> <i>Lists all admins in the group.
Usage: /adminlist</i>

<b>Refreshes admin cache</b>
<blockquote>/admincache</blockquote>
<b>Purpose:</b> <i>Manually refreshes the admin cache for the group.</i>
<b>Usage:</b> <code>/admincache</code>
<b>Example:</b>
<code>/admincache</code> - <b>Updates cached admin list.</b>

<blockquote>/adminerror [yes/no/on/off]</blockquote>
<b>Purpose:</b> <i>Enables/disables admin error messages for failed actions.</i>
<b>Usage:</b> <code>/adminerror [yes/no/on/off]</code>.

<b>Example Workflow</b>
<b>Promote user:</b> <code>/promote 123412 Moderator</code> - <b>Promotes with title.</b>
<b>Demote user:</b> <code>/demote 123412</code> - <b>Removes admin status.</b>
<b>List admins:</b> <code>/adminlist</code> - <b>Shows all admins.</b>
<b>Refresh cache:</b> <code>/admincache</code> - <b>Updates admin list.</b>
    """
    
    buttons = [
        ("˹ 𝗰ʟ𝗼𝘀ᴇ ✘ ˼", "admins_close"),
        ("Back", "admins_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('admins_'))
def handle_help_callback(call):
    try:
        if call.data == 'admins_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'admins_back':
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
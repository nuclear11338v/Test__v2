from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_Forward_help():
    """Generate main help menu content"""
    help_menu = """
            📜 <b>Help Message for Ban Forward Module</b>

<i>The Ban Forward module allows group admins to control forwarded messages in their Telegram group by automatically restricting users who forward messages from other users, chats, or anonymous sources. Admins can enable permanent or temporary bans, choose the restriction type (ban, kick, or mute), and set durations for temporary restrictions. All commands must be used in the group chat by group admins.</i>

<b>Available Commands:</b>

1. <code>/ban_forward [on/off/True/False/yes/no]</code> 
   - Enables or disables permanent restrictions for users who forward messages.  
   - <b>Usage</b>:  
     - <code>/ban_forward</code> - <b>Shows the current status of forward ban (on/off).</b>
     - <code>/ban_forward on</code> - <b>Enables forward ban, applying the set action (see /ban_forward_action) to users who forward messages.</b>
     - <code>/ban_forward off</code> - <b>Disables forward ban.</b>
   - <pre>Example: /ban_forward on</pre> <b>(Enables forward ban with the configured action).</b>

2. <code>/tban_forward [on/off/True/False/yes/no]</code>
   - Enables or disables temporary restrictions for users who forward messages.  
   - <b>Usage</b>:
     - <code>/tban_forward</code> - <b>Shows the current status of temporary forward ban (on/off).</b>
     - <code>/tban_forward on</code> - <b>Enables temporary forward ban, applying a temporary version of the set action (e.g., tban or tmute) for a set duration (default: 24 hours).</b>  
     - <code>/tban_forward off</code> - <b>Disables temporary forward ban.</b>
   - <pre>Example: /tban_forward on</pre><b>(Enables temporary restrictions for forwarded messages).</b>

3. <code>/ban_forward_action [ban/kick/mute]</code>
   - Sets or checks the action taken against users who forward messages when /ban_forward or /tban_forward is enabled.  
   - <b>Usage</b>:  
     - <code>/ban_forward_action</code> - <b>Shows the current action (ban, kick, or mute).</b>
     - <code>/ban_forward_action ban</code>- <b>Sets the action to permanently ban the user.</b>
     - <code>/ban_forward_action kick</code> - <b>Sets the action to kick the user (ban and immediately unban).</b>
     - <code>/ban_forward_action mute</code> - <b>Sets the action to mute the user (prevent sending messages).</b>
   - For /tban_forward, ban becomes tban and mute becomes tmute, applying the action temporarily for the set duration.  
   - <pre>Example: /ban_forward_action mute</pre> <b>(Sets the action to mute users who forward messages).</b>

<i>Important Notes:</i>
<b>- Forward Ban:</b> When enabled (/ban_forward on), users who forward messages are permanently restricted based on the set action (ban , kick , or mute). The forwarded message is deleted, and a notification is sent to the group.

<b>Temporary Forward Ban:</b>
When enabled (/tban_forward on), restrictions are temporary, with a default duration of 24 hours. Use tban for temporary bans or tmute for temporary mutes.

<b>Example Workflow:</b>
1. <b>Set the action:</b> <i>/ban_forward_action mute (Users will be muted for forwarding).</i>
2. <b>Enable forward ban:</b> <i>/ban_forward on (Permanent mute for forwarding messages).</i> 
3. <b>Or enable temporary ban</b>: <i>/tban_forward on (Temporary mute for 24 hours).</i>
4. <blockquote>Check status: /ban_forward or /tban_forward.</blockquote>
    """
    
    buttons = [
        ("Close", "Forward_close"),
        ("Back", "Forward_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('Forward_'))
def handle_help_callback(call):
    try:
        if call.data == 'Forward_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'Forward_back':
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
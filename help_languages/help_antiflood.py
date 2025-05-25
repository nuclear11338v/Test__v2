from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_antiflood_help():
    """Generate main help menu content"""
    help_menu = """
<b>Help for Antiflood Module</b>

<i>The Antiflood module prevents message flooding in groups by limiting how many messages a user can send consecutively or within a time period.</i>
<i>Admins can set the message limit, time-based restrictions, actions (ban, mute, kick, temporary ban/mute), and whether to delete flood messages.</i>

<b>Available Commands</b>

<pre>/flood</pre>
<b>Purpose:</b> <i>Displays current antiflood settings.</i>

<b>Usage:</b> <code>/flood</code>
<b>Output:</b> <i>Shows consecutive message limit, timed flood settings, action, and message deletion status.</i>

<pre>/setflood [number/off]</pre>
<b>Purpose:</b> <i>Sets or disables the consecutive message limit.</i>

<b>Usage:</b>
<code>/setflood [number]</code> - <b>Sets limit (e.g., 5 messages).</b>
<code>/setflood off</code> - <b>Disables consecutive flood detection.</b>

<b>Example:</b>
<code>/setflood 5</code> - <b>Triggers after 5 consecutive messages.</b>
<code>/setflood off</code> - <b>Turns off consecutive flood checks.</b>

<b>Note:</b>
<i>Non-negative numbers only.</i>
<code>/setfloodtimer  /off</code>
<b>Purpose</b>: <i>Sets or disables timed flood detection.</i>

<b>Usage:</b>
<code>/setfloodtimer [count] [duration]</code> - <b>Sets limit (e.g., 10 messages in 30 seconds).</b>
<code>/setfloodtimer off</code> - <b>Disables timed flood detection.</b>

<b>Duration Format:</b> 30s (seconds), 5m (minutes), 3h (hours), 1d (days).

<b>Example:</b>
<code>/setfloodtimer 10 30s</code> - <b>Triggers if 10 messages are sent in 30 seconds.</b>
<code>/setfloodtimer off</code> - <b>Disables timed checks.</b>

<b>Note:</b>
<i>Count must be positive; duration must be valid.</i>
<pre>/floodmode [ban/mute/kick/tban/tmute] [duration]</pre>

<b>Purpose</b>: <i>Sets the action for flood violations.</i>

<b>Usage:</b>
<code>/floodmode [action]</code> - <b>Sets action (ban, mute, kick).</b>
<code>/floodmode [tban/tmute] [duration]</code> - <b>Sets temporary action with duration.</b>

<b>Duration Format:</b> 30s, 5m, 3h, 1d.

<b>Example:</b>
<code>/floodmode mute</code> - <b>Mutes flooders indefinitely.</b>
<code>/floodmode tban 1d</code> - <b>Bans flooders for 1 day.Note: Duration required for tban or tmute.</b>
<pre>/clearflood [yes/no/on/off]</pre>

<b>Purpose:</b>
Enables/disables deletion of flood messages.

<b>Usage:</b>
<code>/clearflood yes/on</code> - <b>Deletes flood messages.</b>
<code>/clearflood no/off</code> - <b>Keeps flood messages.</b>

<b>Example:</b>
<code>/clearflood yes</code> - <b>Deletes messages that trigger flood actions.</b>
<code>/clearflood no</code> - <b>Leaves flood messages in chat.</b>

<b>Important Notes</b>
<b>Flood Detection</b>: Consecutive: Limits how many messages a user can send in a row.
<b>Timed</b>: Limits messages within a time window (e.g., 10 in 30 seconds).

<b>Actions:</b>
<b>ban:</b> Permanent ban.
<b>mute:</b> Mute user.
<b>kick:</b> Kick user from group.
tban/tmute: Temporary ban/mute for specified duration.

<b>Message Deletion</b>: If /clearflood is enabled, flood messages are deleted.

<b>Example WorkflowView settings:</b>
<code>/flood</code> - <b>Check current antiflood configuration.</b>
<i>Set consecutive limit:</i> <code>/setflood 5</code> - <b>Trigger after 5 messages.</b>
<i>Set timed limit</i>: <code>/setfloodtimer 10 30s</code> - <b>Trigger if 10 messages in 30 seconds.</b>
<i>Set action:</i> <code>/floodmode tban 1h</code> - <b>Ban flooders for 1 hour.</b>
<i>Enable deletion:</i> <code>/clearflood yes</code> - <b>Delete flood messages.</b>
<i>Disable antiflood:</i> <code>/setflood off</code> and <code>/setfloodtimer off</code> - <b>Turn off checks.</b>
<b>TroubleshootingFlood Not Triggering:</b> Verify flood_limit or timed_flood settings with /flood.

Messages Not Deleted: Ensure /clearflood is on and bot has can_delete_messages.
    """
    
    buttons = [
        ("Close", "antiflood_close"),
        ("Back", "antiflood_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('antiflood_'))
def handle_help_callback(call):
    try:
        if call.data == 'antiflood_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'antiflood_back':
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
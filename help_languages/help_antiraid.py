from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_antiraid_help():
    """Generate main help menu content"""
    help_menu = """
            📜 <b>Antiraid Help</b>

  <i>The AntiRaid module helps protect your  group from sudden influxes of new members, which could indicate a raid or spam attack. This module allows group admins to enable manual or automatic AntiRaid protection, set ban durations, and configure triggers for automatic detection.</i>

      <b>Available Commands:</b>

1. <code>/antiraid</code> <b>[duration/off]</b>
   - Enables or disables AntiRaid protection manually.  
   - <b>Usage:</b>
     - <code>/antiraid</code> - <b>Toggles AntiRaid on/off (default duration: 6 hours).</b>
     - <code>/antiraid 3h</code> - Enables AntiRaid for a specific duration (e.g., 3 hours). Use formats like <code>30m</code> (minutes), <code>3h</code> (hours), or <code>1d</code> (days).
     - <code>/antiraid off</code> - <b>Disables AntiRaid immediately.</b>
   - When enabled, new members are temporarily banned for the set ban duration (see <code>/raidactiontime</code>).  
   - Example: <code>/antiraid 2h</code> <b>(Enables AntiRaid for 2 hours).</b>

2. <code>/raidtime [duration]</code>
   - Sets or checks the duration for which AntiRaid remains active when enabled.  
   - <b>Usage</b>:  
     - <code>/raidtime</code> - <b>Shows the current AntiRaid duration.</b>  
     - <code>/raidtime 4h</code> - <b>Sets AntiRaid duration to 4 hours</b> (use <code>m</code>, h, or <code>d</code> for minutes, hours, or days).  
   - Example: <code>/raidtime 1d</code> (Sets AntiRaid to stay active for 1 day).

3. <code>/raidactiontime [duration]</code>
   - Sets or checks the duration for which new members are banned during an active AntiRaid.  
   - <b>Usage</b>:  
     - <code>/raidactiontime</code> - Shows the current ban duration.  
     - <code>/raidactiontime 1h</code> - Sets the ban duration to 1 hour (use <code>m</code>, <code>h</code>, or <code>d</code>).  
   - Example: <code>/raidactiontime 30m</code> (Bans new members for 30 minutes during AntiRaid).

4. <code>/autoantiraid [number/off]</code>
   - Configures automatic AntiRaid triggering based on the number of new members joining within a minute.  
   - <b>Usage</b>:  
     - <code>/autoantiraid</code> - <b>Shows the current AutoAntiRaid setting.</b>
     - <code>/autoantiraid 10</code> - <b>Triggers AntiRaid automatically if 10 or more users join in one minute.</b>
     - <code>/autoantiraid off</code> - <b>Disables AutoAntiRaid.</b>  
   - When triggered, AntiRaid enables for the duration set by <code>/raidtime</code>.  
   - Example: <code>/autoantiraid 5</code> (Triggers AntiRaid if 5 users join in a minute).

<b>Important Notes:</b>
- <b>AntiRaid</b>: <i>When active, temporarily bans new members to prevent raids. Bans are lifted after the ban duration expires</i> (set by <code>/raidactiontime</code>).
- <b>AutoAntiRaid</b>: Monitors join rates and automatically enables AntiRaid if the threshold is exceeded.
- AntiRaid automatically disables after the set duration (<code>/raidtime</code>) expires, and a notification is sent to the group.
- Ensure time formats are valid (e.g., <code>30m</code>, <code>2h</code>, <code>1d</code>). Invalid formats will result in an error.

<b>Example Workflow:</b>
1. Set AntiRaid duration: <code>/raidtime 6h</code>
2. Set ban duration: <code>/raidactiontime 1h</code>
3. Enable AutoAntiRaid: <code>/autoantiraid 8</code> (triggers if 8 users join in a minute)
4. Or manually enable: <code>/antiraid 3h</code> (enables AntiRaid for 3 hours)
    """
    
    buttons = [
        ("Close", "antiraid_close"),
        ("Back", "antiraid_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('antiraid_'))
def handle_help_callback(call):
    try:
        if call.data == 'antiraid_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'antiraid_back':
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
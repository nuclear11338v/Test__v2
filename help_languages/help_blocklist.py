from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_blocklist_help():
    """Generate main help menu content"""
    help_menu = """
<b>Blocklist Module Help</b>

<i>The Blocklist module blocks specific content in groups based on trigger patterns. Admins can add triggers with reasons, set actions (e.g., ban, mute, kick), and choose to delete offending messages.</i>

<b>Available Commands:</b>
<code>/addblocklist [text] [reason]</code>
<b>Purpose:</b> Adds a trigger pattern with a reason to the blocklist.

<b>Usage:</b> <code>//blocklist</code>  Use quotes for multi-word triggers: <i>"bad phrase".</i>
<b>Supports wildcards:</b> * (non-whitespace), ** (any characters), ? (single character).

<b>Example:</b>
<code>/addblocklist spam* Spamming detected</code> - <b>Blocks words starting with "spam".</b>
<code>/addblocklist "bad word" Inappropriate language</code> - <b>Blocks exact phrase.</b>

<code>/rmblocklist</code>
<b>Purpose:</b> Removes a specific trigger from the blocklist.
<b>Usage:</b> <code>/rmblocklist</code>
<b>Example:</b>
<code>/rmblocklist spam*</code> - <b>Removes "spam*" trigger.</b>

<code>/unblocklistall</code>
<b>Purpose:</b> Removes all triggers from the blocklist.
<b>Usage:</b> <code>/unblocklistall</code>
<b>Example:</b>
<code>/unblocklistall</code> - <b>Clears all triggers.</b>
<b>Note:</b> Chat creator only.

<code>/blocklist</code>
<b>Purpose:</b> Lists all triggers, action mode, deletion setting, and reason.
<b>Usage:</b> <code>/blocklist</code>

<code>/blocklistmode</code>
<b>Purpose</b>: Sets the action for blocked content.
<b>Usage:</b> /blocklistmode
<b>Modes:</b> nothing, ban, mute, kick, warn, tban, tmute.
<b>Example:</b>
<code>/blocklistmode ban</code> - <b>Bans users for blocked content.</b>
<code>/blocklistmode nothing</code> - <b>No action, may still delete messages.</b>

<code>/blocklistdelete [yes/no/on/off]</code>
<b>Purpose:</b> Enables/disables deletion of blocked messages.
<b>Usage:</b> <code>/blocklistdelete [yes/no/on/off]</code>
<b>Example:</b>
<code>/blocklistdelete yes</code> - <b>Deletes blocked messages.</b>
<code>/blocklistdelete no</code> - <b>Keeps blocked messages.</b>

<code>/setblocklistreason</code>
<b>Purpose:</b> Sets the default reason for blocklist actions.
<b>Usage:</b> <code>/setblocklistreason</code>
<b>Example:</b>
<code>/setblocklistreason Policy violation</code> - <b>Sets default reason.</b>

<code>/resetblocklistreason</code>
<b>Purpose:</b> Resets the default reason to <i>"Blocked content detected"</i>.
<b>Usage:</b> <code>/resetblocklistreason</code>
<b>Example:</b>
<code>/resetblocklistreason</code> - <b>Resets default reason.</b>

<b>Example Workflow</b>
<b>Add trigger:</b> <code>/addblocklist spam* Spamming detected</code> - <b>Blocks "spam" variants.</b>
<b>Set mode:</b> <code>/blocklistmode mute</code> - <b>Mutes users for blocked content.</b>
<b>Enable deletion:</b> <code>/blocklistdelete yes</code> - <b>Deletes blocked messages.</b>
<b>Set reason:</b> <code>/setblocklistreason Policy violation</code> - <b>Sets default reason.</b>
<b>View triggers:</b> <code>/blocklist</code> - <b>Lists all settings.</b>
<b>Remove trigger:</b> <code>/rmblocklist spam*</code> - <b>Removes trigger.</b>
<b>Clear all:</b> <code>/unblocklistall</code> - <b>Removes all triggers (creator only).</b>
    """
    
    buttons = [
        ("Close", "blocklist_close"),
        ("Back", "blocklist_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('blocklist_'))
def handle_help_callback(call):
    try:
        if call.data == 'blocklist_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'blocklist_back':
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
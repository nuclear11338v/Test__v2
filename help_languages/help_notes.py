from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_notes_help():
    """Generate main help menu content"""
    help_menu = """
<b>Help Message for Notes Module</b>

<i>The Notes module allows group admins to save and manage notes in groups, which can be text or media (photo, video, audio, document) with optional buttons. Users can retrieve notes using commands or hashtags, and admins can make notes private to deliver via PM.</i>

<b>Available Commands</b>
<code>/save</code>
<b>Purpose:</b> <i>Saves a text note or media note (if replying to media).</i>

<b>Usage:</b>
<code>/save [notename] [text]</code> - <b>Saves a text note.</b>
Reply to a photo, video, audio, or document with <code>/save [notename] [caption].</code>
<b>Supports buttons:</b> [button text](buttonurl://url).

<b>Example:</b>
<code>/save rules Be kind! [Join](buttonurl://t.me/example)</code> - <b>Saves text note with a button.</b>
Reply to a photo with <code>/save photo1 Nice pic</code> - Saves photo note with caption.

<b>Note:</b>
<i>Max 200 notes per group.</i>
<code>/get</code>
<b>Purpose:</b> <i>Retrieves a note by name.</i>

<blockquote>Usage: /get [notename]</blockquote>
<b>Behavior:</b>
<i>Sends note directly (text or media with buttons) unless private notes are enabled.
If private, sends a PM to view the note.</i>

<b>Example:</b>
<code>/get rules</code> - <b>Sends the "rules" note.</b>

<b>Note:</b> <i>Available to all users.</i>
<code>/notes</code> <b>or</b> <code>/saved</code>
<b>Purpose:</b> <i>Lists all note names in the group.</i>
<b>Usage:</b> <code>/notes</code> <b>or</b> <code>/saved</code>

<code>/clear</code>
<b>Purpose:</b> <i>Deletes a specific note.</i>
<b>Usage:</b> <blockquote>/clear [notename]</blockquote>

<b>Example:</b>
<code>/clear rules</code> - <b>Deletes the "rules" note.</b>
<code>/clearall</code>
<b>Purpose:</b> <i>Deletes all notes in the group.</i>

<blockquote>Usage: /clearall</blockquote>
<b>Example:</b>
<code>/clearall</code> - <b>Removes all notes.</b>
<code>/privatenotes on/off</code>
<b>Purpose:</b> <i>Enables/disables private note delivery via PM.</i>

<blockquote>Usage: /privatenotes [on/off]</blockquote>
<b>Example:</b>
<code>/privatenotes on</code> - <b>Notes sent as PM.</b>
<code>/privatenotes off</code> - <b>Notes sent directly in chat.</b>
<blockquote>#notename</blockquote>
<b>Purpose:</b> <i>Retrieves a note using a hashtag.</i>

<blockquote>Usage: #notename</blockquote>
<b>Example:</b>
<code>#rules</code> - <b>Sends the "rules" note (or PM if private).</b>
<b>Important Notes</b>
<code>Admin Only:</code>
<blockquote>/save, /clear, /clearall, and /privatenotes.</blockquote>

<b>Note Types:</b>
<b>Text:</b> <i>Simple text with optional buttons.</i>
<b>Media:</b> <i>Photo, video, audio, or document with optional caption and buttons.</i>
<b>Buttons:</b> <i>Use [text](buttonurl://url) in text/caption for inline buttons (one row).</i>

<b>Formatting:</b> <i>Notes use MarkdownV2; ensure valid syntax for buttons and text.</i>

<b>Example Workflow</b>
<b>Save a note:</b> <code>/save rules Be kind! [Join](buttonurl://t.me/example)</code> - <b> Saves text note with button.</b>
<b>Save media:</b> Reply to a photo with <code>/save photo1 Nice pic</code> - Saves photo note.
<b>Enable private notes:</b> <code>/privatenotes on</code> - <b>Notes sent via PM.</b>
<b>View notes:</b> <code>/notes</code> - <b>Lists all notes.</b>
<b>Retrieve note:</b> <code>"/get rules"</code> or <code>"#rules"</code> - <b>Sends note or PM.</b>
<b>Delete note:</b> <code>/clear rules</code> - <b>Removes "rules" note.</b>
<b>Clear all:</b> <code>/clearall</code> - <b>Deletes all notes.</b>

<blockquote>- 200 Notes per group</blockquote>

<b>Buttons Not Showing:</b>
<b>Check</b>
<blockquote>[text](buttonurl://url) syntax.</blockquote>
    """
    
    buttons = [
        ("Close", "notes_close"),
        ("Back", "notes_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('notes_'))
def handle_help_callback(call):
    try:
        if call.data == 'notes_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'notes_back':
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
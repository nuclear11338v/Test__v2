from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_locks_help():
    """Generate main help menu content"""
    help_menu = """
<b>Locks Module Help</b>

<i>The Locks module enables admins to restrict specific types of content or actions in chats.</i>

<b>Available Commands</b>
<code>/lock</code>
<b>Purpose:</b> <i>Locks a specific content type or action, preventing non-admins from sending it.</i>

<b>Usage:</b> <code>/lock</code>
<b>Valid types:</b> all, album, invitelink, anonchannel, audio, bot, botlink, button, commands, comment, contact, document, email, emoji, emojicustom, emojigame, externalreply, game, gif, inline, location, phone, photo, poll, spoiler, text, url, video, videonote, voice.
all: Disables all messaging.

<b>Example:</b>
<code>/lock photo</code> - <b>Prevents non-admins from sending photos.</b>
<code>/lock all</code> - <b>Locks the entire chat for non-admins.</b>

<blockquote>/unlock</blockquote>
<b>Purpose:</b> <i>Unlocks a specific content type or action, allowing non-admins to send it.</i>
<b>Usage:</b> <code>/unlock</code> Same valid types as <code>/lock.</code>
all: Restores default chat permissions.

<b>Example:</b>
<code>/unlock photo</code> - <b>Allows non-admins to send photos.</b>
<code>/unlock all</code> - <b>Unlocks the entire chat.</b>

<b>Lock Types:</b>
<b>all:</b> <i>Blocks all messages (sets no permissions).</i>
<b>album:</b> <i>Blocks media groups.</i>
<b>invitelink:</b> <i>Blocks Telegram invite links.</i>
<b>anonchannel:</b> <i>Blocks anonymous channel messages.</i>
<b>audio:</b> <i>Blocks audio files.</i>
<b>bot:</b> <i>Blocks messages from bots.</i>
<b>botlink:</b> <i>Blocks bot mentions.</i>
<b>button:</b> <i>Blocks messages with inline keyboards.</i>
<b>commands:</b> <i>Blocks bot commands (/command).</i>
<b>comment:</b> <i>Blocks topic messages.</i>
<b>contact:</b> <i>Blocks contact sharing.</i>
<b>document:</b> <i>Blocks documents/files.</i>
<b>email:</b> <i>Blocks email addresses.</i>
<b>emoji:</b> <i>Blocks Unicode emojis (U+1F300–U+1F9FF).</i>
<b>emojicustom:</b> <i>Blocks animated stickers.</i>
<b>emojigame:</b> <i>Blocks game messages.</i>
<b>externalreply:</b> <i>Blocks replies to forwarded messages.</i>
<b>game:</b> <i>Blocks Telegram games</i>.
<b>gif:</b> <i>Blocks animations/GIFs.</i>
<b>inline:</b> <i>Blocks inline bot messages.</i>
<b>location:</b> <i>Blocks location sharing.</i>
<b>phone:</b> <i>Blocks phone numbers.</i>
<b>photo:</b> <i>Blocks photos.</i>
<b>poll:</b> <i>Blocks polls.</i>
<b>spoiler:</b> <i>Blocks messages with spoilers.</i>
<b>text:</b> <i>Blocks plain text.</i>
<b>url:</b> <i>Blocks URLs.</i>
<b>video:</b> <i>Blocks videos.</i>
<b>videonote:</b> <i>Blocks video notes.</i>

<b>Example Workflow</b>
<b>Lock content:</b> <code>/lock url</code> - <b>Prevents non-admins from sending URLs.</b>
<b>Lock chat:</b> <code>/lock all</code> - <b>Disables all messaging for non-admins.</b>
<b>Unlock content:</b> <code>/unlock url</code> - <b>Allows URLs again.</b>
<b>Unlock chat:</b> <code>/unlock all</code> - <b>Restores messaging permissions.</b>
    """
    
    buttons = [
        ("Close", "locks_close"),
        ("Back", "locks_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('locks_'))
def handle_help_callback(call):
    try:
        if call.data == 'locks_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'locks_back':
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
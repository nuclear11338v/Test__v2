from telebot import TeleBot, types
import traceback
from config import BOT_TOKEN, logger, bot
from help_languages.help_english import create_english_help

user_stats = {}

import re
def format_message(text: str) -> str:
    """Clean and format message text"""
    return text.strip().replace('    ', '')

def create_custom_help():
    """Generate main help menu content"""
    help_menu = """
<b>Help Message for Custom Commands Module</b>

<i>The Custom Commands module lets group admins create and manage custom group commands that trigger text, media (photos/videos), or buttons. Commands can be for all users, admins only, or non-admins only.</i>

<b>Commands:</b>
<pre>/add_command [command] [response]::[button_text|button_url;...]</pre>
<b>Purpose:</b> Adds a command for all users.

<b>Usage:</b>
<pre>/add_command [command] [response]</pre> - <b>Text response.</b>
<pre>/add_command [command] [response]::[button_text|button_url;...]</pre> - <b>Text with buttons.</b>

<b>Supports:</b>
<i>[text](buttonurl://url) in response.</i>
<b>Details:</b>
<b>[command]</b>: <i>Name (e.g., hello, no /). Not kick, ban, etc.</i>
<b>[response]:</b> <i>Text with placeholders: {username}, {first_name}, {last_name}, {group}, {id}.</i>
<i>[button_text|button_url;...]: Buttons (e.g., Google|https://google.com).</i>

<b>Example:</b>
<pre>/add_command hello Hi {first_name}!::Google|https://google.com</pre>
<pre>/add_command info [Google](buttonurl://https://google.com)</pre>

<b>Admin restricted:</b>
<pre>/rcommand [command] [response]::[button_text|button_url;...]</pre>
<b>Purpose:</b> <i>Admin-only command.</i>
<b>Usage:</b> <i>Same as /add_command, but only admins can use.</i>

<b>Example:</b>
<pre>/rcommand rules Admins: Rules!::Rules|https://example.com</pre>

<b>Non-Admin only:</b>
<pre>/ucommand [command] [response]::[button_text|button_url;...]</pre>
<b>Purpose</b>: <i>Non-admin-only command.</i>
<b>Usage:</b> <i>Same as /add_command, but only non-admins can use.</i>

<b>Example:</b>
<pre>/ucommand faq FAQs: [FAQ](buttonurl://https://faq.com)</pre>
<pre>/add_media_command [command] [photo|video] [media_url]::[caption]::[button_text|button_url;...]</pre>

<b>Purpose:</b> <i>Adds a command to send a photo/video for all users.</i>

<b>Usage:</b>
<pre>/add_media_command [command] [photo|video] [media_url]</pre> - <i>Media only.</i>
<pre>/add_media_command [command] [photo|video] [media_url]::[caption]::[buttons]</pre>- <i>With caption/buttons.</i>

<b>Details:</b>
[media_url]: Direct photo/video URL.
[caption]: Optional, supports placeholders.

<b>Example:</b>
<pre>/add_media_command meme photo https://example.com/meme.jpg::Funny!::More|https://memes.com</pre>

<code>/remove [command]</code>
<b>Purpose:</b> <i>Deletes a command.</i>
<b>Usage</b>: <code>/remove [command]</code>
<b>Example</b>: <code>/remove hello</code>

<code>/commands</code>
<b>Purpose:</b> <i>Lists all commands, showing responses, media, type (all/admin/user), and buttons.</i>
<blockquote>Usage: /commands</blockquote>

<b>Type:</b> all/users/admin Only: /add_command, /rcommand, /ucommand, /add_media_command, /remove

<b>Command Rules: No reserved names (kick, ban, etc).</b>

<b>Buttons</b>: Use text|url;text2|url2 or [text](buttonurl://url).
<b>MarkdownV2:</b> Supports *bold*, _italic_, [link](url). Special chars auto-escaped.
<b>Media:</b> URLs must be direct and accessible.

<b>Errors:</b> Check command syntax, URLs, or bot permissions if issues arise.

<b>Example Workflow</b>
<blockquote>/add_command greet Hi {first_name}!::Join|https://t.me/group</blockquote>
<blockquote>/rcommand admininfo Admins: [Status](buttonurl://https://example.com)</blockquote>
<blockquote>/ucommand help [FAQ](buttonurl://https://faq.com)</blockquote>
<blockquote>/add_media_command promo video https://example.com/promo.mp4::Watch!</blockquote>

<code>/commands</code> - <b>List all.</b>
<code>/remove greet</code> - <b>Delete command.</b>

<b>Troubleshooting:</b>
<i>Command Fails: Verify command exists (/commands), user permissions, bot permissions.</i>

<b>Button Issues:</b> Ensure text|url or [text](buttonurl://url) format.
<b>Media Fails:</b> Check URL validity.
    """
    
    buttons = [
        ("Close", "custom_close"),
        ("Back", "custom_back")
    ]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(buttons[0][0], callback_data=buttons[0][1]),
        types.InlineKeyboardButton(buttons[1][0], callback_data=buttons[1][1])
    )
    
    return format_message(help_menu), markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('custom_'))
def handle_help_callback(call):
    try:
        if call.data == 'custom_close':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return

        if call.data == 'custom_back':
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